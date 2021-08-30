import datetime as dt
from typing import Optional, List
from uuid import UUID

from injector import singleton, inject

from notification.models import Notification
from notification.repo import NotificationRepo


@singleton
class NotificationService:
    @inject
    def __init__(self, repo: NotificationRepo):
        self._repo = repo

    async def create_notification(
            self, new_notification: Notification) -> Notification:
        """Save a new notification."""
        return await self._repo.save_notification(new_notification)

    async def find_notifications_by_profile_id(
            self,
            profile_id: UUID,
            older_than: Optional[dt.datetime] = None,
            limit: Optional[int] = 10) -> List[Notification]:
        """Find notifications by profile id (paginated by creation date)."""
        return await self._repo.find_notifications_by_profile_id(
            profile_id=profile_id,
            older_than=older_than,
            limit=limit)

    async def count_unread_notifications_by_profile_id(
            self, profile_id: UUID) -> int:
        """Count unread notifications by profile id."""
        return await self._repo.count_unread_notifications_by_profile_id(
            profile_id)

    async def mark_notifications_as(
            self,
            notification_ids: List[UUID],
            read: Optional[bool] = None,
            visited: Optional[bool] = None) \
            -> List[Notification]:
        """Mark notifications as read and/or visited."""
        return await self._repo.update_notifications_read_visited_status(
            notification_ids=notification_ids,
            read=read,
            visited=visited)
