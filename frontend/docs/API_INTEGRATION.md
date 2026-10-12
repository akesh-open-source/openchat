# API integration

Browser clients talk **only** to the gateway (`http://localhost:8000`).

## Auth

Register is two steps: `POST /auth/initiate-register` then
`POST /auth/complete-register` with the email token (`registration_token` is
returned only when auth debug is on).

Login requires `device_id`. Store `access_token` and `refresh_token`. Send:

```http
Authorization: Bearer <access_token>
```

`POST /auth/refresh` rotates both tokens. `POST /auth/logout` revokes the
refresh token (204).

## Users

`GET /users/lookup` takes **exactly one** of `email` or `user_id`. Response is
minimal (`user_id`, `display_name`) for starting a 1:1 chat.

`PATCH /users/me` only. Omit fields you do not want to change.

## Conversations

`POST /conversations/direct` with `{ "peer_user_id": "<uuid>" }` is idempotent
(`created: true|false`).

List is membership-only, newest first, keyset cursor via `next_cursor`.

Non-members of `GET /conversations/{id}` receive `404`.

## Not yet on HTTP

Message send/history, WebSocket realtime, and push-token APIs are not wired
through the gateway. Domain `Message` fields:

| Field | Type |
| --- | --- |
| id, conversation_id, sender_id | uuid string |
| client_message_id | string |
| sequence | number |
| body | string |
| status | `SENT` \| `DELIVERED` \| `READ` |
| created_at | ISO datetime string |
