#!/bin/bash
# Plex GPU Balancer System Service Installer

set -e  # Exit on any error

echo "Plex GPU Balancer Service Installer"
echo "==================================="

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Error: This script must be run as root"
    echo "Please run: sudo ./install.sh"
    exit 1
fi

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

echo "Project root: $PROJECT_ROOT"

# Verify project structure
if [ ! -f "$PROJECT_ROOT/src/gpu_collector_service.py" ] || \
   [ ! -f "$PROJECT_ROOT/src/dashboard.py" ] || \
   [ ! -f "$PROJECT_ROOT/src/plex_balancer.py" ]; then
    echo "Error: Required Python files not found in $PROJECT_ROOT/src/"
    exit 1
fi

# Create temporary directory for modified service files
TEMP_DIR=$(mktemp -d)
echo "Preparing service files..."

# Process each service file
for service in plex-gpu-collector.service plex-dashboard.service plex-balancer.service; do
    if [ ! -f "$PROJECT_ROOT/systemd/$service" ]; then
        echo "Error: Service file $service not found"
        exit 1
    fi
    
    # Replace PROJECT_PATH_PLACEHOLDER with actual path
    sed "s|PROJECT_PATH_PLACEHOLDER|$PROJECT_ROOT|g" \
        "$PROJECT_ROOT/systemd/$service" > "$TEMP_DIR/$service"
    
    echo "Prepared $service"
done

# Install service files
echo "Installing service files to /etc/systemd/system/..."
cp "$TEMP_DIR"/*.service /etc/systemd/system/

# Reload systemd
echo "Reloading systemd daemon..."
systemctl daemon-reload

# Enable services (this makes them autostart)
echo "Enabling services for autostart..."
systemctl enable plex-gpu-collector.service
systemctl enable plex-dashboard.service
systemctl enable plex-balancer.service

# Start services in order
echo "Starting services..."
systemctl start plex-gpu-collector.service
echo "GPU collector service started"

# Wait for collector to initialize
sleep 5

systemctl start plex-dashboard.service
echo "Dashboard service started"

systemctl start plex-balancer.service
echo "Balancer service started"

# Cleanup
rm -rf "$TEMP_DIR"

# Verify installation
echo ""
echo "Installation complete! Verifying services..."
for service in plex-gpu-collector plex-dashboard plex-balancer; do
    if systemctl is-active --quiet $service.service; then
        status="running"
    else
        status="stopped"
    fi
    
    if systemctl is-enabled --quiet $service.service; then
        autostart="enabled"
    else
        autostart="disabled"
    fi
    
    echo "$service: $status, autostart: $autostart"
done

echo ""
echo "Services will now start automatically on system boot."
echo "Dashboard available at: http://localhost:8080"
echo ""
echo "To check service status: systemctl status plex-gpu-collector"
echo "To view logs: journalctl -u plex-gpu-collector -f"
