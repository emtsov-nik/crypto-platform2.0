#!/bin/bash
# Automated setup script for Crypto Trading Platform
# This script will install and configure everything needed to run the platform

set -e  # Exit on error

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     Crypto Trading Platform - Automated Setup             ║${NC}"
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo ""

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check service status
check_service() {
    if systemctl is-active --quiet "$1" 2>/dev/null; then
        return 0
    else
        return 1
    fi
}

# Detect OS
detect_os() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS=$ID
        VER=$VERSION_ID
    elif command_exists lsb_release; then
        OS=$(lsb_release -si | tr '[:upper:]' '[:lower:]')
        VER=$(lsb_release -sr)
    else
        OS=$(uname -s | tr '[:upper:]' '[:lower:]')
    fi
    echo -e "${GREEN}✓${NC} Detected OS: $OS $VER"
}

echo -e "${BLUE}[1/8] Detecting system...${NC}"
detect_os

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo -e "${YELLOW}⚠${NC}  Running as root. This is not recommended for development."
    echo -e "   Consider running without sudo (script will ask for sudo when needed)"
fi

echo ""
echo -e "${BLUE}[2/8] Checking required software...${NC}"

NEED_INSTALL=()

# Check PostgreSQL
if command_exists psql; then
    echo -e "${GREEN}✓${NC} PostgreSQL is installed"
else
    echo -e "${YELLOW}✗${NC} PostgreSQL is not installed"
    NEED_INSTALL+=("postgresql")
fi

# Check Redis
if command_exists redis-cli; then
    echo -e "${GREEN}✓${NC} Redis is installed"
else
    echo -e "${YELLOW}✗${NC} Redis is not installed"
    NEED_INSTALL+=("redis")
fi

# Check Python
if command_exists python3; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    echo -e "${GREEN}✓${NC} Python $PYTHON_VERSION is installed"

    # Check if version is >= 3.11
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)
    if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 11 ]); then
        echo -e "${YELLOW}⚠${NC}  Python 3.11+ is recommended (you have $PYTHON_VERSION)"
    fi
else
    echo -e "${YELLOW}✗${NC} Python 3 is not installed"
    NEED_INSTALL+=("python3")
fi

# Check pip
if command_exists pip3; then
    echo -e "${GREEN}✓${NC} pip3 is installed"
else
    echo -e "${YELLOW}✗${NC} pip3 is not installed"
    NEED_INSTALL+=("python3-pip")
fi

# Check Node.js
if command_exists node; then
    NODE_VERSION=$(node --version)
    echo -e "${GREEN}✓${NC} Node.js $NODE_VERSION is installed"
else
    echo -e "${YELLOW}✗${NC} Node.js is not installed"
    NEED_INSTALL+=("nodejs")
fi

# Check npm
if command_exists npm; then
    NPM_VERSION=$(npm --version)
    echo -e "${GREEN}✓${NC} npm $NPM_VERSION is installed"
else
    echo -e "${YELLOW}✗${NC} npm is not installed"
    NEED_INSTALL+=("npm")
fi

