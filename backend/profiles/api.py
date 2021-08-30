from typing import List, Literal, Optional
from uuid import UUID

from fastapi import Depends, HTTPException, Query, BackgroundTasks
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from starlette import status

from auth.models import User
from auth.security import get_user
from common.injection import on
from common.rate_limiter import RateLimitTo
from profiles.models import Relationship
from profiles.notifications import ProfilesNotificationService
from profiles.schemas import ProfileRead
from profiles.service import ProfilesService

profiles_router = InferringRouter()


@cbv(profiles_router)
class ProfilesApi:
    _service: ProfilesService = Depends(on(ProfilesService))
    _notifications: ProfilesNotificationService = Depends(
        (on(ProfilesNotificationService)))

    @profiles_router.get(
        "/profiles",
        response_model=List[ProfileRead],
        dependencies=[Depends(RateLimitTo(times=10, seconds=1))])
    async def get_profiles_by_username_search(self, username_query: str):
        """Return a list of profiles whose usernames match the query."""
        return await self._service.find_profiles_by_username_search(
            username_query)

    @profiles_router.get(
        "/profiles/{profile_id}",
        response_model=ProfileRead,
        dependencies=[Depends(RateLimitTo(times=10, seconds=1))])
    async def get_profile_by_id(self, profile_id: UUID):
        """Get profile's data by profile id."""
        return await self._service.find_profile_by_profile_id(profile_id)

    @profiles_router.post(
        "/profiles/{profile_id}/outgoing_friend_requests/{target_profile_id}",
        status_code=status.HTTP_201_CREATED,
        dependencies=[Depends(RateLimitTo(times=3, seconds=1))])
    async def create_friend_request(
            self,
            profile_id: UUID,
            target_profile_id: UUID,
            background_tasks: BackgroundTasks,
            user: User = Depends(get_user)):
        """Send a friend request from one profile to another."""
        if user.id != profile_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
        if user.id == target_profile_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
        await self._service.create_friend_request(
            requester_profile_id=profile_id,
            target_profile_id=target_profile_id)
        background_tasks.add_task(
            self._notifications.create_new_friendship_request_notification,
            requester_profile_id=profile_id,
            requester_username=user.username,
            target_profile_id=target_profile_id)

    @profiles_router.post(
        "/profiles/{profile_id}/friends/{requester_profile_id}",
        status_code=status.HTTP_201_CREATED,
        dependencies=[Depends(RateLimitTo(times=5, seconds=1))])
    async def accept_friend_request(
            self,
            profile_id: UUID,
            requester_profile_id: UUID,
            background_tasks: BackgroundTasks,
            user: User = Depends(get_user)):
        """Accept an incoming friend request."""
        if user.id != profile_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
        await self._service.accept_friend_request(
            requester_profile_id=requester_profile_id,
            accepter_profile_id=profile_id)
        background_tasks.add_task(
            self._notifications.create_new_friend_notification,
            accepter_profile_id=profile_id,
            accepter_username=user.username,
            other_profile_id=requester_profile_id)

    @profiles_router.delete(
        "/profiles/{profile_id}/incoming_friend_requests/{requester_profile_id}",
        status_code=status.HTTP_204_NO_CONTENT,
        dependencies=[Depends(RateLimitTo(times=5, seconds=1))])
    async def reject_incoming_friend_request(
            self,
            profile_id: UUID,
            requester_profile_id: UUID,
            user: User = Depends(get_user)):
        """Reject an incoming friend request."""
        if user.id != profile_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
        return await self._service.reject_incoming_friend_request(
            requester_profile_id=requester_profile_id,
            rejecter_profile_id=profile_id)

    @profiles_router.delete(
        "/profiles/{profile_id}/outgoing_friend_requests/{target_profile_id}",
        status_code=status.HTTP_204_NO_CONTENT,
        dependencies=[Depends(RateLimitTo(times=5, seconds=1))])
    async def cancel_outgoing_friend_request(
            self,
            profile_id: UUID,
            target_profile_id: UUID,
            user: User = Depends(get_user)):
        """Cancel an outgoing friend request."""
        if user.id != profile_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
        return await self._service.cancel_outgoing_friend_request(
            canceler_profile_id=user.id,
            target_profile_id=target_profile_id)

    @profiles_router.delete(
        "/profiles/{profile_id}/friends/{friend_profile_id}",
        status_code=status.HTTP_204_NO_CONTENT,
        dependencies=[Depends(RateLimitTo(times=3, seconds=1))])
    async def remove_friend(
            self,
            profile_id: UUID,
            friend_profile_id: UUID,
            user: User = Depends(get_user)):
        """Remove a friend from logged user friends list."""
        if user.id != profile_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
        return await self._service.remove_friend(user.id, friend_profile_id)

    @profiles_router.get(
        "/profiles/{profile_id}/friend_suggestions",
        response_model=List[ProfileRead],
        dependencies=[Depends(RateLimitTo(times=5, seconds=1))])
    async def get_friend_suggestions(
            self,
            profile_id: UUID,
            username_gt: Optional[str] = None,
            limit: Optional[int] = Query(20, ge=1, le=50),
            user: User = Depends(get_user)):
        """Get friend suggestions (logged user's friends of friends)."""
        if user.id != profile_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
        return await self._service.find_friend_suggestions(
            user.id, username_gt, limit)

    @profiles_router.get(
        "/profiles/{profile_id}/friends/{friend_profile_id}/mutual_friends",
        response_model=List[ProfileRead],
        dependencies=[Depends(RateLimitTo(times=5, seconds=1))])
    async def get_mutual_friends(
            self,
            profile_id: UUID,
            friend_profile_id: UUID,
            username_gt: Optional[str] = None,
            limit: Optional[int] = Query(20, ge=1, le=50),
            user: User = Depends(get_user)):
        """Get mutual friends between two profiles."""
        if user.id != profile_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
        return await self._service.find_mutual_friends(
            user.id, friend_profile_id, username_gt, limit)

    @profiles_router.get(
        "/profiles/{profile_id}/friends",
        response_model=List[ProfileRead],
        dependencies=[Depends(RateLimitTo(times=5, seconds=1))])
    async def get_friends(
            self,
            profile_id: UUID,
            username_gt: Optional[str] = None,
            limit: Optional[int] = Query(20, ge=1, le=50)):
        """Get specified profile's friends."""
        return await self._service.find_friends(profile_id, username_gt, limit)

    @profiles_router.get(
        "/profiles/{profile_id}/friend_requests",
        response_model=List[ProfileRead],
        dependencies=[Depends(RateLimitTo(times=5, seconds=1))])
    async def get_friend_requests(
            self,
            profile_id: UUID,
            direction: Optional[Literal["incoming",
                                        "outgoing"]] = Query("outgoing"),
            username_gt: Optional[str] = None,
            limit: Optional[int] = Query(20, ge=1, le=50),
            user: User = Depends(get_user)):
        """Get incoming or outgoing friend requests."""
        if user.id != profile_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
        return await self._service.find_friend_requests(
            user.id, direction, username_gt, limit)

    @profiles_router.get(
        "/profiles/{profile_id}/relationships/{other_profile_id}",
        response_model=Relationship,
        dependencies=[Depends(RateLimitTo(times=10, seconds=1))])
    async def get_relationship(self, profile_id: UUID, other_profile_id: UUID):
        """Return current relationship between two profiles."""
        return await self._service.find_relationship(
            profile_id, other_profile_id)
