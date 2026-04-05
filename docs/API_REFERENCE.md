# 🧪 API Quick Reference

## 📌 Base Information

- **Server**: http://localhost:5000
- **API Prefix**: /api
- **Authentication**: Bearer Token (JWT)
- **Content Type**: application/json

---

## 🔐 Authentication Endpoints (/api/auth)

### Register Parent
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
  "message": "Registration successful",
  "parent_id": 1
}
```

### Parent Login
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

### Register Child
```http
POST /api/auth/child/register
Content-Type: application/json

{
  "parent_id": 1,
  "name": "Xiao Ming",
  "age": 8,
  "password": "child123"
}

Response (201):
{
  "message": "Child account created successfully",
  "child_id": 1
}
```

### Child Login
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
  "name": "Xiao Ming"
}
```

---

## 🎹 Practice Record Endpoints (/api/practice)

### Add Practice Record
```http
POST /api/practice/record
Authorization: Bearer {child_token}
Content-Type: application/json

{
  "date": "2026-03-22",
  "practice_minutes": 60,
  "notes": "Practiced piano basics"
}

Response (201):
{
  "message": "Practice record submitted, awaiting parent approval",
  "date": "2026-03-22",
  "practice_minutes": 60
}
```

### Query Practice Records
```http
GET /api/practice/records/{child_id}
Authorization: Bearer {token}

Query Parameters:
- start_date: start date (optional)
- end_date: end date (optional)
- status: pending / approved / rejected (optional)

Response (200):
{
  "child_id": 1,
  "child_name": "Xiao Ming",
  "total_records": 5,
  "approved_records": 3,
  "pending_records": 2,
  "total_approved_minutes": 300,
  "records": [
    {
      "id": 1,
      "date": "2026-03-22",
      "time": "14:35:00",
      "practice_minutes": 60,
      "status": "approved",
      "notes": "Practiced basics",
      "created_at": "2026-03-22T07:38:47",
      "approved_at": "2026-03-22T13:45:20"
    }
  ]
}
```

### Get Statistics
```http
GET /api/practice/statistics/{child_id}
Authorization: Bearer {token}

Response (200):
{
  "child_id": 1,
  "total_approved_minutes": 300,
  "average_daily": 60.0,
  "days_practiced": 5
}
```

### Approve Practice Record
```http
POST /api/practice/record/{record_id}/approve
Authorization: Bearer {parent_token}

Response (200):
{
  "message": "Practice record approved",
  "record_id": 1,
  "practice_minutes": 60,
  "game_minutes_earned": 60,
  "child_new_balance": 120
}
```

### Reject Practice Record
```http
POST /api/practice/record/{record_id}/reject
Authorization: Bearer {parent_token}

Response (200):
{
  "message": "Practice record rejected",
  "record_id": 1
}
```

### Get All Children (Parent)
```http
GET /api/practice/parent/children
Authorization: Bearer {parent_token}

Response (200):
{
  "parent_id": 1,
  "parent_username": "parent1",
  "practice_to_game_ratio": 1.0,
  "children_count": 2,
  "children": [...]
}
```

---

## 🎁 Reward Points Endpoints (/api/awards)

### Grant Reward Points
```http
POST /api/awards/give
Authorization: Bearer {parent_token}
Content-Type: application/json

{
  "child_id": 1,
  "game_minutes": 30,
  "reason": "Completed practice goal"
}

Response (201):
{
  "message": "Reward points granted",
  "child_id": 1,
  "game_minutes": 30,
  "new_balance": 30
}
```

### Redeem Reward Points
```http
POST /api/awards/request
Authorization: Bearer {child_token}
Content-Type: application/json

{
  "game_minutes": 15
}

Response (200):
{
  "message": "Reward points redeemed successfully",
  "game_minutes_used": 15,
  "remaining_balance": 15,
  "request_id": 1,
  "request_time": "2026-03-22T10:30:00"
}
```

### Query Reward Points Balance
```http
GET /api/awards/balance/{child_id}
Authorization: Bearer {token}

Response (200):
{
  "child_id": 1,
  "child_name": "Xiao Ming",
  "game_balance": 30,
  "practice_to_game_ratio": 1.0
}
```

### Query Award History
```http
GET /api/awards/history/{child_id}
Authorization: Bearer {token}

Response (200):
{
  "child_id": 1,
  "child_name": "Xiao Ming",
  "total_awards": 3,
  "total_minutes_given": 90,
  "awards": [
    {
      "id": 1,
      "game_minutes": 30,
      "reason": "Completed practice goal",
      "created_at": "2026-03-22T10:30:00"
    }
  ]
}
```

### Query Redemption History
```http
GET /api/awards/request-history/{child_id}
Authorization: Bearer {token}

Response (200):
{
  "child_id": 1,
  "child_name": "Xiao Ming",
  "total_requests": 2,
  "total_minutes_used": 30,
  "requests": [...]
}
```

### Get Conversion Ratio
```http
GET /api/awards/ratio
Authorization: Bearer {token}

Response (200):
{
  "practice_to_game_ratio": 1.0,
  "description": "1 min practice = 1 reward point(s)"
}
```

