import {
  BehaviorSubject,
  combineLatest,
  debounceTime,
  map,
  Subject,
  tap,
} from "rxjs";
import { singleton } from "tsyringe";

import { AuthService } from "../../auth/service";
import { WebSocketService } from "../../common/websocket";
import { chatApi } from "../api";
import {
  ChatData,
  ChatMessage,
  FriendChat,
  FriendChatStatus,
  IsTypingMessage,
  PrivateChat,
} from "../model";
import { ChatService } from "../service";

/**
 * Store that manages all chat-related data.
 *
 * @export
 * @class ChatStore
 */
@singleton()
export class ChatStore {
  private _footerChats$ = new BehaviorSubject<PrivateChat[]>([]);
  private _privateChats$ = new BehaviorSubject<PrivateChat[]>([]);
  private _onlineFriendsIds$ = new BehaviorSubject<string[]>([]);
  private _friendsChats$ = new BehaviorSubject<FriendChat[]>([]);
  private _unreadConversationsIds$ = new BehaviorSubject<string[]>([]);
  private _lastReadMessages: Map<string, string | null> = new Map();

  public static messagesQueryLimit: number = 20;
  public static isTypingDebounceTime: number = 4000;

  public readonly footerChats$ = this._footerChats$.asObservable();
  public readonly privateChats$ = this._privateChats$.asObservable();
  public readonly onlineFriendsIds$ = this._onlineFriendsIds$.asObservable();
  public readonly friendsChats$ = this._friendsChats$.asObservable();
  public readonly unreadConversationsIds$ =
    this._unreadConversationsIds$.asObservable();
  public chatBoxesData: Map<string, BehaviorSubject<ChatData>> = new Map();

  constructor(
    private _ws: WebSocketService,
    private _chatService: ChatService,
    private _authService: AuthService
  ) {
    // update private chat list
    this._ws
      .listenTo("private_chats")
      .subscribe((privateChats) => this._privateChats$.next(privateChats));

    // handle friend addition, refreshing
    this._ws.listenTo("add_friend").subscribe((privateChat: PrivateChat) => {
      // TODO: Socket.IO session refresh should be performed by backend: this is a hacky way to refresh cached friends
      this._ws.reconnect(localStorage.getItem("jwtToken")!);
    });

    // handler friend deletion, removing chat from footer
    this._ws.listenTo("remove_friend").subscribe((friendId: string) => {
      this._footerChats$.next(
        this._footerChats$.value.filter(
          (footerChat) => footerChat.profileId !== friendId
        )
      );
      this._ws.reconnect(localStorage.getItem("jwtToken")!);
    });

    // show which user is typing on a specific chat
    this._ws
      .listenTo("is_typing")
      .pipe(
        tap((data: IsTypingMessage) => {
          const chatData$ = this._getOrCreateChat(data.chatGroupId);
          chatData$.next({
            ...chatData$.value,
            usernameIsTyping: data.username,
          });
        }),
        debounceTime(ChatStore.isTypingDebounceTime)
      )
      .subscribe((data: IsTypingMessage) => {
        const chatData$ = this._getOrCreateChat(data.chatGroupId);
        chatData$.next({ ...chatData$.value, usernameIsTyping: null });
      });

    // update online friends statuses
    this._ws
      .listenTo("online_friends")
      .subscribe((friendsIds: string[]) =>
        this._onlineFriendsIds$.next(friendsIds)
      );

    // update unread conversations count
    this._ws
      .listenTo("unread_conversations_ids")
      .subscribe((conversationsIds: string[]) => {
        for (const id of this._unreadConversationsIds$.value) {
          if (!conversationsIds.includes(id)) {
            conversationsIds.push(id);
          }
        }
        this._unreadConversationsIds$.next(conversationsIds);
      });

    /*
     Handle new chat message.

     Expected behavior:
     - "is typing" indicator of the chat instantly disappears
     - if chat box is not included in the footer section: add it to footer and open it, load latest messages (only if 
      no message has already been loaded into that chat) and scroll to bottom
     - if chat box is already included in the footer section:
         - if chat box is open, just add the new message and scroll to bottom
         - if chat box is closed, add the new message (keeping chat box closed) and add +1 to unread messages counter
    */
    this._ws.listenTo("chat_message").subscribe((message: ChatMessage) => {
      const chatData$ = this._getOrCreateChat(message.chatGroupId);
      if (message.fromProfileId !== this._authService.user.id) {
        chatData$.next({ ...chatData$.value, usernameIsTyping: null });
      }

      // if chat is not in footer
      if (
        !this._footerChats$.value
          .map((f) => f.chatGroupId)
          .includes(message.chatGroupId)
      ) {
        this.setChatIsOpen(message.chatGroupId, true, false);
        // if chat message history is empty
        if (
          !chatData$.value.messages.length &&
          !chatData$.value.noMoreMessages
        ) {
          this.loadMoreMessages(message.chatGroupId).then(() => {
            if (
              !chatData$.value.messages
                .map((msg) => msg.id)
                .includes(message.id)
            ) {
              chatData$.next({
                ...chatData$.value,
                messages: [...chatData$.value.messages, message],
              });
            }
            chatData$.value.scrollTo.next("bottom");
            this.markChatAsRead(message);
            this._unreadConversationsIds$.next(
              this._unreadConversationsIds$.value.filter(
                (id) => id !== message.chatGroupId
              )
            );
          });
          // if chat has already stored some messages
        } else {
          chatData$.next({
            ...chatData$.value,
            messages: [...chatData$.value.messages, message],
          });
          chatData$.value.scrollTo.next("bottom");
        }
        return;
      }
      // if chat is in footer
      chatData$.next({
        ...chatData$.value,
        messages: [...chatData$.value.messages, message],
      });
      // if its not open
      if (!chatData$.value.isOpen) {
        chatData$.next({
          ...chatData$.value,
          unreadMessages: chatData$.value.unreadMessages + 1,
        });
        if (
          !this._unreadConversationsIds$.value.includes(message.chatGroupId)
        ) {
          this._unreadConversationsIds$.next([
            ...this._unreadConversationsIds$.value,
            message.chatGroupId,
          ]);
        }
        // if its open
      } else {
        this.markChatAsRead(message);
        chatData$.value.scrollTo.next("bottom");
      }
    });

    // combine private chat list and online friends statuses to get a sorted list of online/offline friends
    combineLatest([this._privateChats$, this._onlineFriendsIds$])
      .pipe(
        map(([privateChats, onlineIds]: [PrivateChat[], string[]]) =>
          privateChats
            .map((privateChat: PrivateChat) => ({
              ...privateChat,
              status: onlineIds.includes(privateChat.profileId)
                ? FriendChatStatus.Online
                : FriendChatStatus.Offline,
            }))
            .sort((a, b) =>
              a.status !== b.status
                ? a.status === FriendChatStatus.Online
                  ? -1
                  : 1
                : a.username < b.username
                ? -1
                : 1
            )
        )
      )
      .subscribe((friends) => this._friendsChats$.next(friends));
  }

