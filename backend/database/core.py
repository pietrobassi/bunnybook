from databases import Database
from sqlalchemy import MetaData

from config import cfg

# SQLAlchemy Metadata instance
metadata = MetaData()

# Database instance
db = Database(
    f"postgresql://{cfg.postgres_uri}",
    min_size=cfg.postgres_min_pool_size,
    max_size=cfg.postgres_max_pool_size)
