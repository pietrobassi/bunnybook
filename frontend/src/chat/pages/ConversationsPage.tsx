import { useEffect } from "react";
import { useParams } from "react-router-dom";

import LoadingSpinner from "../../common/components/LoadingSpinner";
import {
  useObservable,
  useOnScrollToBottom,
  useService,
  useUser,
} from "../../common/hooks";
import { routerHistory } from "../../common/router";
import ChatPanel from "../components/ChatPanel";
import ConversationContainer from "../components/ConversationContainer";
import { ChatStore } from "../stores/chatStore";
import { ConversationsPageStore } from "../stores/conversationsPageStore";

const ConversationsPage = () => {
  const store = useService(ConversationsPageStore);
  const chatStore = useService(ChatStore);
  const user = useUser();
  const conversations = useObservable(store.conversations$);
  const isFetchingConversations = useObservable(store.isFetchingConversations$);

  useOnScrollToBottom(() => store.loadMoreConversations());

  const profileId = useParams<{ profile_id: string }>().profile_id;

  useEffect(() => {
    if (user.id !== profileId) {
      routerHistory.push("/login");
    }
    store.loadMoreConversations();
  }, [user, profileId, store]);

  const conversationClickHandler = (chatGroupId: string) => {
    chatStore.setChatIsOpen(chatGroupId, true, true);
    store.markConversationAsRead(chatGroupId);
  };

  return (
    <div className="columns p-4">
      <div className="column is-one-quarter"></div>
      <div className="column is-half">
        <div className="box">
          <p className="title is-3">Conversations:</p>
          {conversations.length === 0 && !isFetchingConversations && (
            <div className="box has-text-centered">
              There are no conversations.
            </div>
          )}
          {conversations.map((conversation) => (
            <div
              key={conversation.chatGroupId}
              className="mb-2 mt-2 is-clickable"
              onClick={() => conversationClickHandler(conversation.chatGroupId)}
            >
              <ConversationContainer
                conversation={conversation}
                lastMessageFromLoggedUser={
                  conversation.fromProfileId === user.id
                }
              ></ConversationContainer>
            </div>
          ))}
          {isFetchingConversations && (
            <LoadingSpinner isLarge isTransparent></LoadingSpinner>
          )}
        </div>
      </div>
      <div className="column is-one-quarter">
        <ChatPanel></ChatPanel>
      </div>
    </div>
  );
};

export default ConversationsPage;
