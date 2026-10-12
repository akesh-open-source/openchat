import type { LookupProfileQuery, UpdateProfileRequest } from "../types";
import { useOpenChatApi } from "./OpenChatApiProvider";
import { useAsync, useMutation } from "./useAsync";

export function useMe() {
  const { users } = useOpenChatApi();
  const query = useAsync(() => users.getMe(), [users]);
  const update = useMutation((body: UpdateProfileRequest) => users.updateMe(body));

  return {
    ...query,
    updateProfile: async (body: UpdateProfileRequest) => {
      const profile = await update.mutate(body);
      await query.refetch();
      return profile;
    },
    updating: update.loading,
    updateError: update.error,
  };
}

export function useUser(userId: string | null) {
  const { users } = useOpenChatApi();
  return useAsync(() => users.getById(userId as string), [users, userId], {
    enabled: Boolean(userId),
  });
}

export function useUserLookup(query: LookupProfileQuery | null) {
  const { users } = useOpenChatApi();
  return useAsync(
    () => users.lookup(query as LookupProfileQuery),
    [users, query && "email" in query ? query.email : null, query && "user_id" in query ? query.user_id : null],
    { enabled: query != null },
  );
}
