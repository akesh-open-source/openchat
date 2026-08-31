# Scenario: Offline Recipient

## Situation

Alice sends to Bob while Bob is offline.

## Expected Behavior

Message persisted in messaging PostgreSQL; outbox → Kafka may trigger push. On reconnect, Bob syncs from PostgreSQL, then can ack `DELIVERED`.

Push is assistive, not the source of truth.
