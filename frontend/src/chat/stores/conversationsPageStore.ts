import { BehaviorSubject } from "rxjs";
import { injectable } from "tsyringe";

import { AuthService } from "../../auth/service";
import { loadPaginatedResults } from "../../common/store";
import { chatApi } from "../api";
import { Conversation } from "../model";

/**
 * Conversations page store.
 *
 * @export
 * @class ConversationsPageStore
 */
@injectable()
export class ConversationsPageStore {
  public _conversations$ = new BehaviorSubject<Conversation[]>([]);
  private _isFetchingConversations$ = new BehaviorSubject<boolean>(false);
  private _noMoreConversations$ = new BehaviorSubject<boolean>(false);

  public readonly conversations$ = this._conversations$.asObservable();
  public readonly isFetchingConversations$ =
    this._isFetchingConversations$.asObservable();
  public readonly noMoreConversations$ =
    this._noMoreConversations$.asObservable();

  public static conversationsQueryLimit: number = 10;

  constructor(private _authService: AuthService) {}

  public loadMoreConversations = loadPaginatedResults(
    this._conversations$,
    this._isFetchingConversations$,
    this._noMoreConversations$,
    ConversationsPageStore.conversationsQueryLimit,
    (olderThan?: string) =>
      chatApi.getConversations(
        this._authService.user.id,
        olderThan,
        ConversationsPageStore.conversationsQueryLimit
      )
  );

  public markConversationAsRead(chatGroupId: string) {
    this._conversations$.next(
      this._conversations$.value.map((conversation) => ({
        ...conversation,
        readAt:
          conversation.chatGroupId !== chatGroupId
            ? conversation.readAt
            : new Date().toLocaleDateString(),
      }))
    );
  }
}
