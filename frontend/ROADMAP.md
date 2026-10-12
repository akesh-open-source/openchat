# OpenChat Frontend — Commit-by-Commit Roadmap

Aligned with [`chat_service_roadmap.md`](../chat_service_roadmap.md).
Clients talk **only** to the gateway (`http://localhost:8000`).

Rules:
- Do **not** build UI for APIs that are not on the gateway yet.
- Toggle `[x]` only when frontend code exists.
- Prefer MVP screens first; High Scale UI (projections, gap buffer, etc.) later.
- One slice = one branch from `staging`, one PR into `staging`.
- Use the **Branch** and **Commit message** listed for that slice (Conventional Commits).

---

## Backend ↔ frontend status (today)

| Backend capability | Backend | Frontend API layer | UI screens |
| --- | --- | --- | --- |
| Auth (register/login/refresh/logout/password/devices/sessions) | done | [x] types + `api/auth` + hooks | [ ] |
| Users (me / lookup / patch) | done | [x] types + `api/users` + hooks | [ ] |
| Conversations (direct / list / get + peer name + last preview) | done | [x] types + `api/conversations` + hooks | [ ] |
| Message schema + server ordering | done (no HTTP send yet) | [x] `Message` type only | n/a |
| Send message + idempotency | [ ] | [ ] | [ ] |
| Message history pagination | [ ] | [ ] | [ ] |
| Kafka / realtime WS | [ ] | [ ] | [ ] |
| Receipts / presence / groups / push | [ ] | [ ] | [ ] |

**Immediate frontend work:** F0 scaffold done → F1 auth UI → F2 inbox/profile for finished backend APIs.

---

## Phase F0 — App scaffold

| # | Slice | Branch | Commit message | Steps | Depends on backend | Done |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Vite + React + TS app in `frontend/` | `build/frontend-vite-scaffold` | `build(frontend): scaffold Vite React TypeScript app` | `package.json`, router, env `VITE_API_BASE_URL` | Gateway :8000 | [x] |
| 2 | Track `frontend/` in git | `chore/frontend-gitignore` | `chore: track frontend directory in git` | Remove `frontend/` from root `.gitignore` | — | [x] |
| 3 | Wire `OpenChatApiProvider` | `feat/frontend-api-provider` | `feat(frontend): wire OpenChatApiProvider at app root` | Root provider + token store | API layer | [x] |

---

## Phase F1 — Auth UI (Phase 0 backend — done)

| # | Slice | Branch | Commit message | Steps | Done |
| --- | --- | --- | --- | --- | --- |
| 1 | Login | `feat/frontend-login` | `feat(frontend): add login page with device_id` | email/password/`device_id` → store tokens | [ ] |
| 2 | Register | `feat/frontend-register` | `feat(frontend): add two-step register flow` | initiate → complete (token from email/debug) | [ ] |
| 3 | Forgot / reset password | `feat/frontend-password-reset` | `feat(frontend): add forgot and reset password pages` | public flows | [ ] |
| 4 | Change password | `feat/frontend-change-password` | `feat(frontend): add authenticated change-password form` | Bearer required | [ ] |
| 5 | Sessions / devices | `feat/frontend-sessions-devices` | `feat(frontend): list devices and revoke sessions` | list + revoke session | [ ] |
| 6 | Auth gate | `feat/frontend-auth-gate` | `feat(frontend): protect routes with auth gate` | redirect unauthenticated users | [ ] |

---

## Phase F2 — Users + conversations UI (Phase 1–2B backend — done)

| # | Slice | Branch | Commit message | Steps | Done |
| --- | --- | --- | --- | --- | --- |
| 1 | Profile | `feat/frontend-profile` | `feat(frontend): view and edit own profile` | `GET/PATCH /users/me` | [ ] |
| 2 | Start chat | `feat/frontend-start-chat` | `feat(frontend): start direct chat via user lookup` | `GET /users/lookup` → `POST /conversations/direct` | [ ] |
| 3 | Inbox | `feat/frontend-inbox` | `feat(frontend): conversation inbox with cursor pagination` | `GET /conversations` (peer name + last-message preview + cursor) | [ ] |
| 4 | Conversation header | `feat/frontend-conversation-header` | `feat(frontend): conversation header without message thread` | `GET /conversations/{id}` (no message thread yet) | [ ] |

