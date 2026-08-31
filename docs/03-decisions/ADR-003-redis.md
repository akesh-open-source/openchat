# ADR-003: Use Redis for Realtime / Ephemeral State

## Status

Accepted

## Context

Presence, typing, connection coordination, and similar state need low latency and do not require durable message history semantics.

## Decision

Use Redis for ephemeral and realtime state.

Redis is **not** the message-history store. Persistent messages remain in the messaging service PostgreSQL database (ADR-008).

## Consequences

Fast ephemeral state; realtime must tolerate Redis failure without losing persisted message history.
