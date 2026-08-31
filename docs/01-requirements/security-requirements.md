# Security Requirements

## Status

Proposed

## Authentication

Protected operations must require valid authentication.

Authentication must support:

- Access tokens
- Refresh tokens
- Session/device tracking
- Token expiration
- Session revocation

---

## Authorization

Every protected resource must verify authorization.

A user must not be able to:

- Read another user's private conversation.
- Send messages to a conversation they are not a member of.
- Modify another user's message.
- Modify a group without appropriate permissions.
- Access another user's device/session information.

---

## Input Validation

All client-controlled input must be validated.

This includes:

- API payloads
- WebSocket events
- Query parameters
- File metadata
- User-generated text

---

## Rate Limiting

Rate limiting must be applied to sensitive or abuse-prone operations.

Examples:

- Login
- OTP requests
- Message sending
- Group creation
- File uploads
- WebSocket connection attempts

---

## Transport Security

Production traffic must use TLS.

WebSocket connections must use secure WebSockets:

```text
wss://
```

---

## Data Security

Sensitive data must not be logged.

Examples:

* Passwords
* Access tokens
* Refresh tokens
* OTPs
* Private credentials

---

## End-to-End Encryption

End-to-end encryption is not part of the initial implementation unless explicitly approved.

If E2E encryption is introduced later, the architecture must be revisited because the server will no longer be able to operate on plaintext message content.
