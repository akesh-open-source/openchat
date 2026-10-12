/**
 * Client types mapped from gateway-facing FastAPI / Pydantic DTOs.
 *
 * Mapping:
 *   UUID / EmailStr / str  → string
 *   datetime               → string (ISO-8601)
 *   int                    → number
 *   bool                   → boolean
 *   Optional[T]            → T | null
 *
 * Internal-only routes (e.g. POST /internal/profiles) are not included.
 */

export type Uuid = string;
export type IsoDateTime = string;
export type Email = string;

export type TokenType = "bearer";

export type ConversationType = "direct" | "group";

export type MessageStatus = "SENT" | "DELIVERED" | "READ";

export interface ApiErrorBody {
  detail: string | Record<string, unknown> | unknown[];
}

export interface HealthResponse {
  status: string;
}

// --- Auth ---

export interface InitiateRegisterRequest {
  email: Email;
  password: string;
  display_name: string;
}

export interface InitiateRegisterResponse {
  detail: string;
  registration_token: string | null;
}

export interface CompleteRegisterRequest {
  token: string;
}

export interface CompleteRegisterResponse {
  user_id: string;
  email: Email;
  display_name: string;
}

export interface LoginUserRequest {
  email: Email;
  password: string;
  device_id: string;
  device_name?: string | null;
}

export interface LoginUserResponse {
  access_token: string;
  refresh_token: string;
  token_type: TokenType;
}

export interface RefreshTokensRequest {
  refresh_token: string;
}

export interface RefreshTokensResponse {
  access_token: string;
  refresh_token: string;
  token_type: TokenType;
}

export interface LogoutRequest {
  refresh_token: string;
}

export interface ForgotPasswordRequest {
  email: Email;
}

export interface ForgotPasswordResponse {
  detail: string;
  reset_token: string | null;
}

export interface ResetPasswordRequest {
  token: string;
  new_password: string;
}

export interface ChangePasswordRequest {
  current_password: string;
  new_password: string;
}

export interface DeviceResponse {
  id: Uuid;
  client_device_id: string;
  name: string | null;
  user_agent: string | null;
  created_at: IsoDateTime;
  last_seen_at: IsoDateTime;
}

export interface SessionResponse {
  id: Uuid;
  device_id: Uuid;
  ip_address: string | null;
  created_at: IsoDateTime;
  last_seen_at: IsoDateTime;
  expires_at: IsoDateTime;
}

// --- Users ---

export interface ProfileResponse {
  user_id: Uuid;
  display_name: string;
  email: Email | null;
  bio: string | null;
  avatar_url: string | null;
  created_at: IsoDateTime;
  updated_at: IsoDateTime;
}

export interface LookupProfileResponse {
  user_id: Uuid;
  display_name: string;
}

export interface UpdateProfileRequest {
  display_name?: string | null;
  bio?: string | null;
  avatar_url?: string | null;
}

export type LookupProfileQuery =
  | { email: Email; user_id?: never }
  | { user_id: Uuid; email?: never };

// --- Conversations ---

export interface CreateDirectConversationRequest {
  peer_user_id: Uuid;
}

export interface DirectConversationResponse {
  id: Uuid;
  type: ConversationType;
  peer_user_id: Uuid;
  created: boolean;
  created_at: IsoDateTime;
  updated_at: IsoDateTime;
}

export interface ConversationResponse {
  id: Uuid;
  type: ConversationType;
  peer_user_id: Uuid | null;
  peer_display_name: string | null;
  last_message_preview: string | null;
  last_message_at: IsoDateTime | null;
  last_activity_at: IsoDateTime;
  created_at: IsoDateTime;
  updated_at: IsoDateTime;
}

export interface ConversationListResponse {
  items: ConversationResponse[];
  next_cursor: string | null;
}

export interface ListConversationsQuery {
  limit?: number;
  cursor?: string | null;
}

/**
 * Domain shape for persisted messages (schema exists; HTTP send/list is not
 * on the gateway yet). Use this when those routes land.
 */
export interface Message {
  id: Uuid;
  conversation_id: Uuid;
  sender_id: Uuid;
  client_message_id: string;
  sequence: number;
  body: string;
  status: MessageStatus;
  created_at: IsoDateTime;
}
