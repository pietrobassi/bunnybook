from typing import Optional

import aioredis
from aioredis import Redis
from injector import singleton, inject


@singleton
class RedisManager:
    """Service that wraps a Redis instance and establishes connection with a
    running Redis server."""

    @inject
    def __init__(self, redis_uri: str):
        self._redis_uri = redis_uri
        self._redis: Optional[Redis] = None

    async def start(self):
        """Establish connection with Redis."""
        try:
            self._redis = await aioredis.create_redis(
                self._redis_uri,
                encoding="utf-8")
        except Exception as e:
            raise Exception("Couldn't connect to Redis", e)

    @property
    def redis(self) -> Redis:
        """Return wrapped Redis instance."""
        return self._redis
