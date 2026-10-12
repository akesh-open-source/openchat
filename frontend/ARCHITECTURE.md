# Frontend architecture

```text
React components
      ↓
hooks/  (useAuth, useMe, useConversations, …)
      ↓
api/    (createOpenChatApi → fetch)
      ↓
Gateway :8000  →  auth / users / messaging
```

- **Types** are 1:1 with gateway JSON, not with SQLAlchemy models.
- **ApiClient** owns base URL, JSON bodies, query strings, and Bearer injection.
- **TokenStore** is swappable (`localStorage` in the browser, memory in tests).
- Public auth paths skip Bearer; everything else requires an access token.
- Errors surface as `ApiError` with HTTP `status` and FastAPI `{ detail }`.
