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

## `GET /conversations/{conversation_id}/messages`

Paginated history for one conversation. **Ordering authority is `sequence`
(ascending)**, not `created_at`.

Requires membership. Non-members and unknown conversation ids both return
**`404`** (no existence leak).

### Query

| Param | Default | Notes |
|---|---|---|
| `limit` | `50` | 1–100 |
| `cursor` | omitted | Opaque keyset cursor from a previous `next_cursor` |

### Cursor

Keyset on **`sequence ASC`**:

- First page (no `cursor`): messages with the lowest sequences, up to `limit`.
- `next_cursor` encodes the last item’s `sequence` on the page.
- Next page: messages with `sequence` **greater than** that value.

Pages are contiguous: if page 1 ends at sequence `N`, page 2 starts at
`N + 1` (when that message exists). Do **not** use offset pagination; clients
must pass the opaque `cursor` string as returned (do not invent offsets).

Malformed `cursor` → **`400`**.

### Response `200 OK`

```json
{
  "items": [
    {
      "id": "0193f2a0-0000-7000-8000-000000000101",
      "conversation_id": "0193f2a0-0000-7000-8000-0000000000aa",
      "sender_id": "0193f2a0-0000-7000-8000-000000000001",
      "client_message_id": "phone-abc-1",
      "sequence": 1,
      "body": "hello",
      "status": "SENT",
      "created_at": "2026-10-12T10:01:00Z"
    }
  ],
  "next_cursor": "<opaque>|null"
}
```

`next_cursor` is `null` when there is no further page.

### Errors

| Status | When |
|---|---|
| `400` | Malformed `cursor` |
| `401` | Missing/invalid Bearer token |
| `404` | Conversation missing **or** caller is not a member |
| `422` | Invalid `limit` |

### Authz

Same as send: outsiders see **`404`**, not `403`.

---

## Not yet implemented

- Kafka / outbox publish (later slices)
- `sync-since` / gap recovery (Phase 3)
