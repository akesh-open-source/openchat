# ADR-006: Server-Side Message Ordering

## Status

Accepted

## Context

Network timing and multiple instances can reorder arrivals. Client clocks are unreliable as a sole ordering source.

## Decision

The messaging service provides an authoritative server-controlled sequence/order within a conversation.

Client timestamps must not be the sole ordering mechanism.

## Consequences

Clients reconstruct history deterministically after sync. Sequence allocation is defined in messaging domain/application design.