### Set Conversion Ratio
```http
POST /api/awards/ratio
Authorization: Bearer {parent_token}
Content-Type: application/json

{
  "ratio": 1.5
}

Response (200):
{
  "message": "Conversion ratio updated",
  "new_ratio": 1.5,
  "description": "1 min practice = 1.5 reward point(s)"
}
```

---

## 👶 Child Account Management (/api/management)

### Create Child Account
```http
POST /api/management/create-child
Authorization: Bearer {parent_token}
Content-Type: application/json

{
  "name": "Xiao Ming",
  "password": "child123",
  "age": 8,
  "id": "xiaoming"  // optional custom ID (alphanumeric, 1-20 chars)
}

Response (201):
{
  "message": "Child account created",
  "child_id": "xiaoming",
  "name": "Xiao Ming",
  "age": 8,
  "created_at": "2026-03-22T10:00:00"
}
```

### Delete Child Account
```http
DELETE /api/management/delete-child/{child_id}
Authorization: Bearer {parent_token}

Response (200):
{
  "message": "Child account \"Xiao Ming\" deleted",
  "child_id": "xiaoming"
}
```

### Update Child Password
```http
POST /api/management/update-child-password/{child_id}
Authorization: Bearer {parent_token}
Content-Type: application/json

{
  "new_password": "newpassword123"
}

Response (200):
{
  "message": "Password for Xiao Ming updated",
  "child_id": "xiaoming",
  "child_name": "Xiao Ming"
}
```

### Update Child Name
```http
POST /api/management/update-child-name/{child_id}
Authorization: Bearer {parent_token}
Content-Type: application/json

{
  "new_name": "Xiao Hong"
}

Response (200):
{
  "message": "Child name updated from \"Xiao Ming\" to \"Xiao Hong\"",
  "child_id": "xiaoming",
  "child_name": "Xiao Hong"
}
```

### Update Child Age
```http
POST /api/management/update-child-age/{child_id}
Authorization: Bearer {parent_token}
Content-Type: application/json

{
  "age": 9
}

Response (200):
{
  "message": "Age for Xiao Ming updated to 9",
  "child_id": "xiaoming",
  "child_name": "Xiao Ming",
  "age": 9
}
```

---

## 🔒 HTTP Status Codes

| Code | Meaning | Example |
|------|---------|---------|
| 200 | Success | GET request successful |
| 201 | Created | POST created new record |
| 400 | Bad Request | Missing required fields |
| 401 | Unauthorized | Invalid Token |
| 403 | Forbidden | Permission denied |
| 404 | Not Found | Resource does not exist |
| 500 | Server Error | Database connection failed |

---

## 📊 Error Response Examples

### Missing Fields
```json
{
  "error": "Missing required fields"
}
```

### Invalid Token
```json
{
  "msg": "Token is invalid or expired"
}
```

### Permission Denied
```json
{
  "error": "Permission denied"
}
```

### Insufficient Reward Points
```json
{
  "error": "Insufficient reward points",
  "current_balance": 10,
  "requested": 20
}
```

---

## 🧪 Test Examples (PowerShell)

### Complete Test Flow

```powershell
# 1. Parent login
$parentBody = @{username="parent1"; password="password123"} | ConvertTo-Json
$parentLogin = Invoke-WebRequest `
  -Uri http://localhost:5000/api/auth/parent/login `
  -Method POST `
  -Headers @{"Content-Type"="application/json"} `
  -Body $parentBody -UseBasicParsing | ConvertFrom-Json
$parentToken = $parentLogin.access_token

# 2. Child login
$childBody = @{child_id=1; password="child123"} | ConvertTo-Json
$childLogin = Invoke-WebRequest `
  -Uri http://localhost:5000/api/auth/child/login `
  -Method POST `
  -Headers @{"Content-Type"="application/json"} `
  -Body $childBody -UseBasicParsing | ConvertFrom-Json
$childToken = $childLogin.access_token

# 3. Add practice record
$practiceBody = @{
  date=(Get-Date).ToString("yyyy-MM-dd")
  practice_minutes=60
  notes="Practiced basics"
} | ConvertTo-Json

Invoke-WebRequest `
  -Uri http://localhost:5000/api/practice/record `
  -Method POST `
  -Headers @{
    "Content-Type"="application/json"
    "Authorization"="Bearer $childToken"
  } `
  -Body $practiceBody -UseBasicParsing

# 4. Query reward points balance
Invoke-WebRequest `
  -Uri http://localhost:5000/api/awards/balance/1 `
  -Method GET `
  -Headers @{"Authorization"="Bearer $childToken"} `
  -UseBasicParsing | ConvertFrom-Json

# 5. Grant reward points
$awardBody = @{
  child_id=1
  game_minutes=30
  reason="Completed practice goal"
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

## 💡 FAQ

### Q: What should I do if my Token has expired?
**A**: Use the login endpoint to get a new Token. The old Token will be invalid.

### Q: How do I modify a saved practice record?
**A**: Call `POST /api/practice/record` with the same date. The system will automatically update it.

### Q: Can a child grant themselves reward points?
**A**: No. Only parents can grant reward points.

### Q: Can one parent manage multiple children?
**A**: Yes. A parent can create and manage multiple child accounts.

---

**Last Updated**: 2026-03-22
**API Version**: 1.0
