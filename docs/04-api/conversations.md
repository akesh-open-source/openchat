# Conversations API

Clients reach conversation routes via the **gateway** (`/conversations/...`).
A Bearer access token is required on every path.

The gateway proxies `/conversations` and `/conversations/{path}` to the
messaging service (`GATEWAY_MESSAGING_SERVICE_URL`). Nested message routes under
a conversation (e.g. `/conversations/{id}/messages`) go through this same proxy.

Messaging re-verifies the access JWT with the auth public key (`sub` = caller).

## Persistence (schema)

| Table | Purpose |
|---|---|
| `conversations` | Chat threads. `type=direct` now; `group` later. Direct rows store a sorted pair (`direct_user_a_id` < `direct_user_b_id`) with a unique constraint so each 1:1 pair has one conversation. Also stores `next_sequence` for server-side message ordering. |
| `memberships` | `(conversation_id, user_id)` PK, `role` (`member`/`admin`), `joined_at`. |
| `messages` | Persisted chat messages with per-conversation `sequence`, `client_message_id`, and `body`. Used for last-message preview on list/get. |

## `POST /conversations/direct`

Create a one-to-one conversation with another user, or return the existing one
for that pair (idempotent).

### Request

```json
{ "peer_user_id": "<uuid>" }
```

### Response `200`

```json
{
  "id": "<conversation uuid>",
  "type": "direct",
  "peer_user_id": "<uuid>",
  "created": true,
  "created_at": "...",
  "updated_at": "..."
}
```

`created` is `false` when the conversation already existed.

### Errors

| Status | When |
|---|---|
| `400` | `peer_user_id` equals the caller (self-chat) |
| `401` | Missing/invalid Bearer token |
| `404` | Peer has no profile in the users service |
| `502` | Users service unreachable / unexpected error during lookup |
| `422` | Invalid body |

### Peer existence

Messaging **does not trust** the client alone. Before create-or-get it calls
users over HTTP (`GET /users/lookup?user_id=…`) with the caller's Bearer token
(`MESSAGING_USERS_SERVICE_URL`). Unknown peers → `404`.

Clients may still call `GET /users/lookup` first for UX (email → `user_id`), but
messaging re-checks on create.

## `GET /conversations`

List conversations the **caller is a member of** only (newest `updated_at` first).

### Query

| Param | Default | Notes |
|---|---|---|
| `limit` | `20` | 1–100 |
| `cursor` | omitted | Opaque keyset cursor from a previous `next_cursor` |

### Response `200`

```json
{
  "items": [
    {
      "id": "<uuid>",
      "type": "direct",
      "peer_user_id": "<uuid>",
      "peer_display_name": "Ada",
      "last_message_preview": "hello…",
      "last_message_at": "...",
      "last_activity_at": "...",
      "created_at": "...",
      "updated_at": "..."
    }
  ],
  "next_cursor": "<opaque>|null"
}
```

- `peer_display_name` comes from users lookup (`GET /users/lookup`) for each
  peer on the page (caller JWT forwarded). If users is down, names are `null`
  and the list still returns `200`.
- `last_message_preview` / `last_message_at` are from the highest-`sequence`
  message in that conversation (preview truncated to ~200 chars). Both are
  `null` when there are no messages yet.
- `last_activity_at` is `last_message_at` when present, otherwise `updated_at`.
- Cursor is keyset on `(updated_at DESC, id DESC)`.

### Errors

| Status | When |
|---|---|
| `400` | Malformed `cursor` |
| `401` | Missing/invalid Bearer token |
| `422` | Invalid `limit` |

## `GET /conversations/{id}`

Return one conversation **only if** the caller is a member.

### Authz

Non-members and unknown ids both return **`404`** (do not leak existence).

### Response `200`

Same item shape as list entries (including peer display name and last-message
preview).

### Errors

| Status | When |
|---|---|
| `401` | Missing/invalid Bearer token |
| `404` | Missing conversation or caller is not a member |
