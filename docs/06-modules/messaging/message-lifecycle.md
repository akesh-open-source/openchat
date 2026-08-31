# Message Lifecycle

## Status

Proposed

## Client Lifecycle

```text
PENDING → SENDING → SENT → DELIVERED → READ
```

## Server Definitions

* **SENT** — persisted in messaging PostgreSQL (transaction committed).
* **DELIVERED** — recipient device acknowledged receipt.
* **READ** — recipient acknowledged read.

Transport success ≠ persistence success.

## Failure

If PostgreSQL persistence fails, do not acknowledge `SENT`. Outbox publish happens only after a successful commit.
