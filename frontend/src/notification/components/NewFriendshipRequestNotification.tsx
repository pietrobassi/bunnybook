import ProfileImage from "../../common/components/ProfileImage";
import { routerHistory } from "../../common/router";

export interface NewFriendshipRequestNotificationProps {
  loggedUserId: string;
  byId: string;
  byUsername: string;
  onVisit: () => any;
}

const NewFriendshipRequestNotification = ({
  loggedUserId,
  byId,
  byUsername,
  onVisit,
}: NewFriendshipRequestNotificationProps) => {
  return (
    <div className="is-flex is-flex-direction-row is-align-items-center">
      <figure className="image is-32x32 is-inline-block mr-1 is-flex-shrink-0">
        <ProfileImage username={byUsername} />
      </figure>
      <div>
        <b
          className="is-clickable underline-on-hover"
          onClick={() => {
            onVisit();
            routerHistory.push(`/profile/${byId}`);
          }}
        >
          {byUsername}{" "}
        </b>
        sent you a friend{" "}
        <b
          className="is-clickable underline-on-hover"
          onClick={() => {
            onVisit();
            routerHistory.push(
              `/profile/${loggedUserId}/friends/INCOMING_FRIEND_REQUEST`
            );
          }}
        >
          request
        </b>
      </div>
    </div>
  );
};

export default NewFriendshipRequestNotification;
