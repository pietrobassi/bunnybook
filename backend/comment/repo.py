import datetime as dt
from typing import List, Set, Optional
from uuid import UUID

from injector import inject, singleton
from sqlalchemy import insert, select, desc

from auth.models import profile
from comment.cache import CommentCache
from comment.models import Comment, comment
from database.core import db
from database.utils import map_to
from post.repo import PostRepo


@singleton
class CommentRepo:
    @inject
    def __init__(self, post_repo: PostRepo, cache: CommentCache):
        self._post_repo = post_repo
        self._cache = cache

    @db.transaction()
    async def save_comment(self, new_comment: Comment) -> Comment:
        await self._post_repo.increment_comments_count(new_comment.post_id)
        saved_comment = await db.fetch_one(
            insert(comment)
                .values(new_comment.dict(exclude_none=True,
                                         exclude={"username"}))
                .returning(comment))
        saved_comment: Comment = map_to(saved_comment, Comment)
        saved_comment.username = new_comment.username
        await self._cache.unset_latest_comments(new_comment.post_id)
        return saved_comment

    async def find_comments_by_post_id(
            self,
            post_id: UUID,
            older_than: Optional[dt.datetime] = None,
            limit: int = 10) -> List[Comment]:
        older_than_clause = older_than or dt.datetime.now(dt.timezone.utc)
        if (comments := await self._cache.get_comments(post_id,
                                                       older_than)) is not None:
            return comments
        comments = await db.fetch_all(
            select([comment, profile.c.username])
                .where(comment.c.profile_id == profile.c.id)
                .where(comment.c.post_id == post_id)
                .where(comment.c.created_at < older_than_clause)
                .order_by(desc(comment.c.created_at))
                .limit(limit))
        await self._cache.set_comments(comments, post_id, older_than)
        return comments

    async def find_comments_authors_by_post_id(self, post_id: UUID) \
            -> Set[UUID]:
        results = await db.fetch_all(select([comment.c.profile_id.distinct()])
                                     .where(comment.c.post_id == post_id))
        return {row["profile_id"] for row in results}
