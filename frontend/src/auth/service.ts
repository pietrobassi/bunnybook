import jwt_decode from "jwt-decode";
import { BehaviorSubject } from "rxjs";
import { filter } from "rxjs/operators";
import { singleton } from "tsyringe";
import { BrowserTabsChannel } from "../common/channel";
import { routerHistory } from "../common/router";
import { WebSocketService } from "../common/websocket";
import { authApi } from "./api";
import { User } from "./model";

const anonymousUser: User = {
  email: "",
  id: "",
  role: "",
  username: "",
  isLogged: false,
};

const getUserInitialValue = () => {
  const jwtToken = localStorage.getItem("jwtToken");
  return jwtToken
    ? { ...(jwt_decode(jwtToken) as any).user, isLogged: true }
    : anonymousUser;
};

/**
 * Service that handles user authentication state.
 *
 * @export
 * @class AuthService
 */
@singleton()
export class AuthService {
  private _user$ = new BehaviorSubject<User>(getUserInitialValue());
  public readonly user$ = this._user$.asObservable();

  constructor(
    private _browserTabsChannel: BrowserTabsChannel,
    private _ws: WebSocketService
  ) {
    this._browserTabsChannel.messages$
      .pipe(filter((msg) => msg.event === "LOGOUT"))
      .subscribe(() => {
        this.logout(true);
      });
  }

  public login(email: string, password: string): Promise<void> {
    return authApi.login(email, password).then((loginData) => {
      this.saveAccessToken(loginData.accessToken);
      this._ws.connect(loginData.accessToken);
    });
  }

  public logout(fromAnotherTab: boolean = false): void {
    this._user$.next(anonymousUser);
    this._ws.disconnect();
    if (!fromAnotherTab) {
      localStorage.removeItem("jwtToken");
      this._browserTabsChannel.postMessage("LOGOUT");
    }
    routerHistory.push("/login");
    routerHistory.go(0);
  }

  public refreshAccessToken(accessToken: string): void {
    this.saveAccessToken(accessToken);
  }

  public saveAccessToken(accessToken: string): void {
    const decodedJwt: any = jwt_decode(accessToken);
    localStorage.setItem("jwtToken", accessToken);
    this._user$.next({ ...decodedJwt.user, isLogged: true });
  }

  public get user(): User {
    return this._user$.value;
  }
}