**Should not:** fake a message composer that calls nonexistent send APIs.

---

## Phase F3 — Messaging UI (Phase 2C backend — wait)

Unlock only when backend slices land:

| Backend slice | Frontend follow-up |
| --- | --- |
| `feat/messaging-idempotency-mvp` | `api/messages.send` + composer with `client_message_id` |
| `feat/messaging-history-pagination-mvp` | `api/messages.list` + thread + cursor scroll |
| `feat/messaging-membership-auth-mvp` | Treat non-member as 404; no existence leak in UI |

| # | Slice | Branch | Commit message | Steps | Done |
| --- | --- | --- | --- | --- | --- |
| 1 | Types + `api/messages.ts` | `feat/frontend-messages-api` | `feat(frontend): add messages API types and client` | request/response from new schemas | [ ] |
| 2 | Hooks | `feat/frontend-messages-hooks` | `feat(frontend): add useMessages and useSendMessage hooks` | `useMessages`, `useSendMessage` | [ ] |
| 3 | Thread UI | `feat/frontend-message-thread` | `feat(frontend): render message history by sequence` | history by `sequence`, not wall-clock | [ ] |
| 4 | Composer | `feat/frontend-message-composer` | `feat(frontend): send composer with client_message_id` | generate `client_message_id`; retry returns same message | [ ] |

---

## Phase F4 — Realtime (Phase 3 backend — wait)

| # | Slice | Branch | Commit message | Steps | Done |
| --- | --- | --- | --- | --- | --- |
| 1 | WS client | `feat/frontend-websocket-client` | `feat(frontend): connect authenticated gateway websocket` | connect via gateway `/ws` with access token | [ ] |
| 2 | Live inbox / thread | `feat/frontend-live-fanout` | `feat(frontend): apply live message.new to inbox and thread` | apply `message.new` without full refetch | [ ] |
| 3 | Gap handling | `feat/frontend-gap-handling` | `feat(frontend): buffer sequence gaps and sync-since` | buffer + sync-since (Phase 3F/3G) | [ ] |
| 4 | Reconnect | `feat/frontend-reconnect-sync` | `feat(frontend): resync history after websocket reconnect` | refresh token + resync cursor | [ ] |

Cross-server delivery is a **server** concern (Redis Pub/Sub). Frontend only needs a working WS + sync.

---

## Phase F5 — Receipts (Phase 4 — wait)

| # | Slice | Branch | Commit message | Done |
| --- | --- | --- | --- | --- |
| 1 | Show SENT / DELIVERED / READ | `feat/frontend-receipts-ui` | `feat(frontend): show SENT DELIVERED READ status` | [ ] |
| 2 | Ack delivered on receive; mark-read API | `feat/frontend-receipts-ack` | `feat(frontend): ack delivered and mark conversation read` | [ ] |

---

## Phase F6 — Presence + typing (Phase 5 — wait)

| # | Slice | Branch | Commit message | Done |
| --- | --- | --- | --- | --- |
| 1 | Online indicator from WS events | `feat/frontend-presence` | `feat(frontend): show conversation-scoped presence` | [ ] |
| 2 | Typing start/stop with local debounce | `feat/frontend-typing` | `feat(frontend): typing indicators with debounce` | [ ] |

---

## Phase F7 — Groups (Phase 6 — wait)

| # | Slice | Branch | Commit message | Done |
| --- | --- | --- | --- | --- |
| 1 | Create/list group conversations | `feat/frontend-groups` | `feat(frontend): create and list group conversations` | [ ] |
| 2 | Member admin UI | `feat/frontend-group-members` | `feat(frontend): manage group members as admin` | [ ] |

---

## Phase F8 — Multi-device + push (Phase 7 — wait)

| # | Slice | Branch | Commit message | Done |
| --- | --- | --- | --- | --- |
| 1 | Device list UX (already partly auth devices) | `feat/frontend-multi-device-ux` | `feat(frontend): polish multi-device session management` | [ ] |
| 2 | Register push token with notifications service | `feat/frontend-push-tokens` | `feat(frontend): register device push tokens` | [ ] |
| 3 | Offline: rely on push wake + sync on open | `feat/frontend-offline-sync` | `feat(frontend): sync history after offline push wake` | [ ] |

