#!/bin/bash

# Plex GPU Balancer - Proxmox Container Installer
# https://github.com/kotysoft/plex-gpu-balancer-public

set -e

# If running from pipe, just download and tell user to run it
if [ ! -t 0 ]; then
    echo "Downloading Plex GPU Balancer installer..."
    
    # Download to current directory
    if curl -sSL https://raw.githubusercontent.com/kotysoft/plex-gpu-balancer-public/main/install.sh -o plex-installer.sh; then
        chmod +x plex-installer.sh
        echo
        echo "✅ Installer downloaded successfully!"
        echo
        echo "Now run:"
        echo "  ./plex-installer.sh"
        echo
        echo "v0.11"
        echo
        exit 0
    else
        echo "❌ Failed to download installer"
        exit 1
    fi
fi

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m'

# Check we're on Proxmox
if ! command -v pct >/dev/null 2>&1; then
    echo -e "${RED}ERROR: This installer must be run on a Proxmox VE host${NC}"
    exit 1
fi

if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}ERROR: This script must be run as root${NC}"
    exit 1
fi

clear
echo -e "${CYAN}============================================================${NC}"
echo -e "${WHITE}        PLEX GPU BALANCER - PROXMOX INSTALLER${NC}"
echo -e "${CYAN}============================================================${NC}"
echo
echo -e "${YELLOW}⚠ WARNING: This is a work-in-progress project${NC}"
echo -e "${YELLOW}⚠ Container MUST be PRIVILEGED for GPU access${NC}"
echo
echo -e "Requirements:"
echo -e "  • Proxmox VE host"
echo -e "  • NVIDIA/Intel GPU with hardware acceleration"
echo -e "  • Plex Pass subscription"
echo
read -p "Press Enter to continue or Ctrl+C to cancel..."

# Container configuration
echo
echo -e "${CYAN}=== Container Configuration ===${NC}"
echo

# Get container ID
while true; do
    read -p "Container ID (100-999999): " CONTAINER_ID
    if [[ "$CONTAINER_ID" =~ ^[0-9]+$ ]] && [ "$CONTAINER_ID" -ge 100 ] && [ "$CONTAINER_ID" -le 999999 ]; then
        if ! pct status "$CONTAINER_ID" >/dev/null 2>&1; then
            echo -e "${GREEN}✓ Container ID $CONTAINER_ID is available${NC}"
            break
        else
            echo -e "${RED}✗ Container $CONTAINER_ID already exists${NC}"
        fi
    else
        echo -e "${RED}✗ Invalid container ID${NC}"
    fi
done

# CPU cores
read -p "CPU cores [1]: " CPU_CORES
CPU_CORES=${CPU_CORES:-1}
if [[ ! "$CPU_CORES" =~ ^[0-9]+$ ]] || [ "$CPU_CORES" -lt 1 ]; then
    CPU_CORES=1
    echo -e "${YELLOW}Using default: 1 core${NC}"
fi

# Memory
read -p "Memory (MB) [512]: " MEMORY
MEMORY=${MEMORY:-512}
if [[ ! "$MEMORY" =~ ^[0-9]+$ ]] || [ "$MEMORY" -lt 128 ]; then
    MEMORY=512
    echo -e "${YELLOW}Using default: 512MB${NC}"
fi

# Storage selection
echo
echo -e "${CYAN}=== Storage Configuration ===${NC}"
echo

echo "Available storage:"
pvesm status -content vztmpl | grep -E "(local|dir)" | awk '{print "  " $1 " (" $2 ")"}'
echo

while true; do
    read -p "Select storage for container [local-lvm]: " STORAGE
    STORAGE=${STORAGE:-local-lvm}
    if pvesm status | grep -q "^$STORAGE "; then
        echo -e "${GREEN}✓ Using storage: $STORAGE${NC}"
        break
    else
        echo -e "${RED}✗ Storage '$STORAGE' not found${NC}"
    fi
done

# Network configuration
echo
echo -e "${CYAN}=== Network Configuration ===${NC}"
echo

