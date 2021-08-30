import datetime as dt
from typing import Optional, Any
from uuid import UUID

from common.schemas import BaseSchema


class NotificationReadData(BaseSchema):
    event: str
    payload: Any


class NotificationRead(BaseSchema):
    id: UUID
    created_at: Optional[dt.datetime]
    profile_id: UUID
    data: NotificationReadData
    read: bool
    visited: bool


class NotificationCreate(BaseSchema):
    profile_id: UUID
    data: NotificationReadData
