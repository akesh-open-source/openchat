# Git Commit Convention

To keep the project history readable, searchable, and easy to generate changelogs from, we follow the [Conventional Commits](https://www.conventionalcommits.org/) specification.

This applies to all commits merged into `main`.

## 📐 Format

```text
<type>(<scope>): <short summary>

<body>

<footer>
```

- **type** — required. What kind of change this is (see below).
- **scope** — optional. The area of the codebase affected (e.g. `auth`, `messaging`, `websocket`, `docs`).
- **short summary** — required. Imperative, present tense, no capital letter, no period at the end.
- **body** — optional. Explains *what* and *why*, not *how*. Wrap at ~72 characters.
- **footer** — optional. Breaking changes, issue references, co-authors.

## 🏷️ Types

| Type | Use for |
|---|---|
| `feat` | A new feature |
| `fix` | A bug fix |
| `docs` | Documentation only changes |
| `style` | Formatting, whitespace, missing semicolons — no code logic change |
| `refactor` | Code change that neither fixes a bug nor adds a feature |
| `perf` | A code change that improves performance |
| `test` | Adding or correcting tests |
| `build` | Changes to build tools, dependencies, or package config |
| `ci` | Changes to CI/CD configuration and scripts |
| `chore` | Routine tasks, tooling, maintenance — no production code change |
| `revert` | Reverts a previous commit |

## ✅ Examples

```text
feat(auth): add refresh token rotation

fix(websocket): prevent duplicate reconnect attempts

docs(readme): clarify project status section

refactor(messaging): extract message delivery status into its own service

test(auth): add unit tests for token expiry handling

chore(deps): bump postgres driver to v3.2.0

ci(github-actions): run lint step before tests
```

## 💥 Breaking Changes

A **breaking change** is any change that makes existing code, clients, or integrations stop working the way they used to — something a consumer of your API, library, or schema would have to update their own code to handle.

Examples: renaming or removing a field, changing a function's required parameters, changing default behavior, removing an endpoint, or changing what an error code means. Adding a new optional field or a new endpoint is **not** breaking.

If a commit introduces a breaking change, note it in the footer:

```text
feat(api): change message payload schema

BREAKING CHANGE: `content` field is now `body`. Clients relying on
`content` must update to the new field name.
```

Alternatively, append `!` after the type/scope:

```text
feat(api)!: change message payload schema
```

Marking it clearly means anyone scanning the changelog knows to stop and read before upgrading, and it signals that this change requires a **major** version bump under [Semantic Versioning](https://semver.org/) (e.g. `1.4.2` → `2.0.0`), rather than a minor or patch bump.

## 🔗 Referencing Issues

Reference related issues in the footer when applicable. GitHub recognizes certain keywords and will **automatically close the referenced issue** once the commit's PR is merged into the default branch:

```text
fix(auth): correct token expiry calculation

Closes #42
```

`Closes`, `Fixes`, and `Resolves` all behave identically — pick whichever reads naturally:

```text
Closes #42
Fixes #42
Resolves #42
```

If you want to **link** an issue for context without auto-closing it (e.g. the commit is related but doesn't fully resolve it), use:

```text
Refs #42
```

**Multiple issues** in one footer:

```text
Closes #42, closes #58
```

**Cross-repo reference** (if the issue lives in a different repository):

```text
Closes anthropic-org/openchat#42
```

Since our bug reports and feature requests live as GitHub issues, using `Closes #<number>` keeps the issue tracker in sync automatically — no one has to remember to close the issue by hand after merging.

## ⌨️ How to Write a Commit with a Footer

The footer is just another paragraph, separated from the summary (and body) by a blank line. A few ways to write one:

**Multiple `-m` flags** (each becomes its own paragraph):

```bash
git commit -m "feat(api): change message payload schema" \
           -m "BREAKING CHANGE: content field is now body. Clients relying on content must update to the new field name."
```

**Single `-m` with `\n\n`:**

```bash
git commit -m "feat(api): change message payload schema

BREAKING CHANGE: content field is now body. Clients relying on
content must update to the new field name."
```

**Open your editor** (best for longer messages with a body and footer):

```bash
git commit
```

```text
feat(api): change message payload schema

Switched the message payload field from `content` to `body` to
align with the new schema used across mobile and web clients.

BREAKING CHANGE: `content` field is now `body`. Clients relying on
`content` must update to the new field name.
```

**Stacking multiple footers** (e.g. breaking change + issue link) — each is its own paragraph:

```text
fix(auth): correct token expiry calculation

BREAKING CHANGE: expired tokens now return 401 instead of 200 with
an error body.

Closes #42
```

> 💡 Tip: set your preferred editor for multi-line commits, e.g. `git config --global core.editor "cursor --wait"`.

## 📝 Guidelines

- Keep the summary line under **72 characters**.
- Use the imperative mood: `add`, not `added` or `adds`.
- Don't end the summary line with a period.
- One logical change per commit — avoid bundling unrelated changes.
- If a commit needs a lot of explanation, that's often a sign it should be split into smaller commits.
- Write commits for the person reviewing your PR and for future contributors reading `git log` — not just for yourself.

## 🚫 What to Avoid

```text
fix stuff
update
wip
asdf
final fix (for real this time)
```

These convey no information and make history harder to search or use for changelog generation.

## 🔍 Why This Matters

Following a consistent commit convention lets us:

- Generate changelogs automatically
- Understand the history of a file or feature at a glance
- Identify breaking changes quickly
- Make code review and rollback easier
- Keep the project approachable for new contributors

Good commit history is part of good documentation.