import datetime as dt
from typing import Optional
from uuid import UUID

from pydantic import BaseModel
from sqlalchemy import Column, String, Table, ForeignKey

from database.core import metadata
from database.utils import uuid_pk, created_at, PgUUID

comment = Table(
    "comment", metadata,
    uuid_pk(),
    Column("content", String),
    created_at(index=True),
    Column("post_id", PgUUID, ForeignKey("post.id", ondelete="CASCADE"),
           nullable=False),
    Column("profile_id", PgUUID,
           ForeignKey("profile.id", ondelete="CASCADE"),
           nullable=False),
)


class Comment(BaseModel):
    id: Optional[UUID]
    content: str
    created_at: Optional[dt.datetime]
    post_id: UUID
    profile_id: UUID
    username: Optional[str]
