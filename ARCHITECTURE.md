# Project File Structure

```
PianoAPPv1/
│
├── 📁 backend/                 # Python Flask REST API backend
│   ├── app.py                 # Flask app entry point
│   ├── config.py              # Configuration management (dev/prod)
│   ├── models.py              # Database models (Parent, Child, PracticeRecord, GameRequest)
│   ├── init_db.py             # Database initialization script (creates test accounts)
│   ├── requirements.txt        # Python dependency list
│   ├── .env.example            # Environment variable example file
│   │
│   ├── 📁 instance/            # Instance data folder
│   │   └── piano_app.db        # SQLite database (local development)
│   │
│   └── 📁 routes/             # API route modules
│       ├── __init__.py
│       ├── auth.py            # Authentication endpoints (parent/child login) ✅ verified
│       ├── practice.py         # Practice record endpoints (15-min units, time rounding, status management) ✅ verified
│       ├── awards.py          # Reward points endpoints (15-min units, balance query, conversion ratio) ✅ verified
│       └── management.py      # Child account management endpoints ✅ verified
│
├── 📁 frontend/               # Frontend files
│   ├── index.html             # Web login and dashboard page (HTML5+JS) ✅ verified
│   ├── DEVELOPMENT.md         # Frontend development guide
│   ├── apiClient.js          # API client
│   ├── services.js           # API service interface wrappers
│   ├── ParentDashboard.js    # Parent control panel (React Native - pending)
│   └── ChildDashboard.js     # Child main page (React Native - pending)
│
├── 📁 database/              # Database related files
│   └── schema.sql            # MySQL database schema (table definitions, indexes)
│
├── 📁 docs/                  # Documentation
│   ├── API_TESTING.md        # API test scripts and usage
│   ├── API_REFERENCE.md      # Complete API endpoint reference
│   ├── TIME_HANDLING.md      # Time handling specification
│   ├── INSTALLATION.md       # Installation guide
│   └── DEPLOYMENT.md         # Deployment guide (local/production)
│
├── README.md                 # Project overview
├── QUICK_START.md            # Quick start guide
├── TESTING_REPORT.md         # Backend test report
├── TESTING_STATUS_2026-03-22.md  # Feature test status
├── DEBUGGING_MULTIPLE_RECORDS.md # Debugging guide
├── .gitignore               # Git ignore list
└── ARCHITECTURE.md          # This file
```

## 🗄️ Database Configuration

### Local Development (default)
- **Type**: SQLite
- **File**: `backend/instance/piano_app.db`
- **Advantages**: No extra installation, auto-created, perfect for development and testing
- **Auto-init**: Database tables created automatically on first run

### Production
- **Type**: MySQL 8.0+
- **Config**: Set via `DATABASE_URL` environment variable
- **Connection string**: `mysql+pymysql://username:password@host:3306/database_name`
- **Note**: Must initialize manually by running `database/schema.sql`

### Environment Variable Configuration
See `.env.example`:
```env
# Local development (default)
# DATABASE_URL=sqlite:///piano_app.db

# Production
# DATABASE_URL=mysql+pymysql://user:password@localhost:3306/piano_app
```

## 📂 Key Files

#### `app.py` - Flask application entry point
```python
# Purpose: create Flask app, initialize DB, register blueprints, serve frontend files
# Run: python app.py
# Output: server starts at http://localhost:5000
# Features:
#   - Provides API endpoints (/api/*)
#   - Serves Web frontend (/)
#   - Auto-serves static files with SPA support
```

#### `models.py` - Database models
Defines 4 main data models:
- **Parent**: Parent account
- **Child**: Child account
- **PracticeRecord**: Practice record
- **GameAward**: Reward points award record

#### `config.py` - Configuration management
- `DevelopmentConfig`: Development environment
- `ProductionConfig`: Production environment
- Supports environment variable overrides

