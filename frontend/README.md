# OpenChat frontend

Vite + React + TypeScript client for the OpenChat gateway
(`http://localhost:8000`).

## Quick start

```bash
cd frontend
cp .env.example .env   # optional; defaults to http://localhost:8000
npm install
npm run dev
```

Open `http://localhost:5173`. Routes: `/` (inbox placeholder), `/login`, `/register`.

| Env | Default | Meaning |
| --- | --- | --- |
| `VITE_API_BASE_URL` | `http://localhost:8000` | Gateway origin only — never call `:8001`/`:8002`/`:8003` |

## Layout

```text
frontend/
  src/
    api/          Gateway fetch client (auth, users, conversations)
    hooks/        React provider + query/mutation hooks
    types/        DTOs mapped from backend schemas
    pages/        Route placeholders (F1/F2 screens next)
    App.tsx       React Router shell
    main.tsx      Entry
  ROADMAP.md      Frontend slices + developer prompts
```

## Scripts

- `npm run dev` — Vite dev server
- `npm run build` — typecheck + production bundle
- `npm run preview` — serve `dist/`

## Next slices

See [ROADMAP.md](./ROADMAP.md): F0.2 (track in git) → F0.3 (wire `OpenChatApiProvider`) → F1 auth UI.

> `frontend/` is tracked; `node_modules/`, `dist/`, and `.env` stay ignored via `frontend/.gitignore`.
