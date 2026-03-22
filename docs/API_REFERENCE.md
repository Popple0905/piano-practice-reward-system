# 🧪 API 快速參考指南

## 📌 基礎資訊

- **服務器地址**: http://localhost:5000
- **API前綴**: /api
- **認證方式**: Bearer Token (JWT)
- **內容類型**: application/json

---

## 🔐 認證端點 (/api/auth)

### 家長註冊
```http
POST /api/auth/parent/register
Content-Type: application/json

{
  "username": "parent1",
  "email": "parent@example.com",
  "password": "password123"
}

Response (201):
{
  "message": "註冊成功",
  "parent_id": 1
}
```

### 家長登錄
```http
POST /api/auth/parent/login
Content-Type: application/json

{
  "username": "parent1",
  "password": "password123"
}

Response (200):
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "parent_id": 1,
  "username": "parent1"
}
```

### 孩子註冊
```http
POST /api/auth/child/register
Content-Type: application/json

{
  "parent_id": 1,
  "name": "小明",
  "age": 8,
  "password": "child123"
}

Response (201):
{
  "message": "孩子帳戶創建成功",
  "child_id": 1
}
```

### 孩子登錄
```http
POST /api/auth/child/login
Content-Type: application/json

{
  "child_id": 1,
  "password": "child123"
}

Response (200):
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "child_id": 1,
  "name": "小明"
}
```

---

## 🎹 練琴記錄端點 (/api/practice)

### 添加練琴記錄
```http
POST /api/practice/record
Authorization: Bearer {child_token}
Content-Type: application/json

{
  "date": "2026-03-22",
  "practice_minutes": 60,
  "notes": "練習鋼琴基礎課程"
}

Response (201):
{
  "message": "練琴記錄已保存",
  "date": "2026-03-22",
  "practice_minutes": 60
}
```

### 查詢練琴記錄
```http
GET /api/practice/records/{child_id}
Authorization: Bearer {token}

Query Parameters:
- start_date: 開始日期 (可選)
- end_date: 結束日期 (可選)

Response (200):
{
  "child_id": 1,
  "child_name": "小明",
  "total_records": 5,
  "total_minutes": 300,
  "records": [
    {
      "id": 1,
      "date": "2026-03-22",
      "practice_minutes": 60,
      "notes": "練習基礎課程"
    }
  ]
}
```

### 獲取統計數據
```http
GET /api/practice/statistics/{child_id}
Authorization: Bearer {token}

Query Parameters:
- period: week / month / year (默認: month)

Response (200):
{
  "child_id": 1,
  "child_name": "小明",
  "period": "month",
  "total_minutes": 300,
  "average_daily": 60.0,
  "days_practiced": 5
}
```

---

## 🎁 遊戲獎勵端點 (/api/awards)

### 發放遊戲時間
```http
POST /api/awards/give
Authorization: Bearer {parent_token}
Content-Type: application/json

{
  "child_id": 1,
  "game_minutes": 30,
  "reason": "完成練琴目標"
}

Response (201):
{
  "message": "遊戲時間已發放",
  "child_id": 1,
  "game_minutes": 30,
  "new_balance": 30
}
```

### 使用遊戲時間
```http
POST /api/awards/deduct
Authorization: Bearer {child_token}
Content-Type: application/json

{
  "game_minutes": 15
}

Response (200):
{
  "message": "遊戲時間已使用",
  "used_minutes": 15,
  "remaining_balance": 15
}
```

### 查詢遊戲時間餘額
```http
GET /api/awards/balance/{child_id}
Authorization: Bearer {token}

Response (200):
{
  "child_id": 1,
  "child_name": "小明",
  "game_balance": 30
}
```

