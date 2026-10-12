# Auth service — UML diagrams

Mermaid diagrams for `app/auth/`. Render in GitHub, VS Code Mermaid preview, or [mermaid.live](https://mermaid.live).

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
    HTTP[HttpxUsersClient]
    Other[Redis / email / JWT / Argon2]
  end
  R --> S
  D --> S
  D --> PG
  D --> HTTP
  S --> C
  S --> P
  S --> E
  PG -.implements.-> P
  HTTP -.implements.-> P
  E --> V
```

## Domain class diagram

```mermaid
classDiagram
  class User {
    +UUID id
    +Email email
    +DisplayName display_name
    +Password password
    +bool is_active
    +datetime created_at
    +datetime updated_at
  }
  class Session {
    +UUID id
    +UUID user_id
    +UUID device_id
    +datetime expires_at
    +datetime last_seen_at
    +str ip_address
    +datetime revoked_at
  }
  class Device {
    +UUID id
    +UUID user_id
    +str client_device_id
    +str name
    +str user_agent
  }
  class RefreshToken {
    +UUID id
    +UUID user_id
    +str token_hash
    +UUID family_id
    +UUID session_id
    +datetime expires_at
    +datetime revoked_at
  }
  class Email {
    +str value
  }
  class DisplayName {
    +str value
  }
  class Password {
    +str hashed_value
  }
  User --> Email
  User --> DisplayName
  User --> Password
  Session --> User : user_id
  Device --> User : user_id
  RefreshToken --> User : user_id
  RefreshToken --> Session : session_id
```

## Ports and adapters

```mermaid
classDiagram
  direction TB
  class CompleteRegisterService {
    +complete(command)
  }
  class LoginService {
    +login(command)
  }
  class UserRepository {
    <<port>>
    +get_by_email()
    +save()
  }
  class SessionRepository {
    <<port>>
  }
  class DeviceRepository {
    <<port>>
  }
  class RefreshTokenRepository {
    <<port>>
  }
  class UsersClient {
    <<port>>
    +create_profile()
  }
  class PendingRegistrationStore {
    <<port>>
  }
  class PostgresUserRepository
  class HttpxUsersClient
  class RedisPendingRegistrationStore

  CompleteRegisterService --> UserRepository
  CompleteRegisterService --> PendingRegistrationStore
  CompleteRegisterService --> UsersClient
  LoginService --> UserRepository
  LoginService --> SessionRepository
  LoginService --> DeviceRepository
  LoginService --> RefreshTokenRepository

  PostgresUserRepository ..|> UserRepository
  HttpxUsersClient ..|> UsersClient
  RedisPendingRegistrationStore ..|> PendingRegistrationStore
```

## Sequence — register (auth → users)

```mermaid
sequenceDiagram
  actor Client
  participant GW as Gateway
  participant Auth
  participant Redis as Redis pending
  participant PG as postgres-auth
  participant Users
  participant PGu as postgres-users

  Client->>GW: POST /auth/initiate-register
  GW->>Auth: proxy
  Auth->>Redis: store pending (email, hash, name)
  Auth-->>Client: 200 (check email)

  Client->>GW: POST /auth/complete-register {token}
  GW->>Auth: proxy
  Auth->>Redis: get pending
  Auth->>PG: INSERT user
  Auth->>Users: POST /internal/profiles
  Users->>PGu: INSERT profile (idempotent)
  Users-->>Auth: 200 {created}
  Note over Auth: If users down: log + continue
  Auth-->>Client: 201 user_id, email, display_name
```

## HTTP surface (via gateway `/auth/*`)

| Method | Path |
|---|---|
| POST | `/auth/initiate-register` |
| POST | `/auth/complete-register` |
| POST | `/auth/login` |
| POST | `/auth/logout` |
| POST | `/auth/refresh` |
| POST | `/auth/forgot-password` |
| POST | `/auth/reset-password` |
| POST | `/auth/change-password` |
| GET | `/auth/devices` |
| GET | `/auth/sessions` |
| DELETE | `/auth/sessions/{session_id}` |

## Cross-service

```text
auth ──POST /internal/profiles──► users
```

Compose-only; not exposed on the gateway.
