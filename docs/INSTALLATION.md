# 📥 完整安裝指南

## 準備工作

### 系統要求
- **操作系統**: Windows / macOS / Linux
- **Python**: 3.10 或更高版本
- **磁盤空間**: 至少 500MB （用於依賴包）
- **網絡**: 良好的網絡連接（用於下載依賴）

### 驗證環境
```bash
# 驗證 Python 版本
python --version
# 預期輸出: Python 3.x.x

# 驗證 pip 已安裝
pip --version
# 預期輸出: pip x.x.x from ...
```

---

## 🚀 快速安裝 (5分鐘)

### 步驟 1: 克隆或下載項目
```bash
# 使用 Git 克隆
git clone <repository-url>
cd PianoAPPv1

# 或直接下載 ZIP 文件並解壓
```

### 步驟 2: 進入後端目錄
```bash
cd backend
```

### 步驟 3: 創建虛擬環境
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

**驗證**: 命令提示符應該在開始處顯示 `(venv)`

### 步驟 4: 安裝依賴
```bash
pip install -r requirements.txt
```

**預期輸出**: 所有包應該成功安裝，無錯誤信息

### 步驟 5: 啟動服務器
```bash
python app.py
```

**預期輸出**:
```
 * Serving Flask app 'app'
 * Debug mode: off
 * Running on http://127.0.0.1:5000
 * Running on http://192.168.x.x:5000
Press CTRL+C to quit
```

✅ **完成！** 後端服務已在 `http://localhost:5000` 運行

---

## 🔧 詳細安裝步驟

### 方式 A: 使用 PowerShell (Windows)

```powershell
# 1. 進入項目目錄
cd "path\to\PianoAPPv1"

# 2. 進入後端目錄
cd backend

# 3. 創建虛擬環境
python -m venv venv

# 4. 激活虛擬環境
.\venv\Scripts\Activate.ps1
# 如果無法執行，可能需要更改執行策略:
# Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# 5. 安裝依賴
pip install --upgrade pip
pip install -r requirements.txt

# 6. 啟動服務器
python app.py
```

### 方式 B: 使用 Bash (macOS / Linux)

```bash
# 1. 進入項目目錄
cd ~/path/to/PianoAPPv1

# 2. 進入後端目錄
cd backend

# 3. 創建虛擬環境
python3 -m venv venv

# 4. 激活虛擬環境
source venv/bin/activate

# 5. 安裝依賴
pip install --upgrade pip
pip install -r requirements.txt

# 6. 啟動服務器
python app.py
```

---

## ⚙️ 配置

### 使用默認配置 (推薦用於開發)
無需額外配置，系統使用默認的 SQLite 數據庫。

### 自定義配置 (可選)

創建 `.env` 文件在 `backend/` 目錄:

```env
FLASK_ENV=development
FLASK_DEBUG=1
JWT_SECRET_KEY=your-custom-secret-key
```

將 `.env.example` 複製為 `.env`:
```bash
cp .env.example .env
```

然後編輯 `.env` 文件根據需要修改。

---

## 🗄️ 數據庫

### 本地開發 (SQLite)

✅ **自動設置**
- 數據庫自動在首次運行時創建
- 文件保存在 `backend/piano_app.db`
- 無需任何額外操作

檢查數據庫文件:
```bash
# 列出數據庫文件
ls backend/piano_app.db  # Linux/macOS
dir backend\piano_app.db  # Windows
```

### 生產環境 (MySQL)

#### 安裝 MySQL
- **Windows**: https://dev.mysql.com/downloads/mysql/
- **macOS**: `brew install mysql`
- **Linux**: `sudo apt-get install mysql-server`

#### 配置連接
修改 `.env` 文件:
```env
DATABASE_URL=mysql+pymysql://username:password@localhost:3306/piano_app
```

#### 初始化數據庫
```bash
# 1. 登錄 MySQL
mysql -u root -p

# 2. 在 MySQL 中執行
mysql> CREATE DATABASE piano_app;
mysql> USE piano_app;
mysql> source ../database/schema.sql;
mysql> exit;
```

或直接:
```bash
mysql -u root -p piano_app < ../database/schema.sql
```

---

## ✅ 驗證安裝

### 測試 1: 檢查服務器狀態
```bash
# 在新終端/PowerShell 運行
curl http://localhost:5000/api/auth/parent/register -X OPTIONS -v

# 預期: 返回 200 或 204 狀態碼
```

