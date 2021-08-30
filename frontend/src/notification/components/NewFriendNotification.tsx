import ProfileImage from "../../common/components/ProfileImage";
import { routerHistory } from "../../common/router";

export interface NewFriendNotificationProps {
  profileId: string;
  profileUsername: string;
  onVisit: () => any;
}

const NewFriendNotification = ({
  profileId,
  profileUsername,
  onVisit,
}: NewFriendNotificationProps) => {
  return (
    <div className="is-flex is-flex-direction-row is-align-items-center">
      <figure className="image is-32x32 is-inline-block mr-1 is-flex-shrink-0">
        <ProfileImage username={profileUsername} />
      </figure>
      <div>
        <b
          className="is-clickable underline-on-hover"
          onClick={() => {
            onVisit();
            routerHistory.push(`/profile/${profileId}`);
          }}
        >
          {profileUsername}
        </b>{" "}
        and you are now{" "}
        <b
          className="is-clickable underline-on-hover"
          onClick={() => {
            onVisit();
            routerHistory.push(`/profile/${profileId}`);
          }}
        >
          friends
        </b>
        !
      </div>
    </div>
  );
};

export default NewFriendNotification;
