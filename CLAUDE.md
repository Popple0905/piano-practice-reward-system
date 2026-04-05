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

**SQLite DB location:** `backend/instance/piano_app.db` (excluded from git).

**Frontend API calls:** all calls go through `API_BASE_URL = window.location.origin + '/api'` (auto-detects host), using `currentToken` stored in the JS global scope.

**Logout / user switching:** `resetNavState()` must be called to clear all dynamic content and hide both `#parentNav` / `#childNav` before showing the new user's dashboard. Forgetting this causes cached content from the previous user to remain visible.

## Environment Variables

| Variable | Purpose | Default |
|---|---|---|
| `DATABASE_URL` | DB connection string | SQLite (dev) |
| `JWT_SECRET_KEY` | JWT signing key | hardcoded dev value |
