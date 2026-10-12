import type { ApiClient } from "./client";
import type {
  ChangePasswordRequest,
  CompleteRegisterRequest,
  CompleteRegisterResponse,
  DeviceResponse,
  ForgotPasswordRequest,
  ForgotPasswordResponse,
  HealthResponse,
  InitiateRegisterRequest,
  InitiateRegisterResponse,
  LoginUserRequest,
  LoginUserResponse,
  LogoutRequest,
  RefreshTokensRequest,
  RefreshTokensResponse,
  ResetPasswordRequest,
  SessionResponse,
} from "../types";

export function createAuthApi(client: ApiClient) {
  return {
    health(): Promise<HealthResponse> {
      return client.get<HealthResponse>("/health", undefined, false);
    },

    initiateRegister(body: InitiateRegisterRequest): Promise<InitiateRegisterResponse> {
      return client.post<InitiateRegisterResponse>("/auth/initiate-register", body, false);
    },

    completeRegister(body: CompleteRegisterRequest): Promise<CompleteRegisterResponse> {
      return client.post<CompleteRegisterResponse>("/auth/complete-register", body, false);
    },

    async login(body: LoginUserRequest): Promise<LoginUserResponse> {
      const tokens = await client.post<LoginUserResponse>("/auth/login", body, false);
      client.tokenStore.setTokens(tokens);
      return tokens;
    },

    async refresh(body?: RefreshTokensRequest): Promise<RefreshTokensResponse> {
      const refresh_token = body?.refresh_token ?? client.tokenStore.getRefreshToken();
      if (!refresh_token) {
        throw new Error("Missing refresh token");
      }
      const tokens = await client.post<RefreshTokensResponse>(
        "/auth/refresh",
        { refresh_token } satisfies RefreshTokensRequest,
        false,
      );
      client.tokenStore.setTokens(tokens);
      return tokens;
    },

    async logout(body?: LogoutRequest): Promise<void> {
      const refresh_token = body?.refresh_token ?? client.tokenStore.getRefreshToken();
      if (refresh_token) {
        await client.post<void>("/auth/logout", { refresh_token } satisfies LogoutRequest, false);
      }
      client.tokenStore.clear();
    },

    forgotPassword(body: ForgotPasswordRequest): Promise<ForgotPasswordResponse> {
      return client.post<ForgotPasswordResponse>("/auth/forgot-password", body, false);
    },

    resetPassword(body: ResetPasswordRequest): Promise<void> {
      return client.post<void>("/auth/reset-password", body, false);
    },

    changePassword(body: ChangePasswordRequest): Promise<void> {
      return client.post<void>("/auth/change-password", body, true);
    },

    listDevices(): Promise<DeviceResponse[]> {
      return client.get<DeviceResponse[]>("/auth/devices");
    },

    listSessions(): Promise<SessionResponse[]> {
      return client.get<SessionResponse[]>("/auth/sessions");
    },

    revokeSession(sessionId: string): Promise<void> {
      return client.delete<void>(`/auth/sessions/${sessionId}`);
    },
  };
}

export type AuthApi = ReturnType<typeof createAuthApi>;
