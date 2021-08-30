import datetime as dt
import json
from typing import List, Optional
from uuid import UUID

from fastapi.encoders import jsonable_encoder
from injector import singleton, inject

from common.cache import fail_silently, hash_cache_key
from common.injection import Cache
from database.utils import map_to
from post.models import Post


@singleton
class PostCache:
    POSTS_EX: int = int(dt.timedelta(minutes=1).total_seconds())

    @inject
    def __init__(self, cache: Cache):
        self._cache = cache

    @fail_silently()
    async def get_posts(
            self,
            wall_profile_id: UUID,
            include_friends: bool,
            older_than: dt.datetime) -> Optional[List[Post]]:
        cached_posts_ids = await self._cache.get(
            f"walls:{wall_profile_id}:posts:"
            f"{hash_cache_key(wall_profile_id, include_friends, older_than)}")
        cached_posts_ids = cached_posts_ids and json.loads(cached_posts_ids)
        if not cached_posts_ids:
            return None
        cached_posts = await self._cache.mget(
            *[f"posts:{post_id}" for post_id in cached_posts_ids])
        return (all(cached_posts) or None) and [map_to(json.loads(post), Post)
                                                for post in cached_posts]

    @fail_silently()
    async def get_post(self, post_id: UUID) -> Optional[Post]:
        cached_post = await self._cache.get(f"posts:{post_id}")
        return cached_post and map_to(json.loads(cached_post), Post)

    @fail_silently()
    async def set_post(self, post: Post) -> None:
        await self._cache.set(f"posts:{post.id}",
                              json.dumps(jsonable_encoder(post)),
                              expire=PostCache.POSTS_EX)

    @fail_silently()
    async def set_posts(
            self,
            posts: List[Post],
            wall_profile_id: UUID,
            include_friends: bool,
            older_than: Optional[dt.date]) -> None:
        params_cache_key = hash_cache_key(
            wall_profile_id, include_friends, older_than)
        posts_ids_key = f"walls:{wall_profile_id}:posts:{params_cache_key}"
        pipe = self._cache.pipeline()
        pipe.mset(posts_ids_key, json.dumps([str(post.id) for post in posts]),
                  *list(sum([(f"posts:{post.id}",
                              json.dumps(jsonable_encoder(post)))
                             for post in posts], ())))
        for key in [posts_ids_key, *[f"posts:{post.id}" for post in posts]]:
            pipe.expire(key, PostCache.POSTS_EX)
        await pipe.execute()

    @fail_silently()
    async def unset_posts_ids(
            self,
            wall_profile_id: UUID,
            include_friends: bool,
            older_than: Optional[dt.date]) -> None:
        await self._cache.delete(
            f"walls:{wall_profile_id}:posts:"
            f"{hash_cache_key(wall_profile_id, include_friends, older_than)}")

    @fail_silently()
    async def unset_post(self, post_id: UUID) -> None:
        await self._cache.delete(f"posts:{post_id}")
