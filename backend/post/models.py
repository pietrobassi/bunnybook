import datetime as dt
import enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel
from sqlalchemy import Column, String, Table, ForeignKey, Enum, Integer

from database.core import metadata
from database.utils import uuid_pk, updated_at, created_at, PgUUID


class PostPrivacy(str, enum.Enum):
    PUBLIC = "PUBLIC"
    FRIENDS = "FRIENDS"


post = Table(
    "post", metadata,
    uuid_pk(),
    Column("content", String),
    created_at(index=True),
    updated_at(),
    Column("wall_profile_id", PgUUID,
           ForeignKey("profile.id", ondelete="CASCADE"),
           nullable=False),
    Column("profile_id", PgUUID,
           ForeignKey("profile.id", ondelete="CASCADE"),
           nullable=False),
    Column("privacy", Enum(PostPrivacy), nullable=False,
           server_default=f"{PostPrivacy.PUBLIC.value}"),
    Column("comments_count", Integer, nullable=False,
           server_default="0"),
)


class Post(BaseModel):
    id: Optional[UUID]
    content: str
    created_at: Optional[dt.datetime]
    updated_at: Optional[dt.datetime]
    wall_profile_id: UUID
    profile_id: UUID
    username: Optional[str]
    privacy: PostPrivacy
    comments_count: int = 0

