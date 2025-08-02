# Service Installation Guide

This guide explains how to install and uninstall the Plex GPU Balancer as system services that automatically start on boot.

## Installation

To install the services and enable autostart:

```bash
sudo ./install.sh
```

This will:
- Read the project path from `config.conf` or use current directory
- Install all three systemd services (gpu-collector, dashboard, balancer)
- Enable autostart on system boot
- Start services in the correct order
- Verify installation

## Uninstallation

To remove the services and disable autostart:

```bash
sudo ./uninstall.sh
```

This will:
- Stop all running services
- Disable autostart
- Remove systemd service files
- Clean up systemd configuration
- Verify removal

## Service Management

After installation, you can manage services using standard systemctl commands:

```bash
# Check service status
systemctl status plex-gpu-collector
systemctl status plex-dashboard
systemctl status plex-balancer

# View logs
journalctl -u plex-gpu-collector -f
journalctl -u plex-dashboard -f
journalctl -u plex-balancer -f

# Manual control
sudo systemctl start plex-gpu-collector
sudo systemctl stop plex-gpu-collector
sudo systemctl restart plex-gpu-collector
```

## Service Order

Services start in this order (matching launcher.sh):
1. plex-gpu-collector (base service)
2. plex-dashboard (depends on collector)
3. plex-balancer (depends on collector)

## Notes

- Services run as root user
- Dashboard will be available at http://localhost:8080
- Project files and configuration remain unchanged during uninstall
- You can still use `launcher.sh` for manual operation
- All services will restart automatically if they crash
