# System Context

## Status

Proposed

## Actors

* Mobile / web clients
* Operators

## External Systems

* PostgreSQL (one DB per service that needs relational storage)
* Kafka
* Redis
* Push providers
* Object storage (media, later)

## Internal Systems

```text
Clients → Gateway/LB → auth | users | messaging | realtime | notifications | media
                              │
                              ├─ own PostgreSQL DBs
                              ├─ Kafka topics
                              └─ Redis (realtime/ephemeral)
```

No shared business database. No Kafka/Redis as message-history source of truth.
