from uuid import UUID

from injector import singleton, inject

from comment.repo import CommentRepo
from notification.manager import NewNotification, NotificationManager
from post.repo import PostRepo


class NewCommentOnPost(NewNotification):
    def __init__(self,
                 comment_author_id: UUID,
                 comment_author_username: str,
                 post_author_id: UUID,
                 post_author_username: str,
                 post_id: UUID,
                 comment_content: str):
        super().__init__(
            event="NEW_COMMENT_ON_POST",
            payload={"byId": comment_author_id,
                     "byUsername": comment_author_username,
                     "postById": post_author_id,
                     "postByUsername": post_author_username,
                     "postId": post_id,
                     "commentPreview": f"{comment_content[:32]}..."
                     if len(comment_content) > 32 else comment_content})


@singleton
class CommentNotificationService:
    @inject
    def __init__(
            self,
            notification_manager: NotificationManager,
            comment_repo: CommentRepo,
            post_repo: PostRepo):
        self._notification_manager = notification_manager
        self._comment_repo = comment_repo
        self._post_repo = post_repo

    async def create_comment_notification(
            self,
            post_id: UUID,
            comment_author_id: UUID,
            comment_author_username: str,
            comment_content: str) -> None:
        post = (await self._post_repo.find_post_by_id(post_id))
        recipients = await self._comment_repo.find_comments_authors_by_post_id(
            post_id)
        recipients.add(post.profile_id)
        recipients.add(post.wall_profile_id)
        recipients.remove(comment_author_id)
        self._notification_manager.add_notification(NewCommentOnPost(
            comment_author_id=comment_author_id,
            comment_author_username=comment_author_username,
            post_author_id=post.profile_id,
            post_author_username=post.username,
            post_id=post.id,
            comment_content=comment_content), recipients)
