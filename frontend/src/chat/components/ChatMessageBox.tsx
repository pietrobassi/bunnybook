import classNames from "classnames";
import { ChatMessage } from "../model";

export interface ChatMessageBoxProps {
  loggedUserId: string;
  message: ChatMessage;
}

const ChatMessageBox = ({ loggedUserId, message }: ChatMessageBoxProps) => {
  const isFromLoggedUser = message.fromProfileId === loggedUserId;

  return (
    <div
      className={classNames("is-flex mt-1", {
        "is-justify-content-flex-end": isFromLoggedUser,
        "is-justify-content-flex-start": !isFromLoggedUser,
      })}
    >
      <div
        className={classNames("notification p-1 pl-2 pr-2 message-content", {
          "is-info ml-6": isFromLoggedUser,
          "mr-6": !isFromLoggedUser,
        })}
      >
        {message.content}
      </div>
      <style jsx>
        {`
          .message-content {
            word-break: break-word;
          }
        `}
      </style>
    </div>
  );
};

export default ChatMessageBox;