#### `routes/auth.py` - Authentication module
**Endpoints:**
- `POST /parent/register` - Register parent
- `POST /parent/login` - Parent login
- `POST /parent/change-password` - Change parent password
- `POST /child/register` - Register child
- `POST /child/login` - Child login
- `GET /parent/me` - Get parent info

#### `routes/practice.py` - Practice record module
**Endpoints:**
- `POST /record` - Add/update practice record
- `POST /record/<id>/approve` - Approve record
- `POST /record/<id>/reject` - Reject record
- `GET /records/<child_id>` - Get practice records list
- `GET /statistics/<child_id>` - Get statistics
- `GET /parent/children` - Get all children with stats

#### `routes/awards.py` - Reward points module
**Endpoints:**
- `POST /give` - Grant reward points
- `POST /request` - Redeem reward points
- `GET /balance/<child_id>` - Query reward points balance
- `GET /history/<child_id>` - Query award history
- `GET /request-history/<child_id>` - Query redemption history
- `GET /ratio` - Get conversion ratio
- `POST /ratio` - Set conversion ratio

#### `routes/management.py` - Child account management module
**Endpoints:**
- `POST /create-child` - Create child account
- `DELETE /delete-child/<child_id>` - Delete child account
- `POST /update-child-password/<child_id>` - Update child password
- `POST /update-child-name/<child_id>` - Update child name
- `POST /update-child-age/<child_id>` - Update child age

## 🌐 Frontend Architecture

### Web Page (index.html)
- **Type**: HTML5 + Vanilla JavaScript
- **Features**:
  - Responsive design (desktop and mobile)
  - User type selection (parent/child)
  - JWT Token management
  - API interaction display
  - Error and success messages
  - Logout functionality

### Integration
- Frontend files served directly by the Flask backend
- Access `http://localhost:5000` to automatically serve `index.html`
- All API calls go through `/api/*` routes
- Cross-origin requests supported (CORS enabled)

### Frontend Files

#### `apiClient.js` - API client
```javascript
// axios instance that automatically:
// - Adds JWT token to request headers
// - Handles 401 errors (token expiry)
// - Sets base URL and timeout
```

#### `services.js` - Service interfaces
Exports the following service objects:
```javascript
parentAuthService    // Parent authentication
childAuthService     // Child authentication
practiceService      // Practice records
awardService         // Reward points
logout()            // Logout function
```

---

## 🔄 Data Flow

```
Client Request
    ↓
apiClient (attach Token, error handling)
    ↓
routes (verify permissions, business logic)
    ↓
models (database operations)
    ↓
Database (SQLite or MySQL)
    ↓
Return JSON response
    ↓
Frontend updates UI
```

---

## 🔐 Security

### Authentication Flow
1. User logs in → backend verifies credentials
2. Login succeeds → returns JWT Token
3. Subsequent requests → send Token in Authorization header
4. Backend validates → checks Token validity and permissions

### Permission Control
- **Parent Only**: grant reward points, view all children's data, manage child accounts
- **Child Only**: add practice records, redeem reward points
- **Parent or Child**: query own information

---

## 📈 Extension Roadmap

### Short-term (v1.0)
- ✅ Basic CRUD operations
- ✅ Authentication and permission control
- ✅ Simple UI

### Mid-term (v1.5)
- 🔔 Push notifications
- 📊 Data visualization charts
- 🎯 Goal setting and tracking

### Long-term (v2.0)
- 🌐 Multi-region multi-language support
- 📸 Photo/video proof of practice
- 🎁 Virtual store (spend points on rewards)
- 👥 Community leaderboard

---

## 🚀 Quick Command Reference

```bash
# Start backend
cd PianoAPPv1/backend
source venv/bin/activate  # or venv\Scripts\activate (Windows)
python app.py

# Initialize database (first run)
python init_db.py

# Test API
curl -X GET http://localhost:5000/api/auth/parent/me \
  -H "Authorization: Bearer {TOKEN}"
```

---

**Done! See QUICK_START.md to start developing.** 🎉
