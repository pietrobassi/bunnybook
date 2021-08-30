import { singleton } from "tsyringe";
import { WebSocketService } from "../common/websocket";

@singleton()
export class ChatService {
  constructor(private _ws: WebSocketService) {}

  public sendMessage(
    message: string,
    to: string,
    callback?: (...args: any[]) => any
  ) {
    this._ws.send("chat_message", { message, to }, callback);
  }

  public isTyping(chatGroupId: string) {
    this._ws.send("is_typing", { chatGroupId });
  }

  public markChatAsRead(chatGroupId: string, chatMessageId: string) {
    this._ws.send("mark_chat_as_read", { chatGroupId, chatMessageId });
  }
}
