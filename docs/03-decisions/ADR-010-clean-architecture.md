# ADR-010: Clean Architecture and SOLID

## Status

Accepted

## Context

Need testable business logic, clear ownership, and infrastructure that can change (Postgres/Kafka/Redis clients) without rewriting domain rules.

## Decision

Inside each business service, use Clean Architecture layers:

```text
Presentation → Application → Domain ← Infrastructure
```

* Domain holds entities, value objects, repository **ports**, domain services, business rules
* Application holds use cases (commands/queries)
* Infrastructure implements ports (persistence, Kafka, Redis, external APIs, logging, outbox)
* Presentation adapts HTTP/WebSocket; maps domain exceptions to HTTP

Apply SOLID as a dependency rule, not a folder checklist. Do not create dumping-ground `utils/` packages by default.

## Consequences

Higher initial structure cost; much clearer testing and evolution of adapters.
