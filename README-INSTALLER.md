# Plex GPU Balancer - Proxmox Container Installer

🚀 **Automated installation script for Proxmox VE environments**

## Quick Installation

Run this command on your **Proxmox VE host** as root:

```bash
curl -sSL https://raw.githubusercontent.com/kotysoft/plex-gpu-balancer-public/main/install.sh | bash
```

## What This Installer Does

### 1. **Container Creation**
- Creates a new privileged LXC container on Proxmox
- Ubuntu 22.04 base template
- Configurable resources (CPU, RAM, storage)
- Network configuration (DHCP or static IP)

### 2. **GPU Passthrough Setup**
- Automatically configures NVIDIA GPU passthrough
- Automatically configures Intel GPU passthrough
- No manual configuration required

### 3. **Project Installation**
- Downloads latest Plex GPU Balancer code
- Installs all system dependencies
- Installs Python dependencies
- Creates configuration files

### 4. **Service Setup**
- Installs systemd services
- Configures auto-start on boot
- Starts all services immediately

## Prerequisites

- **Proxmox VE host** (must run on Proxmox, not inside a container)
- **Root access** to Proxmox host
- **NVIDIA and/or Intel GPU** with hardware acceleration
- **Plex Media Server** accessible on your network
- **Plex Pass subscription** (required for hardware transcoding)

## Installation Steps

### 1. Run the Installer

```bash
curl -sSL https://raw.githubusercontent.com/kotysoft/plex-gpu-balancer-public/main/install.sh | bash
```

### 2. Follow Interactive Setup

The installer will guide you through:

#### Container Configuration
- **Container ID**: Choose a unique ID (100-999999)
- **CPU Cores**: 1, 2, or 4 cores
- **RAM**: 512MB, 1GB, 2GB, or 4GB
- **Storage**: Select from available Proxmox storage

#### Network Configuration
- **DHCP**: Automatic IP assignment (recommended)
- **Static IP**: Manual IP, gateway, and DNS configuration

#### Plex Configuration
- **Server Address**: Your Plex server IP and port (e.g., 192.168.1.100:32400)
- **Access Token**: Get from Plex web interface

### 3. Getting Your Plex Token

1. Open Plex in your browser and log in
2. Press **F12** to open Developer Tools
3. Go to **Console** tab
4. Paste this command and press Enter:
   ```javascript
   localStorage.getItem('myPlexAccessToken')
   ```
5. Copy the token (without quotes) and paste it in the installer

## Post-Installation

### Access the Dashboard
```
http://[CONTAINER-IP]:8080
```

### Useful Commands

#### Container Management
```bash
# Enter the container
pct enter [CONTAINER-ID]

# Start/stop container
pct start [CONTAINER-ID]
pct stop [CONTAINER-ID]

# View container status
pct status [CONTAINER-ID]
```

#### Service Management
```bash
# Check service status
pct exec [CONTAINER-ID] -- systemctl status plex-gpu-collector
pct exec [CONTAINER-ID] -- systemctl status plex-dashboard
pct exec [CONTAINER-ID] -- systemctl status plex-balancer

# View service logs
pct exec [CONTAINER-ID] -- journalctl -u plex-gpu-collector -f
pct exec [CONTAINER-ID] -- journalctl -u plex-dashboard -f
pct exec [CONTAINER-ID] -- journalctl -u plex-balancer -f

# Restart services
pct exec [CONTAINER-ID] -- systemctl restart plex-gpu-collector
pct exec [CONTAINER-ID] -- systemctl restart plex-dashboard
pct exec [CONTAINER-ID] -- systemctl restart plex-balancer
```

## Container Configuration

### Default Settings
- **OS**: Ubuntu 22.04 LXC
- **Privileged**: Yes (required for GPU access)
- **CPU**: 1 core (configurable)
- **RAM**: 512MB (configurable)
- **Disk**: 4GB
- **Network**: DHCP (configurable to static)
- **Auto-start**: Enabled

### GPU Passthrough
The installer automatically configures:

#### NVIDIA GPUs
- `/dev/nvidia0`
- `/dev/nvidiactl`
- `/dev/nvidia-uvm`
- `/dev/nvidia-modeset`
- `/dev/nvidia-uvm-tools`

#### Intel GPUs
- `/dev/dri/` directory and all devices

## Troubleshooting

### Container Creation Issues

**Error: Template not found**
```bash
# Download Ubuntu 22.04 template manually
pveam update
pveam download local ubuntu-22.04-standard_22.04-1_amd64.tar.zst
```

**Error: Storage not available**
- Check storage configuration in Proxmox
- Ensure selected storage supports containers

### GPU Access Issues

**No GPU detected in container**
1. Verify GPU passthrough in container config: `/etc/pve/lxc/[ID].conf`
2. Check if GPUs are available on host: `lspci | grep VGA`
3. Restart container: `pct stop [ID] && pct start [ID]`

### Plex Connection Issues

**Cannot connect to Plex server**
1. Verify Plex server IP and port
2. Check if Plex token is valid
3. Ensure Plex server is accessible from container network

**Token authentication failed**
1. Generate new token from Plex web interface
2. Ensure token is copied correctly (no extra spaces)
3. Check if Plex Pass subscription is active

### Service Issues

**Services not starting**
```bash
# Check systemd status
pct exec [ID] -- systemctl status plex-gpu-collector
pct exec [ID] -- systemctl daemon-reload
pct exec [ID] -- systemctl start plex-gpu-collector
```

**Python module errors**
```bash
# Reinstall Python dependencies
pct exec [ID] -- pip3 install -r /opt/plex-gpu-balancer/requirements.txt
```

## Manual Installation Alternative

If you prefer manual installation or need to customize the setup:

1. Create container manually in Proxmox UI
2. Configure GPU passthrough in container config
3. Install dependencies inside container
4. Clone project and run local installer

## Security Considerations

- Container runs as **privileged** (required for GPU access)
- Services run as **root** (required for hardware access)
- Dashboard accessible on **port 8080** (configure firewall if needed)
- Plex token stored in configuration files (secure container access)

## Updates

To update the Plex GPU Balancer:

```bash
pct exec [ID] -- cd /opt/plex-gpu-balancer
pct exec [ID] -- git pull
pct exec [ID] -- pip3 install -r requirements.txt
pct exec [ID] -- systemctl restart plex-gpu-collector plex-dashboard plex-balancer
```

## Uninstallation

To remove the container:

```bash
# Stop and destroy container
pct stop [CONTAINER-ID]
pct destroy [CONTAINER-ID]
```

## Support

- **Project Repository**: https://github.com/kotysoft/plex-gpu-balancer-public
- **Issues**: Report bugs and feature requests on GitHub
- **Documentation**: Check project README for usage information

---

⚠️ **Warning**: This is a work-in-progress project. Use at your own risk and ensure you have backups of your Plex configuration.