read -p "Use DHCP? [y/n] (default: y): " USE_DHCP
USE_DHCP=${USE_DHCP:-y}

if [[ ! "$USE_DHCP" =~ ^[Yy] ]]; then
    # Static IP
    while true; do
        read -p "Static IP address: " CONTAINER_IP
        if [[ $CONTAINER_IP =~ ^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$ ]]; then
            echo -e "${GREEN}✓ Valid IP address${NC}"
            break
        else
            echo -e "${RED}✗ Invalid IP address${NC}"
        fi
    done
    
    while true; do
        read -p "Gateway: " GATEWAY
        if [[ $GATEWAY =~ ^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$ ]]; then
            echo -e "${GREEN}✓ Valid gateway${NC}"
            break
        else
            echo -e "${RED}✗ Invalid gateway address${NC}"
        fi
    done
    
    read -p "DNS server [8.8.8.8]: " DNS
    DNS=${DNS:-8.8.8.8}
fi

# Plex configuration
echo
echo -e "${CYAN}=== Plex Configuration ===${NC}"
echo
echo "To get your Plex token:"
echo "  1. Open Plex in your browser and log in"
echo "  2. Press F12 to open Developer Tools"
echo "  3. Go to Console tab"
echo "  4. Type: localStorage.getItem('myPlexAccessToken')"
echo "  5. Copy the token (without quotes)"
echo

while true; do
    read -p "Plex server (IP:PORT): " PLEX_SERVER
    if [ -n "$PLEX_SERVER" ]; then
        break
    fi
    echo -e "${RED}✗ Plex server is required${NC}"
done

while true; do
    read -p "Plex token (or 'back' to change server): " PLEX_TOKEN
    if [ "$PLEX_TOKEN" = "back" ]; then
        continue 2  # Go back to server input
    elif [ -n "$PLEX_TOKEN" ]; then
        break
    fi
    echo -e "${RED}✗ Plex token is required${NC}"
done

# Test Plex connection
echo -e "${CYAN}Testing Plex connection...${NC}"
if curl -s "http://${PLEX_SERVER}/?X-Plex-Token=${PLEX_TOKEN}" >/dev/null 2>&1; then
    echo -e "${GREEN}✓ Connected to Plex server${NC}"
else
    echo -e "${YELLOW}⚠ Could not verify Plex connection (continuing anyway)${NC}"
fi

# Create container
echo
echo -e "${CYAN}=== Creating Container ===${NC}"
echo

# Network config
if [[ "$USE_DHCP" =~ ^[Yy] ]]; then
    NET_CONFIG="name=eth0,bridge=vmbr0,ip=dhcp"
else
    NET_CONFIG="name=eth0,bridge=vmbr0,ip=${CONTAINER_IP}/24,gw=${GATEWAY}"
    NAMESERVER="--nameserver $DNS"
fi

echo "Creating container $CONTAINER_ID..."
pct create "$CONTAINER_ID" \
    local:vztmpl/ubuntu-22.04-standard_22.04-1_amd64.tar.zst \
    --memory "$MEMORY" \
    --cores "$CPU_CORES" \
    --rootfs "${STORAGE}:4" \
    --net0 "$NET_CONFIG" \
    ${NAMESERVER:-} \
    --hostname "plex-gpu-balancer" \
    --unprivileged 0 \
    --features nesting=1 \
    --onboot 1

echo -e "${GREEN}✓ Container created${NC}"

# GPU passthrough
echo
echo -e "${CYAN}=== Configuring GPU Passthrough ===${NC}"
echo

cat >> "/etc/pve/lxc/${CONTAINER_ID}.conf" << 'EOF'