---

## Immediate next (frontend)

```text
1. Scaffold Vite/React app (F0)
2. Auth screens (F1)
3. Inbox + start chat + profile (F2)
```

Do **not** start F3 until backend `feat/messaging-idempotency-mvp` (+ history) exists.

---

## Developer slice prompts

Copy-paste one prompt per PR / agent task. Shared constraints for every prompt:

```text
Repo: openchat. Frontend lives in frontend/.
Talk ONLY to gateway http://localhost:8000 (or VITE_API_BASE_URL).
Reuse frontend/src/types, frontend/src/api, frontend/src/hooks — do not call auth/users/messaging ports directly.
Do not invent APIs that are not on the gateway.
Mark roadmap [x] only when code exists. One slice per PR into staging.
Branch from staging using the Branch listed for this slice.
Commit with the Commit message listed (Conventional Commits).
```

Suggested handoff order: F0.1 → F0.2 → F0.3 → F1.1 → F1.6 → rest of F1 → F2.1 → F2.3 → F2.2 → F2.4 → pause until backend send/history → F3 → F4 → …

---

### F0.1 — Vite + React + TS scaffold

```text
Implement frontend slice F0.1 from frontend/ROADMAP.md.

Goal: Scaffold a Vite + React + TypeScript app inside existing frontend/ without deleting the API layer.
Branch: `build/frontend-vite-scaffold`
Commit message:
build(frontend): scaffold Vite React TypeScript app


Should:
- Add package.json, vite.config, tsconfig, index.html, src/main.tsx, src/App.tsx
- React Router for /login, /register, / (inbox placeholder)
- Env: VITE_API_BASE_URL defaulting to http://localhost:8000
- Keep and import existing src/types, src/api, src/hooks
- npm/pnpm install works; app boots

Should not:
- Rewrite the API client in Axios unless already chosen
- Add chat/send UI
- Call internal service ports 8001/8002/8003

Done when: `npm run dev` serves a blank shell with routing.
```

### F0.2 — Track frontend in git

```text
Implement frontend slice F0.2.

Goal: Make frontend/ trackable in git.
Branch: `chore/frontend-gitignore`
Commit message:
chore: track frontend directory in git


Should:
- Remove the `frontend/` line from root .gitignore
- Confirm `git status` shows frontend files as untracked/new

Should not:
- Commit secrets or node_modules
- Change backend ignore rules unrelated to frontend

Done when: frontend source can be staged (node_modules still ignored).
```

### F0.3 — Wire OpenChatApiProvider

```text
Implement frontend slice F0.3.

Goal: Wire OpenChatApiProvider at the app root with LocalStorageTokenStore.
Branch: `feat/frontend-api-provider`
Commit message:
feat(frontend): wire OpenChatApiProvider at app root


Should:
- Wrap App/router in OpenChatApiProvider
- Pass baseUrl from VITE_API_BASE_URL
- useOpenChatApi works in a child page

Should not:
- Create a second HTTP client
- Store tokens in plain React state only (use TokenStore)

Done when: a test page can call api.auth or api.users through the provider.
```

---

### F1.1 — Login

```text
Implement frontend slice F1.1 (Auth UI — Login).

Goal: Login page using existing useAuth / api.auth.login.
Branch: `feat/frontend-login`
Commit message:
feat(frontend): add login page with device_id


Should:
- Form: email, password, stable device_id (generate+persist), optional device_name
- On success: tokens stored; navigate to inbox
- Show ApiError.detail on 401/400

Should not:
- Skip device_id (backend requires it)
- Call auth service directly

Done when: real gateway login works and subsequent authenticated calls succeed.
```

### F1.2 — Register

```text
Implement frontend slice F1.2 (Register).

Goal: Two-step register matching backend.
Branch: `feat/frontend-register`
Commit message:
feat(frontend): add two-step register flow


Should:
- Step A: POST /auth/initiate-register (email, password, display_name)
- Step B: POST /auth/complete-register with token
- Support debug registration_token when AUTH_DEBUG returns it
- After complete, prompt login (or document why not auto-login)

Should not:
- Single-step register that invents a combined API
- Call /internal/profiles from the browser

Done when: initiate + complete creates a user that can login.
```

