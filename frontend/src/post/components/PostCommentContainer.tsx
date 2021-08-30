import { useMemo } from "react";

import ProfileImage from "../../common/components/ProfileImage";
import { PostComment } from "../model";

interface PostCommentProps {
  comment: PostComment;
  onAuthorClick?: (profileId: string) => void;
}
const PostCommentContainer = ({ comment, onAuthorClick }: PostCommentProps) => {
  const createdAt = useMemo(
    () =>
      new Date(comment.createdAt).toLocaleDateString() ===
      new Date().toLocaleDateString()
        ? new Date(comment.createdAt).toLocaleTimeString()
        : new Date(comment.createdAt).toLocaleString(),
    [comment]
  );

  return (
    <div className="box p-2 m-2" key={comment.id}>
      <div className="is-flex is-flex-direction-row is-align-items-center is-justify-content-space-between">
        <div
          onClick={() => onAuthorClick && onAuthorClick(comment.profileId)}
          className="is-flex is-flex-direction-row is-align-items-center"
        >
          <figure className="image is-16x16 is-inline-block is-flex-shrink-0">
            <ProfileImage username={comment.username}></ProfileImage>
          </figure>
          <div className="ml-2 is-clickable underline-on-hover">
            <b>{comment.username}</b>
          </div>
        </div>
        <div className="is-size-6">{createdAt}</div>
      </div>
      <div>{comment.content}</div>
    </div>
  );
};

export default PostCommentContainer;
