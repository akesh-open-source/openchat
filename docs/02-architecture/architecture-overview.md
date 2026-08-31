# Architecture Overview

## Status

Proposed

## Architecture Style

* Microservices (FastAPI), independently deployable
* Database per service (ADR-009)
* Clean Architecture inside each service (ADR-010)
* PostgreSQL for persistence, Kafka for events, Redis for ephemeral realtime

---

## High-Level Architecture

```text
                         Clients
                    Web / Android / iOS
                            |
                    HTTP / WebSocket
                            |
                            v
                     Load Balancer / Gateway
                            |
        +-------------------+-------------------+
        |                   |                   |
        v                   v                   v
  +-----------+      +-----------+      +---------------+
  |   Auth    |      | Messaging |      |   Realtime    |
  |  + Auth DB|      | + Msg DB  |      |   Gateway     |
  +-----------+      | + Outbox  |      | + Redis       |
                     +-----+-----+      +-------+-------+
                           |                    |
                           | outbox →           | consume
                           v                    |
                     +-----------+<-------------+
                     |   Kafka   |
                     +-----+-----+
                           |
                  +--------+--------+
                  |                 |
                  v                 v
           +-----------+    +---------------+
           |Notification|   | Users / Media |
           | + Notif DB |   | + own DBs     |
           +-----------+    +---------------+
```

---

## Main Components

### Auth Service

Registration, login, logout, tokens, sessions. Owns **auth DB**.

### Users Service

Profiles. Owns **users DB**.

### Messaging Service

Conversations, groups, messages, idempotency, ordering. Owns **messaging DB**. Publishes domain events via **outbox → Kafka**.

### Realtime Gateway

WebSockets, presence, typing. Consumes Kafka; uses **Redis** for ephemeral state.

### Notification Service

Push tokens and delivery. Owns **notifications DB**. Consumes Kafka.

### Media Service (deferred)

Media metadata DB + object storage.

### Gateway (optional)

Edge routing; no business database.

---

## Clean Architecture (per service)

```text
Presentation → Application → Domain
                                ↑
                         Infrastructure
```

* Domain: entities, value objects, repository ports, rules
* Application: commands/queries (use cases)
* Infrastructure: PostgreSQL repos, Kafka, Redis, outbox, external APIs
* Presentation: HTTP/WebSocket schemas and routes

---

## Persistence Principle

```text
Persistent state     → PostgreSQL (owning service)
Cross-service events → Kafka (outbox where dual-write risk exists)
Ephemeral/realtime   → Redis
Realtime transport   → WebSocket
Offline notification → Push
```

## Important Rule

A message is not `SENT` until messaging PostgreSQL persistence succeeds.

Kafka publish for that message goes through the outbox in the same transaction (or equivalent reliable pattern) — not an independent write in the use case.
