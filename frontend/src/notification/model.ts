export interface NotificationItemData {
  event: string;
  payload: any;
}

export interface NotificationItem {
  id: string;
  createdAt: string;
  profileId: string;
  data: NotificationItemData;
  read: boolean;
  visited: boolean;
}

export enum NotificationType {
  NewCommentOnPost = "NEW_COMMENT_ON_POST",
  NewPostOnWall = "NEW_POST_ON_WALL",
  NewFriend = "NEW_FRIEND",
  NewFriendshipRequest = "NEW_FRIENDSHIP_REQUEST",
}
