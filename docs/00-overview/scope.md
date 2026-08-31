# Scope

## Status

Proposed

## In Scope (MVP Backend)

* User registration, login, logout
* Access tokens, refresh tokens, session/device tracking
* User profiles (supported fields)
* One-to-one conversations
* Text messaging with persistence in **PostgreSQL**
* Message statuses: `SENT`, `DELIVERED`, `READ`
* Server-authoritative message ordering
* Offline messaging and reconnect synchronization
* Group chat (create, membership, admin roles, messaging)
* Presence (online/offline) via **Redis**
* Typing indicators (ephemeral) via **Redis**
* Multi-device sessions and revocation
* Push notifications for offline users
* Authorization for conversations, messages, groups, devices
* Rate limiting on sensitive operations
* TLS / `wss` in production
* Microservices (FastAPI), independently deployable
* **One database per service**
* **Kafka** as the cross-service event bus
* **Transactional outbox** for messaging → Kafka publish
* Clean Architecture + SOLID (domain / application / infrastructure / presentation)

## Deferred / Later Phase

* Media (images, video, audio, documents) — object storage when added
* End-to-end encryption (requires architecture revisit)
* Voice/video calls
* Stories / status
* Administrative moderation tooling (unless explicitly required)

## Explicit Non-Goals

* Shared database across microservices
* Using Kafka or Redis as the message-history source of truth
* Dual-writing message history to Kafka and PostgreSQL as competing sources of truth
* Treating WebSocket delivery as the source of truth
* Using client timestamps as the sole ordering mechanism
* Generic dumping-ground `utils/` / cross-cutting `repositories/` packages that bypass layer rules
* ORM models used as domain entities

## Contracts Source Of Truth

* Hand-written docs under `04-api/` define intended behavior while design is evolving.
* Generated OpenAPI from FastAPI should stay aligned with those contracts once implementation exists.
* WebSocket event shapes live primarily in `04-api/websocket-protocol.md` and `07-realtime/`.
* Code layout: `app/README.md`
