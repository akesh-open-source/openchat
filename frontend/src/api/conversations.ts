import type { ApiClient } from "./client";
import type {
  ConversationListResponse,
  ConversationResponse,
  CreateDirectConversationRequest,
  DirectConversationResponse,
  ListConversationsQuery,
} from "../types";

export function createConversationsApi(client: ApiClient) {
  return {
    createDirect(
      body: CreateDirectConversationRequest,
    ): Promise<DirectConversationResponse> {
      return client.post<DirectConversationResponse>("/conversations/direct", body);
    },

    list(query: ListConversationsQuery = {}): Promise<ConversationListResponse> {
      return client.get<ConversationListResponse>("/conversations", {
        limit: query.limit,
        cursor: query.cursor,
      });
    },

    get(conversationId: string): Promise<ConversationResponse> {
      return client.get<ConversationResponse>(`/conversations/${conversationId}`);
    },
  };
}

export type ConversationsApi = ReturnType<typeof createConversationsApi>;
