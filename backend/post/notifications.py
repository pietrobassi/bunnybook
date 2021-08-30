from uuid import UUID

from injector import singleton, inject

from notification.manager import NewNotification, NotificationManager


class NewPostOnWall(NewNotification):
    def __init__(self,
                 post_author_id: UUID,
                 post_author_username: str,
                 post_id: UUID,
                 post_content: str):
        super().__init__(
            event="NEW_POST_ON_WALL",
            payload={"byId": post_author_id,
                     "byUsername": post_author_username,
                     "postId": post_id,
                     "postPreview": f"{post_content[:32]}..."
                     if len(post_content) > 32 else post_content})


@singleton
class PostNotificationService:
    @inject
    def __init__(self, notification_manager: NotificationManager):
        self._notification_manager = notification_manager

    def create_post_notification(
            self,
            post_id: UUID,
            author_profile_id: UUID,
            author_username: str,
            post_content: str,
            wall_profile_id: UUID):
        if wall_profile_id != author_profile_id:
            self._notification_manager.add_notification(NewPostOnWall(
                post_author_id=author_profile_id,
                post_author_username=author_username,
                post_id=post_id,
                post_content=post_content
            ), [wall_profile_id])
