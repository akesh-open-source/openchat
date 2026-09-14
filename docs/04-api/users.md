# Users API

Public profile routes are reached via the **gateway** (`/users/...`, JWT required).

Internal routes are **Compose-only** — call the users service directly on the
`edge` network (e.g. `http://users:8002`). They are **not** exposed through the
gateway `/users` proxy.

## Internal: create profile (auth → users)

Used after verified registration so auth can create a profile without sharing DBs.

**Failure policy (auth):** after the auth user is persisted, profile sync is
**best-effort** — if the users service is down or returns an error, registration
still succeeds and auth logs the failure. `POST /internal/profiles` is
idempotent, so a later retry (or manual call) can create the missing profile.

| | |
|---|---|
| Method | `POST` |
| Path | `/internal/profiles` |
| Caller | Auth service via `AUTH_USERS_SERVICE_URL` (Compose `edge` network) |
| Auth | None at edge (network isolation). Do not publish this path on the gateway. |
| Idempotency | Same `user_id` twice returns the existing profile (`created: false`). |

### Request

```json
{
  "user_id": "0193f2a0-0000-7000-8000-000000000001",
  "display_name": "Alice",
  "email": "alice@example.com"
}
```

| Field | Required | Notes |
|---|---|---|
| `user_id` | yes | Same UUID as `auth` user id |
| `display_name` | yes | 3–30 characters |
| `email` | no | Stored normalized lowercase when present |

### Response `200 OK`

```json
{
  "user_id": "0193f2a0-0000-7000-8000-000000000001",
  "display_name": "Alice",
  "email": "alice@example.com",
  "created": true,
  "created_at": "2026-09-15T01:00:00Z",
  "updated_at": "2026-09-15T01:00:00Z"
}
```

On a duplicate create for the same `user_id`, `created` is `false` and the
existing row is returned (no second profile).

### Errors

| Status | When |
|---|---|
| `422` | Validation failure (bad UUID, short display name, invalid email) |
| `400` | Domain validation (e.g. invalid display name after strip) |
