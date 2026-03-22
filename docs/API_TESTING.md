# API 测试脚本

## 1. 家长注册
```bash
curl -X POST http://localhost:5000/api/auth/parent/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "parent1",
    "email": "parent@example.com",
    "password": "password123"
  }'
```

## 2. 家长登录
```bash
curl -X POST http://localhost:5000/api/auth/parent/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "parent1",
    "password": "password123"
  }'
```

## 3. 孩子注册
```bash
curl -X POST http://localhost:5000/api/auth/child/register \
  -H "Content-Type: application/json" \
  -d '{
    "parent_id": 1,
    "name": "小明",
    "age": 8,
    "password": "child123"
  }'
```

## 4. 孩子登录
```bash
curl -X POST http://localhost:5000/api/auth/child/login \
  -H "Content-Type: application/json" \
  -d '{
    "child_id": 1,
    "password": "child123"
  }'
```

## 5. 添加练琴记录
```bash
curl -X POST http://localhost:5000/api/practice/record \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {ACCESS_TOKEN}" \
  -d '{
    "date": "2025-02-28",
    "practice_minutes": 45,
    "notes": "完成练习第五题"
  }'
```

## 6. 获取练琴记录
```bash
curl -X GET 'http://localhost:5000/api/practice/records/1?start_date=2025-01-01&end_date=2025-02-28' \
  -H "Authorization: Bearer {ACCESS_TOKEN}"
```

## 7. 获取统计数据
```bash
curl -X GET http://localhost:5000/api/practice/statistics/1 \
  -H "Authorization: Bearer {ACCESS_TOKEN}"
```

## 8. 发放游戏时间
```bash
curl -X POST http://localhost:5000/api/awards/give \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {ACCESS_TOKEN}" \
  -d '{
    "child_id": 1,
    "game_minutes": 30,
    "reason": "本周练琴表现优秀"
  }'
```

## 9. 获取游戏时间余额
```bash
curl -X GET http://localhost:5000/api/awards/balance/1 \
  -H "Authorization: Bearer {ACCESS_TOKEN}"
```

## 10. 获取奖励历史
```bash
curl -X GET http://localhost:5000/api/awards/history/1 \
  -H "Authorization: Bearer {ACCESS_TOKEN}"
```

## 11. 使用游戏时间
```bash
curl -X POST http://localhost:5000/api/awards/deduct \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {ACCESS_TOKEN}" \
  -d '{
    "game_minutes": 15
  }'
```

## 12. 获取家长信息
```bash
curl -X GET http://localhost:5000/api/auth/parent/me \
  -H "Authorization: Bearer {ACCESS_TOKEN}"
```

---

### 测试流程

1. 先执行第1步（家长注册）获得家长账号
2. 执行第2步（家长登录）获得ACCESS_TOKEN
3. 执行第3步（孩子注册）创建孩子账户
4. 执行第4步（孩子登录）获得孩子的TOKEN
5. 用孩子的TOKEN执行第5步（添加练琴记录）
6. 用家长或孩子的TOKEN查看各项数据
7. 用家长TOKEN执行第8步（发放游戏时间）

### 注意事项

- 将 `{ACCESS_TOKEN}` 替换为实际获得的token（去掉 Bearer 前缀中的 Bearer 关键字，只保留token部分）
- 日期格式为 ISO 8601 (YYYY-MM-DD)
- 所有时间单位为分钟
