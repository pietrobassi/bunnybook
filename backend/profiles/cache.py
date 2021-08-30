import datetime as dt
import json
from typing import List, Optional
from uuid import UUID

from fastapi.encoders import jsonable_encoder
from injector import singleton, inject

from common.cache import fail_silently
from common.injection import Cache
from database.utils import map_to
from profiles.models import Relationship, ProfileShort


@singleton
class ProfilesCache:
    RELATIONSHIP_EX = int(dt.timedelta(minutes=10).total_seconds())

    @inject
    def __init__(self, cache: Cache):
        self._cache = cache

    @fail_silently()
    async def get_relationship(
            self,
            profile_id: UUID,
            other_profile_id: UUID) -> str:
        min_id, max_id = min(profile_id, other_profile_id), \
                         max(profile_id, other_profile_id)
        relationship = await self._cache.get(
            f"profiles:{min_id}:relationships:{max_id}")
        if relationship and min_id != profile_id:
            if relationship == Relationship.INCOMING_FRIEND_REQUEST.value:
                return Relationship.OUTGOING_FRIEND_REQUEST.value
            elif relationship == Relationship.OUTGOING_FRIEND_REQUEST.value:
                return Relationship.INCOMING_FRIEND_REQUEST.value
        return relationship

    @fail_silently()
    async def set_relationship(
            self,
            profile_id: UUID,
            other_profile_id: UUID,
            relationship: Relationship) -> str:
        # keep ids in lexicographic order to avoid the need for duplicate
        # entries
        min_id, max_id = min(profile_id, other_profile_id), \
                         max(profile_id, other_profile_id)
        # swap directional relationships if needed
        if relationship and min_id != profile_id:
            if relationship == Relationship.INCOMING_FRIEND_REQUEST:
                relationship = Relationship.OUTGOING_FRIEND_REQUEST
            elif relationship == Relationship.OUTGOING_FRIEND_REQUEST:
                relationship = Relationship.INCOMING_FRIEND_REQUEST
        return await self._cache.set(
            f"profiles:{min_id}:relationships:{max_id}",
            relationship.value,
            expire=ProfilesCache.RELATIONSHIP_EX)

    @fail_silently()
    async def unset_relationship(
            self,
            profile_id: UUID,
            other_profile_id: UUID,
            delete_cached_friends: bool = False) -> int:
        min_id, max_id = min(profile_id, other_profile_id), \
                         max(profile_id, other_profile_id)
        return await self._cache.delete(
            f"profiles:{min_id}:relationships:{max_id}",
            *([f"profiles:{profile_id}:friends",
               f"profiles:{other_profile_id}:friends"]
              if delete_cached_friends else []))

    @fail_silently()
    async def get_friends(self, profile_id: UUID) \
            -> Optional[List[ProfileShort]]:
        json_friends = await self._cache.get(f"profiles:{profile_id}:friends")
        return map_to(json.loads(json_friends), List[ProfileShort]) \
            if json_friends else None

    @fail_silently()
    async def set_friends(
            self,
            profile_id: UUID,
            friends: List[ProfileShort]) -> None:
        return await self._cache.set(
            f"profiles:{profile_id}:friends",
            json.dumps(jsonable_encoder(friends)),
            expire=ProfilesCache.RELATIONSHIP_EX)

    @fail_silently()
    async def unset_friends(self, profile_ids: List[UUID]) -> None:
        return await self._cache.delete(*[f"profiles:{profile_id}:friends"
                                          for profile_id in profile_ids])
