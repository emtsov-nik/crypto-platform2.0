#!/bin/bash

echo "=== Auto-formatting Code ==="
echo ""

# Check if we're in the backend directory
if [ ! -f "requirements.txt" ]; then
    echo "Error: Please run this script from the backend directory"
    exit 1
fi

echo "Installing formatting tools..."
pip install black isort flake8 -q

echo ""
echo "1. Running isort to fix import ordering..."
isort app/ tests/ --profile black

echo ""
echo "2. Running black to fix code formatting..."
black app/ tests/

echo ""
echo "3. Checking with flake8..."
flake8 app/ --count --statistics

echo ""
echo "=== Formatting complete ==="
echo "Note: Review changes with 'git diff' before committing"
