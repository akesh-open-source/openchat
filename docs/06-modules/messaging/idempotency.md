# Message Idempotency

## Status

Accepted

## Problem

Lost ACKs cause client retries. Without idempotency, duplicates appear.

## Solution

Every client send includes `client_message_id`. Messaging treats it as the identity of the logical send. Uniqueness is enforced in the messaging PostgreSQL store.

Retry returns the existing message; no second logical message.
