#!/bin/bash
# Run E-Commerce Product Intelligence System

PROJECT_DIR="/root/projects/TSEC"
cd "$PROJECT_DIR"

echo "🚀 Starting TSEC System..."

# Kill existing
pkill -f "uvicorn" 2>/dev/null
pkill -f "vite" 2>/dev/null
sleep 2

# Load API key from .env
if [ -f "$PROJECT_DIR/.env" ]; then
    export $(grep -v '^#' "$PROJECT_DIR/.env" | xargs)
fi

# Start backend
echo "📦 Starting Backend..."
cd "$PROJECT_DIR/backend"
source venv/bin/activate
export PYTHONPATH="$PROJECT_DIR/backend"
export GEMINI_API_KEY="$GEMINI_API_KEY"
nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 > /tmp/tsec_backend.log 2>&1 &

# Wait for backend to be ready (with retry loop)
echo "Waiting for backend..."
MAX_RETRIES=30
RETRY_COUNT=0
while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -s http://localhost:8000/health 2>/dev/null | grep -q "healthy"; then
        echo "✅ Backend ready!"
        break
    fi
    RETRY_COUNT=$((RETRY_COUNT + 1))
    sleep 1
    echo -n "."
done
echo ""

if [ $RETRY_COUNT -ge $MAX_RETRIES ]; then
    echo "❌ Backend failed to start (timeout)"
    tail -30 /tmp/tsec_backend.log
    exit 1
fi

echo "✅ Backend: http://localhost:8000"
echo "✅ Products loaded at startup"

# Start frontend
echo "🎨 Starting Frontend..."
cd "$PROJECT_DIR/frontend"
nohup npm run dev > /tmp/tsec_frontend.log 2>&1 &
sleep 5

echo ""
echo "=========================================="
echo "🎉 ALL SERVICES RUNNING!"
echo "=========================================="
echo "  Backend:  http://localhost:8000"
echo "  API Docs: http://localhost:8000/docs"
echo "  Frontend: http://localhost:5173"
echo ""
echo "Press Ctrl+C to stop"
echo "=========================================="

# Keep alive
read -p ""