### F1.3 — Forgot / reset password

```text
Implement frontend slice F1.3.

Goal: Forgot + reset password pages.
Branch: `feat/frontend-password-reset`
Commit message:
feat(frontend): add forgot and reset password pages


Should:
- Forgot: email → show detail; show reset_token only if API returns it (debug)
- Reset: token + new_password → 204 → navigate login
- Clear errors via ApiError

Should not:
- Email the user from the frontend
- Require Bearer on these public routes

Done when: forgot + reset work against gateway.
```

### F1.4 — Change password

```text
Implement frontend slice F1.4.

Goal: Authenticated change-password form.
Branch: `feat/frontend-change-password`
Commit message:
feat(frontend): add authenticated change-password form


Should:
- current_password + new_password → POST /auth/change-password
- Require access token; on 401 send to login
- Success feedback; then optionally force re-login if backend invalidates sessions

Should not:
- Expose this route without auth gate

Done when: logged-in user can change password via gateway.
```

### F1.5 — Sessions / devices

```text
Implement frontend slice F1.5.

Goal: List devices + sessions; revoke a session.
Branch: `feat/frontend-sessions-devices`
Commit message:
feat(frontend): list devices and revoke sessions


Should:
- GET /auth/devices and GET /auth/sessions
- DELETE /auth/sessions/{id} then refresh list
- Use useDevices / useSessions hooks

Should not:
- Invent device revoke if only session revoke exists
- Show internal DB ids without labels

Done when: user can see devices/sessions and revoke a session.
```

### F1.6 — Auth gate

```text
Implement frontend slice F1.6.

Goal: Route protection.
Branch: `feat/frontend-auth-gate`
Commit message:
feat(frontend): protect routes with auth gate


Should:
- If no access_token → redirect /login
- Public routes: login, register, forgot, reset
- Optional: try /auth/refresh once before forcing login

Should not:
- Trust only client “isLoggedIn” flag without token store
- Block public auth pages

Done when: visiting / while logged out always ends on /login.
```

---

### F2.1 — Profile

```text
Implement frontend slice F2.1.

Goal: View/edit own profile.
Branch: `feat/frontend-profile`
Commit message:
feat(frontend): view and edit own profile


Should:
- GET /users/me; PATCH /users/me for display_name, bio, avatar_url
- Omit unchanged fields on patch
- Use useMe

Should not:
- PATCH /users/{other_id}
- Require email edit if API doesn’t support it

Done when: profile loads and updates via gateway.
```

### F2.2 — Start chat

```text
Implement frontend slice F2.2.

Goal: Start 1:1 chat by email or user_id.
Branch: `feat/frontend-start-chat`
Commit message:
feat(frontend): start direct chat via user lookup


Should:
- Lookup exactly one of email | user_id via GET /users/lookup
- POST /conversations/direct { peer_user_id }
- Navigate to conversation route; handle created true/false
- Surface 404 peer / 400 self-chat

Should not:
- Trust client peer id without lookup for email UX
- Build message composer yet

Done when: Alice can open/create a DM with Bob.
```

### F2.3 — Inbox

```text
Implement frontend slice F2.3.

Goal: Conversation list.
Branch: `feat/frontend-inbox`
Commit message:
feat(frontend): conversation inbox with cursor pagination


Should:
- GET /conversations?limit=&cursor=
- Show peer_display_name, last_message_preview, last_activity_at
- Soft-fail UX when peer_display_name is null
- Load-more via next_cursor
- Use useConversations

Should not:
- Show conversations user isn’t a member of (server already filters)
- Order by client clock instead of last_activity_at from API

Done when: inbox matches gateway list + cursor pagination.
```

### F2.4 — Conversation header (no thread)

```text
Implement frontend slice F2.4.

Goal: Conversation detail shell without messages.
Branch: `feat/frontend-conversation-header`
Commit message:
feat(frontend): conversation header without message thread


Should:
- GET /conversations/{id}; show peer name + metadata
- 404 → “not found” (do not claim “forbidden”)
- Placeholder: “Messaging coming soon” — no fake send

Should not:
- Call /messages (not ready)
- Mock a thread from last_message_preview as full history

Done when: opening an inbox row shows conversation header only.
```

