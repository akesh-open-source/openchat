# Message Synchronization

## Status

Proposed

## Purpose

Recover messages/events missed while disconnected.

## Flow

Client sends `last_received_sequence` after reconnect. Messaging loads newer messages from **PostgreSQL** in authoritative order. Sync is idempotent/repeatable.

WebSocket delivery is not the source of truth.
