# Scenario: Application Server Failure

## Situation

Client connected to instance A; A crashes.

## Expected Behavior

Client reconnects (possibly to B). Messages already in messaging PostgreSQL remain. Sync recovers state. Temporary connection state on A may be lost.
