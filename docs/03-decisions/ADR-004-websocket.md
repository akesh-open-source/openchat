# ADR-004: Use WebSockets for Realtime Transport

## Status

Accepted

## Context

Chat needs bidirectional low-latency events. Polling is a poor fit.

## Decision

Use WebSockets for realtime delivery (new messages, receipts, presence, typing).

REST remains for request/response and history/sync.

WebSocket delivery is **not** the source of truth; PostgreSQL is. Clients recover via sync after reconnect.

## Consequences

Must handle connection lifecycle, auth, heartbeats, reconnection, multi-instance fan-out via Kafka, and sync.
