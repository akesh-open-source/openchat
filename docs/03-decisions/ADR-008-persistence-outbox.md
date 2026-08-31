# ADR-008: Persistence Roles and Transactional Outbox

## Status

Accepted

Supersedes earlier drafts that treated Kafka/Redis as selectable message-history stores or allowed dual competing history sources of truth.

## Context

Messaging must persist reliably and notify other services without dual-write failures:

```text
PostgreSQL ✓  Kafka ✗  → message exists, no event
```

## Decision

Fixed responsibilities:

```text
PostgreSQL → persistent data (messages, conversations, groups, outbox)
Kafka      → event bus
Redis      → realtime / ephemeral state
```

Messaging publish path uses a **transactional outbox**:

1. In one DB transaction: write message + outbox row  
2. Commit  
3. Outbox publisher sends to Kafka  
4. Mark outbox processed (at-least-once; consumers idempotent)

## Consequences

### Positive

* Clear ownership of durability vs fan-out
* No competing history stores
* Reliable eventing after persistence

### Negative

* Outbox publisher to operate and monitor
* Eventual delivery lag until publish

## Revisit When

* A different reliable messaging pattern (e.g. change-data-capture) is adopted with equal guarantees
