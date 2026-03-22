# PianoAPP v1 - 快速开始指南

## 📋 项目概述

**PianoAPP** 是一个家长-孩子互动的练琴时间管理系统，让孩子通过记录每日练琴时间来赚取游戏时间奖励。

### 主要特性
✅ **孩子账户** - 记录每日练琴时间和内容  
✅ **家长控制面板** - 查看孩子成绩、发放游戏奖励  
✅ **数据统计** - 周/月/年练琴数据分析  
✅ **游戏时间管理** - 积分制度管理  
✅ **安全认证** - JWT Token身份验证  

---

## 🚀 5分钟快速开始

### 第一步：准备环境

#### 安装必需软件
1. **Python 3.10+** ✅ 已验证 Python 3.13
   - 下载: https://www.python.org/
   - 验证: `python --version`

2. **Git** (可选)
   - 下载: https://git-scm.com/

**注意**: 本地开发使用 SQLite，无需安装 MySQL。生产环境可配置为 MySQL。

### 第二步：设置后端

```bash
# 1. 进入backend目录
cd PianoAPPv1\backend

# 2. 创建Python虚拟环境
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux

# 3. 安装依赖
pip install -r requirements.txt

# 4. (可选) 配置环境变量 - 创建.env文件
# FLASK_ENV=development
# JWT_SECRET_KEY=your-secret-key
# 其他环境变量可选，将使用默认值

# 5. 启动服务器
python app.py
```

✅ 服务器运行在 `http://localhost:5000`
✅ 数据库自动使用 SQLite (piano_app.db 在 backend/instance/ 目录)
✅ 首次运行需要初始化测试数据：`python backend/init_db.py`

### 第三步：访问前端登入页面

✨ **前端已集成！直接访问 Web 界面登入测试：**

1. **打开浏览器** → 访问 `http://localhost:5000`
2. **登入测试账户**
   - 孩子：孩子 ID `1` / 密码 `child123`
   - ✅ 系统已自动创建测试账户（运行 `python init_db.py`）
3. **测试功能**
   - ✅ 记录练琴时间（5分钟单位）
   - ✅ 查看多筆練琴紀錄（已修正显示全部记录）
   - ✅ 时间舍入（无效时间自动调整到最近5分钟）
   - ✅ 查询游戏余额
   - ✅ 本地时间定位（自动检测系统时区）

### 第四步：API 测试（可选）

打开终端/PowerShell 执行 API 测试（已验证工作正常）：

#### PowerShell 测试脚本

```powershell
# 家长登录
$body = @{username="parent2024"; password="securepass123"} | ConvertTo-Json
Invoke-WebRequest -Uri http://localhost:5000/api/auth/parent/login `
  -Method POST -Headers @{"Content-Type"="application/json"} -Body $body -UseBasicParsing | Select-Object -ExpandProperty Content

# 返回示例:
# {"access_token":"eyJ...","parent_id":2,"username":"parent2024"}
```

#### Bash/curl 测试脚本

```bash
# 家长登录
curl -X POST http://localhost:5000/api/auth/parent/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "parent2024",
    "password": "securepass123"
  }'
```

🎉 详见 [TESTING_REPORT.md](TESTING_REPORT.md) 获取完整的测试结果

---

## 📱 前端开发

### React Native (推荐小白)

```bash
# 1. 安装 Node.js (https://nodejs.org/)

# 2. 创建React Native项目
cd frontend
npx react-native init PianoApp
cd PianoApp

# 3. 安装依赖
npm install axios @react-native-async-storage/async-storage

# 4. 运行应用
# iOS
npx react-native run-ios

# Android
npx react-native run-android
```

### Flutter (推荐高性能)

```bash
# 1. 安装Flutter (https://flutter.dev/docs/get-started/install)

# 2. 创建项目
cd frontend
flutter create piano_app
cd piano_app

# 3. 安装依赖 (在pubspec.yaml中添加)
# dependencies:
#   http: ^1.1.0
#   shared_preferences: ^2.2.0

flutter pub get

