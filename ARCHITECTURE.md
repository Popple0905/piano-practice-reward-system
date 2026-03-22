# 项目文件结构说明

```
PianoAPPv1/
│
├── 📁 backend/                 # Python Flask REST API后端
│   ├── app.py                 # Flask应用主文件，启动入口
│   ├── config.py              # 配置管理（开发/生产环境）
│   ├── models.py              # 数据库模型（Parent, Child, PracticeRecord, GameRequest）
│   ├── init_db.py             # 数据库初始化脚本（创建测试账户）✨ NEW
│   ├── requirements.txt        # Python依赖包列表
│   ├── .env.example            # 环境变量示例文件
│   │
│   ├── 📁 instance/            # 实例数据文件夹
│   │   └── piano_app.db        # SQLite 数据库（本地开发）
│   │
│   └── 📁 routes/             # API路由模块
│       ├── __init__.py
│       ├── auth.py            # 认证端点（家长/孩子 登录）✅ 已验证
│       ├── practice.py         # 练琴记录端点（5分鐘單位、時間舍入、狀態管理）✅ 已验证
│       └── awards.py          # 游戏奖励端点（15分鐘單位、餘額查詢、轉換比例）✅ 已验证
│
├── 📁 frontend/               # 前端文件
│   ├── index.html             # Web 登入和仪表板页面（HTML5+JS）✅ 已验证
│   │   ├── 子女登錄和儀表板     # 練琴記錄提交、查詢、遊戲餘額
│   │   ├── 時間處理            # 本地時間轉換、5分鐘舍入
│   │   └── 調試工具            # Console 日誌輸出支持診斷
│   ├── DEVELOPMENT.md         # 前端开发指南
│   ├── apiClient.js          # API 客户端（原 axios 配置）
│   ├── services.js           # API 服务接口封装
│   ├── ParentDashboard.js    # 家长控制面板（React Native - 待实装）
│   └── ChildDashboard.js     # 孩子主页面（React Native - 待实装）
│
├── 📁 database/              # 数据库相关文件
│   └── schema.sql            # MySQL数据库架构（表定义、索引）
│
├── 📁 docs/                  # 文档资料
│   ├── API_TESTING.md        # API测试脚本和使用说明
│   └── DEPLOYMENT.md         # 部署指南（本地/生产）
│
├── README.md                 # 项目总览文档
├── QUICK_START.md            # 快速开始指南（本文件）
├── .gitignore               # Git忽略文件列表
└── ARCHITECTURE.md          # 你正在查看此文件

```

## � 数据库配置

### 本地开发环境 (默认)
- **类型**: SQLite
- **文件**: `backend/piano_app.db`
- **优点**: 无需额外安装，自动创建，完美用于开发和测试
- **自动初始化**: 数据库表在首次运行时自动创建

### 生产环境
- **类型**: MySQL 8.0+
- **配置**: 通过環境變量 `DATABASE_URL` 指定
- **连接字符串**: `mysql+pymysql://username:password@host:3306/database_name`
- **注意**: 需要手动初始化数据库，运行 `database/schema.sql`

### 环境变量配置
详见 `.env.example`:
```env
# 本地开发 (默认)
# DATABASE_URL=sqlite:///piano_app.db

# 生产环境
# DATABASE_URL=mysql+pymysql://user:password@localhost:3306/piano_app
```

#### `app.py` - Flask 应用入口 ✨ 已更新
```python
# 作用：创建 Flask 应用、初始化数据库、注册蓝图、提供前端文件
# 运行：python app.py
# 输出：启动服务器在 http://localhost:5000
# 功能：
#   - 提供 API 端点 (/api/*)
#   - 提供 Web 前端页面 (/)
#   - 自动提供静态文件和单页应用支持
```

#### `models.py` - 数据库模型
定义了4个主要数据模型：
- **Parent**: 家长账户
- **Child**: 孩子账户
- **PracticeRecord**: 练琴记录
- **GameAward**: 游戏奖励记录

#### `config.py` - 配置管理
- `DevelopmentConfig`: 开发环境配置
- `ProductionConfig`: 生产环境配置
- 支持通过环境变量覆盖

#### `routes/auth.py` - 认证模块
**端点：**
- `POST /parent/register` - 家长注册
- `POST /parent/login` - 家长登录
- `POST /child/register` - 孩子注册
- `POST /child/login` - 孩子登录
- `GET /parent/me` - 获取家长信息

#### `routes/practice.py` - 练琴记录模块
**端点：**
- `POST /record` - 添加/更新练琴记录
- `GET /records/<child_id>` - 获取练琴记录列表
- `GET /statistics/<child_id>` - 获取统计数据

#### `routes/awards.py` - 游戏奖励模块
**端点：**
- `POST /give` - 发放游戏时间
- `POST /deduct` - 使用游戏时间
- `GET /balance/<child_id>` - 查询游戏时间余额
- `GET /history/<child_id>` - 查询奖励历史

