# ADR-007: Microservices with Kafka

## Status

Accepted

## Context

Need independent deploy/scale of auth, messaging, realtime, notifications; durable async fan-out after persistence.

## Decision

Microservices (FastAPI) + Kafka as the event bus + database-per-service (ADR-009).

Kafka is not the message-history store. Messaging publishes via outbox (ADR-008).

## Consequences

Independent scaling and deploy cycles; operational cost of brokers and consumer groups; idempotent consumers required.
