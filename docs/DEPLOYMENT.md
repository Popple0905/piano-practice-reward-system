# Deployment Guide

## Local Development Environment

### 1. Backend Setup

#### 1.1 Install MySQL (optional, SQLite is used by default)
```bash
# Windows - via chocolatey
choco install mysql

# macOS - via Homebrew
brew install mysql

# Linux (Ubuntu)
sudo apt-get install mysql-server
```

#### 1.2 Create Database (MySQL only)
```bash
mysql -u root -p < database/schema.sql
```

#### 1.3 Install Python Dependencies
```bash
cd backend
pip install -r requirements.txt
```

#### 1.4 Configure Environment Variables
Copy `.env.example` to `.env` and configure the database connection string:
```
DATABASE_URL=mysql+pymysql://root:your_password@localhost/piano_app
```

#### 1.5 Start Backend Service
```bash
python app.py
```

## Production Deployment

### Using Gunicorn + Nginx

#### 1. Install Gunicorn
```bash
pip install gunicorn
```

#### 2. Start Gunicorn
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:create_app()
```

#### 3. Nginx Configuration
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

### Docker Deployment (optional)

Create a `Dockerfile`:
```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:create_app()"]
```

Build and run:
```bash
docker build -t piano-app-backend .
docker run -p 5000:5000 piano-app-backend
```

## Frontend Deployment

### iOS App Release
```bash
cd frontend/PianoApp
npx react-native run-ios --release
```

### Android App Release
```bash
cd frontend/PianoApp
npx react-native run-android --variant=release
```

## Database Backup

### Manual Backup
```bash
mysqldump -u root -p piano_app > backup_$(date +%Y%m%d_%H%M%S).sql
```

### Restore Backup
```bash
mysql -u root -p piano_app < backup_file.sql
```

## Monitoring and Logging

### Configure Logging
```python
import logging

logging.basicConfig(
    filename='app.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

## Security Recommendations

1. **HTTPS** - Configure SSL/TLS certificate
2. **Passwords** - Use strong passwords and password hashing
3. **Rate Limiting** - Implement rate limiting to prevent abuse
4. **Regular Backups** - Automated daily database backups
5. **Update Dependencies** - Regularly update third-party libraries
6. **Privacy Protection** - Comply with GDPR and personal data protection regulations

## Scaling Suggestions

As user volume grows:

1. Add caching layer (Redis)
2. Use database primary-replica replication
3. Implement CDN acceleration
4. Add message queue (RabbitMQ/Kafka)
5. Refactor to microservices architecture
