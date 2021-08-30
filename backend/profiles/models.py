import enum
from uuid import UUID

from pydantic import BaseModel


class ProfileShort(BaseModel):
    id: UUID
    username: str


class FriendshipRequest(BaseModel):
    profile_id: UUID
    target_profile_id: UUID


class Relationship(str, enum.Enum):
    FRIEND = "FRIEND"
    OUTGOING_FRIEND_REQUEST = "OUTGOING_FRIEND_REQUEST"
    INCOMING_FRIEND_REQUEST = "INCOMING_FRIEND_REQUEST"
    SELF = "SELF"
    NONE = "NONE"
