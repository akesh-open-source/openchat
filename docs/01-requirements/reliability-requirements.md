# Reliability Requirements

## Status

Proposed

## Message Persistence

A message is not `SENT` until persisted in the messaging service PostgreSQL database.

## Outbox

Message-created (and related) events are written to the outbox in the same transaction as the message. An outbox publisher pushes to Kafka after commit. Do not dual-write Postgres and Kafka independently in the use case.

## Duplicate Requests

`client_message_id` uniqueness prevents duplicate logical messages on retry.

## WebSocket Failure

Must not permanently lose persisted messages. Reconnect + sync from PostgreSQL.

## Offline Users

Messages remain in PostgreSQL. Push may assist. Sync after reconnect is authoritative.

## Server Failure

Persisted data remains; clients reconnect to another instance and sync. Temporary connection state may be lost.

## Redis Failure

Must not erase message history. Presence/typing may degrade.

## Kafka Failure

History remains in PostgreSQL. Outbox retains unpublished events until Kafka is available again. Consumers must tolerate redelivery.

## Database Failure

If messaging PostgreSQL is down, new messages must not be acknowledged as `SENT`. Fail safely; retry per policy. Other services fail closed on their own DB outages — never by reading another service’s DB.

## Worker Failure

Outbox publishers, Kafka consumers, and jobs must retry safely and be idempotent where needed.
