# Scaling

## Status

Proposed

## Unit Of Scale

| Service | Typical bottleneck |
|---|---|
| auth | Token/auth QPS, auth DB |
| users | Profile reads, users DB |
| messaging | Persist/outbox throughput, messaging DB |
| realtime | WebSocket connections / instance |
| notifications | Kafka lag, push provider |
| media | Upload/processing (later) |

Scale each service and **its own database** independently.

## Pattern

```text
LB → N replicas of a service → that service's PostgreSQL
              │
              └─ Kafka consumer groups / Redis as needed
```

Outbox publishers scale with messaging; realtime gateways scale with connections.

Targets: `docs/01-requirements/scale-requirements.md`.
