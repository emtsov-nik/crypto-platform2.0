# 🚀 Quick Start Guide

Get the Crypto Trading Platform up and running in minutes!

## One-Command Setup

```bash
./setup.sh
```

This script will automatically:
- ✅ Detect your operating system
- ✅ Check for required software (PostgreSQL, Redis, Python, Node.js)
- ✅ Install missing dependencies (with your permission)
- ✅ Start PostgreSQL and Redis services
- ✅ Create and configure the database
- ✅ Generate .env configuration file
- ✅ Set up Python virtual environment
- ✅ Install all backend dependencies
- ✅ Run database migrations
- ✅ Install all frontend dependencies

## One-Command Run

After setup is complete, start everything with:

```bash
./run.sh
```

Then open your browser to: **http://localhost:5173**

## Available Commands

### Start Services

```bash
# Start both backend and frontend
./run.sh

# Start only backend
./run.sh backend

# Start only frontend
./run.sh frontend
```

### Stop Services

```bash
./run.sh stop
```

### Check Status

```bash
./run.sh status

# Or use the dedicated status script
./check_status.sh
```

### Restart Services

```bash
./run.sh restart
```

## What Gets Installed

### System Services
- **PostgreSQL** - Database server
- **Redis** - Cache and message broker

### Python Packages
- FastAPI, Uvicorn
- SQLAlchemy, Alembic
- Celery, Redis client
- CCXT, python-binance
- And more... (see backend/requirements.txt)

### Node.js Packages
- React, React Router
- Vite, TypeScript
- TanStack Query
- Axios
- And more... (see frontend/package.json)

## Configuration

After setup, edit the `.env` file to configure:

```bash
# Required for live trading
BINANCE_API_KEY=your_api_key_here
BINANCE_API_SECRET=your_api_secret_here

# Optional: Telegram bot
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_ALLOWED_USER_IDS=your_telegram_id
```

**Important:** Keep `BINANCE_TESTNET=true` until you're ready for live trading!

## Accessing the Application

Once running, you can access:

- 🌐 **Web Interface**: http://localhost:5173
- 📚 **API Documentation**: http://localhost:8000/docs
- ❤️ **Health Check**: http://localhost:8000/api/health

## Troubleshooting

### Setup fails with permission errors

Some steps require sudo access. Run:
```bash
./setup.sh
```
And enter your password when prompted.

### Services won't start

Check individual service status:
```bash
./check_status.sh
```

Start services manually if needed:
```bash
# PostgreSQL
sudo systemctl start postgresql

# Redis
sudo systemctl start redis-server
```

### Backend won't start

Check the logs:
```bash
tail -f backend.log
```

Common issues:
- Database connection: Check PostgreSQL is running
- Redis connection: Check Redis is running
- Port 8000 in use: Kill the process using port 8000

### Frontend shows "Network Error"

This means the backend is not running. Start it:
```bash
./run.sh backend
```

Then restart frontend:
```bash
./run.sh stop
./run.sh frontend
```

### Database errors

Reset the database:
```bash
sudo -u postgres dropdb trading_db
sudo -u postgres createdb trading_db

cd backend
source venv/bin/activate
alembic upgrade head
```

## View Logs

```bash
# Backend logs
tail -f backend.log

# Frontend logs
tail -f frontend.log

# Both at once
tail -f backend.log frontend.log
```

## Manual Setup (Alternative)

If you prefer manual setup or the script doesn't work for your system, see:
- [DEVELOPMENT_LOCAL.md](DEVELOPMENT_LOCAL.md) - Detailed local setup
- [README.md](README.md) - Docker setup

## Need Help?

1. Check the logs (backend.log, frontend.log)
2. Run status check: `./check_status.sh`
3. See detailed guides in docs/ folder
4. Open an issue on GitHub

## What's Next?

1. **Configure API Keys**: Edit `.env` with your Binance API credentials
2. **Explore the Dashboard**: Open http://localhost:5173
3. **Try Backtesting**: Create a strategy and run a backtest
4. **Read the Docs**: Check out docs/USER_GUIDE.md
5. **Create Custom Strategies**: See docs/STRATEGY_EXAMPLES.md

Happy Trading! 🚀
