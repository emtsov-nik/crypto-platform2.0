#!/bin/bash
# Script to check the status of all services

echo "🔍 Checking service status..."
echo ""

# Check Redis
echo -n "Redis:      "
if redis-cli ping > /dev/null 2>&1; then
    echo "✅ Running"
else
    echo "❌ Not running"
fi

# Check PostgreSQL
echo -n "PostgreSQL: "
if pg_isready > /dev/null 2>&1; then
    echo "✅ Running"
else
    echo "❌ Not running"
fi

# Check Backend
echo -n "Backend:    "
if curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
    echo "✅ Running on port 8000"
else
    echo "❌ Not running on port 8000"
fi

# Check Frontend
echo -n "Frontend:   "
if curl -s http://localhost:5173 > /dev/null 2>&1; then
    echo "✅ Running on port 5173"
else
    echo "❌ Not running on port 5173"
fi

# Check Docker
echo -n "Docker:     "
if command -v docker > /dev/null 2>&1 && docker info > /dev/null 2>&1; then
    echo "✅ Available"
else
    echo "❌ Not available"
fi

echo ""
echo "📋 Summary:"
if curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
    echo "✅ System is ready! Open http://localhost:5173"
else
    echo "❌ Backend is not running. Chart page will show Network Error."
    echo ""
    echo "To fix:"
    echo "  ./start_services.sh"
    echo ""
    echo "Or see: DEVELOPMENT_LOCAL.md"
fi
