# Project Overview

## Status

Proposed

## What This Is

A WhatsApp-like chat **backend**: authentication, users, conversations, messaging, realtime delivery, multi-device sessions, and push notifications.

## Architecture Commitments

* **Microservices** (FastAPI), independently deployable
* **Database per service** (ADR-009)
* **PostgreSQL** — persistent data
* **Kafka** — event bus (via outbox from messaging)
* **Redis** — realtime / ephemeral state
* **Clean Architecture** + **SOLID** — testable domain/application logic

## Documentation Scope

This `docs/` tree documents the **server and its contracts** with clients. Client UI is out of scope unless it affects backend contracts.

## Core Guarantees

* A message is not `SENT` until persisted in the messaging service PostgreSQL database.
* Kafka events for new messages are published via the **outbox** after that commit (not a separate best-effort write).
* Client retries must not create duplicate logical messages (`client_message_id`).
* Server-side ordering is authoritative within a conversation.
* WebSocket disconnects must not permanently lose persisted messages; clients reconnect and synchronize from PostgreSQL.
* Services never share databases; integration is HTTP or Kafka.

## Where To Start

```text
app/README.md
00-overview/scope.md
01-requirements/functional-requirements.md
02-architecture/architecture-overview.md
02-architecture/component-architecture.md
02-architecture/data-flow.md
03-decisions/
06-modules/messaging/
12-scenarios/
```

## Recommended Design Order

```text
Requirements
     ↓
Architecture + ADRs
     ↓
Data model (per service)
     ↓
WebSocket protocol
     ↓
Messaging use cases + outbox
     ↓
Remaining services
     ↓
Implementation + tests
```
