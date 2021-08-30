import { useObservable, useService } from "../../common/hooks";
import { PrivateChat } from "../model";
import { ChatStore } from "../stores/chatStore";
import ChatBox from "./ChatBox";

const ChatFooter = () => {
  const store = useService(ChatStore);
  const footerChats = useObservable(store.footerChats$);

  return (
    <div className="columns p-0 m-0 is-flex is-flex-direction-row-reverse is-align-items-flex-end chat-footer has-pointer-events-none is-hidden-mobile">
      {footerChats.map((privateChat: PrivateChat) => (
        <div
          key={privateChat.chatGroupId}
          className="column is-2-fullhd is-3-widescreen is-4-tablet p-0 pl-1 pr-1"
        >
          <ChatBox friendChat={privateChat}></ChatBox>
        </div>
      ))}
      <style jsx>
        {`
          .chat-footer {
            position: fixed;
            width: 100%;
            bottom: 0;
            pointerevents: none;
          }
        `}
      </style>
    </div>
  );
};

export default ChatFooter;
