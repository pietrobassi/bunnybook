import { Subject } from "rxjs";

export enum FriendChatStatus {
  Online = "ONLINE",
  Offline = "OFFLINE",
}

export interface PrivateChat {
  profileId: string;
  username: string;
  chatGroupId: string;
}

export interface FriendChat extends PrivateChat {
  status: FriendChatStatus;
}

export interface ChatMessage {
  id: string;
  content: string;
  chatGroupId: string;
  fromProfileId: string;
  createdAt: string;
}

export interface IsTypingMessage {
  profileId: string;
  username: string;
  chatGroupId: string;
}

export interface ChatData {
  messages: ChatMessage[];
  isLoadingMessages: boolean;
  isOpen: boolean;
  noMoreMessages: boolean;
  unreadMessages: number;
  usernameIsTyping: string | null;
  scrollTo: Subject<"top" | "bottom">;
}

export interface Conversation {
  fromProfileId: string;
  fromProfileUsername: string;
  content: string;
  createdAt: string;
  username: string;
  chatGroupId: string;
  chatGroupName: string;
  readAt: string | null;
}
