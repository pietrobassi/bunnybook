from datetime import timedelta
from typing import Optional

from pydantic import BaseSettings


class Settings(BaseSettings):
    prod: bool = False
    fastapi_log_level: str = "info"
    avatar_data_folder: str = "_data-dev/avatar-data"

    postgres_uri: str = "bunny:bunny@localhost:5432/bunnybook"
    postgres_min_pool_size: int = 1
    postgres_max_pool_size: int = 5

    cache_uri: str = "redis://127.0.0.1:6379"
    pubsub_uri: str = "redis://127.0.0.1:6380"

    neo4j_uri: str = "neo4j://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "secret"

    jwt_secret: str = "secret"
    jwt_algorithm: str = "HS256"
    jwt_expiration_seconds: int = timedelta(minutes=15).total_seconds()
    jwt_refresh_expiration_seconds: int = timedelta(weeks=2).total_seconds()

    sentry_dsn: Optional[str] = None


cfg = Settings()
sentry_config = dict(
    dsn=cfg.sentry_dsn
)
