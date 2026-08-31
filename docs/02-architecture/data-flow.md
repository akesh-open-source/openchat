# Data Flow

## Status

Proposed

## Send Message

```text
Client
  |
  | message.send
  v
Realtime Gateway and/or Messaging HTTP
  |
  v
Authentication / Authorization
  |
  v
SendMessage use case (application)
  |
  v
Domain rules + MessageRepository port
  |
  v
PostgreSQL transaction (messaging DB)
  |
  +── persist message
  +── write outbox_events
  |
  | COMMIT
  v
Outbox publisher
  |
  v
Kafka (e.g. message.created)
  |
  +---- Realtime Gateway consumers → recipient WebSocket(s)
  |
  +---- Notification Service (if offline) → push
```

Delivery / read acknowledgements: validated in application/domain, persisted when required, then outbox/Kafka fan-out as designed.

---

## Important Rule

The message is not `SENT` until the messaging PostgreSQL commit succeeds.

Do not publish to Kafka inside the use case as a second independent write. Use the outbox.

---

## Offline Recipient

```text
Sender → Messaging → PostgreSQL (+ outbox) → Kafka
                                              |
                    +---- online → Realtime → WebSocket
                    +---- offline → Notifications → Push
                                              |
                                    Recipient reconnects
                                              |
                                    Sync from Messaging PostgreSQL
```

---

## Reconnection

Client keeps `last_received_sequence`. After reconnect, messaging (or gateway calling messaging) loads messages/events **> that sequence** from PostgreSQL.

Missed Kafka realtime events are recovered from PostgreSQL, not from Kafka retention alone.
