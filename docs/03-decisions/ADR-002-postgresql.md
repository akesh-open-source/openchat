# ADR-002: PostgreSQL Per Service

## Status

Accepted

## Context

Services need relational storage with transactions and constraints. Sharing one DB across services couples ownership (ADR-009).

## Decision

Use PostgreSQL as the relational engine. Each service that needs it owns **its own** database.

Messaging uses PostgreSQL for messages, conversations, groups, and the outbox table.

## Consequences

No cross-service SQL joins. Integration via APIs/Kafka. Schema migrations are per service.
