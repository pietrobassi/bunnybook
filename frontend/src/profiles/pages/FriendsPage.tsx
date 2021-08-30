import classNames from "classnames";
import { useCallback, useEffect } from "react";
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
import RelationshipButtonContainer from "../components/RelationshipButtonContainer";
import { Relationship, RelationshipAction } from "../model";
import { FriendsPageSection, FriendsPageStore } from "../stores/friendsPage";

const sectionRelationshipMap = {
  [FriendsPageSection.Friends]: Relationship.Friend,
  [FriendsPageSection.MutualFriends]: Relationship.Friend,
  [FriendsPageSection.FriendSuggestions]: Relationship.None,
  [FriendsPageSection.IncomingFriendRequest]:
    Relationship.IncomingFriendRequest,
  [FriendsPageSection.OutgoingFriendRequest]:
    Relationship.OutgoingFriendRequest,
};

const FriendsPage = () => {
  const store = useService(FriendsPageStore);
  const user = useUser();
  const profiles = useObservable(store.profiles$);
  const selectedSection = useObservable(store.selectedSection$);
  const isFetchingProfiles = useObservable(store.isFetchingProfiles$);

  const profileId = useParams<{ profile_id: string }>().profile_id;
  const section = useParams<{ section: string }>().section;

  useOnScrollToBottom(() => store.loadMoreProfiles(profileId));

  const goTo = useCallback(
    (section: FriendsPageSection) =>
      routerHistory.push(`/profile/${profileId}/friends/${section}`),
    [profileId]
  );

  const isLoggedUserProfile = profileId === user.id;

  useEffect(() => {
    if (
      !Object.values(FriendsPageSection).includes(section as FriendsPageSection)
    ) {
      goTo(FriendsPageSection.Friends);
      return;
    }
    store.setSection(section as FriendsPageSection, profileId);
  }, [profileId, store, goTo, section]);

  const friendsSectionClickHandler = () => goTo(FriendsPageSection.Friends);
  const mutualFriendsSectionClickHandler = () =>
    goTo(FriendsPageSection.MutualFriends);
  const suggestionsSectionClickHandler = () =>
    goTo(FriendsPageSection.FriendSuggestions);
  const incomingRequestsSectionClickHandler = () =>
    goTo(FriendsPageSection.IncomingFriendRequest);
  const outgoingRequestsSectionClickHandler = () =>
    goTo(FriendsPageSection.OutgoingFriendRequest);

  const actionSuccessHandler = async (
    _: RelationshipAction,
    targetProfileId: string
  ) => store.removeProfile(targetProfileId);

  const profileUsernameClickHandler = (profileId: string) =>
    routerHistory.push(`/profile/${profileId}`);

  return (
    /* eslint-disable jsx-a11y/anchor-is-valid */
    <div className="columns p-4">
      <div className="column is-one-quarter">
        <div className="box">
          <aside className="menu">
            <p className="menu-label">Friends</p>
            <ul className="menu-list">
              <li>
                <a
                  onClick={friendsSectionClickHandler}
                  className={classNames({
                    "is-active": selectedSection === FriendsPageSection.Friends,
                  })}
                >
                  {isLoggedUserProfile ? "Your friends" : "Friends"}
                </a>
              </li>
              {user.isLogged && !isLoggedUserProfile && (
                <li>
                  <a
                    onClick={mutualFriendsSectionClickHandler}
                    className={classNames({
                      "is-active":
                        selectedSection === FriendsPageSection.MutualFriends,
                    })}
                  >
                    Mutual friends
                  </a>
                </li>
              )}
              {isLoggedUserProfile && (
                <li>
                  <a
                    onClick={suggestionsSectionClickHandler}
                    className={classNames({
                      "is-active":
                        selectedSection ===
                        FriendsPageSection.FriendSuggestions,
                    })}
                  >
                    Bunnies you may know
                  </a>
                </li>
              )}
            </ul>
            {isLoggedUserProfile && (
              <>
                <p className="menu-label">Requests</p>
                <ul className="menu-list">
                  <li>
                    <a
                      onClick={incomingRequestsSectionClickHandler}
                      className={classNames({
                        "is-active":
                          selectedSection ===
                          FriendsPageSection.IncomingFriendRequest,
                      })}
                    >
                      Incoming friend requests
                    </a>
                  </li>
                  <li>
                    <a
                      onClick={outgoingRequestsSectionClickHandler}
                      className={classNames({
                        "is-active":
                          selectedSection ===
                          FriendsPageSection.OutgoingFriendRequest,
                      })}
                    >
                      Outgoing friend requests
                    </a>
                  </li>
                </ul>
              </>
            )}
          </aside>
        </div>
      </div>
      <div className="column is-half">
        {profiles.length === 0 && !isFetchingProfiles && (
          <div className="box has-text-centered">No results.</div>
        )}
        {profiles.map((profile) => (
          <div className="box mb-3" key={profile.id}>
            <div className="is-flex is-align-items-center is-justify-content-space-between is-flex-wrap-wrap">
              <div className="is-flex is-align-items-center">
                <figure className="image is-64x64 is-flex is-flex-shrink-0">
                  <ProfileImage username={profile.username} />
                </figure>
                <p
                  className="title is-flex ml-4 is-clickable underline-on-hover"
                  onClick={() => profileUsernameClickHandler(profile.id)}
                >
                  {profile.username}
                </p>
              </div>
              {user.isLogged && isLoggedUserProfile && (
                <RelationshipButtonContainer
                  profileId={user.id}
                  targetProfileId={profile.id}
                  relationship={sectionRelationshipMap[selectedSection]}
                  onActionSuccess={actionSuccessHandler}
                  onActionFailure={async () => null}
                />
              )}
            </div>
          </div>
        ))}
        {isFetchingProfiles && (
          <LoadingSpinner isLarge isTransparent></LoadingSpinner>
        )}
      </div>
      <div className="column is-one-quarter">
        <ChatPanel></ChatPanel>
      </div>
    </div>
  );
};

export default FriendsPage;
