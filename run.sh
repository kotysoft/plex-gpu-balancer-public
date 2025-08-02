#!/bin/bash
# Launcher for Plex GPU Balancer
echo '🚀 Starting Plex GPU Balancer'
echo '============================'

echo '✅ Using system Python installation'

# Get project root from config or use script location
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"

# Check if config exists and has project_path
if [ -f "$SCRIPT_DIR/config.conf" ]; then
    CONFIG_PROJECT_PATH=$(grep "^project_path" "$SCRIPT_DIR/config.conf" | cut -d'=' -f2 | xargs)
    if [ ! -z "$CONFIG_PROJECT_PATH" ]; then
        PROJECT_ROOT="$CONFIG_PROJECT_PATH"
    fi
fi

echo "📁 Project root: $PROJECT_ROOT"

# Set environment
export PYTHONPATH="$PROJECT_ROOT/src"

# Function to handle cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down services..."
    if [ ! -z "$GPU_COLLECTOR_PID" ]; then
        kill $GPU_COLLECTOR_PID 2>/dev/null
        echo "   ✅ Stopped GPU collector"
    fi
    if [ ! -z "$DASHBOARD_PID" ]; then
        kill $DASHBOARD_PID 2>/dev/null
        echo "   ✅ Stopped dashboard"
    fi
    if [ ! -z "$BALANCER_PID" ]; then
        kill $BALANCER_PID 2>/dev/null
        echo "   ✅ Stopped balancer"
    fi
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

cd "$PROJECT_ROOT/src"

echo '⚡ Starting GPU collector service...'
python3 gpu_collector_service.py &
GPU_COLLECTOR_PID=$!
echo "   ✅ GPU collector started (PID: $GPU_COLLECTOR_PID)"

# Wait for collector to initialize
sleep 5

echo '📊 Starting dashboard on port 8080...'
python3 dashboard.py &
DASHBOARD_PID=$!
echo "   ✅ Dashboard started (PID: $DASHBOARD_PID)"

echo '🧠 Starting balancer...'
python3 plex_balancer.py &
BALANCER_PID=$!
echo "   ✅ Balancer started (PID: $BALANCER_PID)"

echo ""
echo "🎯 Services running:"
echo "   ⚡ GPU Collector: Active"
echo "   📊 Dashboard: http://localhost:8080"
echo "   🧠 Balancer: Active"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for all processes
wait
