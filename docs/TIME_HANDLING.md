# ⏰ 時間處理說明文檔

## 系統時間設計

### 概述
音樂APP 採用**本地時間**架構，確保時間記錄與用戶實際練琴時間一致。

---

## 時間單位規範

### 練琴時間（`practice_minutes`）
- **單位**: 5 分鐘
- **最小值**: 5 分鐘
- **驗證**: 必須是 5 的倍數（5, 10, 15, 20...）
- **違反時的行為**: API 返回 HTTP 400 錯誤

**後端驗證代碼**:
```python
if record.practice_minutes % 5 != 0:
    return jsonify({'error': '练琴时间必须以5分钟为单位'}), 400
```

### 遊戲時間（`game_minutes`）
- **單位**: 15 分鐘
- **最小值**: 15 分鐘
- **驗證**: 必須是 15 的倍數（15, 30, 45...）
- **違反時的行為**: API 返回 HTTP 400 錯誤

---

## 時間舍入邏輯

### 舍入規則
系統自動將**任意時間**舍入到**最近的 5 分鐘邊界**。

#### 舍入規則詳情
- **13:27** → **13:25** (向下舍入)
- **13:28** → **13:30** (向上舍入)
- **13:32** → **13:30** (向下舍入)
- **13:33** → **13:35** (向上舍入)

#### 特殊情況：小時邊界
- **13:57** → **14:00** (跨越小時邊界)
- **23:57** → **00:00** (跨越午夜)

### 前端時間舍入
```javascript
// 前端自動舍入（用戶輸入框預設值）
const minutes = Math.round(now.getMinutes() / 5) * 5;
let hours = now.getHours();

if (minutes >= 60) {
    hours = (hours + 1) % 24;  // 處理午夜溢出
    minutes = 0;
}
```

### 後端時間舍入
```python
# 後端再次舍入（確保一致性）
rounded_minutes = round(minutes / 5) * 5
hours = time_obj.hour

if rounded_minutes >= 60:
    hours = (hours + 1) % 24
    rounded_minutes = 0

record_time = time_obj.replace(hour=hours, minute=rounded_minutes, second=0, microsecond=0)
```

---

## 時區處理

### 系統架構
- **前端時間**: 使用本地時間（瀏覽器時區）
- **後端時間**: 以字符串格式存儲（無時區信息）
- **數據庫**: SQLite TIME 類型（純時間，無日期）

### 時間提交流程

#### 步驟 1: 前端收集
```javascript
// 用戶選擇的本地時間
const time = "14:33:00";  // HH:MM:SS 格式

// 發送給後端
const payload = {
    date: "2026-03-22T00:00:00",
    time: "2000-01-01T14:33:00",  // 假日期，實際時間
    practice_minutes: 30
};
```

#### 步驟 2: 後端處理
```python
# 後端收到並舍入
time_obj = datetime.fromisoformat("2000-01-01T14:33:00").time()
# → datetime.time(14, 33, 0)

# 舍入到 5 分鐘
rounded_minutes = round(33 / 5) * 5  # = 35
# → datetime.time(14, 35, 0)

# 存儲到數據庫
record.time = datetime.time(14, 35, 0)
```

#### 步驟 3: 返回給前端
```json
{
  "time": "14:35:00",
  "date": "2026-03-22",
  "practice_minutes": 30
}
```

#### 步驟 4: 前端顯示
```javascript
// 時間輸入框只取前 5 個字符（HH:MM）
const displayTime = r.time.substring(0, 5);  // "14:35"
// 顯示: "2026-03-22 14:35"
```

---

## API 時間參數

### 時間欄位類型

| 欄位 | 類型 | 格式 | 示例 | 說明 |
|------|------|------|------|------|
| `date` | ISO 字符串 | `YYYY-MM-DD` | `2026-03-22` | 練琴日期 |
| `time` | 時間字符串 | `HH:MM:SS` | `14:35:00` | 練琴時間（已舍入） |
| `created_at` | ISO 時間戳 | ISO 8601 | `2026-03-22T07:38:47.294249` | 紀錄建立時間 |
| `approved_at` | ISO 時間戳 | ISO 8601 | `2026-03-22T13:45:20.123456` | 批准時間 |

### 時間相關的查詢參數

#### 查詢時間範圍
```bash
GET /api/practice/records/1?start_date=2026-03-01&end_date=2026-03-31
```

- **start_date**: `YYYY-MM-DD` 格式
- **end_date**: `YYYY-MM-DD` 格式
- **返回**: 在此日期範圍內的所有紀錄

---

## 常見時間問題

