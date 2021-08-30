import classNames from "classnames";
import { useEffect, useRef, useState } from "react";
import { delay, map, Subject, take, throttleTime } from "rxjs";

import LoadingSpinner from "../../common/components/LoadingSpinner";
import ProfileImage from "../../common/components/ProfileImage";
import { useObservable, useService, useUser } from "../../common/hooks";
import { routerHistory } from "../../common/router";
import { PrivateChat } from "../model";
import { ChatStore } from "../stores/chatStore";
import ChatMessageBox from "./ChatMessageBox";

export interface ChatBoxProps {
  friendChat: PrivateChat;
}

const IS_TYPING_THROTTLE_TIME: number = 3000;

const ChatBox = ({ friendChat }: ChatBoxProps) => {
  const user = useUser();
  const store = useService(ChatStore);
  const isOnline = useObservable(
    store.onlineFriendsIds$.pipe(
      map((ids) => !!ids.filter((id) => id === friendChat.profileId)[0])
    ),
    false
  );
  const chatData = useObservable(
    store.chatBoxesData.get(friendChat.chatGroupId)!.asObservable()
  );

  const [messageInput, setMessageInput] = useState<string>("");

  const lastScrollHeight = useRef(0);
  const isTyping$ = useRef(new Subject<string>()).current;
  const messagesBox = useRef<HTMLHeadingElement>(null);
  const messagesBottom = useRef<HTMLHeadingElement>(null);

  const scrollToBottom = () => {
    if (messagesBottom.current) {
      (messagesBottom.current as any).scrollIntoView();
    }
  };

  useEffect(() => {
    const isTypingSubscription = isTyping$
      .pipe(throttleTime(IS_TYPING_THROTTLE_TIME))
      .subscribe(() => {
        store.isTyping(friendChat.chatGroupId);
      });

    const scrollSubscription = store.chatBoxesData
      .get(friendChat.chatGroupId)!
      .asObservable()
      .pipe(
        take(1),
        map((data) =>
          data.scrollTo.pipe(delay(0)).subscribe((direction) => {
            if (direction === "bottom") {
              scrollToBottom();
            } else if (lastScrollHeight.current && messagesBox.current) {
              if (
                messagesBox.current.scrollHeight !== lastScrollHeight.current
              ) {
                const currScrollHeight = messagesBox.current.scrollHeight;
                (messagesBox.current as any).scrollTop =
                  currScrollHeight - lastScrollHeight.current;
                lastScrollHeight.current = currScrollHeight;
              }
            }
          })
        )
      )
      .subscribe();

    return () => {
      scrollSubscription.unsubscribe();
      isTypingSubscription.unsubscribe();
    };
  }, [store, friendChat.chatGroupId, isTyping$]);

  const closeChatHandler = (e: React.MouseEvent<HTMLElement>) => {
    e.stopPropagation();
    store.removeChatFromFooter(friendChat);
  };

  const chatClickHandler = () => {
    store.setChatIsOpen(friendChat.chatGroupId, !chatData.isOpen, true);
  };

  const sendMessageHandler = (message: string) => {
    if (message.trim() === "") {
      return;
    }
    setMessageInput("");
    store.sendMessage(message, friendChat.chatGroupId);
  };

  const messageInputChangeHandler = (text: string) => {
    setMessageInput(text);
    isTyping$.next(friendChat.chatGroupId);
  };

  const handleScroll = (e: any) => {
    if (e.target.scrollTop === 0) {
      lastScrollHeight.current = e.target.scrollHeight;
      store
        .loadMoreMessages(friendChat.chatGroupId)
        .then(() => chatData.scrollTo.next("top"));
    }
  };

  return (
    <div
      className={classNames({
        "has-pointer-events-all": chatData.isOpen,
      })}
    >
      <div
        className={classNames("chat-container is-fullwidth", {
          "is-hidden": !chatData.isOpen,
        })}
      >
        <nav className="is-flex is-flex-direction-column panel is-height-100 has-background-white">
          <div className="panel-heading is-flex is-align-items-center is-justify-content-space-between p-2">
            <div className="is-flex is-align-items-center">
              <figure className="image is-32x32 is-inline-block is-flex-shrink-0">
                <ProfileImage username={friendChat.username} />
              </figure>
              <span
                className="ml-2 is-clickable underline-on-hover"
                onClick={() =>
                  routerHistory.push(`/profile/${friendChat.profileId}`)
                }
              >
                {friendChat.username}
              </span>
            </div>
          </div>
          <div
            className="has-background-white is-flex-grow-1 p-1 chat-messages"
            onScroll={handleScroll}
            ref={messagesBox}
          >
            {chatData.isLoadingMessages && (
              <LoadingSpinner isTransparent></LoadingSpinner>
            )}
            {chatData.messages.map((message) => (
              <ChatMessageBox
                key={message.id}
                loggedUserId={user.id}
                message={message}
              ></ChatMessageBox>
            ))}
            <div
              className={classNames("loading has-text-grey is-size-7 mt-1", {
                "has-visibility-hidden": !chatData.usernameIsTyping,
              })}
            >
              {chatData.usernameIsTyping} is typing
            </div>
            <div ref={messagesBottom}></div>
          </div>
          <div className="field">
            <div className="control has-icons-left">
              <input
                type="text"
                className="input"
                onKeyDown={(e) =>
                  e.key === "Enter" ? sendMessageHandler(messageInput) : null
                }
                onChange={(e) => messageInputChangeHandler(e.target.value)}
                value={messageInput}
              ></input>
              <span className="icon is-small is-left">
                <i className="far fa-comment" />
              </span>
            </div>
          </div>
        </nav>
      </div>
      <div
        className="box is-fullwidth is-flex is-align-items-center is-justify-content-space-between is-clickable is-unselectable chat-thumbnail"
        onClick={chatClickHandler}
      >
        <div>
          <i
            className={classNames("fas fa-circle", {
              "has-text-primary": isOnline,
              "has-text-grey": !isOnline,
            })}
            aria-hidden="true"
          ></i>
          <b className="ml-2">{friendChat.username}</b>
          {chatData.unreadMessages > 0 && (
            <span className="unread-messages-count ml-2">
              {chatData.unreadMessages}
            </span>
          )}
        </div>
        <div className="is-flex is-align-items-center">
          <i
            className={classNames("fas", {
              "fa-chevron-up": chatData.isOpen,
              "fa-chevron-down": !chatData.isOpen,
            })}
            aria-hidden="true"
          ></i>
          <button className="delete ml-3" onClick={closeChatHandler}></button>
        </div>
      </div>
      <style jsx>
        {`
          .chat-container {
            height: 22rem;
            position: relative;
          }

          .chat-messages {
            overflow-y: scroll;
          }

          .chat-thumbnail {
            border: 1px solid #3e8ed0;
            height: 3rem;
          }

          .unread-messages-count {
            padding: 2px 8px;
            border-radius: 50%;
            background: red;
            color: white;
          }

          .loading {
            font-size: 30px;
          }

          .loading:after {
            overflow: hidden;
            display: inline-block;
            vertical-align: bottom;
            -webkit-animation: ellipsis steps(4, end) 1800ms infinite;
            animation: ellipsis steps(4, end) 1800ms infinite;
            content: "...";
            width: 0px;
          }

          @keyframes ellipsis {
            to {
              width: 1.25em;
            }
          }

          @-webkit-keyframes ellipsis {
            to {
              width: 1.25em;
            }
          }
        `}
      </style>
    </div>
  );
};

export default ChatBox;
