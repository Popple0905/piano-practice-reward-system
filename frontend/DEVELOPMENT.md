# 前端应用开发指南

## React Native 开发

### 1. 项目初始化

```bash
cd frontend
npx react-native init PianoApp
cd PianoApp
```

### 2. 必要的依赖包

```bash
npm install axios react-navigation react-native-screens react-native-safe-area-context
npm install @react-native-async-storage/async-storage
npm install react-native-vector-icons
```

### 3. 核心功能模块

#### 认证服务 (services/authService.js)
- 处理登录/注册
- JWT token存储和管理
- 自动登录恢复

#### API客户端 (services/apiClient.js)
- 封装HTTP请求
- 自动添加认证token
- 错误处理

#### 应用屏幕 (screens/)
- **ParentDashboard** - 家长主页面（查看孩子成绩、发放奖励）
- **ChildDashboard** - 孩子主页面（记录练琴、查看积分）
- **PracticeRecord** - 练琴记录详情
- **GameBalance** - 游戏时间管理
- **Statistics** - 成绩统计

## Flutter 开发

### 1. 项目初始化

```bash
cd frontend
flutter create piano_app
cd piano_app
```

### 2. pubspec.yaml 依赖

```yaml
dependencies:
  flutter:
    sdk: flutter
  http: ^1.1.0
  shared_preferences: ^2.2.0
  provider: ^6.0.0
  intl: ^0.19.0
  charts_flutter: ^0.12.0
```

### 3. 文件结构

```
lib/
├── main.dart
├── models/
│   ├── parent.dart
│   ├── child.dart
│   └── practice_record.dart
├── services/
│   ├── api_service.dart
│   └── auth_service.dart
├── screens/
│   ├── auth/
│   ├── parent/
│   └── child/
└── widgets/
```

## 通用UI组件

### Parent App 功能
1. **登录界面** - 家长登入
2. **孩子列表** - 展示所有孩子及其练琴数据
3. **奖励发放** - 发放游戏时间
4. **成绩查看** - 查看孩子的练琴成绩
5. **统计报告** - 周/月/年练琴数据

### Child App 功能
1. **登录界面** - 孩子登入
2. **今日练琴** - 记录每日练琴时间
3. **我的成绩** - 查看自己的练琴记录
4. **我的积分** - 鼓励和游戏时间余额
5. **排行榜** - 与其他孩子比较（可选）

## 后续深化

- 离线支持（本地缓存）
- 推送通知
- 语音识别记录
- 摄像头集成
- 数据同步
