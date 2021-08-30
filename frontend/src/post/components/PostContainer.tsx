import classNames from "classnames";
import { useEffect } from "react";

import { User } from "../../auth/model";
import LoadingSpinner from "../../common/components/LoadingSpinner";
import ProfileImage from "../../common/components/ProfileImage";
import { useObservable, useService } from "../../common/hooks";
import { routerHistory } from "../../common/router";
import { Post, PostPrivacy } from "../model";
import { PostCommentsStore } from "../stores/postComments";
import PostCommentContainer from "./PostCommentContainer";

interface PostContainerProps {
  post: Post;
  isLoggedUserProfile: boolean;
  user: User;
  loadComments?: boolean;
  onDeletePostClick?: (postId: string) => void;
}

const PostContainer = ({
  post,
  isLoggedUserProfile,
  user,
  loadComments,
  onDeletePostClick,
}: PostContainerProps) => {
  const store = useService(PostCommentsStore);
  const commentInput = useObservable(store.commentInput$);
  const comments = useObservable(store.comments$);
  const isPublishingComment = useObservable(store.isPublishingComment$);
  const isFetchingComments = useObservable(store.isFetchingComments$);
  const noMoreComments = useObservable(store.noMoreComments$);

  const commentsCountClickHandler = () => store.loadMoreComments(post.id);
  const commentInputChangeHandler = (content: string) =>
    store.setCommentInput(content);
  const commentPublishHandler = (content: string) =>
    store.publishComment(content, post.id);
  const deletePostClickHandler = () => {
    if (
      window.confirm(
        "Do you really want to delete this post and all its comments?"
      )
    ) {
      onDeletePostClick && onDeletePostClick(post.id);
    }
  };
  const onUsernameClickHandler = (profileId: string) =>
    routerHistory.push(`/profile/${profileId}`);

  useEffect(() => {
    if (loadComments && post.commentsCount > 0) {
      store.loadMoreComments(post.id);
    }
  }, [store, post, loadComments]);

  return (
    <div className="card">
      <div className="card-content">
        <div className="media">
          <div className="media-left">
            <figure className="image is-48x48 is-flex-shrink-0">
              <ProfileImage username={post.username} />
            </figure>
          </div>
          <div className="media-content">
            <div className="is-flex is-flex-direction-row is-align-items-center is-justify-content-space-between">
              <p
                className="title is-4 mb-0 is-clickable underline-on-hover"
                onClick={() => onUsernameClickHandler(post.profileId)}
              >
                {post.username}{" "}
              </p>
              {(isLoggedUserProfile ||
                (user.isLogged && post.profileId === user.id)) && (
                <button
                  className="delete"
                  onClick={deletePostClickHandler}
                ></button>
              )}
            </div>

            <p className="subtitle is-6">
              <i
                className={classNames("fas mr-1", {
                  "fa-globe": post.privacy === PostPrivacy.Public,
                  "fa-user-friends": post.privacy === PostPrivacy.Friends,
                })}
              ></i>
              {new Date(post.createdAt).toLocaleString()}
            </p>
          </div>
        </div>
        <div className="content box post-content">{post.content}</div>
      </div>
      <hr className="solid m-0"></hr>
      {isFetchingComments && <LoadingSpinner></LoadingSpinner>}
      {post.commentsCount !== 0 && !noMoreComments && !isFetchingComments && (
        <div
          className="box p-2 m-0 is-clickable underline-on-hover"
          onClick={commentsCountClickHandler}
        >
          {comments.length
            ? "Load more comments..."
            : `Comments: ${post.commentsCount}`}
        </div>
      )}
      {comments.map((comment) => (
        <PostCommentContainer
          key={comment.id}
          comment={comment}
          onAuthorClick={() =>
            routerHistory.push(`/profile/${comment.profileId}`)
          }
        ></PostCommentContainer>
      ))}
      {isPublishingComment && <LoadingSpinner></LoadingSpinner>}
      {user.isLogged && !isPublishingComment && (
        <div className="is-flex is-flex-direction-row is-align-items-center p-1">
          <figure className="image is-32x32 ml-1 is-inline-block profile-image is-flex-shrink-0">
            <ProfileImage username={user.username}></ProfileImage>
          </figure>
          <input
            onKeyDown={(e) =>
              e.key === "Enter" ? commentPublishHandler(commentInput) : null
            }
            onChange={(e) => commentInputChangeHandler(e.target.value)}
            type="text"
            placeholder="Add a comment..."
            className="input ml-2"
            value={commentInput}
          ></input>
        </div>
      )}
      <style jsx>
        {`
          .profile-image {
            min-width: 32px;
          }

          .post-content {
            word-break: break-word;
          }
        `}
      </style>
    </div>
  );
};

export default PostContainer;