---

### F3.1 — Messages API types + service

```text
Implement frontend slice F3.1 AFTER backend feat/messaging-idempotency-mvp and history routes exist.

Goal: Align types + api/messages.ts with real gateway schemas.
Branch: `feat/frontend-messages-api`
Commit message:
feat(frontend): add messages API types and client


Should:
- Read app/messaging/presentation/http/schemas for send/list DTOs
- Add send + list methods on gateway paths only
- Export from api/index.ts

Should not:
- Guess field names; copy from OpenAPI/schemas
- Use created_at as ordering authority

Done when: TypeScript compiles and methods match backend.
```

### F3.2 — Message hooks

```text
Implement frontend slice F3.2.

Goal: useMessages(conversationId) + useSendMessage.
Branch: `feat/frontend-messages-hooks`
Commit message:
feat(frontend): add useMessages and useSendMessage hooks


Should:
- List with cursor/limit; send with client_message_id
- loading/error/refetch patterns like existing hooks

Should not:
- Duplicate fetch logic outside ApiClient

Done when: hooks usable from a page without raw fetch.
```

### F3.3 — Thread UI

```text
Implement frontend slice F3.3.

Goal: Message history UI ordered by sequence.
Branch: `feat/frontend-message-thread`
Commit message:
feat(frontend): render message history by sequence


Should:
- Render ascending by sequence
- Paginate older via cursor
- Membership 404 → not found

Should not:
- Sort by local timestamp
- Show messages from conversations user can’t access

Done when: history matches GET .../messages order.
```

### F3.4 — Composer + idempotency

```text
Implement frontend slice F3.4.

Goal: Send box with client idempotency.
Branch: `feat/frontend-message-composer`
Commit message:
feat(frontend): send composer with client_message_id


Should:
- Generate client_message_id per send attempt (stable on retry of same tap)
- Optimistic UI optional; final state = server message id/sequence
- Retry of same client_message_id must not duplicate bubbles

Should not:
- Let client set sequence
- Disable retries without documenting why

Done when: double-submit/retry doesn’t create two messages.
```

---

### F4.1 — WebSocket client

```text
Implement frontend slice F4.1 AFTER Phase 3 realtime gateway /ws exists.

Goal: Authenticated WS client.
Branch: `feat/frontend-websocket-client`
Commit message:
feat(frontend): connect authenticated gateway websocket


Should:
- Connect through gateway with access_token
- Reconnect with backoff; refresh token if needed
- Parse server event types from docs/04-api/websocket-protocol.md when filled

Should not:
- Connect to realtime container port bypassing gateway
- Use WS as durable history store

Done when: connect/disconnect works for a logged-in user.
```

### F4.2 — Live inbox / thread

```text
Implement frontend slice F4.2.

Goal: Apply message.new to inbox + open thread without full refetch.
Branch: `feat/frontend-live-fanout`
Commit message:
feat(frontend): apply live message.new to inbox and thread


Should:
- Update last preview/activity on inbox row
- Append to thread if sequence is next expected

Should not:
- Assume arrival order == sequence order without checks

Done when: second browser sees new message via WS.
```

### F4.3 — Gap handling

```text
Implement frontend slice F4.3 (backend Phase 3F/3G).

Goal: Detect sequence gaps; buffer; sync-since.
Branch: `feat/frontend-gap-handling`
Commit message:
feat(frontend): buffer sequence gaps and sync-since


Should:
- Track last_contiguous_sequence
- On gap, fetch sync/history then apply buffer
- Document protocol in frontend docs

Should not:
- Drop buffered messages on gap
- Treat early high sequence as “server missing forever”

Done when: simulated gap recovers to contiguous UI.
```

### F4.4 — Reconnect sync

```text
Implement frontend slice F4.4.

Goal: On WS reconnect, sync missed messages then resume live events.
Branch: `feat/frontend-reconnect-sync`
Commit message:
feat(frontend): resync history after websocket reconnect


Should:
- Call messaging sync/history with last sequence
- Then re-subscribe/listen WS

Should not:
- Rely on Redis/WS replay alone for history

Done when: offline→online fills missed messages.
```

