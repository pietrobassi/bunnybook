import datetime as dt
from typing import Optional
from uuid import UUID

from pydantic import BaseModel
from sqlalchemy import Column, String, Table, ForeignKey, DateTime, Text, \
    UniqueConstraint, Boolean

from database.core import metadata
from database.utils import uuid_pk, created_at, PgUUID

chat_group = Table(
    "chat_group", metadata,
    uuid_pk(),
    Column("name",
           Text),
    Column("private",
           Boolean,
           server_default="true"),
    Column("active",
           Boolean,
           server_default="true")
)

profile_chat_group = Table(
    "profile_chat_group", metadata,
    Column("profile_id", PgUUID, ForeignKey("profile.id", ondelete="CASCADE"),
           nullable=False),
    Column("chat_group_id", PgUUID,
           ForeignKey("chat_group.id", ondelete="CASCADE"),
           nullable=False),
    Column("name",
           Text, nullable=True)
)

chat_message_read_status = Table(
    "chat_message_read_status", metadata,
    uuid_pk(),
    Column("profile_id", PgUUID, ForeignKey("profile.id", ondelete="CASCADE"),
           nullable=False),
    Column("chat_group_id", PgUUID,
           ForeignKey("chat_group.id", ondelete="CASCADE"),
           nullable=False),
    Column("chat_message_id", PgUUID,
           ForeignKey("chat_message.id", ondelete="CASCADE"),
           nullable=False),
    Column("read_at",
           DateTime(timezone=True),
           nullable=False),
    UniqueConstraint("profile_id",
                     "chat_group_id",
                     name="profile_id_chat_group_id_idx")
)

chat_message = Table(
    "chat_message", metadata,
    uuid_pk(),
    created_at(index=True),
    Column("from_profile_id", PgUUID,
           ForeignKey("profile.id", ondelete="CASCADE"),
           nullable=False),
    Column("chat_group_id", PgUUID,
           ForeignKey("chat_group.id", ondelete="CASCADE"),
           nullable=False),
    Column("content", String),
)


class ChatMessage(BaseModel):
    id: Optional[UUID]
    created_at: Optional[dt.datetime]
    from_profile_id: UUID
    chat_group_id: UUID
    content: str


class ChatGroup(BaseModel):
    id: Optional[UUID]
    name: Optional[str]
    private: bool = True
    active: bool = True


class Conversation(BaseModel):
    from_profile_id: UUID
    from_profile_username: str
    content: str
    created_at: dt.datetime
    chat_group_id: UUID
    chat_group_name: str
    read_at: Optional[dt.datetime]


class PrivateChat(BaseModel):
    chat_group_id: UUID
    profile_id: UUID
    username: str
