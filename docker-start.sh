#!/bin/bash
# Quick start script for Docker Desktop users

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔═══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║         Crypto Trading Platform - Docker Quick Start          ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    echo -e "${RED}✗${NC} Docker is not installed!"
    echo ""
    echo "Please install Docker Desktop:"
    echo "  Windows/Mac: https://www.docker.com/products/docker-desktop"
    echo "  Linux: sudo apt install docker.io docker-compose"
    exit 1
fi

# Check if Docker daemon is running
if ! docker info &> /dev/null; then
    echo -e "${RED}✗${NC} Docker is not running!"
    echo ""
    echo "Please start Docker Desktop and try again."
    exit 1
fi

echo -e "${GREEN}✓${NC} Docker is available and running"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚡${NC} Creating .env file from template..."
    cp .env.example .env
    echo -e "${GREEN}✓${NC} .env file created"
    echo ""
    echo -e "${YELLOW}⚠${NC}  IMPORTANT: Edit .env file to add your API keys:"
    echo "  - BINANCE_API_KEY"
    echo "  - BINANCE_API_SECRET"
    echo "  - TELEGRAM_BOT_TOKEN (optional)"
    echo ""
    read -p "Press Enter to continue with default settings..."
fi

echo ""
echo -e "${BLUE}Starting Docker containers...${NC}"
echo ""

# Build and start containers
docker-compose up -d --build

if [ $? -ne 0 ]; then
    echo ""
    echo -e "${RED}✗${NC} Failed to start containers"
    echo ""
    echo "Check logs with:"
    echo "  docker-compose logs"
    exit 1
fi

echo ""
echo -e "${YELLOW}⏳${NC} Waiting for services to be ready..."
echo ""

# Wait for backend to be healthy
for i in {1..60}; do
    if curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} Backend is ready!"
        break
    fi
    if [ $i -eq 60 ]; then
        echo -e "${RED}✗${NC} Backend failed to start within 60 seconds"
        echo ""
        echo "Check logs:"
        echo "  docker-compose logs backend"
        exit 1
    fi
    echo -n "."
    sleep 1
done

echo ""

# Wait for frontend to be ready
for i in {1..30}; do
    if curl -s http://localhost:3000 > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} Frontend is ready!"
        break
    fi
    if [ $i -eq 30 ]; then
        echo -e "${YELLOW}⚠${NC}  Frontend is taking longer than expected"
        echo ""
        echo "It should be available soon. Check logs:"
        echo "  docker-compose logs frontend"
        break
    fi
    echo -n "."
    sleep 1
done

echo ""
echo -e "${GREEN}╔═══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║              Application Started Successfully! 🎉             ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}Access the application:${NC}"
echo ""
echo -e "  🌐 Web UI:       ${GREEN}http://localhost:3000${NC}"
echo -e "  📚 API Docs:     ${GREEN}http://localhost:8000/docs${NC}"
echo -e "  ❤️  Health Check: ${GREEN}http://localhost:8000/api/health${NC}"
echo ""
echo -e "${BLUE}Running containers:${NC}"
docker-compose ps
echo ""
echo -e "${BLUE}Useful commands:${NC}"
echo ""
echo -e "  View logs:         ${YELLOW}docker-compose logs -f${NC}"
echo -e "  View backend logs: ${YELLOW}docker-compose logs -f backend${NC}"
echo -e "  Stop all:          ${YELLOW}docker-compose down${NC}"
echo -e "  Restart:           ${YELLOW}docker-compose restart${NC}"
echo -e "  Status:            ${YELLOW}docker-compose ps${NC}"
echo ""
echo -e "${GREEN}Happy Trading! 🚀${NC}"
echo ""
