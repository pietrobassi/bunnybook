import { BehaviorSubject, filter } from "rxjs";
import { singleton } from "tsyringe";
import { BrowserTabsChannel } from "../common/channel";
import { WebSocketService } from "../common/websocket";

@singleton()
export class NotificationsService {
  private _notificationsCount$ = new BehaviorSubject<number>(0);

  public readonly notificationsCount$ =
    this._notificationsCount$.asObservable();

  constructor(
    private _ws: WebSocketService,
    private _browserTabsChannel: BrowserTabsChannel
  ) {
    this._ws
      .listenTo("unread_notifications_count")
      .subscribe((count: number) => {
        this._notificationsCount$.next(count);
      });
    this._ws.listenTo("new_unread_notification").subscribe((count: number) => {
      this.alterNotificationsCount(count);
    });
    this._browserTabsChannel.messages$
      .pipe(filter((msg) => msg.event === "LOGOUT"))
      .subscribe(() => {
        this.resetNotificationsCount();
      });
  }

  public resetNotificationsCount() {
    this._notificationsCount$.next(0);
  }

  public alterNotificationsCount(amount: number) {
    this._notificationsCount$.next(this._notificationsCount$.value + amount);
  }

  public get notificationsCount(): number {
    return this._notificationsCount$.value;
  }
}
