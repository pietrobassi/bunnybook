import { useEffect } from "react";
import { useParams } from "react-router-dom";

import ChatPanel from "../../chat/components/ChatPanel";
import LoadingSpinner from "../../common/components/LoadingSpinner";
import ProfileImage from "../../common/components/ProfileImage";
import {
  useObservable,
  useOnScrollToBottom,
  useService,
  useUser,
} from "../../common/hooks";
import { routerHistory } from "../../common/router";
import PostContainer from "../../post/components/PostContainer";
import PostForm from "../../post/components/PostForm";
import { PostPrivacy } from "../../post/model";
import RelationshipButtonContainer from "../components/RelationshipButtonContainer";
import { Relationship, RelationshipAction } from "../model";
import { FriendsPageSection } from "../stores/friendsPage";
import { ProfilePageStore } from "../stores/profilePage";

const ProfilePage = () => {
  const store = useService(ProfilePageStore);
  const user = useUser();
  const profile = useObservable(store.profile$);
  const relationship = useObservable(store.relationship$);
  const posts = useObservable(store.posts$);
  const isFetchingPosts = useObservable(store.isFetchingPosts$);

  const profileId = useParams<{ profile_id: string }>().profile_id || user.id;

  const isLoggedUserProfile = profileId === user.id;

  useOnScrollToBottom(() => store.loadMorePosts());

  useEffect(() => {
    store.loadPage(profileId);
  }, [profileId, store]);

  const postPublishedHandler = (content: string, privacy: PostPrivacy) => {
    return store.publishPost(content, privacy, profile!.id);
  };

  const relationshipChangedHandler = async (action: RelationshipAction) => {
    await store.processRelationshipAction(action);
  };

  const friendsButtonClickHandler = () => {
    routerHistory.push(
      `/profile/${profileId}/friends/${FriendsPageSection.Friends}`
    );
  };

  const mutualfriendsButtonClickHandler = () => {
    routerHistory.push(
      `/profile/${profileId}/friends/${FriendsPageSection.MutualFriends}`
    );
  };

  const deletePostClickHandler = (postId: string) => store.deletePost(postId);

  return (
    <div className="columns is-centered p-4">
      <div className="column is-one-quarter"></div>
      <div className="column is-half">
        {profile && (
          <div className="box">
            <div className="is-flex is-align-items-center is-justify-content-space-between is-flex-wrap-wrap mb-2">
              <div className="is-flex is-align-items-center">
                <figure className="image is-128x128 is-flex is-flex-shrink-0">
                  <ProfileImage username={profile.username} />
                </figure>
                <p className="title is-flex ml-4">{profile.username}</p>
              </div>
              {user.isLogged && relationship !== Relationship.Self && (
                <RelationshipButtonContainer
                  profileId={user.id}
                  targetProfileId={profile.id}
                  relationship={relationship}
                  onActionSuccess={relationshipChangedHandler}
                />
              )}
            </div>
            {isLoggedUserProfile && (
              <PostForm
                isLoggedUserProfile
                placeholder="What are you thinking about?"
                onPostPublish={postPublishedHandler}
              ></PostForm>
            )}
            <br />
            {!isLoggedUserProfile && (
              <button
                className="button is-info"
                onClick={friendsButtonClickHandler}
              >
                <span className="icon is-small">
                  <i className="fas fa-user-friends"></i>
                </span>
                <div>Friends</div>
              </button>
            )}
            {relationship === Relationship.Friend && (
              <button
                className="button is-primary ml-2"
                onClick={mutualfriendsButtonClickHandler}
              >
                <span className="icon is-small">
                  <i className="fas fa-users"></i>
                </span>
                <div>Mutual friends</div>
              </button>
            )}
          </div>
        )}
        {user.isLogged &&
          !isLoggedUserProfile &&
          relationship === Relationship.Friend && (
            <div className="box">
              <PostForm
                placeholder={`Write something on ${profile?.username}'s wall...`}
                onPostPublish={postPublishedHandler}
              ></PostForm>
            </div>
          )}
        {!profile && <LoadingSpinner isLarge></LoadingSpinner>}
        {posts &&
          posts.map((post) => (
            <div key={post.id} className="mt-5">
              <PostContainer
                post={post}
                user={user}
                isLoggedUserProfile={isLoggedUserProfile}
                onDeletePostClick={deletePostClickHandler}
              ></PostContainer>
            </div>
          ))}
        {isFetchingPosts && (
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

export default ProfilePage;