# 4. 运行应用
flutter run
```

---

## 📊 数据流示意图

```
┌─────────────────────────────────────────────────────────┐
│                    PianoAPP 系统架构                      │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────┐              ┌──────────┐                │
│  │ 孩子 APP  │              │ 家长 APP  │                │
│  │ (Child)   │              │ (Parent)  │                │
│  └─────┬────┘              └────┬─────┘                │
│        │                        │                       │
│        │ 记录练琴  │  发放奖励    │                       │
│        └─────────┬──────────────┘                       │
│                  │                                      │
│                  ▼                                      │
│        ┌─────────────────┐                             │
│        │   Flask 后端     │                             │
│        │   (REST API)    │                             │
│        └────────┬────────┘                             │
│                 │                                      │
│    ┌────────────┼────────────┐                         │
│    │            │            │                         │
│    ▼            ▼            ▼                         │
│  ┌────────┐ ┌────────┐ ┌──────────┐                    │
│  │ 练琴   │ │孩子   │ │ 游戏时间 │                    │
│  │ 数据库  │ │数据库 │ │ 数据库   │                    │
│  └────────┘ └────────┘ └──────────┘                    │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## 🔑 核心 API 端点

| 功能 | 方法 | 端点 | 说明 |
|------|------|------|------|
| 家长注册 | POST | `/api/auth/parent/register` | 创建家长账号 |
| 家长登录 | POST | `/api/auth/parent/login` | 家长身份验证 |
| 孩子注册 | POST | `/api/auth/child/register` | 创建孩子账号 |
| 孩子登录 | POST | `/api/auth/child/login` | 孩子身份验证 |
| 添加练琴 | POST | `/api/practice/record` | 孩子记录今日练琴 |
| 查看成绩 | GET | `/api/practice/records/<child_id>` | 查看练琴记录 |
| 数据统计 | GET | `/api/practice/statistics/<child_id>` | 查看统计数据 |
| 发放奖励 | POST | `/api/awards/give` | 家长发放游戏时间 |
| 查询积分 | GET | `/api/awards/balance/<child_id>` | 查看游戏时间余额 |

---

## 📝 配置文件说明

### backend/.env
```
FLASK_ENV=development          # 开发/生产环境
DATABASE_URL=mysql+pymysql://root:password@localhost/piano_app
JWT_SECRET_KEY=your-secret-key-change-in-production
SERVER_PORT=5000              # 默认端口
```

### frontend/apiClient.js
```javascript
const API_BASE_URL = 'http://localhost:5000/api';
// 改为你的服务器地址
```

---

## ✨ 核心功能详解

### 1️⃣ 孩子端
- **记录练琴**: 输入今日练琴时间和内容
- **查看积分**: 实时显示可用游戏时间
- **成绩追踪**: 查看历史练琴记录

### 2️⃣ 家长端
- **监督成绩**: 看每个孩子的练琴进度
- **数据分析**: 统计周月年的练琴时间
- **发放奖励**: 根据表现发放游戏时间

### 3️⃣ 激励机制
```
练琴30分钟 → 赚取30分钟游戏时间
            ↓
         孩子可用来玩游戏
```

---

## 🐛 常见问题

### Q1: 无法连接数据库
**A:** 检查MySQL是否正在运行
```bash
# macOS
mysql.server status

# Windows (powershell)
Get-Service MySQL80  # 或对应版本
```

### Q2: 找不到模块 Flask
**A:** 确认虚拟环境已激活并安装依赖
```bash
which python  # 应显示venv路径
pip install -r requirements.txt
```

### Q3: 前端无法连接后端
**A:** 检查
1. 后端是否运行在 `localhost:5000`
2. 前端 `apiClient.js` 中的 `API_BASE_URL` 是否正确
3. 防火墙设置

---

## 📚 下一步

1. **完成后端测试** → 使用 [API_TESTING.md](../docs/API_TESTING.md) 中的脚本
2. **开发前端应用** → 参考 [DEVELOPMENT.md](DEVELOPMENT.md)
3. **部署上线** → 参考 [DEPLOYMENT.md](../docs/DEPLOYMENT.md)
4. **添加新功能** → 查看功能规划部分

---

## 📞 技术支持

遇到问题？检查以下资源：
- 📖 查看 [README.md](../README.md)
- 🧪 查看 [API_TESTING.md](../docs/API_TESTING.md)
- 🚀 查看 [DEPLOYMENT.md](../docs/DEPLOYMENT.md)
- 💻 查看 [DEVELOPMENT.md](DEVELOPMENT.md)

---

**祝您使用愉快！🎉**
