# Functional Requirements

## Status

Proposed

## 1. Authentication

The system must allow users to authenticate securely.

### Requirements

- User registration must be supported.
- User login must be supported.
- User logout must be supported.
- Access tokens must be supported.
- Refresh tokens must be supported.
- Sessions/devices must be tracked.
- Invalid or expired credentials must be rejected.
- Authentication endpoints must be rate limited.

---

## 2. User Management

The system must maintain user accounts.

### Requirements

- Users must have a unique identity.
- Users must have a profile.
- Users must be able to update supported profile information.
- Users must be able to view other users according to privacy rules.
- Users must be able to manage their active devices/sessions.

---

## 3. One-to-One Conversations

Users must be able to communicate through one-to-one conversations.

### Requirements

- A user must be able to create or access a conversation with another user.
- A conversation must have a unique identifier.
- Only authorized members may access the conversation.
- Users must be able to retrieve conversation history.
- Conversation history must support pagination.

---

## 4. Messaging

Users must be able to send and receive messages.

### Requirements

- Users must be able to send text messages.
- Messages must be persisted.
- Messages must have unique server-side identifiers.
- Clients must provide a unique client-side message identifier.
- Messages must be delivered in realtime when the recipient is connected.
- Messages must remain available when the recipient is offline.
- Message history must be retrievable after reconnecting.
- Duplicate message submissions must not create duplicate logical messages.

---

## 5. Message Status

The system must support message lifecycle states.

### States

```text
PENDING
SENDING
SENT
DELIVERED
READ
```

### Definitions

* `SENT`: the server has successfully persisted the message.
* `DELIVERED`: the recipient device has acknowledged receipt.
* `READ`: the recipient has acknowledged that the message was read.

---

## 6. Message Ordering

Messages within a conversation must have deterministic ordering.

### Requirements

* Server-side ordering must be authoritative.
* Client timestamps must not be used as the sole ordering mechanism.
* Messages must remain correctly ordered after synchronization.
* Reconnected clients must be able to reconstruct the correct message order.

---

## 7. Offline Messaging

The system must support users who are temporarily offline.

### Requirements

* Messages sent to offline users must be persisted.
* Offline users must receive missed messages after reconnecting.
* Push notifications may be generated for offline users.
* The client must be able to synchronize messages missed while offline.

---

## 8. Reconnection

The system must tolerate temporary WebSocket disconnections.

### Requirements

* Clients must be able to reconnect.
* Reconnection must re-authenticate the connection where required.
* The client must communicate its last known synchronization position.
* The server must identify missing events/messages.
* Missing messages must be synchronized after reconnect.
* Synchronization must be idempotent.

---

## 9. Read Receipts

The system must support read status.

### Requirements

* Users must be able to mark messages as read.
* Read state must be persisted.
* Read state must synchronize across supported devices.
* Group read behavior must be explicitly defined.

---

## 10. Group Chat

Users must be able to communicate in groups.

### Requirements

* Users must be able to create groups.
* Users must be able to add members.
* Authorized users must be able to remove members.
* Groups must have administrators.
* Group messages must be persisted.
* Group members must receive group messages according to membership state.
* Group membership changes must be represented as events where required.

---

## 11. Presence

The system should support online/offline presence.

### Requirements

* Connected users may be represented as online.
* Disconnected users must eventually be represented as offline.
* Presence must not depend on permanent database writes for every state change.
* Presence must tolerate temporary network failures.

---

## 12. Typing Indicators

The system should support typing indicators.

### Requirements

* Clients may send typing-start events.
* Clients may send typing-stop events.
* Typing events must be realtime.
* Typing events should not be persisted as normal messages.
* Typing state must expire automatically if a client disappears.

---

## 13. Multi-Device

A user should be able to use multiple devices.

### Requirements

* Devices must have unique identifiers.
* Devices must have independent sessions.
* Push notification tokens must be associated with devices.
* Messages must synchronize across supported devices.
* Read state must synchronize according to the defined product behavior.
* Device/session revocation must be supported.

---

## 14. Push Notifications

The system should notify users when appropriate.

### Requirements

* Device push tokens must be stored securely.
* Offline users may receive notifications for new messages.
* Invalid push tokens must be handled.
* Notification delivery should be retryable.
* Notification behavior must respect user/device preferences.

---

## 15. Media

Media support is planned for a later phase.

Potential media types:

* Images
* Videos
* Audio
* Documents

Media must use object storage rather than storing large binary content directly in the primary database.

---

## 16. Authorization

Authentication alone must not grant access to conversations.

The system must verify authorization for:

* Reading conversations
* Sending messages
* Reading messages
* Updating message state
* Group membership operations
* Device/session operations
* Media access

---

## 17. Administration

Administrative functionality is outside the initial MVP unless explicitly required.

Potential future capabilities:

* User moderation
* Group moderation
* Abuse reporting
* Account suspension
* Audit tools