### 測試 2: 家長註冊
```powershell
# PowerShell
$body = @{username="testuser"; email="test@example.com"; password="password123"} | ConvertTo-Json
Invoke-WebRequest -Uri http://localhost:5000/api/auth/parent/register `
  -Method POST -Headers @{"Content-Type"="application/json"} -Body $body -UseBasicParsing

# 預期: 返回 201 狀態和 {"message":"註冊成功","parent_id":1}
```

### 測試 3: 家長登錄
```powershell
$body = @{username="testuser"; password="password123"} | ConvertTo-Json
Invoke-WebRequest -Uri http://localhost:5000/api/auth/parent/login `
  -Method POST -Headers @{"Content-Type"="application/json"} -Body $body -UseBasicParsing

# 預期: 返回 200 狀態和 access_token
```

更多測試見 [TESTING_REPORT.md](../TESTING_REPORT.md)

---

## 🐛 常見問題排查

### 問題 1: 找不到 Python
```
Error: 'python' is not recognized as an internal or external command
```
**解決方案**:
- Windows: 確保 Python 已添加到 PATH（安裝時勾選 "Add Python to PATH"）
- 嘗試使用 `python3` 代替 `python`

### 問題 2: 權限被拒絕 (激活虛擬環境失敗)
```powershell
PS> .\venv\Scripts\Activate.ps1
無法載入檔案 ...\Activate.ps1，因為系統上已停用指令碼執行
```
**解決方案**:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 問題 3: 埠 5000 已在使用
```
OSError: [Errno 48] Address already in use
```
**解決方案**:
```bash
# 找到使用埠 5000 的進程
# Linux/macOS:
lsof -i :5000

# Windows:
netstat -ano | findstr :5000

# 殺死進程或使用不同埠
export FLASK_PORT=5001  # 或在 .env 中設置 FLASK_PORT=5001
python app.py
```

### 問題 4: SQLAlchemy 錯誤
```
ImportError: No module named 'sqlalchemy'
```
**解決方案**:
1. 確保虛擬環境已激活 (命令提示符有 `(venv)`)
2. 重新安裝依賴:
```bash
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

### 問題 5: JWT 錯誤
```
RuntimeError: You must initialize a JWTManager with this flask application
```
**解決方案**:
- 確保使用最新的 app.py (已修復此問題)
- 清除 Python 緩存:
```bash
rm -rf __pycache__  # Linux/macOS
rmdir /s __pycache__  # Windows
python app.py
```

---

## 📁 目錄結構驗證

安裝完成後，您的目錄應如下所示:

```
PianoAPPv1/
├── backend/
│   ├── venv/                 ✅ 虛擬環境 
│   ├── app.py                ✅ Flask 應用
│   ├── config.py             ✅ 配置文件
│   ├── models.py             ✅ 數據模型
│   ├── requirements.txt       ✅ 依賴列表
│   ├── .env.example          ✅ 環境變數示例
│   ├── piano_app.db          ✅ SQLite 數據庫 (首次運行後創建)
│   └── routes/
│       ├── auth.py
│       ├── practice.py
│       └── awards.py
├── frontend/                 (稍後安裝)
├── database/
│   └── schema.sql
├── docs/
│   ├── API_REFERENCE.md
│   ├── DEPLOYMENT.md
│   └── API_TESTING.md
├── README.md
├── QUICK_START.md
├── ARCHITECTURE.md
└── TESTING_REPORT.md
```

---

## 🚀 下一步

安裝完成後:

1. ✅ **測試後端** - 運行 API 測試: [API_TESTING.md](API_TESTING.md)
2. 🎨 **前端開發** - 開始開發移動應用: [DEVELOPMENT.md](DEVELOPMENT.md)
3. 📦 **部署** - 準備生產部署: [DEPLOYMENT.md](DEPLOYMENT.md)

---

## 🆘 獲得幫助

如遇問題:
1. 查看 [TESTING_REPORT.md](../TESTING_REPORT.md) 了解已驗證的功能
2. 查看 [API_REFERENCE.md](API_REFERENCE.md) 了解 API 細節
3. 檢查 `backend/` 中的日誌文件

---

**安裝版本**: 1.0  
**最後更新**: 2026-03-22  
**測試環境**: Python 3.13, Windows 10+, macOS 10.15+, Ubuntu 20.04+