# NVIDIA GPU passthrough
lxc.cgroup2.devices.allow: c 195:* rwm
lxc.cgroup2.devices.allow: c 509:* rwm
lxc.mount.entry: /dev/nvidia0 dev/nvidia0 none bind,optional,create=file
lxc.mount.entry: /dev/nvidiactl dev/nvidiactl none bind,optional,create=file
lxc.mount.entry: /dev/nvidia-uvm dev/nvidia-uvm none bind,optional,create=file
lxc.mount.entry: /dev/nvidia-modeset dev/nvidia-modeset none bind,optional,create=file
lxc.mount.entry: /dev/nvidia-uvm-tools dev/nvidia-uvm-tools none bind,optional,create=file

# Intel GPU passthrough  
lxc.cgroup2.devices.allow: c 226:* rwm
lxc.mount.entry: /dev/dri dev/dri none bind,optional,create=dir
EOF

echo -e "${GREEN}✓ GPU passthrough configured${NC}"

# Start container
echo
echo -e "${CYAN}=== Starting Container ===${NC}"
echo

pct start "$CONTAINER_ID"
echo -e "${GREEN}✓ Container started${NC}"
echo "Waiting for container to initialize..."
sleep 10

# Install dependencies
echo
echo -e "${CYAN}=== Installing Dependencies ===${NC}"
echo

echo "Updating packages..."
pct exec "$CONTAINER_ID" -- apt update -qq

echo "Installing system dependencies..."
pct exec "$CONTAINER_ID" -- apt install -y -qq \
    python3 python3-pip git curl wget unzip \
    intel-gpu-tools nvidia-utils-535

echo -e "${GREEN}✓ Dependencies installed${NC}"

# Download project
echo
echo -e "${CYAN}=== Installing Plex GPU Balancer ===${NC}"
echo

pct exec "$CONTAINER_ID" -- git clone https://github.com/kotysoft/plex-gpu-balancer-public.git /opt/plex-gpu-balancer
pct exec "$CONTAINER_ID" -- pip3 install -r /opt/plex-gpu-balancer/requirements.txt

echo -e "${GREEN}✓ Project installed${NC}"

# Create config
echo
echo -e "${CYAN}=== Creating Configuration ===${NC}"
echo

pct exec "$CONTAINER_ID" -- bash -c "cat > /opt/plex-gpu-balancer/config.conf << EOF
[system]
project_path = /opt/plex-gpu-balancer

[plex]
server = $PLEX_SERVER
token = $PLEX_TOKEN
EOF"

pct exec "$CONTAINER_ID" -- cp /opt/plex-gpu-balancer/balance.conf.template /opt/plex-gpu-balancer/balance.conf

echo -e "${GREEN}✓ Configuration created${NC}"

# Install services
echo
echo -e "${CYAN}=== Installing Services ===${NC}"
echo

pct exec "$CONTAINER_ID" -- bash /opt/plex-gpu-balancer/service-install.sh

echo -e "${GREEN}✓ Services installed${NC}"

# Get container IP if DHCP
if [[ "$USE_DHCP" =~ ^[Yy] ]]; then
    CONTAINER_IP=$(pct exec "$CONTAINER_ID" -- hostname -I | awk '{print $1}')
fi

# Completion
echo
echo -e "${GREEN}============================================================${NC}"
echo -e "${GREEN}            INSTALLATION COMPLETE!${NC}"
echo -e "${GREEN}============================================================${NC}"
echo
echo -e "${WHITE}Container Details:${NC}"
echo -e "  ID: ${CYAN}$CONTAINER_ID${NC}"
echo -e "  IP: ${CYAN}$CONTAINER_IP${NC}"
echo -e "  Resources: ${CYAN}${CPU_CORES} cores, ${MEMORY}MB RAM${NC}"
echo
echo -e "${WHITE}Dashboard:${NC}"
echo -e "  ${CYAN}http://$CONTAINER_IP:8080${NC}"
echo
echo -e "${WHITE}Commands:${NC}"
echo -e "  Enter container: ${CYAN}pct enter $CONTAINER_ID${NC}"
echo -e "  Check logs: ${CYAN}pct exec $CONTAINER_ID -- journalctl -u plex-gpu-collector -f${NC}"
echo
echo -e "${GREEN}✓ All services started automatically${NC}"
echo