## 🌐 前端架构 ✨ NEW

### Web 页面 (index.html)
- **类型**: HTML5 + Vanilla JavaScript
- **特性**:
  - 响应式设计（支持桌面和移动设备）
  - 用户类型选择（家长/孩子）
  - JWT Token 管理
  - API 交互显示
  - 错误和成功消息提示
  - 登出功能

### 集成方式
- 前端文件由后端 Flask 直接提供
- 访问 `http://localhost:5000` 自动服务 `index.html`
- 所有 API 调用通过 `/api/*` 路由进行
- 支持跨域请求（CORS 已启用）

### 前端文件

#### `apiClient.js` - API客户端
```javascript
// axios实例，自动：
// - 添加JWT token到请求头
// - 处理401错误（token过期）
// - 设置基础URL和超时
```

#### `services.js` - 服务接口
导出以下服务对象：
```javascript
parentAuthService    // 家长认证
childAuthService     // 孩子认证
practiceService      // 练琴记录
awardService         // 游戏奖励
logout()            // 登出函数
```

#### `ParentDashboard.js` - 家长控制面板
- 展示所有孩子列表
- 显示孩子成绩统计
- 提供发放游戏时间按钮

#### `ChildDashboard.js` - 孩子主页面
- 显示游戏积分余额
- 展示今日练琴记录
- 提供添加练琴记录表单

## 📦 数据库配置

### 本地开发环境（默认）
- **类型**: SQLite
- **文件**: `backend/piano_app.db`
- **优点**: 无需额外安装，自动创建，完美用于开发和测试
- **自动初始化**: 数据库表在首次运行时自动创建

### 生产环境
- **类型**: MySQL 8.0+
- **配置**: 通过環境變量 `DATABASE_URL` 指定
- **连接字符串**: `mysql+pymysql://username:password@host:3306/database_name`
- **注意**: 需要手动初始化数据库，运行 `database/schema.sql`

### 环境变量配置
详见 `.env.example`:
```env
# 本地开发 (默认)
DATABASE_URL=sqlite:///piano_app.db

# 生产环境
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/piano_app
```

### 数据库文件

#### `schema.sql` - 数据库架构
定义：
- 4个数据表
- 外键关系
- 索引创建
- 约束条件

### 文档文件

#### `QUICK_START.md`
新手快速开始指南，包括：
- 5分钟快速开始步骤
- 环境安装说明
- API端点速查表
- 常见问题解答

#### `API_TESTING.md`
API测试脚本和说明：
- 完整的curl测试命令
- 返回数据示例
- 测试流程指导

#### `DEPLOYMENT.md`
部署指南：
- 本地开发环境配置
- 生产环境部署（Gunicorn + Nginx）
- Docker部署方案
- 数据库备份恢复

#### `DEVELOPMENT.md`
前端开发指南：
- React Native入门
- Flutter入门
- UI组件设计建议
- 离线支持方案

---

## 🔄 数据流示意

```
客户端请求
    ↓
apiClient (添加Token、错误处理)
    ↓
routes (验证权限、处理业务逻辑)
    ↓
models (数据库操作)
    ↓
数据库 (SQLite 或 MySQL)
    ↓
返回JSON响应
    ↓
前端更新UI
```

---

## 🔐 安全性说明

### 认证流程
1. 用户登录 → 后端验证用户名密码
2. 登录成功 → 返回JWT Token
3. 后续请求 → 在Authorization头中发送Token
4. 后端验证 → 检查Token有效性和权限

### 权限控制
- **Parent Only**: 发放游戏时间、查看所有孩子数据
- **Child Only**: 添加练琴记录
- **Parent/Child**: 查询自己的信息

---

## 📈 扩展建议

### 短期（第一版本）
- ✅ 基础CRUD操作
- ✅ 认证和权限控制
- ✅ 简单UI界面

### 中期（v1.5）
- 🔔 推送通知功能
- 📊 数据可视化图表
- 🎯 目标设置和追踪

### 长期（v2.0）
- 🌐 多地区多语言支持
- 📸 照片/视频示证
- 🎁 虚拟商店（用积分买东西）
- 👥 社区排行榜

---

## 🚀 运行命令速查

```bash
# 启动后端
cd PianoAPPv1/backend
source venv/bin/activate  # 或 venv\Scripts\activate (Windows)
python app.py

# 启动前端 (React Native)
cd PianoAPPv1/frontend/PianoApp
npm start

# 初始化数据库
mysql -u root -p < PianoAPPv1/database/schema.sql

# 测试API
curl -X GET http://localhost:5000/api/auth/parent/me \
  -H "Authorization: Bearer {TOKEN}"
```

---

**完成！现在您已经了解了整个项目结构。请查看 QUICK_START.md 开始开发！** 🎉
