from asyncio import Queue, QueueFull, get_event_loop
from dataclasses import dataclass
from typing import List, Dict, Union, Set
from uuid import UUID

from fastapi.encoders import jsonable_encoder
from injector import singleton, inject

from auth.models import User
from common.log import logger
from notification.models import Notification, NotificationData
from notification.service import NotificationService
from pubsub.websocket import WebSockets


class NewNotification:
    """Base notification class; custom notification classes should extend it."""

    def __init__(self, event: str, payload: Dict):
        self.event = event
        self.payload = jsonable_encoder(payload)


@singleton
class NotificationManager:
    @dataclass
    class QueueItem:
        event: str
        payload: Dict
        recipients: List[UUID]

    @inject
    def __init__(self, ws: WebSockets, service: NotificationService):
        self._ws = ws
        self._service = service
        # must postpone Queue creation to FastAPI startup event
        self._notification_queue = None

    def start(self):
        self._notification_queue: Queue[NotificationManager.QueueItem] = Queue()
        get_event_loop().create_task(self._listen_for_notifications())

    def subscribe_to_on_connect(self):
        self._ws.subscribe_to_on_connect(self._on_ws_connect)

    def add_notification(
            self,
            notification: NewNotification,
            recipients: Union[List[UUID], Set[UUID]]) -> None:
        """
        Create and send a new notification to recipients.
        Notifications dispatching is non-blocking and occurs asynchronously.

        :param notification: notification to be sent
        :param recipients: profiles that will receive the notification
        """
        if not recipients:
            return
        try:
            self._notification_queue.put_nowait(NotificationManager.QueueItem(
                event=notification.event,
                payload=notification.payload,
                recipients=recipients))
        except QueueFull:
            logger.error("Notification queue is full")
            pass

    async def _on_ws_connect(self, sid: str, user: User):
        count = await self._service.count_unread_notifications_by_profile_id(
            user.id)
        await self._ws.send("unread_notifications_count", count, to=sid)

    async def _listen_for_notifications(self):
        while True:
            notification = await self._notification_queue.get()
            for recipient in notification.recipients:
                try:
                    await self._service.create_notification(
                        Notification(
                            profile_id=recipient,
                            data=NotificationData(
                                event=notification.event,
                                payload=notification.payload)))
                    await self._ws.send(
                        event="new_unread_notification",
                        payload=1,
                        to=recipient)
                except Exception as e:
                    logger.error("Notification creation failed")
