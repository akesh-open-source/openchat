# Offline Messaging

## Status

Proposed

## Expected Behavior

Persist in messaging PostgreSQL even if the recipient is offline. Outbox → Kafka may trigger push via notifications. On reconnect, sync from PostgreSQL. Status may stay `SENT` until delivery ack, then `DELIVERED`.
