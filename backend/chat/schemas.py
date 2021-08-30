import datetime as dt
from typing import Optional
from uuid import UUID

from common.schemas import BaseSchema


class ChatMessageRead(BaseSchema):
    id: UUID
    created_at: dt.datetime
    from_profile_id: UUID
    chat_group_id: UUID
    content: str


class ConversationRead(BaseSchema):
    from_profile_id: UUID
    from_profile_username: str
    content: str
    created_at: dt.datetime
    chat_group_id: UUID
    chat_group_name: str
    read_at: Optional[dt.datetime]


class IsTypingWsMessage(BaseSchema):
    profile_id: UUID
    username: str
    chat_group_id: UUID


class PrivateChatRead(BaseSchema):
    chat_group_id: UUID
    profile_id: UUID
    username: str
