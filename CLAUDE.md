# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Starting the Server

Use the provided batch file (kills all existing Python processes first, then starts fresh):
```
start_server.bat
```

Or manually:
```bash
cd backend
source venv/Scripts/activate   # Windows Git Bash
python app.py
```

Server runs at `http://localhost:5000`. Flask serves both the API and the frontend static files.

## Architecture Overview

**Single-server design:** Flask serves the frontend (`frontend/`) as static files AND handles all API requests under `/api/`. There is no separate frontend build step — `index.html` is a self-contained SPA with all CSS embedded and JS split across a few plain files.

**Backend layout:**
- `backend/app.py` — app factory, blueprint registration, frontend file serving
- `backend/models.py` — all 7 SQLAlchemy models in one file
- `backend/routes/` — one blueprint per domain: `auth`, `practice`, `awards`, `management`, `special_redemptions`
- `backend/config.py` — `DevelopmentConfig` (SQLite) / `ProductionConfig` (MySQL via `DATABASE_URL` env var)

**Frontend layout:**
- `frontend/index.html` — the entire UI: all CSS (~2300 lines), HTML structure, and inline `<script>` with most JS logic
- `frontend/apiClient.js` — Axios instance with JWT Bearer token injection
- `frontend/services.js` — auth service functions
- `frontend/ChildDashboard.js` / `ParentDashboard.js` — additional dashboard logic (mostly superseded by inline JS in index.html)

## Data Models

JWT identity format: `"parent_<id>"` or `"child_<id>"` — all route permission checks parse this string.

All datetimes are stored as **naive UTC** in the DB. All API responses serialize datetimes with a `Z` suffix (e.g., `.isoformat() + 'Z'`) so the frontend correctly interprets them as UTC.

`game_balance` on `Child` is the live reward points balance — modified directly on approval, redemption, and award events.

`SpecialRedemption.quantity` is `None` for unlimited; decremented on each redeem. Items with `quantity=0` or past `expires_at` are filtered out before returning to children.

## Key Conventions

**Adding a new route:** create a blueprint in `backend/routes/`, import and register it in `app.py` with `app.register_blueprint(bp, url_prefix='/api/...')`. Tables are auto-created via `db.create_all()` on startup, but SQLite won't add new columns to existing tables — use `ALTER TABLE` manually or delete the DB file during development.

**Database migration rule:** Any change to `models.py` that adds or modifies a column on an existing table **must** also add a corresponding entry to the `MIGRATIONS` list in `backend/app.py`. This ensures the live DB (SQLite and MySQL) is automatically updated on next startup without manual intervention. Format:
```python
('table_name', 'column_name', 'ALTER TABLE table_name ADD COLUMN column_name TYPE DEFAULT value'),
```

**Production data safety (before every commit):** pushing to `master` auto-deploys to the cloud server, which runs `_auto_migrate` against the **live MySQL DB holding real family data**. Never commit a change that could damage or hide it. Before committing, check:

1. **Additive only** — `ADD COLUMN` is safe. Dropping, renaming or retyping a column, or any destructive `UPDATE`/`DELETE`, must never run automatically; do it as a deliberate one-off.
2. **Existing rows must stay visible** — if new code filters on a new column (e.g. `mode='random'`), rows written by the old code must end up matching that filter. Add an idempotent backfill to `BACKFILLS` in `app.py` rather than relying on the engine's `DEFAULT` behaviour.
3. **MySQL, not just SQLite** — verify the ALTER syntax works on both, and that new column names aren't MySQL reserved words.
4. **Concurrency** — `Procfile` runs gunicorn with 2 workers, so `create_app()` (and therefore the migration) runs twice in parallel. Migration steps must tolerate losing that race without failing to boot.
5. **Prove it** — simulate the upgrade before committing: build a DB with the *old* schema, populate it with representative data, boot the new code against it twice, and confirm row counts, balances and existing records are unchanged.

**SQLite DB location:** `backend/instance/piano_app.db` (excluded from git).

**Frontend API calls:** all calls go through `API_BASE_URL = window.location.origin + '/api'` (auto-detects host), using `currentToken` stored in the JS global scope.

**Logout / user switching:** `resetNavState()` must be called to clear all dynamic content and hide both `#parentNav` / `#childNav` before showing the new user's dashboard. Forgetting this causes cached content from the previous user to remain visible.

## Environment Variables

| Variable | Purpose | Default |
|---|---|---|
| `DATABASE_URL` | DB connection string | SQLite (dev) |
| `JWT_SECRET_KEY` | JWT signing key | hardcoded dev value |
