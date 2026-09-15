# Conversations API

Clients reach conversation routes via the **gateway** (`/conversations/...`).
A Bearer access token is required on every path.

The gateway proxies `/conversations` and `/conversations/{path}` to the
messaging service (`GATEWAY_MESSAGING_SERVICE_URL`). Nested message routes under
a conversation (e.g. `/conversations/{id}/messages`) go through this same proxy.

Endpoint details will land with Phase 2 messaging commits (`POST /conversations/direct`,
`GET /conversations`, etc.).
