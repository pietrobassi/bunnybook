import API from "../common/api";
import { ChatMessage, Conversation } from "./model";

export const chatApi = {
  getChatMessages: (
    chat_group_id: string,
    older_than?: string,
    limit?: number
  ): Promise<ChatMessage[]> =>
    API.get<ChatMessage[]>(`/chat/${chat_group_id}/messages`, {
      params: {
        older_than,
        limit,
      },
    }).then((response) => response.data),
  getConversations: (
    profile_id: string,
    older_than?: string,
    limit?: number
  ): Promise<Conversation[]> =>
    API.get<Conversation[]>(`/profiles/${profile_id}/conversations`, {
      params: {
        older_than,
        limit,
      },
    }).then((response) => response.data),
};
