import { ApiClient, type ApiClientOptions } from "./client";
import { createAuthApi } from "./auth";
import { createConversationsApi } from "./conversations";
import { createUsersApi } from "./users";

export function createOpenChatApi(options: ApiClientOptions = {}) {
  const client = new ApiClient(options);
  return {
    client,
    auth: createAuthApi(client),
    users: createUsersApi(client),
    conversations: createConversationsApi(client),
  };
}

export type OpenChatApi = ReturnType<typeof createOpenChatApi>;

export { ApiClient } from "./client";
export type { ApiClientOptions } from "./client";
export { ApiError, isApiError } from "./errors";
export {
  LocalStorageTokenStore,
  MemoryTokenStore,
  type TokenStore,
} from "./tokenStore";
