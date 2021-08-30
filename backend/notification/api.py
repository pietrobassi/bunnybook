import datetime as dt
from typing import List, Optional
from uuid import UUID

from fastapi import Query, Depends
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter

from common.injection import on
from common.rate_limiter import RateLimitTo
from notification.schemas import NotificationRead
from notification.service import NotificationService

notification_router = InferringRouter()


@cbv(notification_router)
class NotificationApi:
    _service: NotificationService = Depends(on(NotificationService))

    @notification_router.get(
        "/profiles/{profile_id}/notifications",
        response_model=List[NotificationRead],
        dependencies=[Depends(RateLimitTo(times=5, seconds=1))])
    async def get_notifications(
            self,
            profile_id: UUID,
            older_than: Optional[dt.datetime] = Query(None),
            limit: Optional[int] = Query(10, ge=1, le=20)):
        """Get notifications for a specific profile."""
        return await self._service.find_notifications_by_profile_id(
            profile_id, older_than=older_than, limit=limit)

    @notification_router.patch(
        "/profiles/{profile_id}/notifications",
        response_model=List[NotificationRead],
        dependencies=[Depends(RateLimitTo(times=5, seconds=1))])
    async def patch_notifications(
            self,
            notification_ids: List[UUID],
            read: Optional[bool] = Query(None),
            visited: Optional[bool] = Query(None)):
        """Mark specified notifications as read and/or visited."""
        return await self._service.mark_notifications_as(
            notification_ids, read, visited)
