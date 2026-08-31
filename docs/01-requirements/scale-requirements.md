# Scale Requirements

## Status

Proposed

## Initial Engineering Target

| Metric | Initial Target |
|---|---:|
| Registered users | 10,000 |
| Concurrent connections | 2,000 |
| Messages/sec | 100 |
| Maximum group size | 500 |
| Service instances (per service) | 1–3 |
| Persistence | PostgreSQL per service |
| Event bus | Kafka |
| Ephemeral state | Redis |

## Future Target

Millions of users, high concurrency, independently scaled services, partition scaling on Kafka, DB scaling per service.

## Scaling Strategy

```text
LB → Auth / Users / Messaging / Realtime / Notifications (each + own DB)
                 │
               Kafka
                 │
         consumers / workers
```

Scale by bottleneck. Do not share a database to simplify joins.
