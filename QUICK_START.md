# PianoAPP v1 - Quick Start Guide

## 📋 Project Overview

**PianoAPP** is a parent-child interactive piano practice management system where children earn reward points by logging daily practice sessions.

### Key Features
✅ **Child Accounts** - Log daily practice time and notes
✅ **Parent Dashboard** - View children's progress, grant reward points
✅ **Statistics** - Weekly/monthly/yearly practice data analysis
✅ **Reward Points Management** - Point-based incentive system
✅ **Secure Authentication** - JWT Token verification

---

## 🚀 5-Minute Quick Start

### Step 1: Set Up Environment

#### Install Required Software
1. **Python 3.10+** ✅ Verified with Python 3.13
   - Download: https://www.python.org/
   - Verify: `python --version`

2. **Git** (optional)
   - Download: https://git-scm.com/

**Note**: Local development uses SQLite — no MySQL installation needed. MySQL can be configured for production.

### Step 2: Set Up Backend

```bash
# 1. Enter backend directory
cd PianoAPPv1\backend

# 2. Create Python virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. (Optional) Configure environment variables - create .env file
# FLASK_ENV=development
# JWT_SECRET_KEY=your-secret-key
# Other environment variables are optional and will use defaults

# 5. Start server
python app.py
```

✅ Server running at `http://localhost:5000`
✅ Database auto-uses SQLite (piano_app.db in backend/instance/)
✅ First run: initialize test data with `python init_db.py`

### Step 3: Access the Frontend

✨ **Frontend is integrated — open the web interface directly:**

1. **Open browser** → go to `http://localhost:5000`
2. **Login with test accounts**
   - Child: ID `1` / password `child123`
   - ✅ Test accounts created automatically (run `python init_db.py`)
3. **Test features**
   - ✅ Log practice time (15-minute units)
   - ✅ View multiple practice records
   - ✅ Time rounding (invalid times auto-adjusted to nearest 5 min)
   - ✅ Query reward points balance
   - ✅ Local time detection (auto-detects system timezone)

### Step 4: API Testing (optional)

Open terminal/PowerShell to run API tests (verified working):

#### PowerShell Test Script

```powershell
# Parent login
$body = @{username="parent2024"; password="securepass123"} | ConvertTo-Json
Invoke-WebRequest -Uri http://localhost:5000/api/auth/parent/login `
  -Method POST -Headers @{"Content-Type"="application/json"} -Body $body -UseBasicParsing | Select-Object -ExpandProperty Content

# Example response:
# {"access_token":"eyJ...","parent_id":2,"username":"parent2024"}
```

#### Bash/curl Test Script

```bash
# Parent login
curl -X POST http://localhost:5000/api/auth/parent/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "parent2024",
    "password": "securepass123"
  }'
```

🎉 See [TESTING_REPORT.md](TESTING_REPORT.md) for the full test results

---

## 📱 Frontend Development

### React Native (recommended for beginners)

```bash
# 1. Install Node.js (https://nodejs.org/)

# 2. Create React Native project
cd frontend
npx react-native init PianoApp
cd PianoApp

# 3. Install dependencies
npm install axios @react-native-async-storage/async-storage

# 4. Run the app
# iOS
npx react-native run-ios

# Android
npx react-native run-android
```

### Flutter (recommended for performance)

```bash
# 1. Install Flutter (https://flutter.dev/docs/get-started/install)

# 2. Create project
cd frontend
flutter create piano_app
cd piano_app

# 3. Add dependencies (in pubspec.yaml)
# dependencies:
#   http: ^1.1.0
#   shared_preferences: ^2.2.0

flutter pub get

