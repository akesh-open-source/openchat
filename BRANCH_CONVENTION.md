# Git Branch Convention

To keep the repository organized and make it obvious what any branch is for at a glance, we follow a consistent branch naming convention. This applies to all branches pushed to the shared repository.

## 📐 Format

```text
<type>/<short-description>
```

- **type** — required. What kind of work this branch contains (see below).
- **short-description** — required. Lowercase, hyphen-separated, concise. No spaces, underscores, or camelCase.

Optionally, include an issue number to link the branch to its tracking issue:

```text
<type>/<issue-number>-<short-description>
```

## 🏷️ Types

| Type | Use for |
|---|---|
| `feat` | A new feature |
| `fix` | A bug fix |
| `docs` | Documentation only changes |
| `refactor` | Code change that neither fixes a bug nor adds a feature |
| `perf` | A performance improvement |
| `test` | Adding or correcting tests |
| `build` | Build tooling, dependencies, or package config |
| `ci` | CI/CD configuration and scripts |
| `chore` | Routine maintenance, tooling — no production code change |
| `hotfix` | Urgent fix applied directly against a release/production branch |
| `release` | Preparing a release (version bump, changelog, final checks) |
| `experiment` | Exploratory work or a prototype not yet committed to |

## ✅ Examples

```text
feat/websocket-reconnect
feat/42-message-read-receipts
fix/auth-token-expiry
fix/108-duplicate-notifications
docs/update-architecture-doc
refactor/extract-message-delivery-service
perf/optimize-message-query
test/auth-token-expiry-coverage
build/upgrade-postgres-driver
ci/add-lint-step
chore/update-dependencies
hotfix/websocket-crash-on-reconnect
release/v0.2.0
experiment/redis-pubsub-presence
```

## 🌳 Base Branches

| Branch | Purpose |
|---|---|
| `main` | Production-ready. **Protected.** Only updated by an admin merging from `staging`. |
| `staging` | Integration branch for upcoming work. **Protected.** All contributor PRs merge here. |

> **Direct pushes and pull requests are not allowed on `main` or `staging`.** Both branches are protected. Contributors must never push directly to either, and must never open a PR targeting `main`.

Collaborators must:

1. Create their **own branch** off `staging`.
2. Push their work to that branch only.
3. Open a pull request from their branch **into `staging`**.

Merging `staging` → `main` is handled separately, later, by a project admin — not something contributors do themselves.

## 🔄 Typical Workflow

```bash
# 1. Start from an up-to-date staging branch
git checkout staging
git pull origin staging

# 2. Create your own branch off staging
git checkout -b feat/42-message-read-receipts

# 3. Work, committing using the Commit Convention
git add .
git commit -m "feat(messaging): add read receipt tracking"

# 4. Keep your branch up to date with staging as needed
git fetch origin
git rebase origin/staging

# 5. Push to YOUR branch (never to staging or main directly)
git push -u origin feat/42-message-read-receipts

# 6. Open a pull request: your-branch → staging
#    (never open a PR targeting main)
```

An admin will later merge `staging` into `main` when the accumulated work is ready for production. This is not part of the regular contributor workflow.

## 📝 Guidelines

- **Never push directly to `staging` or `main`.** Both are protected branches.
- **Never open a PR targeting `main`.** All contributor PRs target `staging`.
- One branch per logical unit of work — avoid mixing unrelated changes.
- Keep branch names short but descriptive; someone should understand the purpose without opening it.
- Link the related issue number when one exists — it makes tracking and changelog generation easier.
- Delete your branch after it's merged into `staging` to keep the repository clean.
- Rebase (rather than merge) your branch onto the latest `staging` before opening or updating a PR, to keep history linear where practical.
- Long-lived branches drift and get harder to merge — prefer small, frequent PRs over large, long-running branches.

## 🚫 What to Avoid

```text
patch1
my-branch
test123
johns-fix
new-stuff
final-final-fix
```

These don't communicate the type of work, the scope, or the intent, and make it hard to tell what's safe to delete later.

## 🔍 Why This Matters

A consistent branch naming convention lets us:

- Understand what a branch is for without reading its diff
- Filter and search branches easily (e.g. `git branch --list "fix/*"`)
- Link work back to issues and PRs automatically
- Keep the repository tidy as the number of contributors grows
- Onboard new contributors faster — the convention is self-explanatory

Good branch hygiene is part of good collaboration.