# ADR-001: Use FastAPI

## Status

Accepted

## Context

The backend requires:

- REST APIs
- WebSocket support
- Async request handling
- Strong request validation
- API documentation
- A modular Python architecture

## Options

- FastAPI
- Django
- Flask

## Decision

Use FastAPI for backend microservices.

## Reasons

- Strong async support
- Native WebSocket support
- Pydantic-based validation
- Automatic OpenAPI documentation
- Good fit for realtime APIs
- Lightweight application structure

## Consequences

### Positive

- Good fit for WebSocket-heavy workloads.
- Clear API contracts.
- Easy to build independently deployable FastAPI microservices.

### Negative

- Some functionality available in Django must be implemented or selected separately.
- The team must establish project conventions for authentication, database access, and administration.

## Revisit When

Reconsider if:

- The project becomes primarily a traditional web application.
- Django's ecosystem provides significant advantages.
- Operational requirements change substantially.
