import classNames from "classnames";

import ProfileImage from "../../common/components/ProfileImage";
import { Conversation } from "../model";

export interface ConversationContainerProps {
  conversation: Conversation;
  lastMessageFromLoggedUser: boolean;
}

const ConversationContainer = ({
  conversation,
  lastMessageFromLoggedUser,
}: ConversationContainerProps) => {
  return (
    <div className="card">
      <div
        className={classNames("conversation-container card-content", {
          "not-read": !conversation.readAt,
        })}
      >
        <div
          className="is-flex is-align-items-center is-justify-content-space-between"
          key={conversation.chatGroupId}
        >
          <div className="media mb-0 conversation-inner-container">
            <div className="media-left">
              <figure className="image is-64x64 is-flex-shrink-0">
                <ProfileImage username={conversation.chatGroupName} />
              </figure>
            </div>
            <div className="media-content last-message-container">
              <div>
                <p className="title is-4 mb-0">{conversation.chatGroupName}</p>
              </div>
              <p className="subtitle is-6 content-container mt-4">
                {lastMessageFromLoggedUser
                  ? "You: "
                  : `${conversation.chatGroupName}: `}
                {conversation.content}
              </p>
            </div>
          </div>
          {!conversation.readAt && (
            <i className="fas fa-circle has-text-info"></i>
          )}
        </div>
      </div>
      <hr className="solid m-0"></hr>
      <style jsx>
        {`
          .conversation-container {
            border-radius: 4px;
          }

          .conversation-inner-container {
            overflow: hidden;
          }

          .last-message-container {
            overflow: hidden;
            white-space: nowrap;
          }

          .content-container {
            overflow: hidden;
            text-overflow: ellipsis;
          }

          .not-read {
            border: 1px solid #3e8ed0;
          }
        `}
      </style>
    </div>
  );
};

export default ConversationContainer;