### 問題 1: 前端顯示時間不對

**症狀**: 提交 14:33，顯示卻是 06:33

**原因**: 時區轉換錯誤。如果使用 `.toISOString()` 會轉成 UTC

**解決方案**:
```javascript
// ❌ 錯誤
body: JSON.stringify({
    date: new Date(date).toISOString(),  // 導致時區轉換
    time: new Date(`2000-01-01T${time}`).toISOString()
})

// ✅ 正確
body: JSON.stringify({
    date: `${date}T00:00:00`,  // 保持本地時間
    time: `2000-01-01T${time}:00`
})
```

### 問題 2: 舍入後時間跳變

**症狀**: 提交 23:57，顯示變成 00:00（跨日期）

**原因**: 舍入導致小時溢出

**預期行為**: 系統正確處理，不改變日期（23:57 應該舍入為 00:00，但停留在 2026-03-22，不會自動推進到 2026-03-23）

**驗證代碼**:
```python
# 舍入邏輯已在 practice.py 中正確實現
if rounded_minutes >= 60:
    hours = (hours + 1) % 24  # 防止超過 23
    rounded_minutes = 0
```

### 問題 3: 查詢不到預期的紀錄

**症狀**: 提交紀錄後檢查查詢結果，卻沒看到

**原因**: 前端可能未正確加載所有紀錄

**調試步驟**:
1. 打開瀏覽器 DevTools (F12) 
2. 進入 Console 標籤
3. 點擊「練琴紀錄」標籤
4. 查看 Console 日誌：
   ```
   📊 loadPracticeRecords 收到的數據: { records_array_length: 5, ... }
   📝 即將顯示 5 筆記錄
   ✅ 成功渲染 5 筆記錄到頁面
   ```

---

## 系統時區信息

### 支持的時區
系統使用**瀏覽器本地時區**，自動檢測用戶所在地區。

### 時區偏移查詢
```javascript
// 在瀏覽器 Console 中執行
console.log(Intl.DateTimeFormat().resolvedOptions().timeZone);
// 輸出示例: "Asia/Taipei" 或 "Asia/Hong_Kong"

console.log(new Date().getTimezoneOffset());
// 輸出示例: -480 (UTC+08:00, 負數表示領先 UTC)
```

---

## 開發參考

### 時間相關的檔案位置

**後端**:
- [backend/routes/practice.py](../backend/routes/practice.py) - 時間舍入邏輯
  - `add_practice_record()` 函數，行 35-49
- [backend/models.py](../backend/models.py) - `PracticeRecord` 模型
  - `time` 欄位定義

**前端**:
- [frontend/index.html](../frontend/index.html) - 時間處理代碼
  - `loadChildDashboard()` 函數（行 879-910）
  - `submitPracticeRecord()` 函數（行 968-1000）
  - `loadPracticeRecords()` 函數（行 1010-1045）

---

## 測試時間功能

### 手動測試步驟

1. **測試舍入功能**
   - 登入：Child ID 1, 密碼: child123
   - 打開「登錄練琴」標籤
   - 手動設置時間為 14:27 (不是 5 分鐘倍數)
   - 提交，檢查返回時間是否自動舍入為 14:25 或 14:30

2. **測試多紀錄查詢**
   - 提交 3-5 筆不同日期的紀錄
   - 點擊「練琴紀錄」標籤
   - 確認 Console 顯示 `records_array_length: 5`
   - 確認頁面顯示全部 5 筆紀錄

3. **測試時區**
   - 打開 Console，執行：
     ```javascript
     console.log(new Date().toString());
     console.log(Intl.DateTimeFormat().resolvedOptions().timeZone);
     ```
   - 確認時區與系統時區相符

### API 測試腳本

```bash
# 提交時間舍入測試
curl -X POST http://localhost:5000/api/practice/record \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2026-03-22T00:00:00",
    "time": "2000-01-01T14:27:00",
    "practice_minutes": 30,
    "notes": "舍入測試"
  }'

# 預期返回時間: "14:25:00" 或 "14:30:00"
```

---

## 更新歷史

| 日期 | 變更 | 狀態 |
|------|------|------|
| 2026-03-22 | 實裝時間舍入邏輯（5分鐘單位） | ✅ 完成 |
| 2026-03-22 | 修復時區轉換問題（本地時間） | ✅ 完成 |
| 2026-03-22 | 添加 Console 調試日誌 | ✅ 完成 |
| 待定 | 時區選擇器（家長設置） | ⏳ 計劃中 |
| 待定 | 自動夏令時調整 | ⏳ 計劃中 |
