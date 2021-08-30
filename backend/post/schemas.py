import datetime as dt
from typing import Optional
from uuid import UUID

from pydantic import Field

from common.schemas import BaseSchema
from post.models import PostPrivacy


class PostCreate(BaseSchema):
    content: str = Field(min_length=1, max_length=4096)
    wall_profile_id: Optional[UUID]
    privacy: PostPrivacy = PostPrivacy.PUBLIC


class PostCreateRead(BaseSchema):
    id: UUID
    content: str
    created_at: dt.datetime
    updated_at: Optional[dt.datetime]
    wall_profile_id: UUID
    profile_id: UUID
    privacy: PostPrivacy
    comments_count: int = 0


class PostRead(PostCreateRead):
    username: str
