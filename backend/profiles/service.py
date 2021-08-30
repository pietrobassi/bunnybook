from typing import List, Literal, Optional
from uuid import UUID

from injector import singleton, inject

from chat.schemas import PrivateChatRead
from profiles.exceptions import UnexpectedRelationshipState
from profiles.models import Relationship, ProfileShort
from profiles.repo import ProfilesRepo
from pubsub.websocket import WebSockets


@singleton
class ProfilesService:
    @inject
    def __init__(self, repo: ProfilesRepo, ws: WebSockets):
        self._repo = repo
        self._ws = ws

    async def find_profiles_by_username_search(self, username: str) \
            -> List[ProfileShort]:
        """Return profiles that match username query string."""
        return await self._repo.find_profiles_by_username_search(username)

    async def find_profile_by_profile_id(self, profile_id: UUID) \
            -> ProfileShort:
        """Return profile by profile id."""
        return await self._repo.find_profile_by_id(profile_id)

    async def create_friend_request(
            self,
            requester_profile_id: UUID,
            target_profile_id: UUID) -> None:
        """Send a friend request from 'requester_profile_id' to
        'target_profile_id'."""
        await self._check_relationship(
            requester_profile_id,
            target_profile_id,
            [Relationship.NONE])
        await self._repo.save_friend_request(requester_profile_id,
                                             target_profile_id)

    async def accept_friend_request(
            self,
            requester_profile_id: UUID,
            accepter_profile_id: UUID) -> None:
        """Accept a friend request (where accepter is 'accepter_profile_id')
        that was previously sent by 'requester_profile_id'."""
        await self._check_relationship(
            requester_profile_id,
            accepter_profile_id,
            [Relationship.OUTGOING_FRIEND_REQUEST])
        chat_group = await self._repo.save_friendship_relationship(
            requester_profile_id,
            accepter_profile_id)
        profiles = await self._repo.find_profiles_by_ids([
            requester_profile_id, accepter_profile_id])
        for recipient in [requester_profile_id, accepter_profile_id]:
            other = [p for p in profiles if p.id != recipient][0]
            await self._ws.send(
                event="add_friend",
                payload=PrivateChatRead(
                    chat_group_id=chat_group.id,
                    profile_id=other.id,
                    username=other.username),
                to=recipient)

    async def reject_incoming_friend_request(
            self,
            requester_profile_id: UUID,
            rejecter_profile_id: UUID) -> None:
        """Reject a friend request (where rejecter is 'rejecter_profile_id')
        that was previously sent by 'requester_profile_id'."""
        await self._check_relationship(
            requester_profile_id,
            rejecter_profile_id,
            [Relationship.OUTGOING_FRIEND_REQUEST])
        await self._repo.delete_friend_request(
            from_profile_id=requester_profile_id,
            to_profile_id=rejecter_profile_id)

    async def cancel_outgoing_friend_request(
            self,
            canceler_profile_id: UUID,
            target_profile_id: UUID) -> None:
        """Delete the outgoing friend request that was previously sent from
        'canceler_profile_id' to 'target_profile_id'."""
        await self._check_relationship(
            canceler_profile_id,
            target_profile_id,
            [Relationship.OUTGOING_FRIEND_REQUEST])
        await self._repo.delete_friend_request(
            from_profile_id=canceler_profile_id,
            to_profile_id=target_profile_id)

    async def remove_friend(
            self,
            profile_id: UUID,
            friend_profile_id: UUID) -> None:
        """Delete friendship relationship between 'profile_id' and
        'friend_profile_id'."""
        await self._check_relationship(
            profile_id,
            friend_profile_id,
            [Relationship.FRIEND])
        await self._repo.delete_friend(profile_id, friend_profile_id)
        for recipient in [profile_id, friend_profile_id]:
            await self._ws.send(
                event="remove_friend",
                payload=profile_id if recipient != profile_id
                else friend_profile_id,
                to=recipient)

    async def find_friends(
            self,
            profile_id: UUID,
            username_gt: Optional[str] = None,
            limit: int = 10) -> List[ProfileShort]:
        """Return friends of profile_id (paginated by username)."""
        return await self._repo.find_friends(profile_id, username_gt, limit)

    async def find_friend_requests(
            self,
            profile_id: UUID,
            direction: Optional[Literal["incoming", "outgoing"]] = "outgoing",
            username_gt: Optional[str] = None,
            limit: int = 10) -> List[ProfileShort]:
        """Return friendship requests for profile_id, based on direction
        incoming/outgoing (paginated by username)."""
        return await self._repo.find_friend_requests(
            profile_id, direction, username_gt, limit)

    async def find_friend_suggestions(
            self,
            profile_id: UUID,
            username_gt: Optional[str] = None,
            limit: int = 10) -> List[ProfileShort]:
        """Return friend suggestions for profile_id (paginated by username)."""
        return await self._repo.find_friends_of_friends(
            profile_id, username_gt, limit)

    async def find_mutual_friends(
            self,
            profile_id: UUID,
            other_profile_id: UUID,
            username_gt: Optional[str] = None,
            limit: int = 10) -> List[ProfileShort]:
        """Return common friends between 'profile_id' and 'other_profile_id'
        (paginated by username)."""
        return await self._repo.find_mutual_friends(
            profile_id, other_profile_id, username_gt, limit)

    async def find_relationship(self, profile_id: UUID, other_profile_id: UUID) \
            -> Relationship:
        """Return current realtionship status between 'profile_id' and
        'other_profile_id'."""
        return await self._repo.find_relationship(profile_id, other_profile_id)

    async def is_friend_with(self, profile_id: UUID, other_profile_id: UUID) \
            -> bool:
        """Determine whether 'profile_id' and 'other_profile_id' are friends or
        not."""
        return profile_id == other_profile_id \
               or Relationship.FRIEND == await self._repo.find_relationship(
            profile_id, other_profile_id)

    async def _check_relationship(
            self,
            profile_id: UUID,
            other_profile_id: UUID,
            allowed_relationships: List[Relationship]):
        if await self.find_relationship(profile_id, other_profile_id) \
                not in allowed_relationships:
            raise UnexpectedRelationshipState()