### 查詢獎勵歷史
```http
GET /api/awards/history/{child_id}
Authorization: Bearer {token}

Response (200):
{
  "child_id": 1,
  "child_name": "小明",
  "total_awards": 3,
  "total_minutes_given": 90,
  "awards": [
    {
      "id": 1,
      "game_minutes": 30,
      "reason": "完成練琴目標",
      "created_at": "2026-03-22T10:30:00"
    }
  ]
}
```

---

## 🔒 HTTP 狀態碼

| 狀態碼 | 說明 | 示例 |
|--------|------|------|
| 200 | 成功 | GET 請求成功 |
| 201 | 創建成功 | POST 創建新記錄 |
| 400 | 請求錯誤 | 缺少必要字段 |
| 401 | 未授權 | 無效的Token |
| 403 | 禁止訪問 | 權限不足 |
| 404 | 未找到 | 資源不存在 |
| 500 | 服務器錯誤 | 數據庫連接失敗 |

---

## 📊 錯誤響應示例

### 缺少字段
```json
{
  "error": "缺少必要字段"
}
```

### 無效的Token
```json
{
  "msg": "Token 無效或已過期"
}
```

### 權限不足
```json
{
  "error": "權限不足"
}
```

### 遊戲時間不足
```json
{
  "error": "遊戲時間不足",
  "current_balance": 10,
  "requested": 20
}
```

---

## 🧪 測試示例 (PowerShell)

### 完整測試流程

```powershell
# 1. 家長登錄
$parentBody = @{username="parent1"; password="password123"} | ConvertTo-Json
$parentLogin = Invoke-WebRequest `
  -Uri http://localhost:5000/api/auth/parent/login `
  -Method POST `
  -Headers @{"Content-Type"="application/json"} `
  -Body $parentBody -UseBasicParsing | ConvertFrom-Json
$parentToken = $parentLogin.access_token

# 2. 孩子登錄
$childBody = @{child_id=1; password="child123"} | ConvertTo-Json
$childLogin = Invoke-WebRequest `
  -Uri http://localhost:5000/api/auth/child/login `
  -Method POST `
  -Headers @{"Content-Type"="application/json"} `
  -Body $childBody -UseBasicParsing | ConvertFrom-Json
$childToken = $childLogin.access_token

# 3. 添加練琴記錄
$practiceBody = @{
  date=(Get-Date).ToString("yyyy-MM-dd")
  practice_minutes=60
  notes="練習基礎課程"
} | ConvertTo-Json

Invoke-WebRequest `
  -Uri http://localhost:5000/api/practice/record `
  -Method POST `
  -Headers @{
    "Content-Type"="application/json"
    "Authorization"="Bearer $childToken"
  } `
  -Body $practiceBody -UseBasicParsing

# 4. 查詢遊戲餘額
Invoke-WebRequest `
  -Uri http://localhost:5000/api/awards/balance/1 `
  -Method GET `
  -Headers @{"Authorization"="Bearer $childToken"} `
  -UseBasicParsing | ConvertFrom-Json

# 5. 發放遊戲時間
$awardBody = @{
  child_id=1
  game_minutes=30
  reason="完成練琴目標"
} | ConvertTo-Json

Invoke-WebRequest `
  -Uri http://localhost:5000/api/awards/give `
  -Method POST `
  -Headers @{
    "Content-Type"="application/json"
    "Authorization"="Bearer $parentToken"
  } `
  -Body $awardBody -UseBasicParsing
```

---

## 💡 常見問題

### Q: Token 已過期怎麼辦？
**A**: 使用登錄端點重新獲取新 Token, 舊 Token 將失效。

### Q: 如何修改已保存的練琴記錄？
**A**: 使用相同日期調用 `POST /api/practice/record` 端點，系統將自動更新。

### Q: 孩子可以自己發放遊戲時間嗎？
**A**: 不可以，只有家長才能發放遊戲時間。

### Q: 一個家長可以管理多個孩子嗎？
**A**: 是的，家長可以註冊多個孩子帳戶。

---

**Last Updated**: 2026-03-22  
**API Version**: 1.0