# Install missing packages
if [ ${#NEED_INSTALL[@]} -gt 0 ]; then
    echo ""
    echo -e "${YELLOW}[!] Missing packages: ${NEED_INSTALL[*]}${NC}"
    echo ""
    read -p "Do you want to install missing packages? (y/n) " -n 1 -r
    echo

    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${BLUE}Installing packages...${NC}"

        if [ "$OS" = "ubuntu" ] || [ "$OS" = "debian" ]; then
            sudo apt-get update
            for pkg in "${NEED_INSTALL[@]}"; do
                case $pkg in
                    postgresql)
                        sudo apt-get install -y postgresql postgresql-contrib
                        ;;
                    redis)
                        sudo apt-get install -y redis-server
                        ;;
                    python3)
                        sudo apt-get install -y python3 python3-venv python3-dev
                        ;;
                    python3-pip)
                        sudo apt-get install -y python3-pip
                        ;;
                    nodejs)
                        sudo apt-get install -y nodejs npm
                        ;;
                esac
            done
        elif [ "$OS" = "centos" ] || [ "$OS" = "rhel" ] || [ "$OS" = "fedora" ]; then
            for pkg in "${NEED_INSTALL[@]}"; do
                case $pkg in
                    postgresql)
                        sudo yum install -y postgresql postgresql-server
                        ;;
                    redis)
                        sudo yum install -y redis
                        ;;
                    python3)
                        sudo yum install -y python3 python3-devel
                        ;;
                    python3-pip)
                        sudo yum install -y python3-pip
                        ;;
                    nodejs)
                        sudo yum install -y nodejs npm
                        ;;
                esac
            done
        else
            echo -e "${RED}✗${NC} Automatic installation not supported for $OS"
            echo "   Please install manually: ${NEED_INSTALL[*]}"
            exit 1
        fi
    else
        echo -e "${RED}✗${NC} Cannot proceed without required packages"
        exit 1
    fi
fi

echo ""
echo -e "${BLUE}[3/8] Starting required services...${NC}"

# Start PostgreSQL
if check_service postgresql; then
    echo -e "${GREEN}✓${NC} PostgreSQL is running"
else
    echo -e "${YELLOW}⚡${NC} Starting PostgreSQL..."
    sudo systemctl start postgresql 2>/dev/null || true
    sudo systemctl enable postgresql 2>/dev/null || true
    sleep 2
    if check_service postgresql; then
        echo -e "${GREEN}✓${NC} PostgreSQL started successfully"
    else
        echo -e "${YELLOW}⚠${NC}  PostgreSQL service not available via systemctl"
        echo "   You may need to start it manually"
    fi
fi

# Start Redis
if check_service redis-server || check_service redis; then
    echo -e "${GREEN}✓${NC} Redis is running"
else
    echo -e "${YELLOW}⚡${NC} Starting Redis..."
    sudo systemctl start redis-server 2>/dev/null || sudo systemctl start redis 2>/dev/null || true
    sudo systemctl enable redis-server 2>/dev/null || sudo systemctl enable redis 2>/dev/null || true
    sleep 1
    if check_service redis-server || check_service redis; then
        echo -e "${GREEN}✓${NC} Redis started successfully"
    else
        echo -e "${YELLOW}⚠${NC}  Redis service not available via systemctl"
        echo "   You may need to start it manually"
    fi
fi

echo ""
echo -e "${BLUE}[4/8] Configuring database...${NC}"

# Create database if it doesn't exist
DB_NAME="trading_db"
DB_USER="trading_user"
DB_PASSWORD="trading_password_$(date +%s)"

if sudo -u postgres psql -lqt 2>/dev/null | cut -d \| -f 1 | grep -qw "$DB_NAME"; then
    echo -e "${GREEN}✓${NC} Database '$DB_NAME' already exists"
else
    echo -e "${YELLOW}⚡${NC} Creating database '$DB_NAME'..."

    # Create user
    sudo -u postgres psql -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';" 2>/dev/null || true

    # Create database
    sudo -u postgres createdb -O $DB_USER $DB_NAME 2>/dev/null || true

    if sudo -u postgres psql -lqt 2>/dev/null | cut -d \| -f 1 | grep -qw "$DB_NAME"; then
        echo -e "${GREEN}✓${NC} Database created successfully"
        echo -e "   User: $DB_USER"
        echo -e "   Password: $DB_PASSWORD"
    else
        echo -e "${YELLOW}⚠${NC}  Could not create database automatically"
        echo "   You may need to create it manually:"
        echo "   sudo -u postgres createdb $DB_NAME"
    fi
fi

echo ""
echo -e "${BLUE}[5/8] Creating .env file...${NC}"

