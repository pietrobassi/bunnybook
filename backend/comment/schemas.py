import datetime as dt
from uuid import UUID

from pydantic import Field

from common.schemas import BaseSchema


class CommentCreate(BaseSchema):
    content: str = Field(min_length=1, max_length=1024, regex="^$|.*\S+.*")


class CommentCreateRead(BaseSchema):
    id: UUID
    content: str
    created_at: dt.datetime
    post_id: UUID
    profile_id: UUID
    username: str


class CommentRead(BaseSchema):
    id: UUID
    content: str
    created_at: dt.datetime
    post_id: UUID
    profile_id: UUID
    username: str
