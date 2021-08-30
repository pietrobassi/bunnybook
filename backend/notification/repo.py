import datetime as dt
from typing import List, Optional
from uuid import UUID

from injector import singleton
from sqlalchemy import insert, select, update, literal, func, desc

from database.core import db
from database.utils import map_result
from notification.models import Notification, notification


@singleton
class NotificationRepo:
    @map_result
    async def save_notification(self, new_notification: Notification) \
            -> Notification:
        return await db.fetch_one(
            insert(notification)
                .values(new_notification.dict(exclude_none=True))
                .returning(notification))

    @map_result
    async def find_notifications_by_profile_id(
            self,
            profile_id: UUID,
            older_than: Optional[dt.datetime] = None,
            limit: int = 10) -> List[Notification]:
        older_than = older_than or dt.datetime.now(dt.timezone.utc)
        return await db.fetch_all(
            select([notification])
                .where(notification.c.profile_id == profile_id)
                .where(notification.c.created_at < older_than)
                .order_by(desc(notification.c.created_at))
                .limit(limit))

    @map_result
    async def count_unread_notifications_by_profile_id(self, profile_id: UUID) \
            -> int:
        return await db.fetch_val(
            select([func.count()])
                .where(notification.c.profile_id == profile_id)
                .where(notification.c.read == False))

    @map_result
    async def update_notifications_read_visited_status(
            self,
            notification_ids: List[UUID],
            read: Optional[bool] = None,
            visited: Optional[bool] = None) -> List[Notification]:
        return await db.fetch_all(
            update(notification)
                .where(notification.c.id.in_([literal(n)
                                              for n in notification_ids]))
                .values(**(dict(read=read)
                           if read is not None else {}),
                        **(dict(visited=visited)
                           if visited is not None else {}))
                .returning(notification))
