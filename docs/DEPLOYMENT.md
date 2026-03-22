# 部署指南

## 本地开发环境部署

### 1. 后端部署

#### 1.1 安装MySQL
```bash
# Windows - 通过 chocolatey
choco install mysql

# macOS - 通过 Homebrew
brew install mysql

# Linux (Ubuntu)
sudo apt-get install mysql-server
```

#### 1.2 创建数据库
```bash
mysql -u root -p < database/schema.sql
```

#### 1.3 安装Python依赖
```bash
cd backend
pip install -r requirements.txt
```

#### 1.4 配置环境变量
复制 `.env.example` 为 `.env` 并配置数据库连接字符串：
```
DATABASE_URL=mysql+pymysql://root:your_password@localhost/piano_app
```

#### 1.5 启动后端服务
```bash
python app.py
```

## 生产环境部署

### 使用 Gunicorn + Nginx

#### 1. 安装 Gunicorn
```bash
pip install gunicorn
```

#### 2. 启动 Gunicorn
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:create_app()
```

#### 3. Nginx 配置
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Docker 部署 (可选)

创建 `Dockerfile`:
```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:create_app()"]
```

构建和运行：
```bash
docker build -t piano-app-backend .
docker run -p 5000:5000 piano-app-backend
```

## 前端部署

### iOS 应用发布
```bash
cd frontend/PianoApp
npx react-native run-ios --release
```

### Android 应用发布
```bash
cd frontend/PianoApp
npx react-native run-android --variant=release
```

## 数据库备份

### 手动备份
```bash
mysqldump -u root -p piano_app > backup_$(date +%Y%m%d_%H%M%S).sql
```

### 恢复备份
```bash
mysql -u root -p piano_app < backup_file.sql
```

## 监控和日志

### 配置日志
```python
import logging

logging.basicConfig(
    filename='app.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

## 安全建议

1. **HTTPS** - 配置SSL/TLS证书
2. **密码** - 使用强密码和密码哈希算法
3. **API限流** - 实现速率限制防止滥用
4. **定期备份** - 自动每日备份数据库
5. **更新依赖** - 定期更新第三方库
6. **隐私保护** - 遵守GDPR和个人信息保护法规

## 扩展建议

当用户量增长时：

1. 添加缓存层 (Redis)
2. 使用数据库主从复制
3. 实现CDN加速
4. 添加消息队列 (RabbitMQ/Kafka)
5. 微服务架构重构