# 4. Run the app
flutter run
```

---

## 📊 System Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│                  PianoAPP System Architecture            │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────┐              ┌──────────┐                │
│  │ Child APP │              │ Parent   │                │
│  │           │              │ APP      │                │
│  └─────┬────┘              └────┬─────┘                │
│        │                        │                       │
│        │  log practice  │  grant rewards │              │
│        └─────────┬──────────────┘                       │
│                  │                                      │
│                  ▼                                      │
│        ┌─────────────────┐                             │
│        │   Flask Backend  │                             │
│        │   (REST API)    │                             │
│        └────────┬────────┘                             │
│                 │                                      │
│    ┌────────────┼────────────┐                         │
│    │            │            │                         │
│    ▼            ▼            ▼                         │
│  ┌────────┐ ┌────────┐ ┌──────────┐                    │
│  │Practice│ │Child   │ │ Rewards  │                    │
│  │  DB    │ │  DB    │ │   DB     │                    │
│  └────────┘ └────────┘ └──────────┘                    │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## 🔑 Core API Endpoints

| Feature | Method | Endpoint | Description |
|---------|--------|----------|-------------|
| Register Parent | POST | `/api/auth/parent/register` | Create parent account |
| Parent Login | POST | `/api/auth/parent/login` | Parent authentication |
| Register Child | POST | `/api/auth/child/register` | Create child account |
| Child Login | POST | `/api/auth/child/login` | Child authentication |
| Add Practice | POST | `/api/practice/record` | Child logs today's practice |
| View Records | GET | `/api/practice/records/<child_id>` | View practice records |
| Statistics | GET | `/api/practice/statistics/<child_id>` | View statistics |
| Grant Reward | POST | `/api/awards/give` | Parent grants reward points |
| Check Balance | GET | `/api/awards/balance/<child_id>` | View reward points balance |

---

## 📝 Configuration Files

### backend/.env
```
FLASK_ENV=development          # development / production
DATABASE_URL=mysql+pymysql://root:password@localhost/piano_app
JWT_SECRET_KEY=your-secret-key-change-in-production
SERVER_PORT=5000              # default port
```

### frontend/apiClient.js
```javascript
const API_BASE_URL = 'http://localhost:5000/api';
// Change to your server address
```

---

## ✨ Core Features

### 1️⃣ Child Side
- **Log Practice**: Enter today's practice duration and notes
- **View Points**: Real-time display of available reward points
- **Track History**: View practice record history

### 2️⃣ Parent Side
- **Monitor Progress**: View each child's practice progress
- **Data Analysis**: Weekly/monthly/yearly practice statistics
- **Grant Rewards**: Award reward points based on performance

### 3️⃣ Incentive System
```
30 min practice → earn 30 reward points
                  ↓
         child redeems for game time
```

---

## 🐛 Common Issues

### Q1: Cannot connect to database
**A:** Check if MySQL is running
```bash
# macOS
mysql.server status

# Windows (PowerShell)
Get-Service MySQL80  # or corresponding version
```

### Q2: Module Flask not found
**A:** Confirm the virtual environment is activated and dependencies installed
```bash
which python  # should show venv path
pip install -r requirements.txt
```

### Q3: Frontend cannot connect to backend
**A:** Check
1. Is backend running at `localhost:5000`
2. Is `API_BASE_URL` in frontend `apiClient.js` correct
3. Firewall settings

---

## 📚 Next Steps

1. **Complete backend testing** → Use scripts in [API_TESTING.md](../docs/API_TESTING.md)
2. **Develop frontend app** → See [DEVELOPMENT.md](DEVELOPMENT.md)
3. **Deploy** → See [DEPLOYMENT.md](../docs/DEPLOYMENT.md)
4. **Add new features** → See the feature roadmap section

---

## 📞 Support

Having issues? Check these resources:
- 📖 See [README.md](../README.md)
- 🧪 See [API_TESTING.md](../docs/API_TESTING.md)
- 🚀 See [DEPLOYMENT.md](../docs/DEPLOYMENT.md)
- 💻 See [DEVELOPMENT.md](DEVELOPMENT.md)

---

**Happy coding! 🎉**
