import classNames from "classnames";
import { useEffect } from "react";
import { useParams } from "react-router-dom";

import ChatPanel from "../../chat/components/ChatPanel";
import LoadingSpinner from "../../common/components/LoadingSpinner";
import {
  useObservable,
  useOnScrollToBottom,
  useService,
  useUser,
} from "../../common/hooks";
import { routerHistory } from "../../common/router";
import CommentNotification from "../components/CommentNotification";
import NewFriendNotification from "../components/NewFriendNotification";
import NewFriendshipRequestNotification from "../components/NewFriendshipRequestNotification";
import PostNotification from "../components/PostNotification";
import { NotificationType } from "../model";
import { NotificationsPageStore } from "../stores/notificationsPage";

const getNotificationComponent = (
  notificationType: string,
  loggedUserId: string,
  payload: any,
  onVisit: (notificationId: string) => any
) => {
  switch (notificationType) {
    case NotificationType.NewCommentOnPost:
      return (
        <CommentNotification
          loggedUserId={loggedUserId}
          {...payload}
          onVisit={onVisit}
        ></CommentNotification>
      );
    case NotificationType.NewPostOnWall:
      return (
        <PostNotification {...payload} onVisit={onVisit}></PostNotification>
      );
    case NotificationType.NewFriend:
      return (
        <NewFriendNotification
          {...payload}
          onVisit={onVisit}
        ></NewFriendNotification>
      );
    case NotificationType.NewFriendshipRequest:
      return (
        <NewFriendshipRequestNotification
          loggedUserId={loggedUserId}
          {...payload}
          onVisit={onVisit}
        ></NewFriendshipRequestNotification>
      );
  }
};

const NotificationsPage = () => {
  const store = useService(NotificationsPageStore);
  const user = useUser();
  const notifications = useObservable(store.notifications$);
  const isFetchingNotifications = useObservable(store.isFetchingNotifications$);

  const onVisit = (notificationId: string) =>
    store.markNotificationsAsVisited([notificationId]);

  useOnScrollToBottom(() => store.loadMoreNotifications());

  const profileId = useParams<{ profile_id: string }>().profile_id;

  useEffect(() => {
    if (user.id !== profileId) {
      routerHistory.push("/");
    }
    store.loadMoreNotifications();
  }, [user, profileId, store]);

  return (
    <div className="columns p-4">
      <div className="column is-one-quarter"></div>
      <div className="column is-half">
        <div className="box">
          <p className="title is-3">Notifications:</p>
          {notifications.length === 0 && !isFetchingNotifications && (
            <div className="box has-text-centered">
              There are no notifications.
            </div>
          )}
          {notifications.map((notification) => (
            <div
              className={classNames(
                "box is-flex is-align-items-center is-justify-content-space-between",
                {
                  "not-visited": !notification.visited,
                }
              )}
              key={notification.id}
            >
              {getNotificationComponent(
                notification.data.event,
                user.id,
                notification.data.payload,
                () => onVisit(notification.id)
              )}
              {!notification.read && (
                <i className="fas fa-circle has-text-info"></i>
              )}
            </div>
          ))}
          {isFetchingNotifications && (
            <LoadingSpinner isLarge isTransparent></LoadingSpinner>
          )}
        </div>
      </div>
      <div className="column is-one-quarter">
        <ChatPanel></ChatPanel>
      </div>
      <style jsx>
        {`
          .not-visited {
            border: 1px solid #3e8ed0;
          }
        `}
      </style>
    </div>
  );
};

export default NotificationsPage;