---

### F5.1 — Show receipts

```text
Implement frontend slice F5.1 AFTER Phase 4 receipt APIs/events exist.

Goal: Show SENT → DELIVERED → READ (monotonic).
Branch: `feat/frontend-receipts-ui`
Commit message:
feat(frontend): show SENT DELIVERED READ status


Should:
- Never move status backwards in UI
- Map server status/events to ticks/labels

Should not:
- Invent per-device read state that disagrees with server

Done when: status updates match server.
```

### F5.2 — Ack delivered + mark read

```text
Implement frontend slice F5.2.

Goal: Send delivered ack on receive; mark conversation read when opened/visible.
Branch: `feat/frontend-receipts-ack`
Commit message:
feat(frontend): ack delivered and mark conversation read


Should:
- Use documented WS/HTTP receipt APIs only
- Idempotent acks OK

Should not:
- HTTP-chatty ack per keystroke if WS ack is the path

Done when: peer sees DELIVERED/READ.
```

---

### F6.1 — Presence

```text
Implement frontend slice F6.1 AFTER Phase 5 presence events exist.

Goal: Online/offline indicator from WS presence.updated.
Branch: `feat/frontend-presence`
Commit message:
feat(frontend): show conversation-scoped presence


Should:
- Conversation-scoped presence only
- Treat presence as ephemeral (TTL)

Should not:
- Persist presence in local DB as truth
- Global “who’s online” directory unless API exists

Done when: peer online state updates live.
```

### F6.2 — Typing

```text
Implement frontend slice F6.2.

Goal: Typing start/stop with debounce; show peer typing.
Branch: `feat/frontend-typing`
Commit message:
feat(frontend): typing indicators with debounce


Should:
- Debounce start; send stop on blur/unmount
- Membership-safe (server enforces)

Should not:
- Persist typing to Postgres from client
- Spam events every keypress without throttle

Done when: typing indicator appears/clears correctly.
```

---

### F7.1 — Group list/create

```text
Implement frontend slice F7.1 AFTER Phase 6A group APIs exist.

Goal: Create group + list group conversations.
Branch: `feat/frontend-groups`
Commit message:
feat(frontend): create and list group conversations


Should:
- Follow group DTOs from gateway schemas/docs
- Reuse inbox patterns with type=group

Should not:
- Reuse direct-pair unique constraints in client logic

Done when: user can create a group and see it in inbox.
```

### F7.2 — Group members admin

```text
Implement frontend slice F7.2.

Goal: Add/remove members; respect admin/last-admin rules via API errors.
Branch: `feat/frontend-group-members`
Commit message:
feat(frontend): manage group members as admin


Should:
- Admin-only actions; show API errors clearly

Should not:
- Allow client-side-only admin bypass

Done when: admin flows match backend authz.
```

---

### F8.1 — Device list UX

```text
Implement frontend slice F8.1.

Goal: Polish multi-device session UX (extend F1.5).
Branch: `feat/frontend-multi-device-ux`
Commit message:
feat(frontend): polish multi-device session management


Should:
- Clear current vs other devices; revoke others

Should not:
- Register push here unless notifications API exists

Done when: multi-device management is usable.
```

### F8.2 — Push token registration

```text
Implement frontend slice F8.2 AFTER Phase 7 notifications token API exists.

Goal: PUT device push token via gateway JWT.
Branch: `feat/frontend-push-tokens`
Commit message:
feat(frontend): register device push tokens


Should:
- Upsert token; handle permission denied from OS
- Tie to device_id used at login

Should not:
- Send push from the web app itself
- Store tokens without auth

Done when: token stored in notifications service.
```

### F8.3 — Offline wake + sync

```text
Implement frontend slice F8.3.

Goal: On app open after push/offline, sync history; don’t treat push payload as source of truth.
Branch: `feat/frontend-offline-sync`
Commit message:
feat(frontend): sync history after offline push wake


Should:
- Open app → sync-since / history → then WS
- Push is wake-up only

Should not:
- Persist full message body only from push

Done when: offline message appears after open+sync.
```
