# Contributing (frontend)

- Keep types aligned with `app/*/presentation/http/schemas/*.py`.
- Add a service method only when the gateway exposes the route.
- Do not call internal service ports (`8001`/`8002`/`8003`) from the browser.
- Map `datetime` → ISO string, `UUID` → string, `int` → number.
- When messaging send/list HTTP lands, add `src/api/messages.ts` and hooks;
  reuse the existing `Message` interface.
