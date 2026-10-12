import type { ApiClient } from "./client";
import type {
  LookupProfileQuery,
  LookupProfileResponse,
  ProfileResponse,
  UpdateProfileRequest,
} from "../types";

export function createUsersApi(client: ApiClient) {
  return {
    getMe(): Promise<ProfileResponse> {
      return client.get<ProfileResponse>("/users/me");
    },

    getById(userId: string): Promise<ProfileResponse> {
      return client.get<ProfileResponse>(`/users/${userId}`);
    },

    lookup(query: LookupProfileQuery): Promise<LookupProfileResponse> {
      return client.get<LookupProfileResponse>("/users/lookup", query);
    },

    updateMe(body: UpdateProfileRequest): Promise<ProfileResponse> {
      return client.patch<ProfileResponse>("/users/me", body);
    },
  };
}

export type UsersApi = ReturnType<typeof createUsersApi>;
