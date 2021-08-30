import ProfileImage from "../../common/components/ProfileImage";
import { routerHistory } from "../../common/router";

export interface CommentNotificationProps {
  loggedUserId: string;
  byId: string;
  byUsername: string;
  postById: string;
  postByUsername: string;
  postId: string;
  commentPreview: string;
  onVisit: () => any;
}

const CommentNotification = ({
  loggedUserId,
  byId,
  byUsername,
  postById,
  postByUsername,
  postId,
  commentPreview,
  onVisit,
}: CommentNotificationProps) => {
  return (
    <div className="is-flex is-flex-direction-row is-align-items-center">
      <figure className="image is-32x32 is-inline-block mr-1 is-flex-shrink-0">
        <ProfileImage username={byUsername} />
      </figure>
      <div>
        <b
          className="is-clickable underline-on-hover"
          onClick={() => routerHistory.push(`/profile/${byId}`)}
        >
          {byUsername}
        </b>{" "}
        has commented{" "}
        {loggedUserId === postById ? "your" : `${postByUsername}'s`}{" "}
        <b
          className="is-clickable underline-on-hover"
          onClick={() => {
            onVisit();
            routerHistory.push(`/post/${postId}`);
          }}
        >
          post
        </b>
        : "{commentPreview}"
      </div>
    </div>
  );
};

export default CommentNotification;
