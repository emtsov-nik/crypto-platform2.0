#!/bin/bash
# Script to start required services for local development

set -e

echo "🔍 Checking environment..."

# Check if Docker is available
if command -v docker &> /dev/null && docker info &> /dev/null; then
    echo "✅ Docker is available"
    echo ""
    echo "Starting services with Docker..."

    # Check if .env exists
    if [ ! -f .env ]; then
        echo "Creating .env file from .env.example..."
        cp .env.example .env
        echo "⚠️  Please edit .env with your Binance API keys!"
    fi

    echo "Starting PostgreSQL, Redis, and Backend..."
    docker compose up -d postgres redis backend

    echo ""
    echo "✅ Services started!"
    echo "Waiting for backend to be ready..."

    # Wait for backend
    for i in {1..30}; do
        if curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
            echo "✅ Backend is ready!"
            break
        fi
        echo -n "."
        sleep 1
    done

    echo ""
    echo "You can now start the frontend:"
    echo "  cd frontend"
    echo "  npm install"
    echo "  npm run dev"

else
    echo "❌ Docker is not available"
    echo ""
    echo "To run this application, you need to either:"
    echo ""
    echo "Option 1: Install Docker (RECOMMENDED)"
    echo "  - Visit: https://docs.docker.com/get-docker/"
    echo "  - Then run: docker compose up -d"
    echo ""
    echo "Option 2: Manual setup"
    echo "  1. Start PostgreSQL:"
    echo "     sudo systemctl start postgresql"
    echo "     createdb trading_db"
    echo ""
    echo "  2. Start Redis:"
    echo "     sudo systemctl start redis"
    echo ""
    echo "  3. Create .env file:"
    echo "     cp .env.example .env"
    echo "     # Edit .env with your config"
    echo ""
    echo "  4. Start backend:"
    echo "     cd backend"
    echo "     python3 -m venv venv"
    echo "     source venv/bin/activate"
    echo "     pip install -r requirements.txt"
    echo "     uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
    echo ""
    echo "  5. Start frontend (in new terminal):"
    echo "     cd frontend"
    echo "     npm install"
    echo "     npm run dev"
    echo ""
    echo "See DEVELOPMENT_LOCAL.md for detailed instructions"
fi
