from uuid import UUID

from injector import singleton, inject

from notification.manager import NewNotification, NotificationManager


class NewFriend(NewNotification):
    def __init__(self,
                 accepter_profile_id: UUID,
                 accepter_username: str):
        super().__init__(
            event="NEW_FRIEND",
            payload={"profileId": accepter_profile_id,
                     "profileUsername": accepter_username})


class NewFriendshipRequest(NewNotification):
    def __init__(self, requester_profile_id: UUID, requester_username: str):
        super().__init__(
            event="NEW_FRIENDSHIP_REQUEST",
            payload={"byId": requester_profile_id,
                     "byUsername": requester_username})


@singleton
class ProfilesNotificationService:
    @inject
    def __init__(self, notification_manager: NotificationManager):
        self._notification_manager = notification_manager

    def create_new_friend_notification(
            self,
            accepter_profile_id: UUID,
            accepter_username: str,
            other_profile_id: UUID):
        self._notification_manager.add_notification(NewFriend(
            accepter_profile_id=accepter_profile_id,
            accepter_username=accepter_username,
        ), [other_profile_id])

    def create_new_friendship_request_notification(
            self,
            requester_profile_id: UUID,
            requester_username: str,
            target_profile_id: UUID):
        self._notification_manager.add_notification(NewFriendshipRequest(
            requester_profile_id=requester_profile_id,
            requester_username=requester_username,
        ), [target_profile_id])
