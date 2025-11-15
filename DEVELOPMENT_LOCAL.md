# Local Development Setup (Without Docker)

This guide helps you run the Crypto Trading Platform locally without Docker.

## ⚠️ Important: Backend Must Be Running

The frontend requires the backend API server to be running on port 8000. Without it, you'll see:
```
Error loading data: AxiosError: Network Error
```

## Quick Start

### Option 1: Start Backend Locally (Recommended for Development)

1. **Install PostgreSQL and Redis** (if not already installed):
   ```bash
   # macOS
   brew install postgresql@15 redis
   brew services start postgresql@15
   brew services start redis

   # Ubuntu/Debian
   sudo apt-get install postgresql-15 redis-server
   sudo systemctl start postgresql
   sudo systemctl start redis
   ```

2. **Set up Python environment**:
   ```bash
   cd backend
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Create .env file**:
   ```bash
   cp ../.env.example ../.env
   # Edit .env with your configuration
   ```

4. **Initialize database**:
   ```bash
   # Create database
   createdb trading_db

   # Run migrations
   alembic upgrade head
   ```

5. **Start backend server**:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

6. **In a new terminal, start frontend**:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

7. **Access the application**:
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

### Option 2: Use Docker for Backend Only

If you have Docker but want to run frontend locally:

1. **Start only backend services**:
   ```bash
   docker-compose up -d postgres redis backend
   ```

2. **Start frontend locally**:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

The Vite proxy will automatically forward API requests to the backend.

### Option 3: Full Docker Setup

```bash
docker-compose up -d
```

Access frontend at http://localhost:3000 (Note: different port!)

## Troubleshooting

### "Network Error" in Chart page

**Cause**: Backend is not running on port 8000

**Solutions**:
1. Check if backend is running: `curl http://localhost:8000/api/health`
2. Start backend using one of the options above
3. Check backend logs for errors

### Backend Port Conflicts

If port 8000 is already in use:

1. Find and kill the process:
   ```bash
   lsof -ti:8000 | xargs kill -9
   ```

2. Or use a different port:
   ```bash
   # Edit .env
   BACKEND_PORT=8001

   # Edit frontend/.env
   VITE_BACKEND_URL=http://localhost:8001

   # Start backend
   uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
   ```

### Database Connection Errors

If you see database connection errors:

1. Ensure PostgreSQL is running:
   ```bash
   # Check status
   pg_isready

   # Or
   sudo systemctl status postgresql
   ```

2. Check database exists:
   ```bash
   psql -l | grep trading_db
   ```

3. Verify credentials in .env match your PostgreSQL setup

### Redis Connection Errors

1. Check if Redis is running:
   ```bash
   redis-cli ping
   # Should return: PONG
   ```

2. Start Redis if needed:
   ```bash
   # macOS
   brew services start redis

   # Linux
   sudo systemctl start redis
   ```

## Environment Variables

### Frontend (.env in frontend/)

```env
# Leave empty to use Vite proxy (recommended)
VITE_API_URL=

# Optional: override backend URL for proxy
# VITE_BACKEND_URL=http://localhost:8000
```

### Backend (.env in project root)

See `.env.example` for full configuration. Minimum required:

```env
# Database
POSTGRES_USER=trading_user
POSTGRES_PASSWORD=your_password
POSTGRES_DB=trading_db
DATABASE_URL=postgresql://trading_user:your_password@localhost:5432/trading_db

# Redis
REDIS_URL=redis://localhost:6379/0

# Binance (use testnet for development!)
BINANCE_API_KEY=your_api_key
BINANCE_API_SECRET=your_api_secret
BINANCE_TESTNET=true

# App
SECRET_KEY=your-secret-key-min-32-chars
DEBUG=true
```

## Development Tips

1. **Hot Reload**: Both frontend and backend support hot reload in development mode
2. **API Docs**: Visit http://localhost:8000/docs to explore API endpoints
3. **Logs**: Backend logs appear in the terminal where you ran uvicorn
4. **Database**: Use `psql trading_db` to inspect database directly

## Need Help?

- Check the [main README](README.md) for Docker setup
- See [Developer Guide](docs/DEVELOPER_GUIDE.md) for architecture details
- Open an issue on GitHub if you encounter problems
