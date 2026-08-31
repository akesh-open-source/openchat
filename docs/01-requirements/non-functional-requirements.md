# Non-Functional Requirements

## Status

Proposed

## 1. Performance

Low-latency realtime messaging under expected load. Exact SLOs after load testing.

## 2. Scalability

Horizontal scaling of microservices; each with its own database. Kafka for async fan-out. Realtime must work across gateway instances.

## 3. Availability

Tolerate instance failure. Persisted messages must survive WebSocket/server loss; clients reconnect and sync.

## 4. Consistency

* Messaging PostgreSQL is the source of truth for message history.
* Kafka carries events (via outbox); Redis is ephemeral.
* Database-per-service; no shared DB.

## 5. Reliability

Handle network failures, disconnects, retries, duplicates, restarts, worker/Kafka/Redis/DB failures. Retries must not create duplicate logical messages. Kafka consumers and outbox publish must be idempotent where redelivery occurs.

## 6. Security

Authn/authz, input validation, rate limits, protect secrets, TLS/`wss`, no unauthorized conversation access.

## 7. Maintainability

Microservices + Clean Architecture + SOLID. Clear use cases; repository ports in domain; adapters in infrastructure. No dumping-ground `utils/` packages by default.

## 8. Observability

Structured logs, metrics, error tracking, WebSocket/message/outbox/Kafka lag metrics, DB metrics. Do not log passwords, tokens, OTPs, or private message content without strong justification.

## 9. Testability

Domain and application logic unit-testable without Kafka/Postgres/Redis. Integration and contract tests per service.
