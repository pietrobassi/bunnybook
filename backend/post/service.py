import datetime as dt
from typing import Optional, List
from uuid import UUID

from injector import inject, singleton

from auth.models import User
from notification.manager import NotificationManager
from post.models import Post
from post.repo import PostRepo
from profiles.service import ProfilesService


@singleton
class PostService:
    @inject
    def __init__(
            self,
            repo: PostRepo,
            profiles_service: ProfilesService,
            notification_manager: NotificationManager):
        self._repo = repo
        self._profiles_service = profiles_service
        self._notification_manager = notification_manager

    async def save_post(self, new_post: Post) -> Post:
        """Save a new post."""
        return await self._repo.save_post(new_post=new_post)

    async def find_posts_by_wall_profile_id(
            self,
            wall_profile_id: UUID,
            user: Optional[User],
            older_than: Optional[dt.datetime] = None,
            limit: Optional[int] = 10) -> List[Post]:
        """Find posts by wall profile id (paginated by creation date)."""
        return await self._repo.find_posts_by_wall_profile_id(
            wall_profile_id=wall_profile_id,
            include_friends=user and (
                    user.id == wall_profile_id
                    or await self._profiles_service.is_friend_with(
                user.id, wall_profile_id)),
            older_than=older_than,
            limit=limit)

    async def find_post_by_id(self, post_id: UUID) -> Optional[Post]:
        """Find a post by its id."""
        return await self._repo.find_post_by_id(post_id=post_id)

    async def delete_post(self, post_id: UUID) -> Optional[Post]:
        """Delete an existing post."""
        return await self._repo.delete_post(post_id=post_id)
