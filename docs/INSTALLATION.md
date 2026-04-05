# 📥 Complete Installation Guide

## Prerequisites

### System Requirements
- **OS**: Windows / macOS / Linux
- **Python**: 3.10 or higher
- **Disk Space**: At least 500MB (for dependencies)
- **Network**: Good internet connection (for downloading dependencies)

### Verify Environment
```bash
# Verify Python version
python --version
# Expected output: Python 3.x.x

# Verify pip is installed
pip --version
# Expected output: pip x.x.x from ...
```

---

## 🚀 Quick Installation (5 minutes)

### Step 1: Clone or Download Project
```bash
# Clone with Git
git clone <repository-url>
cd PianoAPPv1

# Or download ZIP and extract
```

### Step 2: Enter Backend Directory
```bash
cd backend
```

### Step 3: Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

**Verify**: The command prompt should show `(venv)` at the beginning

### Step 4: Install Dependencies
```bash
pip install -r requirements.txt
```

**Expected output**: All packages installed successfully, no errors

### Step 5: Start Server
```bash
python app.py
```

**Expected output**:
```
 * Serving Flask app 'app'
 * Debug mode: off
 * Running on http://127.0.0.1:5000
 * Running on http://192.168.x.x:5000
Press CTRL+C to quit
```

✅ **Done!** Backend service is running at `http://localhost:5000`

---

## 🔧 Detailed Installation Steps

### Method A: Using PowerShell (Windows)

```powershell
# 1. Enter project directory
cd "path\to\PianoAPPv1"

# 2. Enter backend directory
cd backend

# 3. Create virtual environment
python -m venv venv

# 4. Activate virtual environment
.\venv\Scripts\Activate.ps1
# If cannot execute, you may need to change execution policy:
# Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# 5. Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 6. Start server
python app.py
```

### Method B: Using Bash (macOS / Linux)

```bash
# 1. Enter project directory
cd ~/path/to/PianoAPPv1

# 2. Enter backend directory
cd backend

# 3. Create virtual environment
python3 -m venv venv

# 4. Activate virtual environment
source venv/bin/activate

# 5. Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 6. Start server
python app.py
```

---

## ⚙️ Configuration

### Default Configuration (recommended for development)
No extra configuration needed. The system uses SQLite by default.

### Custom Configuration (optional)

Create a `.env` file in the `backend/` directory:

```env
FLASK_ENV=development
FLASK_DEBUG=1
JWT_SECRET_KEY=your-custom-secret-key
```

Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

Then edit the `.env` file as needed.

---

## 🗄️ Database

### Local Development (SQLite)

✅ **Auto Setup**
- Database created automatically on first run
- File saved at `backend/instance/piano_app.db`
- No additional steps required

Verify the database file:
```bash
# List database file
ls backend/instance/piano_app.db  # Linux/macOS
dir backend\instance\piano_app.db  # Windows
```

### Production (MySQL)

#### Install MySQL
- **Windows**: https://dev.mysql.com/downloads/mysql/
- **macOS**: `brew install mysql`
- **Linux**: `sudo apt-get install mysql-server`

#### Configure Connection
Edit `.env` file:
```env
DATABASE_URL=mysql+pymysql://username:password@localhost:3306/piano_app
```

#### Initialize Database
```bash
# 1. Login to MySQL
mysql -u root -p

# 2. Run in MySQL
mysql> CREATE DATABASE piano_app;
mysql> USE piano_app;
mysql> source ../database/schema.sql;
mysql> exit;
```

Or directly:
```bash
mysql -u root -p piano_app < ../database/schema.sql
```

---

## ✅ Verify Installation

### Test 1: Check Server Status
```bash
# Run in new terminal/PowerShell
curl http://localhost:5000/api/auth/parent/register -X OPTIONS -v

# Expected: returns 200 or 204 status code
```

