import classNames from "classnames";

import ProfileImage from "../../common/components/ProfileImage";
import { useObservable, useService, useUser } from "../../common/hooks";
import { FriendChat, FriendChatStatus } from "../model";
import { ChatStore } from "../stores/chatStore";

const ChatPanel = () => {
  const store = useService(ChatStore);
  const user = useUser();
  const friendsChats = useObservable(store.friendsChats$);

  const friendClickHandler = (chatGroupId: string) => {
    store.setChatIsOpen(chatGroupId, true, true);
  };

  if (!user.isLogged) {
    return <div></div>;
  }

  return (
    /* eslint-disable jsx-a11y/anchor-is-valid */
    <div className="pr-4 chat-panel-container is-hidden-mobile">
      <nav className="panel chat-panel">
        <p className="panel-heading">Chat</p>
        <div className="has-background-white friends-container">
          {friendsChats.map((friendChat: FriendChat) => (
            <a
              key={friendChat.chatGroupId}
              className="panel-block friend"
              onClick={() => friendClickHandler(friendChat.chatGroupId)}
            >
              <span className="panel-icon">
                <i
                  className={classNames("fas fa-circle", {
                    "has-text-primary":
                      friendChat.status === FriendChatStatus.Online,
                  })}
                  aria-hidden="true"
                ></i>
              </span>
              <figure className="image is-32x32 is-inline-block is-flex-shrink-0">
                <ProfileImage username={friendChat.username} />
              </figure>
              <span className="ml-2">{friendChat.username}</span>
            </a>
          ))}
        </div>
      </nav>
      <style jsx>
        {`
          .chat-panel-container {
            position: fixed;
            height: 100%;
            width: inherit;
          }

          .chat-panel {
            position: relative;
            height: calc(100% + 2rem);
            width: 80%;
            float: right;
          }

          .friends-container {
            height: calc(100% - 9.71rem);
            overflow-y: scroll;
          }

          .friend {
            border: none;
          }
        `}
      </style>
    </div>
  );
};

export default ChatPanel;
