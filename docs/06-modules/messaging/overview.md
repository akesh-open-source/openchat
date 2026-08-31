# Messaging Module

## Status

Proposed

## Purpose

Owns the lifecycle of chat messages, conversations, and groups inside the **messaging** microservice.

## Clean Architecture

```text
presentation → application (SendMessage, …) → domain
                                                ↑
                     infrastructure (Postgres repos, outbox, Kafka)
```

## Responsibilities

* Create/validate/persist messages
* Conversations and groups
* Idempotency (`client_message_id`)
* Server-side ordering
* Message state and sync
* Outbox events for Kafka fan-out

## Non-Responsibilities

* Auth credentials / sessions (auth service)
* User profiles (users service)
* WebSocket connection management (realtime)
* Push transport (notifications)

## Persistence

PostgreSQL (messaging DB) is the history store. Kafka is the event bus via outbox. Redis is not used for message history.
