#!/bin/bash

echo "=== Checking GitHub Workflow Issues ==="
echo ""

# Navigate to backend
cd /home/user/Binance_bot/backend

echo "1. Checking if pytest-cov is needed..."
pip list | grep pytest-cov || echo "   pytest-cov NOT installed"

echo ""
echo "2. Checking Python syntax errors..."
python -m py_compile app/main.py 2>&1 | head -20

echo ""
echo "3. Checking import structure in main files..."
find app -name "*.py" -type f | head -10

echo ""
echo "4. Testing basic imports..."
python -c "from app.config import settings; print('✓ Config imports OK')" 2>&1 || echo "✗ Config import failed"
python -c "from app.database import Base; print('✓ Database imports OK')" 2>&1 || echo "✗ Database import failed"
python -c "from app.strategies.rsi_bb_strategy import RSIBBStrategy; print('✓ Strategy imports OK')" 2>&1 || echo "✗ Strategy import failed"

echo ""
echo "5. Checking for common issues..."
grep -r "from app import" app/ | head -5 && echo "Found 'from app import' statements" || echo "No 'from app import' issues"

echo ""
echo "=== Check complete ==="
