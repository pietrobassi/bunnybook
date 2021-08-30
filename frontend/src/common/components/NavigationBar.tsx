import { AuthService } from "../../auth/service";
import { ChatStore } from "../../chat/stores/chatStore";
import { NotificationsService } from "../../notification/service";
import ProfileSearch from "../../profiles/components/ProfileSearch";
import { useObservable, useService, useUser } from "../hooks";
import { routerHistory } from "../router";
import ProfileImage from "./ProfileImage";

const NavigationBar = () => {
  const authService = useService(AuthService);
  const user = useUser();
  const chatStore = useService(ChatStore);
  const notificationsService = useService(NotificationsService);
  const unreadConversationsIds = useObservable(
    chatStore.unreadConversationsIds$
  );
  const notificationsCount = useObservable(
    notificationsService.notificationsCount$
  );

  const logoutButtonClickHandler = () => authService.logout();
  const profileButtonClickHandler = () => routerHistory.push("/profile");
  const loginButtonClickHandler = () => routerHistory.push("/login");
  const registerButtonClickHandler = () => routerHistory.push("/register");
  const friendsButtonClickHandler = () =>
    routerHistory.push(`/profile/${user.id}/friends`);
  const notificationsButtonClickHandler = () =>
    routerHistory.push(`/profile/${user.id}/notifications`);
  const chatButtonClickHandler = () =>
    routerHistory.push(`/profile/${user.id}/conversations`);

  return (
    <div className="navbar has-shadow p-2 is-fixed-top is-flex is-flex-direction-row is-align-items-center is-justify-content-space-between is-flex-wrap-wrap">
      <div>
        <ProfileSearch></ProfileSearch>
      </div>

      <div>
        {user.isLogged && (
          <>
            <div className="is-flex">
              <button
                className="button is-info is-right mr-2"
                onClick={friendsButtonClickHandler}
              >
                <span className="icon is-small">
                  <i className="fas fa-user-friends"></i>
                </span>
              </button>
              <div className="is-relative">
                <button
                  className="button is-info is-right mr-2"
                  onClick={chatButtonClickHandler}
                >
                  <span className="icon is-small">
                    <i className="fas fa-comments"></i>
                  </span>
                </button>
                {unreadConversationsIds.length > 0 && (
                  <span
                    onClick={chatButtonClickHandler}
                    className="items-count is-size-7"
                  >
                    {unreadConversationsIds.length}
                  </span>
                )}
              </div>
              <div className="is-relative">
                <button
                  className="button is-info is-right mr-2"
                  onClick={notificationsButtonClickHandler}
                >
                  <span className="icon is-small">
                    <i className="fas fa-bell"></i>
                  </span>
                </button>
                {notificationsCount > 0 && (
                  <span
                    onClick={notificationsButtonClickHandler}
                    className="items-count is-size-7"
                  >
                    {notificationsCount}
                  </span>
                )}
              </div>
              <button
                className="button is-primary is-right mr-2 p-0"
                onClick={profileButtonClickHandler}
              >
                <figure className="image is-32x32 is-inline-block m-1 ml-3 is-flex-shrink-0">
                  <ProfileImage username={user.username} />
                </figure>
                <span className="mr-3">{user.username}</span>
              </button>
              <button
                className="button is-right is-inverted"
                onClick={logoutButtonClickHandler}
              >
                Log out
              </button>
            </div>
          </>
        )}
        {!user.isLogged && (
          <>
            <button
              className="button is-right"
              onClick={loginButtonClickHandler}
            >
              Log in
            </button>
            <button
              className="button is-primary is-right ml-1"
              onClick={registerButtonClickHandler}
            >
              Sign up
            </button>
          </>
        )}
      </div>
      <style jsx>
        {`
          .items-count {
            position: absolute;
            bottom: -5px;
            right: 2px;
            padding: 2px 8px;
            border-radius: 50%;
            background: red;
            color: white;
          }

          .items-count:hover {
            cursor: pointer;
          }
        `}
      </style>
    </div>
  );
};

export default NavigationBar;
