from typing import List, Optional, Literal
from uuid import UUID

from injector import singleton, inject
from sqlalchemy import select, desc, literal

from auth.models import profile
from chat.models import ChatGroup
from chat.repo import ChatRepo
from database.core import db
from database.graph import AsyncGraphDatabase
from database.utils import map_result, map_graph_result, map_to
from profiles.cache import ProfilesCache
from profiles.models import ProfileShort, Relationship


@singleton
class ProfilesRepo:
    @inject
    def __init__(self, cache: ProfilesCache, graph_db: AsyncGraphDatabase,
                 chat_repo: ChatRepo):
        self._cache = cache
        self._graph_db = graph_db
        self._chat_repo = chat_repo

    @map_result
    async def find_profiles_by_username_search(
            self,
            username: str,
            limit: int = 5) -> List[ProfileShort]:
        return await db.fetch_all(select([profile.c.id, profile.c.username])
            .where(profile.c.username.ilike(f"%{username}%"))
            .limit(limit)
            .order_by(
            desc(profile.c.username.ilike(f"{username}%"))))

    @map_result
    async def find_profile_by_id(self, profile_id: UUID) \
            -> Optional[ProfileShort]:
        return await db.fetch_one(select([profile])
                                  .where(profile.c.id == profile_id))

    @map_result
    async def find_profiles_by_ids(self, profile_ids: List[UUID]) \
            -> List[ProfileShort]:
        return await db.fetch_all(
            select([profile])
                .where(profile.c.id.in_([
                literal(profile_id) for profile_id in profile_ids])))

    async def save_friend_request(
            self,
            requester_profile_id: UUID,
            target_profile_id: UUID) -> None:
        await self._graph_db.write_tx(lambda tx: tx.run(f"""
        MATCH (requester:Profile {{id: '{requester_profile_id}'}})
        MATCH (target:Profile {{id: '{target_profile_id}'}})
        WHERE NOT (requester)-[:FRIEND]-(target)
        MERGE (requester)-[:FRIEND_REQUEST]-(target)"""))
        await self._cache.unset_relationship(requester_profile_id,
                                             target_profile_id)

    @db.transaction()
    async def save_friendship_relationship(
            self,
            requester_profile_id: UUID,
            accepter_profile_id: UUID) -> ChatGroup:
        chat_group = await self._chat_repo.find_private_chat_group(
            requester_profile_id, accepter_profile_id)
        if chat_group and not chat_group.active:
            await self._chat_repo.update_chat_group(chat_group.id, True)
        else:
            chat_group = await self._chat_repo.save_chat_group(
                [requester_profile_id, accepter_profile_id])
        await self._graph_db.write_tx(lambda tx: tx.run(f"""
        MATCH (requester:Profile {{id: '{requester_profile_id}'}})\
        -[r:FRIEND_REQUEST]->\
        (accepter:Profile {{id: '{accepter_profile_id}'}})
        DELETE r
        MERGE (requester)-[f:FRIEND]->(accepter)"""))
        await self._cache.unset_relationship(requester_profile_id,
                                             accepter_profile_id,
                                             delete_cached_friends=True)
        return chat_group

    async def delete_friend_request(
            self,
            from_profile_id: UUID,
            to_profile_id: UUID) -> None:
        await self._graph_db.write_tx(lambda tx: tx.run(f"""
        MATCH (requester:Profile {{id: '{from_profile_id}'}})\
        -[f:FRIEND_REQUEST]->\
        (rejecter:Profile {{id: '{to_profile_id}'}})
        DELETE f"""))
        await self._cache.unset_relationship(from_profile_id, to_profile_id)

    @db.transaction()
    async def delete_friend(
            self,
            profile_id: UUID,
            friend_profile_id: UUID) -> None:
        chat_group = await self._chat_repo.find_private_chat_group(
            profile_id, friend_profile_id)
        await self._chat_repo.update_chat_group(chat_group.id, False)
        await self._graph_db.write_tx(lambda tx: tx.run(f"""
        MATCH (requester:Profile {{id: '{profile_id}'}})\
        -[f:FRIEND]-\
        (rejecter:Profile {{id: '{friend_profile_id}'}})
        DELETE f"""))
        await self._cache.unset_relationship(profile_id,
                                             friend_profile_id,
                                             delete_cached_friends=True)

    async def find_friends(
            self,
            profile_id: UUID,
            username_gt: Optional[str] = None,
            limit: int = 10) -> List[ProfileShort]:
        if friends := await self._cache.get_friends(profile_id):
            return friends
        friends = await self._graph_db.read_tx(lambda tx: list(tx.run(f"""
        MATCH (profile:Profile {{id: '{profile_id}'}})\
        -[f:FRIEND]-\
        (friend:Profile)
        {f"WHERE friend.username > '{username_gt}'" if username_gt else ""}
        WITH friend
        ORDER BY friend.username
        LIMIT {limit}
        RETURN friend""")))
        friends = map_to(friends, List[ProfileShort], is_graph_result=True)
        await self._cache.set_friends(profile_id, friends)
        return friends

    @map_graph_result
    async def find_friends_of_friends(
            self,
            profile_id: UUID,
            username_gt: Optional[str] = None,
            limit: int = 10) -> List[ProfileShort]:
        return await self._graph_db.read_tx(lambda tx: list(tx.run(f"""
        MATCH (profile:Profile {{id: '{profile_id}'}})
        MATCH (profile)-[:FRIEND*2]-(friend_of_friends)
        WHERE NOT (profile)-[:FRIEND]-(friend_of_friends)
        {f"AND friend_of_friends.username > '{username_gt}'"
        if username_gt else ""}
        WITH DISTINCT friend_of_friends
        ORDER BY friend_of_friends.username
        LIMIT {limit}
        RETURN friend_of_friends""")))

    @map_graph_result
    async def find_mutual_friends(
            self,
            profile_id: UUID,
            other_profile_id: UUID,
            username_gt: Optional[str] = None,
            limit: int = 10) -> List[ProfileShort]:
        return await self._graph_db.read_tx(lambda tx: list(tx.run(f"""
        MATCH (profile:Profile {{id: '{profile_id}'}})
        -[:FRIEND]-\
        (mutual_friend)\
        -[:FRIEND]-\
        (other_profile:Profile {{id: '{other_profile_id}'}})
        {f"WHERE mutual_friend.username > '{username_gt}'"
        if username_gt else ""}
        WITH DISTINCT mutual_friend
        ORDER BY mutual_friend.username
        LIMIT {limit}
        RETURN mutual_friend""")))

    @map_graph_result
    async def find_friend_requests(
            self,
            profile_id: UUID,
            direction: Optional[Literal["incoming", "outgoing"]],
            username_gt: Optional[str] = None,
            limit: int = 10) -> List[ProfileShort]:
        return await self._graph_db.read_tx(lambda tx: list(tx.run(f"""
        MATCH (profile:Profile {{id: '{profile_id}'}})\
        {"<" if direction == "incoming" else ""}\
        -[f:FRIEND_REQUEST]-\
        {">" if direction == "outgoing" else ""}\
        (friend:Profile)
        {f"WHERE friend.username > '{username_gt}'" if username_gt else ""}
        WITH friend
        ORDER BY friend.username
        LIMIT {limit}
        RETURN friend""")))

    async def find_relationship(
            self,
            profile_id: UUID,
            other_profile_id: UUID) -> Relationship:
        if relationship := await self._cache.get_relationship(profile_id,
                                                              other_profile_id):
            return Relationship(relationship)
        if profile_id == other_profile_id:
            return Relationship.SELF
        result = await self._graph_db.read_tx(lambda tx: list(tx.run(f"""
        MATCH (profile:Profile {{id: '{profile_id}'}})\
        -[r]-\
        (other_profile:Profile {{id: '{other_profile_id}'}})
        RETURN profile, other_profile, type(r), (startNode(r) = profile)""")))
        if not result:
            relationship = Relationship.NONE
        else:
            relationship = result[0][2]
            if relationship == "FRIEND_REQUEST":
                is_from_profile_to_other_profile = result[0][3]
                relationship = Relationship.OUTGOING_FRIEND_REQUEST \
                    if is_from_profile_to_other_profile \
                    else Relationship.INCOMING_FRIEND_REQUEST
            elif relationship == "FRIEND":
                relationship = Relationship.FRIEND
        await self._cache.set_relationship(
            profile_id, other_profile_id, relationship)
        return relationship
