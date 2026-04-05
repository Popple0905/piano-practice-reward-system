# ⏰ Time Handling Documentation

## System Time Design

### Overview
The app uses a **local time** architecture to ensure recorded times match the user's actual practice time.

---

## Time Unit Specifications

### Practice Duration (`practice_minutes`)
- **Unit**: 15 minutes
- **Minimum**: 15 minutes
- **Validation**: Must be a multiple of 15 (15, 30, 45, 60...)
- **On violation**: API returns HTTP 400

**Backend validation code**:
```python
if data['practice_minutes'] % 15 != 0:
    return jsonify({'error': 'Practice duration must be in 15-minute increments'}), 400
```

### Reward Points (`game_minutes`)
- **Unit**: 15 minutes
- **Minimum**: 15 minutes
- **Validation**: Must be a multiple of 15 (15, 30, 45...)
- **On violation**: API returns HTTP 400

---

## Time Rounding Logic

### Rounding Rule
The system automatically rounds any submitted time to the nearest 5-minute boundary.

#### Rounding Examples
- **13:27** → **13:25** (round down)
- **13:28** → **13:30** (round up)
- **13:32** → **13:30** (round down)
- **13:33** → **13:35** (round up)

#### Special Case: Hour Boundary
- **13:57** → **14:00** (crosses hour boundary)
- **23:57** → **00:00** (crosses midnight)

### Frontend Time Rounding
```javascript
// Frontend auto-rounds (default value in input field)
const minutes = Math.round(now.getMinutes() / 5) * 5;
let hours = now.getHours();

if (minutes >= 60) {
    hours = (hours + 1) % 24;  // Handle midnight overflow
    minutes = 0;
}
```

### Backend Time Rounding
```python
# Backend rounds again (ensures consistency)
rounded_minutes = round(minutes / 5) * 5
hours = time_obj.hour

if rounded_minutes >= 60:
    hours = (hours + 1) % 24
    rounded_minutes = 0

record_time = time_obj.replace(hour=hours, minute=rounded_minutes, second=0, microsecond=0)
```

---

## Timezone Handling

### System Architecture
- **Frontend time**: Uses local time (browser timezone)
- **Backend time**: Stored as string (no timezone info)
- **Database**: SQLite TIME type (time only, no date)

### Time Submission Flow

#### Step 1: Frontend Collection
```javascript
// User-selected local time
const time = "14:33:00";  // HH:MM:SS format

// Send to backend
const payload = {
    date: "2026-03-22T00:00:00",
    time: "2000-01-01T14:33:00",  // Dummy date, actual time
    practice_minutes: 30
};
```

#### Step 2: Backend Processing
```python
# Backend receives and rounds
time_obj = datetime.fromisoformat("2000-01-01T14:33:00").time()
# → datetime.time(14, 33, 0)

# Round to 5 minutes
rounded_minutes = round(33 / 5) * 5  # = 35
# → datetime.time(14, 35, 0)

# Store to database
record.time = datetime.time(14, 35, 0)
```

#### Step 3: Return to Frontend
```json
{
  "time": "14:35:00",
  "date": "2026-03-22",
  "practice_minutes": 30
}
```

#### Step 4: Frontend Display
```javascript
// Time input shows only first 5 characters (HH:MM)
const displayTime = r.time.substring(0, 5);  // "14:35"
// Displays: "2026-03-22 14:35"
```

---

## API Time Parameters

### Time Field Types

| Field | Type | Format | Example | Description |
|-------|------|--------|---------|-------------|
| `date` | ISO string | `YYYY-MM-DD` | `2026-03-22` | Practice date |
| `time` | Time string | `HH:MM:SS` | `14:35:00` | Practice time (after rounding) |
| `created_at` | ISO timestamp | ISO 8601 | `2026-03-22T07:38:47.294249` | Record creation time |
| `approved_at` | ISO timestamp | ISO 8601 | `2026-03-22T13:45:20.123456` | Approval time |

### Time-Related Query Parameters

#### Query by Date Range
```bash
GET /api/practice/records/1?start_date=2026-03-01&end_date=2026-03-31
```

