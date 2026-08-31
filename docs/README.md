# Backend Documentation

## Overview

Technical documentation for the WhatsApp-like chat backend.

Organized around **overview, requirements, architecture, decisions, contracts, modules, realtime behavior, reliability, security, operations, testing, and real-world scenarios**.

The goal is to make the system understandable before, during, and after implementation.

---

## Start Here

```text
00-overview/project_overview.md
00-overview/scope.md
00-overview/glossary.md
01-requirements/functional-requirements.md
02-architecture/architecture-overview.md
02-architecture/data-flow.md
03-decisions/
06-modules/messaging/
12-scenarios/
```

Fill remaining placeholders as each area is designed. Do not document the entire system before writing code.

**Recommended order:** requirements → architecture → ADRs → data model → WebSocket protocol → messaging/sync → remaining modules → implementation → tests → doc updates.

---

## Documentation Structure

```text
docs/
│
├── 00-overview/
├── 01-requirements/
├── 02-architecture/
├── 03-decisions/
├── 04-api/
├── 05-data/
├── 06-modules/
├── 07-realtime/
├── 08-security/
├── 09-reliability/
├── 10-operations/
├── 11-testing/
└── 12-scenarios/
```

---

## 00 — Overview

**Question answered:** What are we building, and what is in/out of scope?

Contains:

* Project overview
* Scope (MVP vs deferred)
* Glossary
* Requirements index

---

## 01 — Requirements

**Question answered:** What should the system do?

Contains functional, non-functional, scale, security, and reliability requirements.

Requirements describe **what** the system must achieve, not how it will be implemented.

---

## 02 — Architecture

**Question answered:** How does the overall system work?

Contains system/component architecture, data flows, realtime architecture, scaling, and failure handling.

Start with `architecture-overview.md`, `component-architecture.md`, and `data-flow.md`.

---

## 03 — Decisions

**Question answered:** Why did we choose this approach?

Contains Architecture Decision Records (ADRs).

```text
ADR-001-fastapi.md
ADR-002-postgresql.md
ADR-003-redis.md
ADR-004-websocket.md
ADR-005-message-idempotency.md
ADR-006-message-ordering.md
ADR-007-kafka-microservices.md
ADR-008-persistence-outbox.md
ADR-009-database-per-service.md
ADR-010-clean-architecture.md
```

An ADR should explain:

```text
Context → Problem → Options → Decision → Consequences
```

Do not use ADRs for small implementation details.

Accepted ADRs cover FastAPI, PostgreSQL per service, Redis (ephemeral), WebSocket transport, idempotency, server-side ordering, microservices + Kafka, persistence roles + outbox, database-per-service, and Clean Architecture / SOLID.

---

## 04 — API

**Question answered:** How do clients communicate with the backend?

Contracts for authentication, users, conversations, messages, groups, devices, and the WebSocket protocol.

While design is evolving, hand-written docs here are the intended contract. Keep generated OpenAPI aligned once implementation exists.

---

## 05 — Data

**Question answered:** How is persistent data represented and stored?

Database overview, schema, indexes, migrations, retention.

PostgreSQL is the default relational engine, applied with **one database per service**.

---

## 06 — Modules

**Question answered:** How does each business module work?

```text
auth/  users/  conversations/  messaging/
groups/  realtime/  devices/  notifications/  media/
```

Add module documents only when they represent meaningful behavior or design. Prefer focused files (e.g. messaging idempotency) over empty boilerplate sets.

### Modules vs cross-cutting docs

* `06-modules/<name>/` — domain behavior owned by that module
* `07-realtime/`, `08-security/`, `09-reliability/` — shared mechanisms used by multiple modules

Avoid duplicating the same design in both places; link instead.

---

## 07 — Realtime

**Question answered:** How does realtime communication work?

WebSocket events, connection lifecycle, delivery guarantees, reconnection.

```text
Connect → Authenticate → Deliver → Acknowledge
       → Disconnect → Reconnect → Synchronize
```

---

## 08 — Security

**Question answered:** How is the system protected?

Authentication, authorization, rate limiting, threat model, encryption.

Rules should be explicit — e.g. a user may access a conversation only if they are a member.

---

## 09 — Reliability

**Question answered:** What happens when something goes wrong?

Failure scenarios, retries, idempotency, disaster recovery, consistency.

Cover disconnects, timeouts, duplicates, DB/Redis/worker failure, restarts, and reconnect sync.

---

## 10 — Operations

**Question answered:** How do we run and operate the backend?

Local development, configuration, deployment, monitoring, logging, troubleshooting.

---

## 11 — Testing

**Question answered:** How do we verify the system works?

Strategy plus unit, integration, WebSocket, and failure tests — including distributed failure cases.

---

## 12 — Scenarios

**Question answered:** What happens in a real-world situation?

```text
Situation → Expected behavior → System flow → Failure cases
```

Scenarios can become integration and failure tests.

Priority scenarios already drafted: duplicate message, offline user, server failure.

---

# Documentation Principles

## 1. Document behavior, not just code

Prefer:

> The server uses `client_message_id` to make message retries idempotent.

Instead of:

> `message_service.py` calls `repository.create()`.

## 2. Explain why

Important architectural choices get an ADR: problem, alternatives, decision, trade-offs.

## 3. Keep requirements separate from implementation

* Requirements = **what**
* Architecture = **how**
* ADR = **why**

## 4. Document failure cases

Failure behavior is part of the design for a distributed chat system. Detail lives in `09-reliability/` and scenarios; call out failure modes in module docs where they are specific.

## 5. Keep docs consistent with implementation

Update docs when architecture changes. Docs should describe the **current** system.

---

# Document Status

Use where appropriate (especially ADRs and architecture docs):

```text
Draft | Proposed | Accepted | Deprecated
```

Example:

```markdown
## Status

Proposed
```

Scenarios may omit status unless deprecated.

---

# Core Principle

```text
What are we building?
        ↓
Why this way?
        ↓
How does it work?
        ↓
How do modules communicate?
        ↓
What happens when things fail?
        ↓
How do we test and operate it?
```

If a future developer can answer those by reading `docs/`, the documentation is doing its job.
