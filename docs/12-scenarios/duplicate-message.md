# Scenario: Duplicate Message

## Situation

Client sends a message. Backend persists it, ACK is lost, client retries.

## Expected Behavior

Second request finds existing `client_message_id` in messaging PostgreSQL and returns the same logical message. No duplicate.

## Test

Cover with an integration test against the messaging service DB.
