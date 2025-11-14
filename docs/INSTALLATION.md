# Installation Guide

Complete installation instructions for the Crypto Trading Platform.

## Table of Contents

- [System Requirements](#system-requirements)
- [Quick Installation (Docker)](#quick-installation-docker)
- [Manual Installation](#manual-installation)
- [Configuration](#configuration)
- [Verification](#verification)
- [Troubleshooting](#troubleshooting)

## System Requirements

### Minimum Requirements

- **OS:** Linux, macOS, or Windows 10+
- **RAM:** 4GB minimum, 8GB recommended
- **Storage:** 10GB free space
- **CPU:** 2 cores minimum, 4 cores recommended
- **Internet:** Stable broadband connection

### Software Requirements

- **Docker:** 20.10+ and Docker Compose 2.0+
- **Python:** 3.11+ (for local development)
- **Node.js:** 18+ (for frontend development)
- **Git:** 2.30+

## Quick Installation (Docker)

The easiest way to get started is using Docker Compose.

### Step 1: Install Docker

#### Linux (Ubuntu/Debian)
```bash
# Update packages
sudo apt update

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

#### macOS
```bash
# Install Docker Desktop for Mac
# Download from: https://www.docker.com/products/docker-desktop

# Or use Homebrew
brew install --cask docker

# Verify installation
docker --version
docker compose version
```

#### Windows
```powershell
# Install Docker Desktop for Windows
# Download from: https://www.docker.com/products/docker-desktop

# Enable WSL 2 backend (recommended)
wsl --install
wsl --set-default-version 2

# Verify installation (in PowerShell)
docker --version
docker compose version
```

### Step 2: Clone Repository

```bash
# Clone the repository
git clone https://github.com/emtsov-nik/crypto-trading-platform.git
cd crypto-trading-platform

# Check current branch
git branch
```

### Step 3: Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit with your favorite editor
nano .env
# or
vim .env
# or
code .env
```

**Required Configuration:**

1. **Binance API Keys** (Get from [Binance](https://www.binance.com/en/my/settings/api-management))
```env
BINANCE_API_KEY=your_api_key_here
BINANCE_API_SECRET=your_api_secret_here
BINANCE_TESTNET=true  # IMPORTANT: Start with testnet!
```

2. **Telegram Bot** (Get from [@BotFather](https://t.me/BotFather))
```env
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_ALLOWED_USER_IDS=123456789  # Get from @userinfobot
```

3. **Database & Security**
```env
POSTGRES_PASSWORD=choose_strong_password_here
SECRET_KEY=generate_with_python_secrets_module
```

**Generate Secret Key:**
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Step 4: Start Services

```bash
# Start all services in detached mode
docker-compose up -d

# View logs (optional)
docker-compose logs -f

# Check service status
docker-compose ps
```

### Step 5: Access Application

- **Web UI:** http://localhost:3000
- **API Documentation:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/api/health
- **Telegram Bot:** Open Telegram and search for your bot, send `/start`

### Step 6: Verify Installation

```bash
# Check if all services are running
docker-compose ps

# You should see:
# - postgres (healthy)
# - redis (healthy)
# - backend (healthy)
# - frontend (healthy)
# - telegram_bot (healthy)
# - celery_worker (healthy)

# Test API endpoint
curl http://localhost:8000/api/health

# Expected response:
# {"status":"healthy","timestamp":"2024-..."}
```

## Manual Installation

For development or custom deployments without Docker.

### Prerequisites

```bash
# Install Python 3.11+
python3 --version

# Install Node.js 18+
node --version
npm --version

# Install PostgreSQL 15+
psql --version

# Install Redis 7+
redis-cli --version
```

### Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# Linux/macOS:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Install development dependencies (optional)
pip install pytest pytest-cov black flake8 isort mypy
```

### Database Setup

```bash
# Start PostgreSQL (adjust for your system)
sudo systemctl start postgresql

# Create database and user
sudo -u postgres psql
```

```sql
CREATE USER trading_user WITH PASSWORD 'your_password';
CREATE DATABASE trading_db OWNER trading_user;
GRANT ALL PRIVILEGES ON DATABASE trading_db TO trading_user;
\q
```

### Redis Setup

```bash
# Start Redis
sudo systemctl start redis

# Or start manually
redis-server

# Test connection
redis-cli ping
# Should respond: PONG
```

### Environment Configuration

```bash
# Copy .env.example to .env
cp .env.example .env

# Edit for local development
nano .env
```

**Update these values for local setup:**
```env
# Database (localhost instead of docker service name)
DATABASE_URL=postgresql://trading_user:your_password@localhost:5432/trading_db

# Redis (localhost)
REDIS_URL=redis://localhost:6379/0

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Backend API (for frontend)
VITE_API_URL=http://localhost:8000
```

### Run Backend

```bash
# From backend directory with venv activated
cd backend
source venv/bin/activate

# Run development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# In another terminal, start Celery worker
celery -A app.celery_app worker --loglevel=info

# In another terminal, start Telegram bot
python -m telegram_bot.bot
```

### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev

# Frontend will be available at http://localhost:3000
```

## Configuration

### Binance API Setup

1. **Create API Key:**
   - Go to [Binance API Management](https://www.binance.com/en/my/settings/api-management)
   - Click "Create API"
   - Complete verification
   - Save API Key and Secret (shown only once!)

2. **Configure API Restrictions:**
   - ✅ Enable "Enable Reading"
   - ✅ Enable "Enable Spot & Margin Trading"
   - ❌ Disable "Enable Withdrawals" (for safety!)
   - ✅ Enable IP Access Restrictions (add your server IP)

3. **Testnet Setup (Recommended):**
   - Go to [Binance Testnet](https://testnet.binance.vision/)
   - Create testnet API keys
   - Use these keys for testing
   - Set `BINANCE_TESTNET=true` in .env

### Telegram Bot Setup

1. **Create Bot:**
   - Open Telegram and search for [@BotFather](https://t.me/BotFather)
   - Send `/newbot`
   - Follow instructions
   - Save the bot token

2. **Get Your User ID:**
   - Search for [@userinfobot](https://t.me/userinfobot)
   - Send `/start`
   - Copy your user ID

3. **Configure:**
```env
TELEGRAM_BOT_TOKEN=your_bot_token_from_botfather
TELEGRAM_ALLOWED_USER_IDS=your_user_id
```

### Safety Limits Configuration

Adjust these based on your risk tolerance:

```env
# Position limits
MAX_POSITION_SIZE_USD=1000      # Max size per position
MAX_OPEN_POSITIONS=3             # Max concurrent positions

# Risk limits
MAX_DAILY_TRADES=10              # Max trades per day
MAX_DAILY_LOSS_PERCENT=5.0       # Max daily loss %
MAX_TOTAL_LOSS_PERCENT=20.0      # Max total drawdown %

# Capital requirements
MIN_CAPITAL_USD=100              # Minimum capital to start
DEFAULT_INITIAL_CAPITAL=10000    # Default backtest capital
```

## Verification

### Check Services

```bash
# Docker installation
docker-compose ps

# Manual installation
# Check if backend is running
curl http://localhost:8000/api/health

# Check if frontend is accessible
curl http://localhost:3000

# Check if Telegram bot responds
# Send /start to your bot in Telegram
```

### Run Health Checks

```bash
# Backend health
curl http://localhost:8000/api/health

# Database connectivity
curl http://localhost:8000/api/strategies

# Redis connectivity
docker-compose exec redis redis-cli ping
# or for manual installation:
redis-cli ping
```

### Access API Documentation

Open http://localhost:8000/docs in your browser to see interactive API documentation.

### Test Telegram Bot

1. Open Telegram
2. Search for your bot (use the username from @BotFather)
3. Send `/start`
4. You should see the welcome message and main menu
5. Try `/status` to check bot status

## Troubleshooting

### Docker Issues

**Issue: Port already in use**
```bash
# Check what's using the port
sudo lsof -i :8000

# Either stop the conflicting service or change port in docker-compose.yml
```

**Issue: Permission denied**
```bash
# Add user to docker group
sudo usermod -aG docker $USER

# Logout and login again, or:
newgrp docker
```

**Issue: Services won't start**
```bash
# Check logs
docker-compose logs backend
docker-compose logs postgres

# Restart services
docker-compose restart

# Rebuild if needed
docker-compose down
docker-compose up --build
```

### Database Issues

**Issue: Connection refused**
```bash
# Check if PostgreSQL is running
docker-compose ps postgres
# or
sudo systemctl status postgresql

# Check DATABASE_URL in .env
echo $DATABASE_URL
```

**Issue: Authentication failed**
```bash
# Verify credentials in .env match docker-compose.yml
# Try connecting manually:
psql -h localhost -U trading_user -d trading_db
```

### API Issues

**Issue: 502 Bad Gateway**
```bash
# Check backend logs
docker-compose logs backend

# Restart backend
docker-compose restart backend
```

**Issue: CORS errors**
```bash
# Check CORS_ORIGINS in .env includes frontend URL
CORS_ORIGINS=http://localhost:3000,http://localhost:8000
```

### Telegram Bot Issues

**Issue: Bot doesn't respond**
```bash
# Check bot logs
docker-compose logs telegram_bot

# Verify token is correct
echo $TELEGRAM_BOT_TOKEN

# Check if your user ID is in allowed list
echo $TELEGRAM_ALLOWED_USER_IDS
```

**Issue: "Access Denied" message**
- Make sure your Telegram user ID is in `TELEGRAM_ALLOWED_USER_IDS`
- Get your ID from @userinfobot
- Restart bot after updating .env:
```bash
docker-compose restart telegram_bot
```

### Frontend Issues

**Issue: Can't connect to API**
```bash
# Check VITE_API_URL in .env
echo $VITE_API_URL

# Should be: http://localhost:8000

# Restart frontend
docker-compose restart frontend
# or
npm run dev
```

### Binance Connection Issues

**Issue: Invalid API key**
- Double-check API key and secret in .env
- Make sure there are no extra spaces
- Verify API restrictions allow trading

**Issue: IP not whitelisted**
- Add your IP to Binance API restrictions
- For testnet, IP restrictions might not apply

**Issue: Insufficient permissions**
- Ensure "Enable Spot & Margin Trading" is checked
- Ensure "Enable Reading" is checked

## Next Steps

After successful installation:

1. **Read the [User Guide](USER_GUIDE.md)** to learn how to use the platform
2. **Review [Security Best Practices](SECURITY.md)** before live trading
3. **Test with testnet** before using real money
4. **Join the community** for support and updates

## Getting Help

- **Documentation:** Check other guides in `/docs`
- **Issues:** Report bugs at [GitHub Issues](https://github.com/emtsov-nik/crypto-trading-platform/issues)
- **Discussions:** Ask questions at [GitHub Discussions](https://github.com/emtsov-nik/crypto-trading-platform/discussions)
- **Telegram:** Join our community (link in README)

---

**Next:** [User Guide](USER_GUIDE.md) | [Developer Guide](DEVELOPER_GUIDE.md)
