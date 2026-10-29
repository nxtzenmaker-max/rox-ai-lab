#!/usr/bin/env bash
set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

echo "=========================================="
echo "🚀 STARTING ROX AI LAB - 3D & PHONE AGENT"
echo "=========================================="

# Check venv
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    ./venv/bin/pip install --upgrade pip
    ./venv/bin/pip install -r requirements.txt
fi

# Load .env if exists
if [ -f ".env" ]; then
    export $(grep -v '^#' .env | xargs)
fi

PORT="${PORT:-8000}"

echo "🤖 Starting Rox FastAPI Server on port $PORT..."
./venv/bin/uvicorn server:app --host 0.0.0.0 --port "$PORT" &
SERVER_PID=$!

# Trap signals to cleanup background server
cleanup() {
    echo "🛑 Shutting down server..."
    kill $SERVER_PID 2>/dev/null || true
    exit 0
}
trap cleanup SIGINT SIGTERM EXIT

sleep 2

# Check if cloudflared is available
CLOUDFLARED_BIN=""
if [ -x "/home/ipx/cloudflared" ]; then
    CLOUDFLARED_BIN="/home/ipx/cloudflared"
elif which cloudflared >/dev/null 2>&1; then
    CLOUDFLARED_BIN="$(which cloudflared)"
fi

if [ -n "$CLOUDFLARED_BIN" ]; then
    echo "🌐 Starting Cloudflare Public Tunnel for Mobile / Web / Twilio..."
    echo "👉 Share the generated URL to open Rox on your phone!"
    echo "--------------------------------------------------------"
    "$CLOUDFLARED_BIN" tunnel --url "http://localhost:$PORT"
else
    echo "✅ Rox server running locally at: http://localhost:$PORT"
    wait $SERVER_PID
fi
