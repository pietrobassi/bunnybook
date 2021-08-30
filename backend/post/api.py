import datetime as dt
from typing import List, Optional
from uuid import UUID

from fastapi import Depends, HTTPException, status, Query, BackgroundTasks
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter

from auth.models import User
from auth.security import get_user, get_optional_user
from common.injection import on
from common.rate_limiter import RateLimitTo
from post.api_utils import PostApiUtils
from post.models import Post
from post.notifications import PostNotificationService
from post.schemas import PostRead, PostCreate, PostCreateRead
from post.service import PostService
from profiles.service import ProfilesService

post_router = InferringRouter()


@cbv(post_router)
class PostApi:
    _service: PostService = Depends(on(PostService))
    _api_utils: PostApiUtils = Depends(on(PostApiUtils))
    _profiles_service: ProfilesService = Depends(on(ProfilesService))
    _notifications: PostNotificationService = Depends(
        on(PostNotificationService))

    @post_router.post(
        "/posts",
        response_model=PostCreateRead,
        status_code=status.HTTP_201_CREATED,
        dependencies=[Depends(RateLimitTo(times=5, seconds=1))])
    async def create_post(
            self,
            post_in: PostCreate,
            background_tasks: BackgroundTasks,
            user: User = Depends(get_user)):
        """Create a new post on a profile's wall."""
        post_in.wall_profile_id = post_in.wall_profile_id or user.id
        if not await self._profiles_service.is_friend_with(
                user.id, post_in.wall_profile_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
        post = await self._service.save_post(Post(
            **post_in.dict(),
            profile_id=user.id,
            username=user.username))
        background_tasks.add_task(
            self._notifications.create_post_notification,
            post.id, user.id, user.username, post.content, post.wall_profile_id)
        return post

    @post_router.get(
        "/posts",
        response_model=List[PostRead],
        dependencies=[Depends(RateLimitTo(times=5, seconds=1))])
    async def get_posts(
            self,
            wall_profile_id: UUID,
            older_than: Optional[dt.datetime] = Query(None),
            limit: Optional[int] = Query(10, ge=1, le=20),
            user: Optional[User] = Depends(get_optional_user)):
        """Return public posts on a profile's wall; if logged user is friend
        with wall owner, posts for friends only are included as well."""
        return await self._service.find_posts_by_wall_profile_id(
            wall_profile_id, user=user, older_than=older_than, limit=limit)

    @post_router.get(
        "/posts/{post_id}",
        response_model=PostRead,
        dependencies=[Depends(RateLimitTo(times=5, seconds=1))])
    async def get_post_by_id(
            self,
            post_id: UUID,
            user: Optional[User] = Depends(get_optional_user)):
        """Get a post by its id."""
        return await self._api_utils.check_user_can_see_post(user, post_id)

    @post_router.delete(
        "/posts/{post_id}",
        status_code=status.HTTP_204_NO_CONTENT,
        dependencies=[Depends(RateLimitTo(times=5, seconds=1))])
    async def delete_post(
            self,
            post_id: UUID,
            user: User = Depends(get_user)):
        """Delete a post. To perform the removal, logged user must be the author
        of the post or the post must be on his wall."""
        post = await self._service.find_post_by_id(post_id)
        if not post:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        if post.profile_id != user.id and post.wall_profile_id != user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
        if not await self._service.delete_post(post_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
