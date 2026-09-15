# Users service — UML diagrams

Mermaid diagrams for `app/users/`. Render in GitHub, VS Code Mermaid preview, or [mermaid.live](https://mermaid.live).

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
  end
  subgraph Domain
    E[Entities]
    V[Value objects]
    X[Domain exceptions]
  end
  subgraph Infrastructure
    PG[Postgres repos + models]
    Sec[JWT verify + PEM]
  end
  R --> S
  D --> S
  D --> PG
  S --> C
  S --> P
  S --> E
  PG -.implements.-> P
  E --> V
```

## Domain class diagram

```mermaid
classDiagram
  class Profile {
    +UUID user_id
    +DisplayName display_name
    +str email
    +str bio
    +str avatar_url
    +datetime created_at
    +datetime updated_at
  }
  class DisplayName {
    +str value
  }
  Profile --> DisplayName
  note for Profile "PK = auth user_id\nNo password / sessions here"
```

## Ports and adapters

```mermaid
classDiagram
  direction TB
  class CreateProfileService {
    +create(command)
  }
  class GetProfileService {
    +get(command)
  }
  class UpdateProfileService {
    +update(command)
  }
  class LookupProfileService {
    +lookup(query)
  }
  class ProfileRepository {
    <<port>>
    +get_by_user_id()
    +get_by_email()
    +save()
    +delete()
  }
  class PostgresProfileRepository

  CreateProfileService --> ProfileRepository
  GetProfileService --> ProfileRepository
  UpdateProfileService --> ProfileRepository
  LookupProfileService --> ProfileRepository
  PostgresProfileRepository ..|> ProfileRepository
```

## Sequence — inbound callers

```mermaid
sequenceDiagram
  participant Auth
  participant Messaging
  participant Users
  participant PG as postgres-users

  Auth->>Users: POST /internal/profiles
  Users->>PG: upsert profile by user_id
  Users-->>Auth: 200 {created}

  Messaging->>Users: GET /users/lookup?user_id=… + Bearer JWT
  Users->>PG: SELECT by user_id / email
  Users-->>Messaging: 200 {user_id, display_name}
```

## HTTP surface

| Method | Path | Notes |
|---|---|---|
| GET | `/health` | Public |
| POST | `/internal/profiles` | Auth → users (Compose-only) |
| GET | `/users/me` | JWT via gateway |
| PATCH | `/users/me` | JWT via gateway |
| GET | `/users/lookup` | JWT; used by messaging |
| GET | `/users/{user_id}` | JWT via gateway |

## Cross-service

```text
auth ──POST /internal/profiles──► users
messaging ──GET /users/lookup (+ JWT)──► users
```

Users does **not** call auth or messaging.
