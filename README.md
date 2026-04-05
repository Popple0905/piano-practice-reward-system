# Piano Practice Reward System 🎹

A parent-child interactive system for managing piano practice time, where children earn reward points by logging daily practice sessions.

## ✨ Project Status

✅ **Backend API** - Fully functional (all endpoints tested)
✅ **Frontend Web** - Implemented (HTML5 + Vanilla JS, served by backend)
✅ **Child Dashboard** - Implemented (login, record submission, history, reward balance)
✅ **Parent Dashboard** - Implemented (children list, pending approvals, account management)
✅ **Database** - SQLite (development) / MySQL (production)
✅ **Authentication** - JWT Token
✅ **Time Handling** - 5-min rounding, local timezone support
✅ **Feature Testing** - All core features verified

**Latest Updates (2026-03-23)**:
- ✅ Parent page: "Award Game Time" renamed to "Award Practice Points" throughout
- ✅ Child page: Merged "Redeem Game Time" and "Game Time" tabs; balance shown as "Practice Reward Points" below nickname; added "Reward History" tab
- ✅ Parent page: Added "Approved Records" tab showing past 30 days, grouped by child
- ✅ New UI design: Eevee watercolor light theme (warm amber × teal × deep indigo)
- ✅ Custom App Icon as website favicon and Apple touch icon
- ✅ Mobile layout optimization (responsive CSS overhaul)
- ✅ Login form: "Remember account" feature (credentials stored in localStorage)
- ✅ Cleared default credentials from login form
- ✅ Removed frontend test buttons (query game balance, query practice records) and output box
- ✅ Fixed ratio display format (1.0 → 1)
- ✅ Parent account settings: change own password after login
- ✅ Practice time unit changed to 15 minutes (default 15 min)
- ✅ Fixed mobile login issue (dynamic API URL, disabled autocapitalize on ID input)
- ✅ System renamed to "Piano Practice Reward System"
- ✅ Child account ID supports alphanumeric characters (up to 20 chars)
- ✅ Parent "Manage Child Accounts" feature (add / delete / rename / change password)

⏳ **Next Steps**: Practice goal setting, data visualization charts

## System Architecture

```
PianoAPPv1/
├── backend/              # Python Flask REST API + frontend serving
│   ├── app.py            # Flask app entry point (serves frontend files and API)
│   ├── config.py         # Configuration management
│   ├── models.py         # Database models
│   ├── requirements.txt  # Python dependencies
│   ├── routes/           # API routes
│   │   ├── auth.py       # Authentication endpoints
│   │   ├── practice.py   # Practice record endpoints
│   │   ├── awards.py     # Reward points endpoints
│   │   └── management.py # Child account management endpoints
│   └── venv/             # Python virtual environment
├── frontend/             # Frontend files (HTML5 + Vanilla JS)
│   ├── index.html        # Web login and dashboard interface
│   ├── apiClient.js      # API client
│   ├── services.js       # Business logic
│   ├── ParentDashboard.js   # Parent control panel (React Native)
│   └── ChildDashboard.js    # Child main page (React Native)
├── database/             # Database files
│   └── schema.sql        # Database schema
└── docs/                 # Documentation
    ├── API_REFERENCE.md  # Complete API endpoint reference
    ├── INSTALLATION.md   # Installation and troubleshooting
    ├── API_TESTING.md    # Test scripts
    └── DEPLOYMENT.md     # Deployment guide
```

## Feature Modules

### 1. Authentication
- ✅ Child login (multi-account support, alphanumeric IDs)
- ✅ Parent login / registration
- ✅ Parent password change
- ✅ JWT Token authentication

### 2. Practice Tracking
- ✅ Child logs practice time (15-min units, default 15 min)
- ✅ View multiple practice history records
- ✅ Time rounding (automatic local time adjustment)
- ✅ Status management (pending / approved / rejected)
- ✅ Parent approve / reject practice records

### 3. Game Reward System
- ✅ Child views reward points balance
- ✅ Reward point redemption (15-min units)
- ✅ Conversion ratio configuration
- ✅ Parent grants reward points

### 4. Child Account Management
- ✅ Parent adds child accounts (name, password, age)
- ✅ Parent deletes child accounts
- ✅ Parent updates child name
- ✅ Parent updates child password

## 🚀 Quick Start (5 minutes)

### 1. Set Up Environment

```bash
cd PianoAPPv1/backend
pip install -r requirements.txt
```

### 2. Start Server

```bash
python app.py
```

✅ Server running at `http://localhost:5000`
✅ SQLite database auto-created in `backend/instance/`
✅ First run: initialize test accounts if needed