  public sendMessage(message: string, to: string): void {
    this._chatService.sendMessage(message, to);
  }

  public isTyping(chatGroupId: string): void {
    this._chatService.isTyping(chatGroupId);
  }

  public markChatAsRead(message: ChatMessage): void {
    if (this._lastReadMessages.get(message.chatGroupId) !== message.id) {
      this._chatService.markChatAsRead(message.chatGroupId, message.id);
      this._lastReadMessages.set(message.chatGroupId, message.id);
    }
  }

  public addChatToFooter(friend: FriendChat): void {
    if (
      !this._footerChats$.value
        .map((f) => f.chatGroupId)
        .includes(friend.chatGroupId)
    ) {
      this._getOrCreateChat(friend.chatGroupId);
      this._footerChats$.next([...this._footerChats$.value, friend]);
    }
  }

  public async loadMoreMessages(chatGroupId: string): Promise<void> {
    const chatData$ = this._getOrCreateChat(chatGroupId);
    if (chatData$.value.isLoadingMessages || chatData$.value.noMoreMessages) {
      return;
    }
    chatData$.next({ ...chatData$.value, isLoadingMessages: true });
    const olderThan =
      chatData$.value.messages[0] && chatData$.value.messages[0]?.createdAt;

    try {
      const messages = await chatApi.getChatMessages(chatGroupId, olderThan);
      chatData$.next({
        ...chatData$.value,
        messages: [...messages.reverse(), ...chatData$.value.messages],
      });
      if (messages.length < ChatStore.messagesQueryLimit) {
        chatData$.next({ ...chatData$.value, noMoreMessages: true });
      }
    } finally {
      chatData$.next({ ...chatData$.value, isLoadingMessages: false });
    }
  }

  public setChatIsOpen(
    chatGroupId: string,
    isOpen: boolean,
    loadMessages: boolean = false
  ): void {
    const chatData$ = this._getOrCreateChat(chatGroupId);
    if (isOpen) {
      this.addChatToFooter(
        this._friendsChats$.value.filter(
          (friendChat) => friendChat.chatGroupId === chatGroupId
        )[0]
      );
      if (
        chatData$.value.messages.length &&
        this._unreadConversationsIds$.value.includes(chatGroupId)
      ) {
        this.markChatAsRead(
          chatData$.value.messages[chatData$.value.messages.length - 1]
        );
        this._unreadConversationsIds$.next(
          this._unreadConversationsIds$.value.filter((id) => id !== chatGroupId)
        );
      }
      chatData$.value.scrollTo.next("bottom");
    }
    chatData$.next({
      ...chatData$.value,
      isOpen: isOpen,
      unreadMessages: isOpen ? 0 : chatData$.value.unreadMessages,
    });
    if (
      !chatData$.value.messages.length &&
      !chatData$.value.noMoreMessages &&
      loadMessages
    ) {
      this.loadMoreMessages(chatGroupId).then(() => {
        if (chatData$.value.messages.length === 0) {
          return;
        }
        chatData$.value.scrollTo.next("bottom");
        if (
          chatData$.value.messages.length &&
          this._unreadConversationsIds$.value.includes(chatGroupId)
        ) {
          this.markChatAsRead(
            chatData$.value.messages[chatData$.value.messages.length - 1]
          );
          this._unreadConversationsIds$.next(
            this._unreadConversationsIds$.value.filter(
              (id) => id !== chatGroupId
            )
          );
        }
      });
    }
  }

  public removeChatFromFooter(privateChat: PrivateChat): void {
    this._footerChats$.next(
      this._footerChats$.value.filter(
        (f) => f.chatGroupId !== privateChat.chatGroupId
      )
    );
    this.chatBoxesData.delete(privateChat.chatGroupId);
  }

  private _getOrCreateChat(chatGroupId: string): BehaviorSubject<ChatData> {
    const chatData$ = this.chatBoxesData.get(chatGroupId);
    if (chatData$) {
      return chatData$;
    }
    const chatData = new BehaviorSubject<ChatData>({
      messages: [],
      isLoadingMessages: false,
      noMoreMessages: false,
      isOpen: false,
      unreadMessages: 0,
      usernameIsTyping: null,
      scrollTo: new Subject<"top" | "bottom">(),
    });
    this.chatBoxesData.set(chatGroupId, chatData);
    return chatData;
  }
}
