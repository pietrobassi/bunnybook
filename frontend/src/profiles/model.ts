export interface Profile {
  id: string;
  username: string;
}

export enum Relationship {
  Friend = "FRIEND",
  OutgoingFriendRequest = "OUTGOING_FRIEND_REQUEST",
  IncomingFriendRequest = "INCOMING_FRIEND_REQUEST",
  Self = "SELF",
  None = "NONE",
  Unknown = "UNKNOWN",
}

export enum RelationshipAction {
  AddFriend = "ADD_FRIEND",
  RemoveFriend = "REMOVE_FRIEND",
  AcceptFriendshipRequest = "ACCEPT_FRIENDSHIP_REQUEST",
  RejectFriendshipRequest = "REJECT_FRIENDSHIP_REQUEST",
  CancelFriendshipRequest = "CANCEL_FRIENDSHIP_REQUEST",
}
