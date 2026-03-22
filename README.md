# 練琴獎勵系統 (Piano App) 🎹

一個家長與孩子互動的練琴時間管理系統，讓孩子透過記錄每日練琴時間來賺取遊戲時間獎勵。

## ✨ 專案狀態

✅ **後端 API** - 完全功能（所有端點測試通過）
✅ **前端 Web** - 已實現（HTML5 + Vanilla JS，整合在後端）
✅ **子女儀表板** - 已實現（登入、記錄提交、多筆記錄查詢、遊戲餘額）
✅ **家長儀表板** - 已實現（孩子列表、待批准記錄、管理兒童帳號）
✅ **資料庫** - SQLite（開發）/ MySQL（生產）
✅ **認證系統** - JWT Token 認證
✅ **時間處理** - 5分鐘單位捨入、本地時區支援
✅ **功能測試** - 所有核心功能已驗證

**最新更新 (2026-03-23)**：
- ✅ 家長頁面「獎勵遊戲時間」改為「獎勵練琴點數」，全面以「獎勵點數」取代「遊戲時間」
- ✅ 兒童頁面整合「申請遊戲時間」與「遊戲時間」tab：餘額改為「練琴獎勵點數」顯示於暱稱下方，新增「獎勵兌換紀錄」tab
- ✅ 家長頁面新增「已批准紀錄」tab：顯示過去30天批准記錄，以兒童為單位分組
- ✅ 全新 UI 設計：Eevee 水彩淺色主題（暖琥珀 × 青色 × 深靛藍）
- ✅ 使用自訂 App Icon 作為網站 favicon 及 Apple touch icon
- ✅ 手機版排版優化（響應式 CSS 全面調整）
- ✅ 登入表單新增「記住帳號」功能（使用 localStorage 儲存憑證）
- ✅ 清除登入表單預設帳號密碼
- ✅ 移除前端測試用按鈕（查詢遊戲餘額、查詢練琴記錄）與 output box
- ✅ 修正兌換比例顯示格式（1.0 → 1）
- ✅ 家長帳號設定：登入後可修改自己的密碼
- ✅ 練琴時間單位改為15分鐘（預設15分鐘）
- ✅ 修復手機端無法登入問題（API URL 改為動態、ID 輸入停用自動大寫）
- ✅ 系統更名為「練琴獎勵系統」
- ✅ 兒童帳號 ID 支援英文字母與數字（最長20字元）
- ✅ 家長「管理兒童帳號」功能（新增 / 刪除 / 改名 / 改密碼）
- ✅ 前端介面全面更新為繁體中文

⏳ **下一步計劃**：練習目標設置、數據圖表視覺化

## 系統架構

```
PianoAPPv1/
├── backend/              # Python Flask REST API + 前端服務
│   ├── app.py            # Flask 應用入口（提供前端檔案和 API）
│   ├── config.py         # 設定管理
│   ├── models.py         # 資料庫模型
│   ├── requirements.txt  # Python 依賴套件
│   ├── routes/           # API 路由
│   │   ├── auth.py       # 認證端點
│   │   ├── practice.py   # 練琴記錄端點
│   │   ├── awards.py     # 遊戲獎勵端點
│   │   └── management.py # 兒童帳號管理端點
│   └── venv/             # Python 虛擬環境
├── frontend/             # 前端檔案（HTML5 + Vanilla JS）
│   ├── index.html        # Web 登入和儀表板介面
│   ├── apiClient.js      # API 客戶端
│   ├── services.js       # 業務邏輯
│   ├── ParentDashboard.js   # 家長控制面板（React Native）
│   └── ChildDashboard.js    # 孩子主頁面（React Native）
├── database/             # 資料庫檔案
│   └── schema.sql        # 資料庫結構
└── docs/                 # 文件
    ├── API_REFERENCE.md  # API 端點完整參考
    ├── INSTALLATION.md   # 安裝和故障排除
    ├── API_TESTING.md    # 測試腳本
    └── DEPLOYMENT.md     # 部署指南
```

## 功能模組

### 1. 認證系統 (Authentication)
- ✅ 孩子登入（支援多帳號，ID 支援英數字）
- ✅ 家長登入／註冊
- ✅ 家長修改登入密碼
- ✅ JWT Token 認證

### 2. 練琴記錄 (Practice Tracking)
- ✅ 孩子新增練琴時間（15分鐘單位，預設15分鐘）
- ✅ 查看多筆練琴歷史記錄
- ✅ 時間捨入處理（本地時間自動調整）
- ✅ 狀態管理（待審核 / 已批准 / 已拒絕）
- ✅ 家長批准／拒絕練琴記錄

### 3. 遊戲獎勵系統 (Game Rewards)
- ✅ 孩子查看遊戲時間餘額
- ✅ 遊戲時間申請（15分鐘單位）
- ✅ 兌換比例設定
- ✅ 家長發放遊戲時間

### 4. 兒童帳號管理 (Child Account Management)
- ✅ 家長新增兒童帳號（姓名、密碼、年齡）
- ✅ 家長刪除兒童帳號
- ✅ 家長修改兒童名稱
- ✅ 家長修改兒童密碼

## 🚀 快速開始 (5 分鐘)

### 1. 準備環境

```bash
cd PianoAPPv1/backend
pip install -r requirements.txt
```

### 2. 啟動伺服器

```bash
python app.py
```