### 3. Initialize Test Accounts (first run only)

```bash
# Run from the backend directory
python init_db.py
```

**Auto-created test accounts:**
- Child: ID `1`, password `child123`, name "Test Child"

### Environment Variables (optional)

Create a `.env` file to customize settings:
```
FLASK_ENV=development
JWT_SECRET_KEY=your-secret-key-change-in-production
DATABASE_URL=sqlite:///piano_app.db
```

## API Endpoints

### Authentication (/api/auth)
- `POST /parent/register` - Register parent
- `POST /parent/login` - Parent login
- `POST /parent/change-password` - Parent change password
- `POST /child/register` - Register child
- `POST /child/login` - Child login
- `GET /parent/me` - Get parent info

### Practice (/api/practice)
- `POST /record` - Add practice record
- `POST /record/<id>/approve` - Approve practice record
- `POST /record/<id>/reject` - Reject practice record
- `GET /records/<child_id>` - Get practice records
- `GET /statistics/<child_id>` - Get statistics
- `GET /parent/children` - Get all children with stats

### Awards (/api/awards)
- `POST /give` - Grant reward points
- `POST /request` - Redeem reward points
- `GET /balance/<child_id>` - Get reward points balance
- `GET /history/<child_id>` - Get award history
- `GET /request-history/<child_id>` - Get redemption history
- `GET /ratio` - Get conversion ratio
- `POST /ratio` - Set conversion ratio

### Child Account Management (/api/management)
- `POST /create-child` - Create child account
- `DELETE /delete-child/<child_id>` - Delete child account
- `POST /update-child-password/<child_id>` - Update child password
- `POST /update-child-name/<child_id>` - Update child name
- `POST /update-child-age/<child_id>` - Update child age

## Data Models

### Parent
```
- id: unique identifier
- username: username
- email: email address
- password_hash: hashed password
- practice_to_game_ratio: practice-to-reward conversion ratio
- created_at: creation timestamp
```

### Child
```
- id: unique identifier (alphanumeric, up to 20 chars)
- parent_id: associated parent
- name: display name
- age: age
- password_hash: hashed password
- game_balance: reward points balance
- created_at: creation timestamp
```

### PracticeRecord
```
- id: unique identifier
- child_id: associated child
- date: practice date
- time: practice start time
- practice_minutes: duration in minutes (5-min units)
- notes: notes
- status: status (pending / approved / rejected)
- created_at: creation timestamp
- approved_at: approval timestamp
```

### GameAward
```
- id: unique identifier
- parent_id: awarding parent
- child_id: receiving child
- game_minutes: reward points granted
- reason: reason for award
- created_at: creation timestamp
```

### GameRequest
```
- id: unique identifier
- child_id: associated child
- game_minutes: points redeemed (15-min units)
- request_date: redemption timestamp
- status: status (approved)
- created_at: creation timestamp
```

## 🔧 Test Status

✅ **Backend API fully tested — all tests passed**

**Verified features**:
- ✅ Parent registration / login
- ✅ Child login
- ✅ Child account management (add, delete, rename, change password)
- ✅ Practice record submission and retrieval
- ✅ Reward points granting and retrieval
- ✅ JWT authentication and permission control
- ✅ Database persistence

## 📊 Database

### Local Development (default)
- Uses SQLite (piano_app.db)
- No MySQL installation required
- Data automatically persisted to file

### Production
- Supports MySQL 8.0+
- Modify `DATABASE_URL` in config.py
- Or set via environment variable: `DATABASE_URL=mysql+pymysql://user:password@localhost/piano_app`

## Security Considerations

1. Change `JWT_SECRET_KEY` in production
2. Use HTTPS for encrypted communication
3. Regularly update dependencies
4. Validate all input data
5. Implement rate limiting to prevent brute-force attacks
6. Back up the database regularly
7. Input validation and SQL injection protection

## Planned Features

- [ ] Email notifications (practice reminders, reward notifications)
- [ ] Practice time export (PDF/Excel)
- [ ] Multi-account management (multiple children)
- [ ] Push notifications
- [ ] Practice goal setting and progress tracking
- [ ] Leaderboard
- [ ] Data visualization charts

## Tech Stack

- **Backend**: Python 3.8+, Flask, SQLAlchemy, SQLite / MySQL
- **Authentication**: JWT (Flask-JWT-Extended)
- **Frontend**: HTML5 + Vanilla JS (Web) / React Native (mobile)
- **API**: RESTful

## Developer

Created for managing children's piano practice and game time rewards.

## License

MIT License