if [ -f .env ]; then
    echo -e "${YELLOW}⚠${NC}  .env file already exists"
    read -p "Do you want to overwrite it? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${GREEN}✓${NC} Keeping existing .env file"
    else
        cp .env.example .env
        # Update database settings
        sed -i "s/POSTGRES_USER=.*/POSTGRES_USER=$DB_USER/" .env
        sed -i "s/POSTGRES_PASSWORD=.*/POSTGRES_PASSWORD=$DB_PASSWORD/" .env
        sed -i "s/POSTGRES_DB=.*/POSTGRES_DB=$DB_NAME/" .env
        sed -i "s|DATABASE_URL=.*|DATABASE_URL=postgresql://$DB_USER:$DB_PASSWORD@localhost:5432/$DB_NAME|" .env
        sed -i "s|REDIS_URL=.*|REDIS_URL=redis://localhost:6379/0|" .env
        echo -e "${GREEN}✓${NC} .env file created"
    fi
else
    cp .env.example .env
    # Update database settings
    sed -i "s/POSTGRES_USER=.*/POSTGRES_USER=$DB_USER/" .env
    sed -i "s/POSTGRES_PASSWORD=.*/POSTGRES_PASSWORD=$DB_PASSWORD/" .env
    sed -i "s/POSTGRES_DB=.*/POSTGRES_DB=$DB_NAME/" .env
    sed -i "s|DATABASE_URL=.*|DATABASE_URL=postgresql://$DB_USER:$DB_PASSWORD@localhost:5432/$DB_NAME|" .env
    sed -i "s|REDIS_URL=.*|REDIS_URL=redis://localhost:6379/0|" .env
    echo -e "${GREEN}✓${NC} .env file created"
fi

echo ""
echo -e "${BLUE}[6/8] Setting up Python backend...${NC}"

cd backend

# Create virtual environment
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}⚡${NC} Creating Python virtual environment..."
    python3 -m venv venv
    echo -e "${GREEN}✓${NC} Virtual environment created"
else
    echo -e "${GREEN}✓${NC} Virtual environment already exists"
fi

# Activate and install dependencies
echo -e "${YELLOW}⚡${NC} Installing Python dependencies..."
source venv/bin/activate
pip install --upgrade pip setuptools wheel > /dev/null
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} Python dependencies installed"
else
    echo -e "${RED}✗${NC} Failed to install Python dependencies"
    exit 1
fi

# Run migrations
if command_exists alembic; then
    echo -e "${YELLOW}⚡${NC} Running database migrations..."
    alembic upgrade head 2>/dev/null || echo -e "${YELLOW}⚠${NC}  Migrations skipped (run manually if needed)"
fi

deactivate
cd ..

echo ""
echo -e "${BLUE}[7/8] Setting up frontend...${NC}"

cd frontend

# Create .env if doesn't exist
if [ ! -f .env ]; then
    cp .env.example .env
    echo -e "${GREEN}✓${NC} Frontend .env created"
fi

# Install npm dependencies
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}⚡${NC} Installing npm dependencies..."
    npm install
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓${NC} npm dependencies installed"
    else
        echo -e "${RED}✗${NC} Failed to install npm dependencies"
        exit 1
    fi
else
    echo -e "${GREEN}✓${NC} npm dependencies already installed"
fi

cd ..

echo ""
echo -e "${BLUE}[8/8] Setup complete!${NC}"
echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                  Setup Completed!                         ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${YELLOW}⚠  IMPORTANT: Configure your API keys in .env file:${NC}"
echo -e "   - BINANCE_API_KEY"
echo -e "   - BINANCE_API_SECRET"
echo -e "   - TELEGRAM_BOT_TOKEN (optional)"
echo ""
echo -e "${BLUE}To start the application:${NC}"
echo -e "   ./run.sh"
echo ""
echo -e "${BLUE}Or manually:${NC}"
echo -e "   Terminal 1: ./run.sh backend"
echo -e "   Terminal 2: ./run.sh frontend"
echo ""
