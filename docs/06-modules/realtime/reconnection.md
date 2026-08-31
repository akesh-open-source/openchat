# WebSocket Reconnection

## Status

Proposed

## Expected Behavior

```text
CONNECTED → DISCONNECTED → RECONNECTING → CONNECTED → SYNCHRONIZING → READY
```

After reconnect, client provides `last_received_sequence`. Backend syncs from messaging PostgreSQL.

Successful WebSocket reconnect ≠ synchronized; sync must complete.
