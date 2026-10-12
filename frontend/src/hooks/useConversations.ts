import type { CreateDirectConversationRequest, ListConversationsQuery } from "../types";
import { useOpenChatApi } from "./OpenChatApiProvider";
import { useAsync, useMutation } from "./useAsync";

export function useConversations(query: ListConversationsQuery = {}) {
  const { conversations } = useOpenChatApi();
  const list = useAsync(
    () => conversations.list(query),
    [conversations, query.limit, query.cursor],
  );
  const createDirect = useMutation((body: CreateDirectConversationRequest) =>
    conversations.createDirect(body),
  );

  return {
    ...list,
    createDirect: async (body: CreateDirectConversationRequest) => {
      const created = await createDirect.mutate(body);
      await list.refetch();
      return created;
    },
    creating: createDirect.loading,
    createError: createDirect.error,
  };
}

export function useConversation(conversationId: string | null) {
  const { conversations } = useOpenChatApi();
  return useAsync(
    () => conversations.get(conversationId as string),
    [conversations, conversationId],
    { enabled: Boolean(conversationId) },
  );
}
