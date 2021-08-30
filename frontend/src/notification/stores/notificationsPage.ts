import { BehaviorSubject } from "rxjs";
import { injectable } from "tsyringe";
import { AuthService } from "../../auth/service";
import { loadPaginatedResults } from "../../common/store";
import { notificationApi } from "../api";
import { NotificationItem } from "../model";
import { NotificationsService } from "../service";

@injectable()
export class NotificationsPageStore {
  public _notifications$ = new BehaviorSubject<NotificationItem[]>([]);
  private _isFetchingNotifications$ = new BehaviorSubject<boolean>(false);
  private _noMoreNotifications$ = new BehaviorSubject<boolean>(false);

  public readonly notifications$ = this._notifications$.asObservable();
  public readonly isFetchingNotifications$ =
    this._isFetchingNotifications$.asObservable();
  public readonly noMoreNotifications$ =
    this._noMoreNotifications$.asObservable();

  public static notificationsQueryLimit: number = 10;

  constructor(
    private _authService: AuthService,
    private _notificationsService: NotificationsService
  ) {}

  public loadMoreNotifications = loadPaginatedResults(
    this._notifications$,
    this._isFetchingNotifications$,
    this._noMoreNotifications$,
    NotificationsPageStore.notificationsQueryLimit,
    (olderThan?: string) =>
      notificationApi.getNotifications(
        this._authService.user.id,
        olderThan,
        NotificationsPageStore.notificationsQueryLimit
      ),
    false,
    (notifications) => {
      const unreadNotifications = notifications
        .filter((n) => !n.read)
        .map((n) => n.id);
      if (unreadNotifications.length) {
        notificationApi
          .markNotificationsAs(
            this._authService.user.id,
            unreadNotifications,
            true
          )
          .then((updatedNotifications) => {
            this._notificationsService.alterNotificationsCount(
              -updatedNotifications.length
            );
          });
      }
      return notifications;
    }
  );

  public markNotificationsAsVisited(notificationIds: string[]) {
    notificationApi
      .markNotificationsAs(
        this._authService.user.id,
        notificationIds,
        undefined,
        true
      )
      .catch((e) => null);
  }
}
