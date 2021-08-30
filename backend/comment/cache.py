import datetime as dt
import json
from typing import List, Optional
from uuid import UUID

from fastapi.encoders import jsonable_encoder
from injector import singleton, inject

from comment.models import Comment
from common.cache import fail_silently, hash_cache_key
from common.injection import Cache
from database.utils import map_to


@singleton
class CommentCache:
    COMMENTS_EX: int = int(dt.timedelta(minutes=1).total_seconds())

    @inject
    def __init__(self, cache: Cache):
        self._cache = cache

    @fail_silently()
    async def get_comments(
            self,
            post_id: UUID,
            older_than: dt.datetime) -> Optional[List[Comment]]:
        cached_comments = await self._cache.get(
            f"posts:{post_id}:comments:{hash_cache_key(older_than)}")
        return cached_comments and map_to(json.loads(cached_comments),
                                          List[Comment])

    @fail_silently()
    async def set_comments(
            self,
            comments: List[Comment],
            post_id: UUID,
            older_than: Optional[dt.date]) -> None:
        await self._cache.set(
            f"posts:{post_id}:comments:{hash_cache_key(older_than)}",
            json.dumps([jsonable_encoder(c) for c in comments]),
            expire=CommentCache.COMMENTS_EX)

    @fail_silently()
    async def unset_latest_comments(self, post_id: UUID) -> None:
        await self._cache.delete(
            f"posts:{post_id}:comments:{hash_cache_key(None)}")
