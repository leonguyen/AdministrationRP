# TailAdmin — NiceGUI

A rebuild of the TailAdmin admin dashboard (originally built with
[Reflex](https://reflex.dev)) using [NiceGUI](https://nicegui.io) and SQLite.

The previous Reflex app (`rxconfig.py`, `build_and_run_attached_zip/`, svar grids,
Mantine components, Postgres + Alembic migrations) has been removed and replaced by a
pure-Python NiceGUI app with a self-contained SQLite database.

## Screens

- `/` — Ecommerce dashboard: metric cards, monthly-sales bar chart, monthly-target
  gauge, statistics line chart (echarts), account-access strip.
- `/menu` — Menu hierarchy management: searchable grid + add/edit/delete dialog
  (session-only state).
- `/files` — Private file manager (auth-guarded): folders, upload (≤5 files, ≤10 MB),
  rename, delete, download. Files are stored in SQLite per account.
- `/github` — GitHub Sync placeholder (feature unavailable).
- `/auth` — Sign in / sign up (modal, argon2-hashed passwords).
- `/account` — Account profile (auth-guarded).

## Features

- **Local auth**: argon2 password hashing, email normalization, account lockout
  (5 failed attempts → 15-minute lock), per-browser session identity.
- **File storage**: per-account namespaces, folder hierarchy, binary content,
  duplicate-name protection, 10 MB per-file limit.
- **Hosting resources footer**: cgroup CPU/memory + disk metrics with refresh.
- **Footer links**: fetched from a remote YAML API.
- **Global search** in the header (Dashboard / Menu / Files / GitHub / Auth).

## Requirements

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) (recommended)

## Run

```bash
uv sync                 # install dependencies
uv run python main.py   # start the app
```

Then open http://localhost:8080

The SQLite database is created automatically at `tailadmin.db` (override with
`TAILADMIN_DB` or `DATABASE_URL`).

## Structure

```
main.py                 # entry point, routes
app/
  db.py                 # SQLite engine + session
  models.py             # SQLAlchemy models (FileItem, LocalAccount)
  auth_service.py       # argon2 auth, normalization, lockout
  files_service.py      # folder/upload/rename/delete/download
  hosting_service.py    # cgroup CPU/memory/disk metrics
  footer_service.py     # remote footer links
  session.py            # per-user identity + per-tab view state
  theme.py              # TailAdmin palette + CSS
  layout.py             # shell: sidebar + header + hosting/footer
  shell_state.py        # global search
  menu_data.py          # initial menu rows
  dashboard_page.py     # Ecommerce dashboard
  menu_page.py          # Menu grid + dialog
  files_page.py         # File manager (auth-guarded)
  account_page.py       # Auth + account pages
  github_page.py        # GitHub placeholder
assets/                 # favicon + source reference
```

## Deploy (Render.com)

A `render.yaml` blueprint and `Dockerfile` are included. In Render: **New →
Blueprint**, connect this repo, and apply. The SQLite DB is persisted on a mounted
disk at `/app/data`.

## Notes

- `storage_secret` (used to sign the browser session cookie) should be set via the
  `STORAGE_SECRET` env var in production; a dev default is used locally.
- The Reflex source is preserved under `assets/Administration-main.zip` for
  reference; the running app does not depend on it.