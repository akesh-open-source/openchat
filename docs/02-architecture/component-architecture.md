# Component Architecture

## Status

Proposed

## Repository Shape

```text
app/
├── shared/            # events, HTTP clients — no shared DB
├── gateway/           # optional edge
├── auth/
├── users/
├── messaging/
├── realtime/
├── notifications/
└── media/
```

See `app/README.md`.

## Layers (Clean Architecture)

```text
presentation/     HTTP + WebSocket adapters
application/      commands, queries, DTOs
domain/           entities, VOs, repository ports, rules
infrastructure/   PostgreSQL, Kafka, Redis, outbox, external
security/         authentication + API authorization
```

Dependency rule: infrastructure and presentation depend inward; domain depends on almost nothing.

## Messaging Internals (target)

```text
messaging/
├── domain/entities|value_objects|repositories|services|rules
├── application/commands|queries
├── infrastructure/
│   ├── persistence/postgresql/
│   ├── messaging/kafka/
│   ├── outbox/
│   └── logging/
└── presentation/http/
```

Repository **interfaces** live in `domain/repositories`.  
Repository **implementations** live in `infrastructure/persistence/postgresql/repositories`.

Domain entities ≠ SQLAlchemy models.

## Service Technology Mix

| Service | Typical stack |
|---|---|
| auth | domain + application + PostgreSQL + security |
| users | domain + application + PostgreSQL |
| messaging | domain + application + PostgreSQL + Kafka + outbox |
| realtime | presentation/websocket + Kafka consumers + Redis |
| notifications | domain + application + PostgreSQL + Kafka + push provider |
| media | domain + application + PostgreSQL + object storage |

Do not force identical empty folders in every service.

## Communication

```text
Client → Gateway/LB → Service
Service ↔ Service → shared/clients or Kafka
Service → Data → own PostgreSQL / Redis only
```
