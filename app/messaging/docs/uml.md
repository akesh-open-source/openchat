# Messaging service — UML diagrams

Mermaid diagrams for `app/messaging/`. Render in GitHub, VS Code Mermaid preview, or [mermaid.live](https://mermaid.live).

## Clean Architecture layers

```mermaid
flowchart TB
  subgraph Presentation
    R[HTTP routes + schemas]
    D[dependencies.py DI]
  end
  subgraph Application
    C[Commands / Queries]
    S[Application services]
    P[Ports / Protocols]
    DTO[ConversationSummary enricher]
  end
  subgraph Domain
    E[Entities]
    V[Value objects]
    X[Domain exceptions]
  end
  subgraph Infrastructure
    PG[Postgres repos + models]
    HTTP[HttpxUsersClient]
  end
  R --> S
  D --> S
  D --> PG
  D --> HTTP
  S --> C
  S --> P
  S --> DTO
  S --> E
  PG -.implements.-> P
  HTTP -.implements.-> P
  E --> V
```

## Domain class diagram

```mermaid
classDiagram
  class Conversation {
    +UUID id
    +ConversationType type
    +UUID direct_user_a_id
    +UUID direct_user_b_id
    +int next_sequence
    +datetime created_at
    +datetime updated_at
    +create_direct()
    +is_direct()
  }
  class Membership {
    +UUID conversation_id
    +UUID user_id
    +MembershipRole role
    +datetime joined_at
  }
  class Message {
    +UUID id
    +UUID conversation_id
    +UUID sender_id
    +str client_message_id
    +int sequence
    +str body
    +MessageStatus status
    +datetime created_at
  }
  class ConversationType {
    <<enumeration>>
    DIRECT
    GROUP
  }
  class MembershipRole {
    <<enumeration>>
    MEMBER
    ADMIN
  }
  class MessageStatus {
    <<enumeration>>
    SENT
    DELIVERED
    READ
  }
  Conversation --> ConversationType
  Membership --> MembershipRole
  Message --> MessageStatus
  Conversation "1" --> "*" Membership
  Conversation "1" --> "*" Message
```

## Ports and adapters

```mermaid
classDiagram
  direction TB
  class ListConversationsService {
    +execute(query)
  }
  class GetOrCreateDirectConversationService {
    +execute(command)
  }
  class GetConversationService {
    +execute(query)
  }
  class ConversationRepository {
    <<port>>
    +get_by_id()
    +get_direct_between()
    +list_for_user()
    +save()
  }
  class MembershipRepository {
    <<port>>
    +get()
    +save_many()
  }
  class MessageRepository {
    <<port>>
    +get_latest_by_conversation_ids()
    +save()
  }
  class UsersClient {
    <<port>>
    +user_exists()
    +get_display_names()
  }
  class PostgresConversationRepository
  class PostgresMembershipRepository
  class PostgresMessageRepository
  class HttpxUsersClient

  ListConversationsService --> ConversationRepository
  ListConversationsService --> MessageRepository
  ListConversationsService --> UsersClient
  GetOrCreateDirectConversationService --> ConversationRepository
  GetOrCreateDirectConversationService --> MembershipRepository
  GetOrCreateDirectConversationService --> UsersClient
  GetConversationService --> ConversationRepository
  GetConversationService --> MembershipRepository
  GetConversationService --> MessageRepository
  GetConversationService --> UsersClient

  PostgresConversationRepository ..|> ConversationRepository
  PostgresMembershipRepository ..|> MembershipRepository
  PostgresMessageRepository ..|> MessageRepository
  HttpxUsersClient ..|> UsersClient
```

## ER diagram (Postgres)

```mermaid
erDiagram
  CONVERSATIONS ||--o{ MEMBERSHIPS : has
  CONVERSATIONS ||--o{ MESSAGES : has
  CONVERSATIONS {
    uuid id PK
    string type
    uuid direct_user_a_id
    uuid direct_user_b_id
    int next_sequence
    timestamptz created_at
    timestamptz updated_at
  }
  MEMBERSHIPS {
    uuid conversation_id PK,FK
    uuid user_id PK
    string role
    timestamptz joined_at
  }
  MESSAGES {
    uuid id PK
    uuid conversation_id FK
    uuid sender_id
    string client_message_id
    int sequence
    text body
    string status
    timestamptz created_at
  }
```

## Sequence — start 1:1 chat + list

```mermaid
sequenceDiagram
  actor Alice
  participant GW as Gateway
  participant Msg as Messaging
  participant PGm as postgres-messaging
  participant Users

  Alice->>GW: POST /conversations/direct {peer=Bob} + JWT
  GW->>Msg: proxy + JWT
  Msg->>Msg: verify JWT → Alice
  Msg->>Users: GET /users/lookup?user_id=Bob + Bearer
  Users-->>Msg: 200 display_name
  Msg->>PGm: INSERT conversation (sorted pair)
  Msg->>PGm: INSERT memberships Alice, Bob
  Msg-->>Alice: 200 {id, created:true, peer_user_id}

  Alice->>GW: GET /conversations + JWT
  GW->>Msg: proxy
  Msg->>PGm: memberships ⨝ conversations
  Msg->>PGm: latest message per conversation
  Msg->>Users: GET /users/lookup (peers) + Bearer
  Note over Msg: Soft-fail names if users down
  Msg-->>Alice: items with peer_display_name, last_message_preview
```

## System context (messaging neighborhood)

```mermaid
flowchart LR
  Client -->|JWT| GW[Gateway]
  GW -->|/conversations/*| Messaging
  GW -.->|/messages/* proxied<br/>handlers TBD| Messaging
  Messaging -->|GET /users/lookup| Users
  Messaging --- PG[(postgres-messaging)]
```

## HTTP surface (via gateway)

| Method | Path |
|---|---|
| GET | `/health` |
| POST | `/conversations/direct` |
| GET | `/conversations` |
| GET | `/conversations/{conversation_id}` |

Send/list message routes are not implemented yet; gateway still proxies `/messages/*`.

## Cross-service

```text
messaging ──GET /users/lookup (+ JWT)──► users
```
