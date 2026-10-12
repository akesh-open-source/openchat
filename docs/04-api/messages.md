# Messages API

Clients reach conversation-scoped message routes via the **gateway**
(`/conversations/{id}/messages/...`). A Bearer access token is required.

The gateway proxies `/conversations` (including nested `/messages`) to the
messaging service (`GATEWAY_MESSAGING_SERVICE_URL`). Top-level `/messages/...`
is also proxied for future routes.

Messaging re-verifies the access JWT with the auth public key (`sub` = caller).

## Persistence (schema)

| Field | Role |
|---|---|
| `id` | Server-generated message UUID |
| `conversation_id` | Conversation scope |
| `sender_id` | Auth user id of sender |
| `client_message_id` | Client idempotency key (unique per conversation) |
| `sequence` | Server-assigned logical order **within** the conversation |
| `body` | Text (MVP) |
| `status` | Default `SENT` |
| `created_at` | Metadata only (not the ordering authority) |

Constraints:

```text
UNIQUE(conversation_id, client_message_id)
UNIQUE(conversation_id, sequence)
```

MVP ordering authority: `SELECT conversation FOR UPDATE`, bump
`conversations.next_sequence`, insert message with that `sequence` in the same
transaction.

---

## `POST /conversations/{conversation_id}/messages`

Send a text message. Requires membership. Retries with the same
`client_message_id` return the **original** message (same `id` / `sequence`).

### Request

```json
{
  "client_message_id": "phone-abc-1",
  "body": "hello"
}
```

| Field | Required | Notes |
|---|---|---|
| `client_message_id` | yes | 1–128 chars; unique per conversation |
| `body` | yes | 1–10000 chars; non-empty after strip rules in domain |

Clients **must not** send `sequence`. The server assigns it.

### Response `200 OK`

```json
{
  "id": "0193f2a0-0000-7000-8000-000000000101",
  "conversation_id": "0193f2a0-0000-7000-8000-0000000000aa",
  "sender_id": "0193f2a0-0000-7000-8000-000000000001",
  "client_message_id": "phone-abc-1",
  "sequence": 1,
  "body": "hello",
  "status": "SENT",
  "created_at": "2026-10-12T10:01:00Z",
  "created": true
}
```

On idempotent retry, the body matches the first successful send and
`created` is `false`.

### Errors

| Status | When |
|---|---|
| `401` | Missing/invalid Bearer token |
| `404` | Conversation missing **or** caller is not a member (no existence leak) |
| `422` | Validation failure (empty body, bad UUID, etc.) |

### Authz

Non-members and unknown conversation ids both return **`404`**.

---

## Not yet implemented

- `GET /conversations/{id}/messages` history pagination (Phase 2C #4)
- Kafka / outbox publish (later slices)
