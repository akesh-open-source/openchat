# ADR-005: Client Message Idempotency

## Status

Accepted

## Context

Network failures can cause a client to retry a message after the server has already persisted it.

Without idempotency:

```text
Client
  |
  | Message
  v
Server
  |
  | persisted
  X ACK lost
  |
Client retries
  |
  v
Server
```

The same logical message could be persisted twice.

## Decision

Clients must generate a unique `client_message_id`.

The server must recognize repeated submissions of the same client message.

## Example

```json
{
  "client_message_id": "550e8400-e29b-41d4-a716"
}
```

The server must enforce appropriate uniqueness.

## Consequences

Client retries become safe.

The database requires a suitable unique constraint/index.
