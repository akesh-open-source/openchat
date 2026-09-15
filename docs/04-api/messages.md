# Messages API

Clients reach top-level message routes via the **gateway** (`/messages/...`).
A Bearer access token is required on every path.

The gateway proxies `/messages` and `/messages/{path}` to the messaging service
(`GATEWAY_MESSAGING_SERVICE_URL`).

Conversation-scoped message routes (send/list under `/conversations/{id}/messages`)
are proxied with the conversations routes — see [conversations.md](./conversations.md).

Endpoint details will land with Phase 2 messaging commits.
