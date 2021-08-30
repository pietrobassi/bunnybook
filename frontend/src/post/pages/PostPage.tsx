import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import ChatPanel from "../../chat/components/ChatPanel";
import LoadingSpinner from "../../common/components/LoadingSpinner";
import { useUser } from "../../common/hooks";
import { routerHistory } from "../../common/router";
import { postApi } from "../api";
import PostContainer from "../components/PostContainer";
import { Post } from "../model";

const PostPage = () => {
  const user = useUser();
  const [post, setPost] = useState<Post | null>(null);
  const [isLoadingPost, setIsLoadingPost] = useState<boolean>(false);
  const postId = useParams<{ post_id: string }>().post_id;

  useEffect(() => {
    setIsLoadingPost(true);
    postApi
      .getPost(postId)
      .then((post) => {
        setPost(post);
      })
      .catch((err) => routerHistory.replace("/404"))
      .finally(() => setIsLoadingPost(false));
  }, [postId]);

  const deletePostClickHandler = async (postId: string) => {
    await postApi.deletePost(postId);
    setPost(null);
  };

  return (
    <div className="columns p-4">
      <div className="column is-one-quarter"></div>
      <div className="column is-half">
        {post && (
          <PostContainer
            post={post!}
            user={user}
            loadComments
            isLoggedUserProfile={user.id === post?.wallProfileId}
            onDeletePostClick={deletePostClickHandler}
          ></PostContainer>
        )}
        {isLoadingPost && (
          <div className="mt-4">
            <LoadingSpinner isLarge></LoadingSpinner>
          </div>
        )}
      </div>
      <div className="column is-one-quarter">
        <ChatPanel></ChatPanel>
      </div>
    </div>
  );
};

export default PostPage;
