import { useCallback } from "react";
import type {
  ChangePasswordRequest,
  CompleteRegisterRequest,
  ForgotPasswordRequest,
  InitiateRegisterRequest,
  LoginUserRequest,
  ResetPasswordRequest,
} from "../types";
import { useOpenChatApi } from "./OpenChatApiProvider";
import { useAsync, useMutation } from "./useAsync";

export function useAuth() {
  const { auth, client } = useOpenChatApi();
  const isAuthenticated = Boolean(client.tokenStore.getAccessToken());

  const login = useMutation(auth.login);
  const logout = useMutation(async () => {
    await auth.logout();
  });
  const refresh = useMutation(async () => auth.refresh());
  const initiateRegister = useMutation(auth.initiateRegister);
  const completeRegister = useMutation(auth.completeRegister);
  const forgotPassword = useMutation(auth.forgotPassword);
  const resetPassword = useMutation(auth.resetPassword);
  const changePassword = useMutation(auth.changePassword);

  return {
    isAuthenticated,
    login: (body: LoginUserRequest) => login.mutate(body),
    logout: () => logout.mutate(undefined),
    refresh: () => refresh.mutate(undefined),
    initiateRegister: (body: InitiateRegisterRequest) => initiateRegister.mutate(body),
    completeRegister: (body: CompleteRegisterRequest) => completeRegister.mutate(body),
    forgotPassword: (body: ForgotPasswordRequest) => forgotPassword.mutate(body),
    resetPassword: (body: ResetPasswordRequest) => resetPassword.mutate(body),
    changePassword: (body: ChangePasswordRequest) => changePassword.mutate(body),
    loginState: login,
    logoutState: logout,
    registerState: { initiateRegister, completeRegister },
    forgotPasswordState: forgotPassword,
    resetPasswordState: resetPassword,
    changePasswordState: changePassword,
  };
}

export function useDevices() {
  const { auth } = useOpenChatApi();
  return useAsync(() => auth.listDevices(), [auth]);
}

export function useSessions() {
  const { auth } = useOpenChatApi();
  const list = useAsync(() => auth.listSessions(), [auth]);
  const revoke = useCallback(
    async (sessionId: string) => {
      await auth.revokeSession(sessionId);
      await list.refetch();
    },
    [auth, list],
  );
  return { ...list, revokeSession: revoke };
}