✅ 伺服器啟動在 `http://localhost:5000`
✅ SQLite 資料庫自動建立在 `backend/instance/`
✅ 首次執行：需要初始化測試帳號

### 3. 初始化測試帳號（首次執行）

```bash
# 在 backend 目錄執行
python init_db.py
```

**自動建立的測試帳號：**
- 子女：ID `1`，密碼 `child123`，名稱 "Test Child"

### 環境變數設定（選填）

建立 `.env` 檔案自訂設定：
```
FLASK_ENV=development
JWT_SECRET_KEY=your-secret-key-change-in-production
DATABASE_URL=sqlite:///piano_app.db
```

## API 端點

### 認證 (/api/auth)
- `POST /parent/register` - 家長註冊
- `POST /parent/login` - 家長登入
- `POST /parent/change-password` - 家長修改密碼
- `POST /child/register` - 孩子註冊
- `POST /child/login` - 孩子登入
- `GET /parent/me` - 取得家長資訊

### 練琴 (/api/practice)
- `POST /record` - 新增練琴記錄
- `POST /record/<id>/approve` - 批准練琴記錄
- `POST /record/<id>/reject` - 拒絕練琴記錄
- `GET /records/<child_id>` - 取得練琴記錄
- `GET /statistics/<child_id>` - 取得統計資料
- `GET /parent/children` - 取得所有孩子列表與統計

### 獎勵 (/api/awards)
- `POST /give` - 發放遊戲時間
- `POST /request` - 申請使用遊戲時間
- `GET /balance/<child_id>` - 取得遊戲時間餘額
- `GET /history/<child_id>` - 取得獎勵歷史
- `GET /request-history/<child_id>` - 取得申請歷史
- `GET /ratio` - 取得兌換比例
- `POST /ratio` - 設定兌換比例

### 兒童帳號管理 (/api/management)
- `POST /create-child` - 建立孩子帳號
- `DELETE /delete-child/<child_id>` - 刪除孩子帳號
- `POST /update-child-password/<child_id>` - 修改孩子密碼
- `POST /update-child-name/<child_id>` - 修改孩子名稱
- `POST /update-child-age/<child_id>` - 修改孩子年齡

## 資料模型

### Parent（家長）
```
- id: 唯一識別碼
- username: 使用者名稱
- email: 電子郵件
- password_hash: 密碼雜湊
- practice_to_game_ratio: 練琴換遊戲時間比例
- created_at: 建立時間
```

### Child（孩子）
```
- id: 唯一識別碼
- parent_id: 所屬家長
- name: 名稱
- age: 年齡
- password_hash: 密碼雜湊
- game_balance: 遊戲時間餘額（分鐘）
- created_at: 建立時間
```

### PracticeRecord（練琴記錄）
```
- id: 唯一識別碼
- child_id: 所屬孩子
- date: 練琴日期
- time: 練琴時間
- practice_minutes: 練琴時間（分鐘，以5分鐘為單位）
- notes: 備註
- status: 狀態（pending / approved / rejected）
- created_at: 建立時間
- approved_at: 批准時間
```

### GameAward（遊戲時間獎勵）
```
- id: 唯一識別碼
- parent_id: 發放家長
- child_id: 接收孩子
- game_minutes: 獎勵時間（分鐘）
- reason: 原因
- created_at: 建立時間
```

### GameRequest（遊戲時間申請）
```
- id: 唯一識別碼
- child_id: 所屬孩子
- game_minutes: 申請時間（分鐘，以15分鐘為單位）
- request_date: 申請時間
- status: 狀態（approved）
- created_at: 建立時間
```

## 🔧 測試狀態

✅ **後端 API 已完全測試並通過所有測試**

**已驗證功能**：
- ✅ 家長註冊／登入
- ✅ 孩子登入
- ✅ 兒童帳號管理（新增、刪除、改名、改密碼）
- ✅ 練琴記錄新增和查詢
- ✅ 遊戲時間發放和查詢
- ✅ JWT 認證和權限控制
- ✅ 資料庫持久化

## 📊 資料庫說明

### 本地開發（預設）
- 使用 SQLite (piano_app.db)
- 無需安裝 MySQL
- 資料自動持久化到檔案

### 生產環境
- 支援設定為 MySQL 8.0+
- 修改 config.py 中的 DATABASE_URL
- 或透過環境變數設定：`DATABASE_URL=mysql+pymysql://user:password@localhost/piano_app`

## 安全考量

1. 在生產環境中修改 `JWT_SECRET_KEY`
2. 使用 HTTPS 加密通訊
3. 定期更新依賴套件
4. 驗證所有輸入資料
5. 實作速率限制防止暴力攻擊
6. 定期備份資料庫
7. 輸入驗證和 SQL 注入防護

## 後續功能規劃

- [ ] 電子郵件通知（練琴提醒、獎勵通知）
- [ ] 練琴時間匯出（PDF/Excel）
- [ ] 多帳號管理（多個孩子）
- [ ] 推播通知功能
- [ ] 練琴目標設置和進度追蹤
- [ ] 成績排行榜
- [ ] 資料視覺化圖表

## 技術棧

- **後端**：Python 3.8+、Flask、SQLAlchemy、SQLite／MySQL
- **認證**：JWT（Flask-JWT-Extended）
- **前端**：HTML5 + Vanilla JS（Web）／React Native（行動端）
- **API**：RESTful

## 開發者

Created for managing children's piano practice and game time rewards.

## License

MIT License
