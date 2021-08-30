import datetime as dt
from typing import Optional, List
from uuid import UUID

from injector import singleton, inject
from sqlalchemy import insert, select, delete, desc, literal, update

from auth.models import profile
from database.core import db
from database.utils import map_result, map_to
from post.cache import PostCache
from post.models import Post, post, PostPrivacy


@singleton
class PostRepo:
    @inject
    def __init__(self, cache: PostCache):
        self._cache = cache

    async def save_post(self, new_post: Post) -> Post:
        saved_post = await db.fetch_one(
            insert(post)
                .values(new_post.dict(exclude_none=True,
                                      exclude={"username"}))
                .returning(post))
        saved_post: Post = map_to(saved_post, Post)
        saved_post.username = new_post.username
        await self._cache.unset_posts_ids(
            new_post.wall_profile_id, True, None)
        if new_post.privacy == PostPrivacy.PUBLIC:
            await self._cache.unset_posts_ids(
                new_post.wall_profile_id, False, None)
        return saved_post

    @map_result
    async def delete_post(self, post_id: UUID) -> Optional[Post]:
        deleted_post = await db.fetch_one(delete(post)
                                          .where(post.c.id == post_id)
                                          .returning(post))
        await self._cache.unset_post(post_id)
        return deleted_post

    async def find_posts_by_wall_profile_id(
            self,
            wall_profile_id: UUID,
            include_friends: bool = False,
            older_than: Optional[dt.datetime] = None,
            limit: int = 10) -> List[Post]:
        older_than_clause = older_than or dt.datetime.now(dt.timezone.utc)
        if (posts := await self._cache.get_posts(
                wall_profile_id, include_friends, older_than)) is not None:
            return posts
        in_clause_values = [
            privacy for privacy, should_include in
            zip([literal(PostPrivacy.PUBLIC.value),
                 literal(PostPrivacy.FRIENDS.value)],
                [True, include_friends]) if should_include]
        posts = await db.fetch_all(
            select([post, profile.c.username])
                .where(post.c.wall_profile_id == wall_profile_id)
                .where(post.c.profile_id == profile.c.id)
                .where(post.c.created_at < older_than_clause)
                .where(post.c.privacy.in_(in_clause_values))
                .group_by(post.c.id, profile.c.username)
                .order_by(desc(post.c.created_at))
                .limit(limit))
        posts = map_to(posts, List[Post])
        await self._cache.set_posts(
            posts, wall_profile_id, include_friends, older_than)
        return posts

    async def find_post_by_id(self, post_id: UUID) -> Optional[Post]:
        if cached_post := await self._cache.get_post(post_id):
            return cached_post
        post_by_id = await db.fetch_one(
            select([post, profile.c.username])
                .where(post.c.profile_id == profile.c.id)
                .where(post.c.id == post_id))
        post_by_id = map_to(post_by_id, Post)
        if post_by_id:
            await self._cache.set_post(post_by_id)
        return post_by_id

    async def increment_comments_count(self, post_id: UUID) -> int:
        return await self._alter_comments_count(post_id, +1)

    async def decrement_comments_count(self, post_id: UUID) -> int:
        return await self._alter_comments_count(post_id, -1)

    async def _alter_comments_count(self, post_id: UUID, value: int) -> int:
        result = await db.fetch_val(
            update(post)
                .where(post.c.id == post_id)
                .values(comments_count=post.c.comments_count + value)
                .returning(post.c.comments_count))
        await self._cache.unset_post(post_id)
        return result
