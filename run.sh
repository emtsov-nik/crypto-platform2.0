#!/bin/bash
# Automated run script for Crypto Trading Platform
# Usage:
#   ./run.sh           - Start both backend and frontend
#   ./run.sh backend   - Start only backend
#   ./run.sh frontend  - Start only frontend
#   ./run.sh stop      - Stop all services

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_PID_FILE="$PROJECT_DIR/.backend.pid"
FRONTEND_PID_FILE="$PROJECT_DIR/.frontend.pid"

# Function to check if service is running
is_running() {
    if [ -f "$1" ]; then
        PID=$(cat "$1")
        if ps -p "$PID" > /dev/null 2>&1; then
            return 0
        else
            rm -f "$1"
            return 1
        fi
    fi
    return 1
}

# Function to stop service
stop_service() {
    if [ -f "$1" ]; then
        PID=$(cat "$1")
        if ps -p "$PID" > /dev/null 2>&1; then
            echo -e "${YELLOW}⚡${NC} Stopping process $PID..."
            kill "$PID" 2>/dev/null || true
            sleep 2
            if ps -p "$PID" > /dev/null 2>&1; then
                echo -e "${YELLOW}⚡${NC} Force stopping..."
                kill -9 "$PID" 2>/dev/null || true
            fi
            echo -e "${GREEN}✓${NC} Stopped"
        fi
        rm -f "$1"
    fi
}

# Function to start backend
start_backend() {
    if is_running "$BACKEND_PID_FILE"; then
        echo -e "${YELLOW}⚠${NC}  Backend is already running (PID: $(cat $BACKEND_PID_FILE))"
        return 0
    fi

    echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║              Starting Backend Server                      ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""

    # Check if setup was run
    if [ ! -d "$PROJECT_DIR/backend/venv" ]; then
        echo -e "${RED}✗${NC} Backend not set up. Please run ./setup.sh first"
        return 1
    fi

    # Check services
    echo -e "${BLUE}Checking required services...${NC}"

    # Check Redis
    if redis-cli ping > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} Redis is running"
    else
        echo -e "${YELLOW}⚡${NC} Starting Redis..."
        sudo systemctl start redis-server 2>/dev/null || sudo systemctl start redis 2>/dev/null || true
        sleep 1
        if ! redis-cli ping > /dev/null 2>&1; then
            echo -e "${RED}✗${NC} Failed to start Redis"
            echo "   Start it manually: sudo systemctl start redis"
            return 1
        fi
        echo -e "${GREEN}✓${NC} Redis started"
    fi

    # Check PostgreSQL
    if pg_isready > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} PostgreSQL is running"
    else
        echo -e "${YELLOW}⚡${NC} Starting PostgreSQL..."
        sudo systemctl start postgresql 2>/dev/null || true
        sleep 2
        if ! pg_isready > /dev/null 2>&1; then
            echo -e "${RED}✗${NC} Failed to start PostgreSQL"
            echo "   Start it manually: sudo systemctl start postgresql"
            return 1
        fi
        echo -e "${GREEN}✓${NC} PostgreSQL started"
    fi

    echo ""
    echo -e "${YELLOW}⚡${NC} Starting backend server..."

    cd "$PROJECT_DIR/backend"
    source venv/bin/activate

    # Start uvicorn in background
    nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload \
        > "$PROJECT_DIR/backend.log" 2>&1 &

    BACKEND_PID=$!
    echo $BACKEND_PID > "$BACKEND_PID_FILE"

    # Wait for backend to start
    echo -e "${YELLOW}⏳${NC} Waiting for backend to start..."
    for i in {1..30}; do
        if curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
            echo -e "${GREEN}✓${NC} Backend started successfully!"
            echo -e "   PID: $BACKEND_PID"
            echo -e "   URL: ${BLUE}http://localhost:8000${NC}"
            echo -e "   API Docs: ${BLUE}http://localhost:8000/docs${NC}"
            echo -e "   Logs: ${BLUE}$PROJECT_DIR/backend.log${NC}"
            return 0
        fi
        echo -n "."
        sleep 1
    done

    echo ""
    echo -e "${RED}✗${NC} Backend failed to start within 30 seconds"
    echo -e "   Check logs: tail -f $PROJECT_DIR/backend.log"
    return 1
}

