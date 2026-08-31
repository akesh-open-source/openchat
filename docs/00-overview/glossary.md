# Glossary

## Status

Proposed

## Terms

| Term | Meaning |
|---|---|
| `client_message_id` | Client-generated unique id for a send attempt; idempotency key on retries. |
| `message_id` | Server-generated unique id for a persisted message. |
| Sequence / order value | Server-controlled ordering key within a conversation. |
| Sync position | Client’s last known sequence used after reconnect. |
| `SENT` | Messaging service has successfully persisted the message in PostgreSQL. |
| `DELIVERED` | Recipient device acknowledged receipt. |
| `READ` | Recipient acknowledged the message was read. |
| Outbox | Same-DB transactional table of events; publisher pushes to Kafka after commit. |
| Domain entity | Business object in `domain/entities` — not an ORM model. |
| Repository port | Interface in `domain/repositories`; implemented in infrastructure. |
| Use case | Application command/query (e.g. `SendMessage`). |
| Database per service | Each microservice owns its own database; no shared tables. |
| Microservice | Independently deployable FastAPI service with a bounded domain. |
| ADR | Architecture Decision Record. |

## Persistence Roles

```text
Persistent data      → PostgreSQL (per service)
Cross-service events → Kafka (via outbox where needed)
Ephemeral/realtime   → Redis
Realtime transport   → WebSocket
Offline assist       → Push notification
```

Push notifications assist delivery; they do not replace PostgreSQL synchronization.
