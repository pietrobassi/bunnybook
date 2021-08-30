import datetime as dt
from typing import List, Optional
from uuid import UUID

from fastapi import Depends, Query, BackgroundTasks
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from starlette import status

from auth.models import User
from auth.security import get_user, get_optional_user
from comment.models import Comment
from comment.notifications import CommentNotificationService
from comment.schemas import CommentCreateRead, CommentCreate, CommentRead
from comment.service import CommentService
from common.injection import on
from common.rate_limiter import RateLimitTo
from post.api_utils import PostApiUtils
from post.service import PostService

comment_router = InferringRouter()


@cbv(comment_router)
class CommentApi:
    _service: CommentService = Depends(on(CommentService))
    _post_service: PostService = Depends(on(PostService))
    _post_api_utils: PostApiUtils = Depends(on(PostApiUtils))
    _notifications: CommentNotificationService = Depends(
        on(CommentNotificationService))

    @comment_router.post(
        "/posts/{post_id}/comments",
        response_model=CommentCreateRead,
        status_code=status.HTTP_201_CREATED,
        dependencies=[Depends(RateLimitTo(times=5, seconds=1))])
    async def create_comment(
            self,
            post_id: UUID,
            comment_in: CommentCreate,
            background_tasks: BackgroundTasks,
            user: User = Depends(get_user)):
        """Create a new comment under a post."""
        await self._post_api_utils.check_user_can_see_post(user, post_id)
        new_comment = await self._service.create_comment(
            Comment(**comment_in.dict(),
                    post_id=post_id,
                    profile_id=user.id,
                    username=user.username))
        background_tasks.add_task(
            self._notifications.create_comment_notification,
            post_id, user.id, user.username, new_comment.content)
        return new_comment

    @comment_router.get(
        "/posts/{post_id}/comments",
        response_model=List[CommentRead],
        dependencies=[Depends(RateLimitTo(times=5, seconds=1))])
    async def get_comments(
            self,
            post_id: UUID,
            older_than: Optional[dt.datetime] = Query(None),
            limit: Optional[int] = Query(10, ge=1, le=20),
            user: Optional[User] = Depends(get_optional_user)):
        """Get comments under a post."""
        await self._post_api_utils.check_user_can_see_post(user, post_id)
        return await self._service.find_comments_by_post_id(
            post_id, older_than, limit)