### Test 2: Parent Registration
```powershell
# PowerShell
$body = @{username="testuser"; email="test@example.com"; password="password123"} | ConvertTo-Json
Invoke-WebRequest -Uri http://localhost:5000/api/auth/parent/register `
  -Method POST -Headers @{"Content-Type"="application/json"} -Body $body -UseBasicParsing

# Expected: returns 201 status and {"message":"Registration successful","parent_id":1}
```

### Test 3: Parent Login
```powershell
$body = @{username="testuser"; password="password123"} | ConvertTo-Json
Invoke-WebRequest -Uri http://localhost:5000/api/auth/parent/login `
  -Method POST -Headers @{"Content-Type"="application/json"} -Body $body -UseBasicParsing

# Expected: returns 200 status and access_token
```

More tests in [TESTING_REPORT.md](../TESTING_REPORT.md)

---

## 🐛 Troubleshooting

### Issue 1: Python Not Found
```
Error: 'python' is not recognized as an internal or external command
```
**Solution**:
- Windows: Make sure Python is added to PATH (check "Add Python to PATH" during installation)
- Try using `python3` instead of `python`

### Issue 2: Permission Denied (Virtual Environment Activation Failed)
```powershell
PS> .\venv\Scripts\Activate.ps1
Cannot load file ...\Activate.ps1 because running scripts is disabled on this system
```
**Solution**:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Issue 3: Port 5000 Already in Use
```
OSError: [Errno 48] Address already in use
```
**Solution**:
```bash
# Find the process using port 5000
# Linux/macOS:
lsof -i :5000

# Windows:
netstat -ano | findstr :5000

# Kill the process or use a different port
export FLASK_PORT=5001  # or set FLASK_PORT=5001 in .env
python app.py
```

### Issue 4: SQLAlchemy Error
```
ImportError: No module named 'sqlalchemy'
```
**Solution**:
1. Make sure the virtual environment is activated (prompt shows `(venv)`)
2. Reinstall dependencies:
```bash
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

### Issue 5: JWT Error
```
RuntimeError: You must initialize a JWTManager with this flask application
```
**Solution**:
- Make sure you are using the latest app.py (this issue has been fixed)
- Clear Python cache:
```bash
rm -rf __pycache__  # Linux/macOS
rmdir /s __pycache__  # Windows
python app.py
```

---

## 📁 Directory Structure Verification

After installation, your directory should look like this:

```
PianoAPPv1/
├── backend/
│   ├── venv/                 ✅ Virtual environment
│   ├── instance/
│   │   └── piano_app.db      ✅ SQLite database (created after first run)
│   ├── app.py                ✅ Flask app
│   ├── config.py             ✅ Config file
│   ├── models.py             ✅ Data models
│   ├── requirements.txt       ✅ Dependency list
│   ├── .env.example          ✅ Environment variable example
│   └── routes/
│       ├── auth.py
│       ├── practice.py
│       ├── awards.py
│       └── management.py
├── frontend/
├── database/
│   └── schema.sql
├── docs/
│   ├── API_REFERENCE.md
│   ├── DEPLOYMENT.md
│   ├── TIME_HANDLING.md
│   └── API_TESTING.md
├── README.md
├── QUICK_START.md
├── ARCHITECTURE.md
└── TESTING_REPORT.md
```

---

## 🚀 Next Steps

After installation:

1. ✅ **Test backend** - Run API tests: [API_TESTING.md](API_TESTING.md)
2. 🎨 **Frontend development** - Build the mobile app: [DEVELOPMENT.md](DEVELOPMENT.md)
3. 📦 **Deploy** - Production deployment: [DEPLOYMENT.md](DEPLOYMENT.md)

---

## 🆘 Getting Help

If you encounter issues:
1. See [TESTING_REPORT.md](../TESTING_REPORT.md) for verified features
2. See [API_REFERENCE.md](API_REFERENCE.md) for API details
3. Check log files in `backend/`

---

**Installation Version**: 1.0
**Last Updated**: 2026-03-22
**Tested On**: Python 3.13, Windows 10+, macOS 10.15+, Ubuntu 20.04+
