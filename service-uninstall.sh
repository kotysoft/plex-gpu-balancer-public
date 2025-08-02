#!/bin/bash
# Plex GPU Balancer System Service Uninstaller

echo "Plex GPU Balancer Service Uninstaller"
echo "====================================="

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Error: This script must be run as root"
    echo "Please run: sudo ./uninstall.sh"
    exit 1
fi

# Define services in reverse order for stopping
SERVICES=("plex-balancer" "plex-dashboard" "plex-gpu-collector")

echo "Stopping services..."
# Stop services in reverse order
for service in "${SERVICES[@]}"; do
    if systemctl is-active --quiet $service.service; then
        echo "Stopping $service..."
        systemctl stop $service.service
    else
        echo "$service is already stopped"
    fi
done

echo "Disabling services from autostart..."
# Disable services
for service in "${SERVICES[@]}"; do
    if systemctl is-enabled --quiet $service.service; then
        echo "Disabling $service..."
        systemctl disable $service.service
    else
        echo "$service is already disabled"
    fi
done

echo "Removing service files..."
# Remove service files
for service in "${SERVICES[@]}"; do
    service_file="/etc/systemd/system/$service.service"
    if [ -f "$service_file" ]; then
        echo "Removing $service.service..."
        rm "$service_file"
    else
        echo "$service.service not found (already removed)"
    fi
done

# Reload systemd to clean up
echo "Reloading systemd daemon..."
systemctl daemon-reload
systemctl reset-failed

echo ""
echo "Uninstallation complete! Verifying removal..."

# Verify removal
all_removed=true
for service in "${SERVICES[@]}"; do
    if systemctl list-unit-files --type=service | grep -q "$service.service"; then
        echo "Warning: $service.service still exists"
        all_removed=false
    else
        echo "$service.service: removed"
    fi
done

if [ "$all_removed" = true ]; then
    echo ""
    echo "All services successfully removed from system."
    echo "Services will no longer start automatically on boot."
else
    echo ""
    echo "Warning: Some services may not have been completely removed."
    echo "Please check manually with: systemctl list-unit-files | grep plex"
fi

echo ""
echo "Note: Project files and configuration remain unchanged."
echo "You can still run services manually using launcher.sh"