# Function to start frontend
start_frontend() {
    if is_running "$FRONTEND_PID_FILE"; then
        echo -e "${YELLOW}⚠${NC}  Frontend is already running (PID: $(cat $FRONTEND_PID_FILE))"
        return 0
    fi

    echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║              Starting Frontend Server                     ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""

    # Check if setup was run
    if [ ! -d "$PROJECT_DIR/frontend/node_modules" ]; then
        echo -e "${RED}✗${NC} Frontend not set up. Please run ./setup.sh first"
        return 1
    fi

    # Check if backend is running
    if ! curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
        echo -e "${YELLOW}⚠${NC}  Backend is not running. Frontend will show errors."
        echo -e "   Start backend first: ./run.sh backend"
        echo ""
        read -p "Continue anyway? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            return 1
        fi
    else
        echo -e "${GREEN}✓${NC} Backend is running"
    fi

    echo ""
    echo -e "${YELLOW}⚡${NC} Starting frontend server..."

    cd "$PROJECT_DIR/frontend"

    # Start npm dev in background
    nohup npm run dev -- --host 0.0.0.0 \
        > "$PROJECT_DIR/frontend.log" 2>&1 &

    FRONTEND_PID=$!
    echo $FRONTEND_PID > "$FRONTEND_PID_FILE"

    # Wait for frontend to start
    echo -e "${YELLOW}⏳${NC} Waiting for frontend to start..."
    for i in {1..30}; do
        if curl -s http://localhost:5173 > /dev/null 2>&1; then
            echo -e "${GREEN}✓${NC} Frontend started successfully!"
            echo -e "   PID: $FRONTEND_PID"
            echo -e "   URL: ${BLUE}http://localhost:5173${NC}"
            echo -e "   Logs: ${BLUE}$PROJECT_DIR/frontend.log${NC}"
            echo ""
            echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
            echo -e "${GREEN}║          Application is Ready!                            ║${NC}"
            echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
            echo ""
            echo -e "   Open in browser: ${BLUE}http://localhost:5173${NC}"
            echo ""
            echo -e "   To view logs:"
            echo -e "     Backend:  tail -f $PROJECT_DIR/backend.log"
            echo -e "     Frontend: tail -f $PROJECT_DIR/frontend.log"
            echo ""
            echo -e "   To stop: ./run.sh stop"
            echo ""
            return 0
        fi
        echo -n "."
        sleep 1
    done

    echo ""
    echo -e "${RED}✗${NC} Frontend failed to start within 30 seconds"
    echo -e "   Check logs: tail -f $PROJECT_DIR/frontend.log"
    return 1
}

# Function to stop all services
stop_all() {
    echo -e "${BLUE}Stopping all services...${NC}"
    echo ""

    echo -n "Frontend: "
    stop_service "$FRONTEND_PID_FILE"

    echo -n "Backend: "
    stop_service "$BACKEND_PID_FILE"

    echo ""
    echo -e "${GREEN}✓${NC} All services stopped"
}

# Function to show status
show_status() {
    echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║              Service Status                               ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""

    # Check backend
    echo -n "Backend:    "
    if is_running "$BACKEND_PID_FILE"; then
        echo -e "${GREEN}✓ Running${NC} (PID: $(cat $BACKEND_PID_FILE))"
    else
        echo -e "${RED}✗ Not running${NC}"
    fi

    # Check frontend
    echo -n "Frontend:   "
    if is_running "$FRONTEND_PID_FILE"; then
        echo -e "${GREEN}✓ Running${NC} (PID: $(cat $FRONTEND_PID_FILE))"
    else
        echo -e "${RED}✗ Not running${NC}"
    fi

    # Check Redis
    echo -n "Redis:      "
    if redis-cli ping > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Running${NC}"
    else
        echo -e "${RED}✗ Not running${NC}"
    fi

    # Check PostgreSQL
    echo -n "PostgreSQL: "
    if pg_isready > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Running${NC}"
    else
        echo -e "${RED}✗ Not running${NC}"
    fi

    echo ""

    # Show URLs if services are running
    if is_running "$BACKEND_PID_FILE" && is_running "$FRONTEND_PID_FILE"; then
        echo -e "${BLUE}URLs:${NC}"
        echo -e "  Frontend:  http://localhost:5173"
        echo -e "  Backend:   http://localhost:8000"
        echo -e "  API Docs:  http://localhost:8000/docs"
    fi
}

# Main script
case "${1:-all}" in
    backend)
        start_backend
        ;;
    frontend)
        start_frontend
        ;;
    stop)
        stop_all
        ;;
    status)
        show_status
        ;;
    restart)
        stop_all
        sleep 2
        start_backend
        sleep 2
        start_frontend
        ;;
    all|*)
        start_backend
        if [ $? -eq 0 ]; then
            sleep 2
            start_frontend
        fi
        ;;
esac