- **start_date**: `YYYY-MM-DD` format
- **end_date**: `YYYY-MM-DD` format
- **Returns**: All records within the date range

---

## Common Time Issues

### Issue 1: Frontend displays wrong time

**Symptom**: Submitted 14:33, displayed as 06:33

**Cause**: Timezone conversion error. Using `.toISOString()` converts to UTC.

**Solution**:
```javascript
// ❌ Wrong
body: JSON.stringify({
    date: new Date(date).toISOString(),  // Causes timezone conversion
    time: new Date(`2000-01-01T${time}`).toISOString()
})

// ✅ Correct
body: JSON.stringify({
    date: `${date}T00:00:00`,  // Keep as local time
    time: `2000-01-01T${time}:00`
})
```

### Issue 2: Time jumps after rounding

**Symptom**: Submitted 23:57, displayed as 00:00 (crosses day)

**Cause**: Hour overflow from rounding

**Expected behavior**: System handles correctly — does not change the date (23:57 rounds to 00:00 but stays on 2026-03-22, does not advance to 2026-03-23)

**Validation code**:
```python
# Rounding logic implemented correctly in practice.py
if rounded_minutes >= 60:
    hours = (hours + 1) % 24  # Prevent exceeding 23
    rounded_minutes = 0
```

### Issue 3: Cannot find expected records after submission

**Symptom**: Records submitted but not visible in query results

**Cause**: Frontend may not be loading all records correctly

**Debug steps**:
1. Open browser DevTools (F12)
2. Go to Console tab
3. Click the "Practice Records" tab
4. Check Console logs:
   ```
   📊 loadPracticeRecords data received: { records_array_length: 5, ... }
   📝 About to display 5 records
   ✅ Successfully rendered 5 records to page
   ```

---

## System Timezone Info

### Supported Timezones
The system uses the **browser's local timezone**, automatically detecting the user's region.

### Timezone Query
```javascript
// Run in browser Console
console.log(Intl.DateTimeFormat().resolvedOptions().timeZone);
// Example output: "Asia/Taipei" or "Asia/Hong_Kong"

console.log(new Date().getTimezoneOffset());
// Example output: -480 (UTC+08:00, negative means ahead of UTC)
```

---

## Developer Reference

### Time-Related File Locations

**Backend**:
- [backend/routes/practice.py](../backend/routes/practice.py) - Time rounding logic
  - `add_practice_record()` function, lines 35-49
- [backend/models.py](../backend/models.py) - `PracticeRecord` model
  - `time` field definition

**Frontend**:
- [frontend/index.html](../frontend/index.html) - Time handling code
  - `loadChildDashboard()` function
  - `submitPracticeRecord()` function
  - `loadPracticeRecords()` function

---

## Testing Time Features

### Manual Test Steps

1. **Test Rounding**
   - Login: Child ID 1, password: child123
   - Open "Log Practice" tab
   - Manually set time to 14:27 (not a 5-min multiple)
   - Submit, check if returned time is auto-rounded to 14:25 or 14:30

2. **Test Multiple Records**
   - Submit 3-5 records on different dates
   - Click "Practice Records" tab
   - Confirm Console shows `records_array_length: 5`
   - Confirm page displays all 5 records

3. **Test Timezone**
   - Open Console, run:
     ```javascript
     console.log(new Date().toString());
     console.log(Intl.DateTimeFormat().resolvedOptions().timeZone);
     ```
   - Confirm timezone matches system timezone

### API Test Script

```bash
# Submit time rounding test
curl -X POST http://localhost:5000/api/practice/record \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2026-03-22T00:00:00",
    "time": "2000-01-01T14:27:00",
    "practice_minutes": 30,
    "notes": "Rounding test"
  }'

# Expected returned time: "14:25:00" or "14:30:00"
```

---

## Update History

| Date | Change | Status |
|------|--------|--------|
| 2026-03-22 | Implemented time rounding (5-min units) | ✅ Done |
| 2026-03-22 | Fixed timezone conversion (local time) | ✅ Done |
| 2026-03-22 | Added Console debug logs | ✅ Done |
| TBD | Timezone selector (parent setting) | ⏳ Planned |
| TBD | Auto daylight saving time adjustment | ⏳ Planned |
