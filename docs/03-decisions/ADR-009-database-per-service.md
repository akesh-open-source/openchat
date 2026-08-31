# ADR-009: Database Per Service

## Status

Accepted

## Context

The backend uses microservices (ADR-007). Sharing one database across services couples deploy cycles, ownership, and failure domains, and encourages cross-service joins.

## Options

* Shared database for all services
* Shared database server with separate schemas per service
* One database (logical DB / schema / cluster endpoint) **owned by each service**

## Decision

**One database per service.**

Each microservice owns its persistent data store and is the only writer (and primary reader) of that store.

Cross-service needs are met via:

* Synchronous APIs (HTTP)
* Asynchronous events (Kafka)

Never via direct queries or writes against another service's database.

## Ownership examples

| Service | Owns (examples) |
|---|---|
| Auth | Credentials, sessions/tokens as designed |
| Users | Profiles |
| Messaging | Conversations, memberships, messages (when store mode uses a DB owned by messaging) |
| Notifications | Device push tokens, notification delivery state |
| Realtime | Connection/presence data it persists (if any); often Redis-backed |

PostgreSQL may still be the engine technology for multiple services, but each service gets its **own** database (or equivalent isolated schema/instance that other services must not touch).

## Consequences

### Positive

* Clear data ownership
* Independent schema migrations
* Reduced accidental coupling
* Failure isolation per service data plane

### Negative

* No cross-service SQL joins
* Need for eventual consistency / data replication via events where denormalized reads are required
* More databases to operate

## Revisit When

* A platform decision mandates a shared datastore with hard tenancy controls that preserve the same ownership rules.
* Read-model projection services are introduced (still must not write to another service's source DB).
