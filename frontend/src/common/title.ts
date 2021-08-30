import { combineLatest, distinctUntilChanged, map } from "rxjs";
import { singleton } from "tsyringe";
import { ChatStore } from "../chat/stores/chatStore";
import { NotificationsService } from "../notification/service";

/**
 * Service that manages browser tab title.
 *
 * @export
 * @class TabTitleService
 */
@singleton()
export class TabTitleService {
  public static defaultTabTitle: string = "Bunnybook";
  constructor(
    private _chatStore: ChatStore,
    private _notificationsService: NotificationsService
  ) {
    combineLatest([
      this._chatStore.unreadConversationsIds$,
      this._notificationsService.notificationsCount$,
    ])
      .pipe(
        map(
          ([conversionsIds, count]: [string[], number]) =>
            conversionsIds.length + count
        ),
        distinctUntilChanged()
      )
      .subscribe((count) => {
        document.title =
          (count === 0 ? "" : `(${count}) `) + TabTitleService.defaultTabTitle;
      });
  }
}
