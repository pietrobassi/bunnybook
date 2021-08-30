from typing import Optional
from uuid import UUID

from fastapi import HTTPException
from injector import inject, singleton
from starlette import status

from auth.models import User
from post.models import Post, PostPrivacy
from post.service import PostService
from profiles.service import ProfilesService


@singleton
class PostApiUtils:
    @inject
    def __init__(
            self,
            service: PostService,
            profiles_service: ProfilesService):
        self._service = service
        self._profiles_service = profiles_service

    async def check_user_can_see_post(
            self, user: Optional[User], post_id: UUID) -> Post:
        """Determine whether a user has read permission over a specific post,
        checking current business logic driven privacy rules."""
        post = await self._service.find_post_by_id(post_id)
        if not post:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        if not user and post.privacy == PostPrivacy.FRIENDS \
                or post.privacy == PostPrivacy.FRIENDS \
                and user and user.id != post.wall_profile_id \
                and not await self._profiles_service.is_friend_with(
            user.id, post.wall_profile_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
        return post
