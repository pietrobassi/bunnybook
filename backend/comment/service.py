import datetime as dt
from typing import Optional, List
from uuid import UUID

from injector import singleton, inject

from comment.models import Comment
from comment.repo import CommentRepo
from post.repo import PostRepo


@singleton
class CommentService:
    @inject
    def __init__(self, repo: CommentRepo, post_repo: PostRepo):
        self._repo = repo
        self._post_repo = post_repo

    async def create_comment(self, new_comment: Comment) -> Comment:
        """Save a new comment under a post."""
        return await self._repo.save_comment(new_comment=new_comment)

    async def find_comments_by_post_id(
            self,
            post_id: UUID,
            older_than: Optional[dt.datetime] = None,
            limit: Optional[int] = 10) -> List[Comment]:
        """Find comments under specified post (paginated by creation date)."""
        return await self._repo.find_comments_by_post_id(
            post_id=post_id,
            older_than=older_than,
            limit=limit)
