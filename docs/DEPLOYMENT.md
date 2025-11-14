# Deployment Guide

Production deployment guide for the Crypto Trading Platform.

## Table of Contents

- [Deployment Options](#deployment-options)
- [Pre-Deployment Checklist](#pre-deployment-checklist)
- [Docker Deployment](#docker-deployment)
- [Cloud Deployment](#cloud-deployment)
- [Database Setup](#database-setup)
- [SSL/HTTPS Configuration](#sslhttps-configuration)
- [Monitoring](#monitoring)
- [Backup & Recovery](#backup--recovery)
- [Scaling](#scaling)
- [Troubleshooting](#troubleshooting)

## Deployment Options

### Option 1: Docker Compose (Recommended for Single Server)

**Pros:**
- Easy to set up and manage
- All services containerized
- Suitable for VPS or dedicated server
- Good for small to medium scale

**Cons:**
- Single point of failure
- Limited scalability
- Manual scaling required

### Option 2: Kubernetes

**Pros:**
- Highly scalable
- Self-healing
- Load balancing
- Rolling updates

**Cons:**
- Complex setup
- Requires DevOps expertise
- Higher resource requirements

### Option 3: Cloud Platforms

**Pros:**
- Managed services
- Auto-scaling
- High availability
- Backup included

**Cons:**
- Higher costs
- Vendor lock-in
- Learning curve

## Pre-Deployment Checklist

### Security

- [ ] Generate strong `SECRET_KEY` (min 32 characters)
- [ ] Use strong database passwords
- [ ] Configure firewall rules
- [ ] Set up SSL/HTTPS certificates
- [ ] Enable API key IP restrictions on Binance
- [ ] Disable `DEBUG` mode (`DEBUG=false`)
- [ ] Remove default credentials
- [ ] Configure CORS properly

### Configuration

- [ ] Review all `.env` variables
- [ ] Set `ENVIRONMENT=production`
- [ ] Set `BINANCE_TESTNET=false` (only when ready!)
- [ ] Configure backup schedule
- [ ] Set up monitoring and alerts
- [ ] Configure log rotation
- [ ] Test all endpoints

### Testing

- [ ] Run full test suite
- [ ] Test on testnet first
- [ ] Verify backup/restore process
- [ ] Load testing
- [ ] Security audit
- [ ] Test emergency stop procedures

### Documentation

- [ ] Document deployment architecture
- [ ] Create runbook for common issues
- [ ] Document backup procedures
- [ ] Create incident response plan

## Docker Deployment

### 1. Server Setup

**Minimum Server Requirements:**
- CPU: 4 cores
- RAM: 8GB
- Storage: 50GB SSD
- OS: Ubuntu 22.04 LTS (recommended)
- Network: Stable connection with low latency to exchange

**Install Docker:**

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker

# Install Docker Compose
sudo apt install docker-compose-plugin

# Verify installation
docker --version
docker compose version
```

### 2. Application Deployment

```bash
# Clone repository
git clone https://github.com/emtsov-nik/crypto-trading-platform.git
cd crypto-trading-platform

# Checkout production branch
git checkout main

# Create production .env
cp .env.example .env
nano .env
```

**Production .env Configuration:**

```env
# Environment
ENVIRONMENT=production
DEBUG=false

# Database
POSTGRES_USER=trading_user
POSTGRES_PASSWORD=<STRONG_PASSWORD_HERE>
POSTGRES_DB=trading_db
DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB}

# Redis
REDIS_URL=redis://redis:6379/0

# Binance
BINANCE_API_KEY=<YOUR_API_KEY>
BINANCE_API_SECRET=<YOUR_API_SECRET>
BINANCE_TESTNET=false  # ⚠️ Use testnet first!

# Telegram
TELEGRAM_BOT_TOKEN=<YOUR_BOT_TOKEN>
TELEGRAM_ALLOWED_USER_IDS=<YOUR_TELEGRAM_ID>
TELEGRAM_REQUIRE_AUTH=true

# Security
SECRET_KEY=<GENERATED_SECRET_KEY>

# Application
BACKEND_API_URL=https://your-domain.com
VITE_API_URL=https://your-domain.com
CORS_ORIGINS=https://your-domain.com

# Safety Limits (adjust as needed)
MAX_POSITION_SIZE_USD=1000
MAX_OPEN_POSITIONS=3
MAX_DAILY_TRADES=10
MAX_DAILY_LOSS_PERCENT=5.0
```

**Generate Secrets:**

```bash
# Generate SECRET_KEY
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# Generate database password
python3 -c "import secrets; print(secrets.token_urlsafe(24))"
```

### 3. Build and Start Services

```bash
# Build images
docker-compose build

# Start services in detached mode
docker-compose up -d

# Check logs
docker-compose logs -f

# Check service status
docker-compose ps
```

### 4. Verify Deployment

```bash
# Check backend health
curl https://your-domain.com/api/health

# Check if services are running
docker-compose ps

# Expected output: All services should show "Up" status

# Test database connection
docker-compose exec backend python -c "from app.database import engine; print('DB OK' if engine else 'DB FAILED')"

# Test Telegram bot
# Send /start to your bot in Telegram
```

### 5. Production Docker Compose

Create `docker-compose.prod.yml` with production optimizations:

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    restart: always
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backups:/backups
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - trading_network

  redis:
    image: redis:7-alpine
    restart: always
    command: redis-server --appendonly yes --maxmemory 512mb --maxmemory-policy allkeys-lru
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - trading_network

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    restart: always
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
      - SECRET_KEY=${SECRET_KEY}
      - BINANCE_API_KEY=${BINANCE_API_KEY}
      - BINANCE_API_SECRET=${BINANCE_API_SECRET}
      - ENVIRONMENT=production
      - DEBUG=false
    ports:
      - "8000:8000"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    networks:
      - trading_network
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  celery_worker:
    build:
      context: ./backend
      dockerfile: Dockerfile
    restart: always
    command: celery -A app.celery_app worker --loglevel=info
    depends_on:
      - redis
      - postgres
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
      - CELERY_BROKER_URL=${CELERY_BROKER_URL}
      - CELERY_RESULT_BACKEND=${CELERY_RESULT_BACKEND}
    networks:
      - trading_network
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  telegram_bot:
    build:
      context: ./backend
      dockerfile: Dockerfile
    restart: always
    command: python -m telegram_bot.bot
    depends_on:
      - backend
    environment:
      - TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
      - TELEGRAM_ALLOWED_USER_IDS=${TELEGRAM_ALLOWED_USER_IDS}
      - BACKEND_API_URL=${BACKEND_API_URL}
    networks:
      - trading_network
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    restart: always
    ports:
      - "3000:80"
    depends_on:
      - backend
    networks:
      - trading_network

  nginx:
    image: nginx:alpine
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - backend
      - frontend
    networks:
      - trading_network

volumes:
  postgres_data:
  redis_data:

networks:
  trading_network:
    driver: bridge
```

## Cloud Deployment

### AWS Deployment

**Architecture:**
```
Internet → ALB → ECS (Fargate)
                  ↓
              RDS (PostgreSQL)
              ElastiCache (Redis)
```

**Steps:**

1. **Create VPC and Subnets**
2. **Set up RDS PostgreSQL:**
   ```bash
   # Create RDS instance
   aws rds create-db-instance \
     --db-instance-identifier trading-db \
     --db-instance-class db.t3.medium \
     --engine postgres \
     --master-username admin \
     --master-user-password <password> \
     --allocated-storage 20
   ```

3. **Set up ElastiCache Redis:**
   ```bash
   aws elasticache create-cache-cluster \
     --cache-cluster-id trading-cache \
     --engine redis \
     --cache-node-type cache.t3.micro \
     --num-cache-nodes 1
   ```

4. **Deploy to ECS:**
   - Create ECR repository
   - Push Docker images
   - Create ECS cluster
   - Define task definitions
   - Create services

### DigitalOcean Deployment

**Using App Platform:**

1. **Create App:**
   - Connect GitHub repository
   - Select branch
   - Configure build settings

2. **Add Database:**
   - Add PostgreSQL managed database
   - Add Redis managed database

3. **Configure Environment:**
   - Set all environment variables
   - Configure health checks

4. **Deploy:**
   - Click "Deploy"
   - Monitor deployment logs

### Google Cloud Platform

**Using Cloud Run:**

1. **Build and Push Images:**
   ```bash
   gcloud builds submit --tag gcr.io/PROJECT_ID/backend
   gcloud builds submit --tag gcr.io/PROJECT_ID/frontend
   ```

2. **Deploy Services:**
   ```bash
   gcloud run deploy backend \
     --image gcr.io/PROJECT_ID/backend \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated
   ```

3. **Set up Cloud SQL:**
   - Create PostgreSQL instance
   - Configure connection
   - Update DATABASE_URL

## Database Setup

### PostgreSQL Configuration

**Production postgresql.conf:**

```ini
# Connection Settings
max_connections = 100
shared_buffers = 2GB
effective_cache_size = 6GB
maintenance_work_mem = 512MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200
work_mem = 10MB
min_wal_size = 1GB
max_wal_size = 4GB

# Logging
logging_collector = on
log_directory = 'log'
log_filename = 'postgresql-%Y-%m-%d_%H%M%S.log'
log_rotation_age = 1d
log_rotation_size = 100MB
log_line_prefix = '%t [%p]: [%l-1] user=%u,db=%d,app=%a,client=%h '
log_min_duration_statement = 1000
```

### Database Backups

**Automated Backup Script:**

```bash
#!/bin/bash
# backup-db.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups"
DB_NAME="trading_db"
DB_USER="trading_user"

# Create backup
pg_dump -U $DB_USER -d $DB_NAME | gzip > $BACKUP_DIR/backup_$DATE.sql.gz

# Keep only last 7 days
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +7 -delete

# Upload to S3 (optional)
# aws s3 cp $BACKUP_DIR/backup_$DATE.sql.gz s3://my-backups/
```

**Cron Job:**

```bash
# Edit crontab
crontab -e

# Add backup job (daily at 2 AM)
0 2 * * * /opt/scripts/backup-db.sh >> /var/log/backup.log 2>&1
```

## SSL/HTTPS Configuration

### Using Let's Encrypt (Free)

**Install Certbot:**

```bash
sudo apt install certbot python3-certbot-nginx
```

**Obtain Certificate:**

```bash
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

**Auto-Renewal:**

```bash
# Test renewal
sudo certbot renew --dry-run

# Certbot adds this cron job automatically
# /etc/cron.d/certbot
```

### Nginx SSL Configuration

```nginx
# nginx.conf
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com www.your-domain.com;

    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Backend API
    location /api {
        proxy_pass http://backend:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Frontend
    location / {
        proxy_pass http://frontend:80;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

## Monitoring

### Prometheus + Grafana

**docker-compose.monitoring.yml:**

```yaml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
    networks:
      - trading_network

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3001:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=<password>
    volumes:
      - grafana_data:/var/lib/grafana
    depends_on:
      - prometheus
    networks:
      - trading_network

volumes:
  prometheus_data:
  grafana_data:

networks:
  trading_network:
    external: true
```

### Application Monitoring

**Add to backend requirements.txt:**
```
prometheus-client
prometheus-fastapi-instrumentator
```

**Instrument FastAPI:**

```python
# app/main.py
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI()

# Add Prometheus metrics
Instrumentator().instrument(app).expose(app, endpoint="/metrics")
```

### Log Aggregation

**Using ELK Stack or Loki:**

```yaml
# docker-compose.logging.yml
services:
  loki:
    image: grafana/loki:latest
    ports:
      - "3100:3100"
    volumes:
      - loki_data:/loki
    networks:
      - trading_network

  promtail:
    image: grafana/promtail:latest
    volumes:
      - /var/log:/var/log
      - ./promtail-config.yml:/etc/promtail/config.yml
    networks:
      - trading_network
```

## Backup & Recovery

### Backup Strategy

**What to Backup:**
- Database (PostgreSQL)
- Redis snapshots
- Configuration files (.env)
- Application code
- SSL certificates

**Backup Schedule:**
- Database: Daily full backup, hourly incremental
- Redis: Daily snapshot
- Config: After each change
- Code: Git repository

### Recovery Procedures

**Database Recovery:**

```bash
# Restore from backup
gunzip -c backup_20240101_120000.sql.gz | psql -U trading_user -d trading_db

# Verify restoration
psql -U trading_user -d trading_db -c "SELECT COUNT(*) FROM strategies;"
```

**Full System Recovery:**

1. Restore configuration files
2. Restore database
3. Restore Redis data (if needed)
4. Restart services
5. Verify all endpoints
6. Check active trades

## Scaling

### Horizontal Scaling

**Load Balancer Configuration:**

```nginx
upstream backend_servers {
    least_conn;
    server backend1:8000;
    server backend2:8000;
    server backend3:8000;
}

server {
    listen 443 ssl;

    location /api {
        proxy_pass http://backend_servers;
    }
}
```

### Database Scaling

**Read Replicas:**

```yaml
services:
  postgres_primary:
    image: postgres:15-alpine
    # ... primary config

  postgres_replica:
    image: postgres:15-alpine
    environment:
      - POSTGRES_REPLICATION_MODE=slave
      - POSTGRES_MASTER_HOST=postgres_primary
    depends_on:
      - postgres_primary
```

### Caching Strategy

```python
# Implement caching for market data
import redis
import json

redis_client = redis.Redis(host='redis', port=6379)

def get_market_data(symbol: str):
    # Check cache first
    cache_key = f"market:{symbol}"
    cached = redis_client.get(cache_key)

    if cached:
        return json.loads(cached)

    # Fetch from exchange
    data = fetch_from_binance(symbol)

    # Cache for 5 minutes
    redis_client.setex(cache_key, 300, json.dumps(data))

    return data
```

## Troubleshooting

### High CPU Usage

**Check container stats:**
```bash
docker stats

# Identify resource-heavy containers
```

**Solutions:**
- Scale horizontally
- Optimize database queries
- Add caching
- Use connection pooling

### Memory Leaks

**Monitor memory:**
```bash
docker stats --no-stream

# Check backend logs for memory issues
docker-compose logs backend | grep -i memory
```

**Solutions:**
- Restart services periodically
- Fix memory leaks in code
- Increase memory limits
- Use memory profiling tools

### Database Connection Errors

**Check connections:**
```sql
SELECT count(*) FROM pg_stat_activity;
```

**Solutions:**
- Increase max_connections
- Use connection pooling
- Close idle connections
- Check firewall rules

### Slow API Response

**Enable query logging:**
```python
# Log slow queries
logging.basicConfig(level=logging.DEBUG)
```

**Solutions:**
- Add database indexes
- Optimize queries
- Implement caching
- Use async operations

---

**Previous:** [Strategy Examples](STRATEGY_EXAMPLES.md) | **Next:** [Security Best Practices](SECURITY.md)
