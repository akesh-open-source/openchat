# Conversations API

Clients reach conversation routes via the **gateway** (`/conversations/...`).
A Bearer access token is required on every path.

The gateway proxies `/conversations` and `/conversations/{path}` to the
messaging service (`GATEWAY_MESSAGING_SERVICE_URL`). Nested message routes under
a conversation (e.g. `/conversations/{id}/messages`) go through this same proxy.

## Persistence (schema)

Messaging owns:

| Table | Purpose |
|---|---|
| `conversations` | Chat threads. `type=direct` now; `group` later. Direct rows store a sorted pair (`direct_user_a_id` < `direct_user_b_id`) with a unique constraint so each 1:1 pair has one conversation. |
| `memberships` | `(conversation_id, user_id)` PK, `role` (`member`/`admin`), `joined_at`. |

HTTP create/list endpoints land in later Phase 2 commits (`POST /conversations/direct`,
`GET /conversations`, etc.).
