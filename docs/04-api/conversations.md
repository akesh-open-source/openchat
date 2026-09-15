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
| `conversations` | Chat threads. `type=direct` now; `group` later. Direct rows store a sorted pair (`direct_user_a_id` < `direct_user_b_id`) with a unique constraint so each 1:1 pair has one conversation. |
| `memberships` | `(conversation_id, user_id)` PK, `role` (`member`/`admin`), `joined_at`. |

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
