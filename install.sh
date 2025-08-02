#!/bin/bash

# Plex GPU Balancer - Proxmox Container Installer
# Simple interactive installer for Proxmox VE
# https://github.com/kotysoft/plex-gpu-balancer-public

# If running from pipe, download and run interactively (but only if not already downloaded)
if [ ! -t 0 ] && [ "$PLEX_INSTALLER_DOWNLOADED" != "1" ]; then
    echo "Detected piped input - downloading installer for interactive mode..."
    
    # Basic checks
    if ! command -v pct >/dev/null 2>&1; then
        echo "ERROR: This installer must be run on a Proxmox VE host"
        exit 1
    fi
    
    if [ "$EUID" -ne 0 ]; then
        echo "ERROR: This script must be run as root"
        exit 1
    fi
    
    # Clean up any previous installers
    rm -f /tmp/plex-gpu-installer-*.sh /tmp/plex-installer.sh 2>/dev/null
    
    # Download installer
    TEMP_INSTALLER="/tmp/plex-installer.sh"
    echo "Downloading latest installer..."
    
    if curl -sSL https://raw.githubusercontent.com/kotysoft/plex-gpu-balancer-public/main/install.sh -o "$TEMP_INSTALLER"; then
        chmod +x "$TEMP_INSTALLER"
        echo "Starting interactive installer..."
        export PLEX_INSTALLER_DOWNLOADED=1
        exec "$TEMP_INSTALLER"
    else
        echo "ERROR: Failed to download installer"
        exit 1
    fi
fi

# Clean up on exit
cleanup() {
    rm -f /tmp/plex-installer.sh 2>/dev/null
}
trap cleanup EXIT

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m'

# Global variables
CONTAINER_ID=""
CPU_CORES="1"
MEMORY="512"
CONTAINER_IP=""
GATEWAY=""
DNS="8.8.8.8"
PLEX_SERVER=""
PLEX_TOKEN=""
PLEX_SERVER_NAME=""
PROJECT_PATH="/opt/plex-gpu-balancer"

# Simple logging
log() {
    echo -e "${CYAN}[INFO]${NC} $1"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Input function
ask() {
    local prompt="$1"
    local default="$2"
    local input=""
    
    if [ -n "$default" ]; then
        echo -n "$prompt [$default]: "
    else
        echo -n "$prompt: "
    fi
    
    read -r input
    
    if [ -z "$input" ] && [ -n "$default" ]; then
        input="$default"
    fi
    
    echo "$input"
}

# Validation functions
validate_container_id() {
    local id="$1"
    if [[ ! "$id" =~ ^[0-9]+$ ]] || [ "$id" -lt 100 ] || [ "$id" -gt 999999 ]; then
        return 1
    fi
    if pct status "$id" >/dev/null 2>&1; then
        return 1
    fi
    return 0
}

validate_ip() {
    local ip="$1"
    if [[ $ip =~ ^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$ ]]; then
        IFS='.' read -ra parts <<< "$ip"
        for part in "${parts[@]}"; do
            if [ "$part" -gt 255 ]; then
                return 1
            fi
        done
        return 0
    fi
    return 1
}

validate_plex() {
    local server="$1"
    local token="$2"
    
    log "Testing Plex connection to $server..."
    
    local response
    response=$(curl -s -w "%{http_code}" -o /tmp/plex_test.json \
        "http://${server}/?X-Plex-Token=${token}" \
        --connect-timeout 10 \
        --max-time 15 2>/dev/null || echo "000")
    
    local http_code="${response: -3}"
    
    if [ "$http_code" = "200" ] && [ -f /tmp/plex_test.json ]; then
        if command -v python3 >/dev/null 2>&1; then
            PLEX_SERVER_NAME=$(python3 -c "
import json
try:
    with open('/tmp/plex_test.json') as f:
        data = json.load(f)
    print(data.get('MediaContainer', {}).get('friendlyName', 'Unknown'))
except:
    print('Unknown')
" 2>/dev/null)
        else
            PLEX_SERVER_NAME=$(grep -o '"friendlyName":"[^"]*"' /tmp/plex_test.json | cut -d'"' -f4 2>/dev/null || echo "Unknown")
        fi
        rm -f /tmp/plex_test.json
        return 0
    fi
    
    rm -f /tmp/plex_test.json
    return 1
}

# Configuration functions
show_warning() {
    echo
    echo "=================================================="
    echo "              WARNING - WORK IN PROGRESS"
    echo "=================================================="
    echo
    echo "This project is NOT fully tested and should be used with caution."
    echo
    echo "Requirements:"
    echo "  • Must run on Proxmox VE host (not in container)"
    echo "  • Container MUST be PRIVILEGED for GPU access"
    echo "  • NVIDIA/Intel GPU with hardware acceleration"
    echo "  • Plex Pass subscription required"
    echo
    echo -n "Press Enter to continue or Ctrl+C to cancel..."
    read -r
}

get_container_config() {
    echo
    echo "=== Container Configuration ==="
    
    while true; do
        CONTAINER_ID=$(ask "Container ID (100-999999)")
        if [ -z "$CONTAINER_ID" ]; then
            error "Container ID is required"
            continue
        fi
        
        if validate_container_id "$CONTAINER_ID"; then
            success "Container ID $CONTAINER_ID is available"
            break
        else
            error "Invalid ID or container already exists"
        fi
    done
    
    CPU_CORES=$(ask "CPU cores" "1")
    if [[ ! "$CPU_CORES" =~ ^[0-9]+$ ]] || [ "$CPU_CORES" -lt 1 ] || [ "$CPU_CORES" -gt 32 ]; then
        warning "Invalid CPU cores, using default: 1"
        CPU_CORES="1"
    fi
    
    MEMORY=$(ask "Memory (MB)" "512")
    if [[ ! "$MEMORY" =~ ^[0-9]+$ ]] || [ "$MEMORY" -lt 128 ]; then
        warning "Invalid memory, using default: 512MB"
        MEMORY="512"
    fi
    
    log "Container: ID=$CONTAINER_ID, CPU=$CPU_CORES, RAM=${MEMORY}MB"
}

get_network_config() {
    echo
    echo "=== Network Configuration ==="
    
    local use_dhcp=$(ask "Use DHCP" "y")
    
    if [[ ! "$use_dhcp" =~ ^[Yy] ]]; then
        while true; do
            CONTAINER_IP=$(ask "Static IP address")
            if [ -z "$CONTAINER_IP" ]; then
                error "IP address is required for static configuration"
                continue
            fi
            
            if validate_ip "$CONTAINER_IP"; then
                break
            else
                error "Invalid IP address format"
            fi
        done
        
        while true; do
            GATEWAY=$(ask "Gateway IP address")
            if [ -z "$GATEWAY" ]; then
                error "Gateway is required for static configuration"
                continue
            fi
            
            if validate_ip "$GATEWAY"; then
                break
            else
                error "Invalid gateway IP address format"
            fi
        done
        
        local dns_input=$(ask "DNS server" "8.8.8.8")
        if validate_ip "$dns_input"; then
            DNS="$dns_input"
        fi
        
        log "Network: Static IP=$CONTAINER_IP, Gateway=$GATEWAY, DNS=$DNS"
    else
        log "Network: DHCP enabled"
    fi
}

get_plex_config() {
    echo
    echo "=== Plex Server Configuration ==="
    echo
    echo "To get your Plex token:"
    echo "  1. Open Plex in your browser and log in"
    echo "  2. Press F12 to open Developer Tools"
    echo "  3. Go to Console tab"
    echo "  4. Type: localStorage.getItem('myPlexAccessToken')"
    echo "  5. Copy the token (without quotes)"
    echo
    
    while true; do
        PLEX_SERVER=$(ask "Plex server (IP:PORT, e.g., 192.168.1.100:32400)")
        if [ -z "$PLEX_SERVER" ]; then
            error "Plex server address is required"
            continue
        fi
        
        PLEX_TOKEN=$(ask "Plex token")
        if [ -z "$PLEX_TOKEN" ]; then
            error "Plex token is required"
            continue
        fi
        
        if validate_plex "$PLEX_SERVER" "$PLEX_TOKEN"; then
            success "Connected to Plex server: $PLEX_SERVER_NAME"
            break
        else
            error "Cannot connect to Plex server. Please check server address and token."
        fi
    done
}

# Installation functions
create_container() {
    echo
    echo "=== Creating Proxmox Container ==="
    
    local net_config="name=eth0,bridge=vmbr0"
    if [ -n "$CONTAINER_IP" ]; then
        net_config+=",ip=${CONTAINER_IP}/24,gw=${GATEWAY}"
    else
        net_config+=",ip=dhcp"
    fi
    
    log "Creating container with ID $CONTAINER_ID..."
    
    if pct create "$CONTAINER_ID" \
        local:vztmpl/ubuntu-22.04-standard_22.04-1_amd64.tar.zst \
        --memory "$MEMORY" \
        --cores "$CPU_CORES" \
        --rootfs "local:4" \
        --net0 "$net_config" \
        --nameserver "$DNS" \
        --hostname "plex-gpu-balancer" \
        --unprivileged 0 \
        --features nesting=1 \
        --onboot 1; then
        
        success "Container created successfully"
    else
        error "Failed to create container"
        exit 1
    fi
}

setup_gpu_passthrough() {
    echo
    echo "=== Configuring GPU Passthrough ==="
    
    local config_file="/etc/pve/lxc/${CONTAINER_ID}.conf"
    
    log "Adding GPU passthrough configuration..."
    
    cat >> "$config_file" << 'EOF'

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
    
    success "GPU passthrough configured"
}

start_container() {
    echo
    echo "=== Starting Container ==="
    
    log "Starting container $CONTAINER_ID..."
    if pct start "$CONTAINER_ID"; then
        success "Container started"
        log "Waiting for container to initialize..."
        sleep 10
    else
        error "Failed to start container"
        exit 1
    fi
}

install_dependencies() {
    echo
    echo "=== Installing Dependencies ==="
    
    log "Updating package lists..."
    pct exec "$CONTAINER_ID" -- apt update
    
    log "Installing system packages..."
    pct exec "$CONTAINER_ID" -- apt install -y \
        python3 python3-pip git curl wget unzip \
        intel-gpu-tools nvidia-utils-535
    
    success "Dependencies installed"
}

download_project() {
    echo
    echo "=== Downloading Plex GPU Balancer ==="
    
    log "Cloning project repository..."
    pct exec "$CONTAINER_ID" -- mkdir -p /tmp/download
    pct exec "$CONTAINER_ID" -- git clone \
        https://github.com/kotysoft/plex-gpu-balancer-public.git \
        /tmp/download
    
    log "Installing project files..."
    pct exec "$CONTAINER_ID" -- mkdir -p "$PROJECT_PATH"
    pct exec "$CONTAINER_ID" -- cp -r /tmp/download/* "$PROJECT_PATH/"
    pct exec "$CONTAINER_ID" -- rm -rf /tmp/download
    
    log "Installing Python dependencies..."
    pct exec "$CONTAINER_ID" -- pip3 install -r "$PROJECT_PATH/requirements.txt"
    
    success "Project downloaded and installed"
}

create_configs() {
    echo
    echo "=== Creating Configuration Files ==="
    
    log "Creating main configuration..."
    pct exec "$CONTAINER_ID" -- bash -c "cat > $PROJECT_PATH/config.conf << EOF
[system]
project_path = $PROJECT_PATH

[plex]
server = $PLEX_SERVER
token = $PLEX_TOKEN
EOF"
    
    log "Creating balance configuration..."
    pct exec "$CONTAINER_ID" -- cp \
        "$PROJECT_PATH/balance.conf.template" \
        "$PROJECT_PATH/balance.conf"
    
    success "Configuration files created"
}

install_services() {
    echo
    echo "=== Installing System Services ==="
    
    log "Running service installer..."
    pct exec "$CONTAINER_ID" -- bash "$PROJECT_PATH/service-install.sh"
    
    success "System services installed and started"
}

show_completion() {
    echo
    echo "=================================================="
    echo "            INSTALLATION COMPLETE!"
    echo "=================================================="
    echo
    echo "Container Information:"
    echo "  Container ID: $CONTAINER_ID"
    echo "  Hostname: plex-gpu-balancer"
    echo "  Resources: ${CPU_CORES} CPU cores, ${MEMORY}MB RAM"
    if [ -n "$CONTAINER_IP" ]; then
        echo "  IP Address: $CONTAINER_IP"
        echo "  Gateway: $GATEWAY"
        echo "  DNS: $DNS"
    else
        echo "  Network: DHCP"
    fi
    echo
    echo "Plex Configuration:"
    echo "  Server: $PLEX_SERVER"
    echo "  Server Name: $PLEX_SERVER_NAME"
    echo
    echo "Service Information:"
    echo "  Dashboard: http://${CONTAINER_IP:-localhost}:8080"
    echo "  Project Path: $PROJECT_PATH"
    echo "  Services: plex-gpu-collector, plex-dashboard, plex-balancer"
    echo
    echo "Useful Commands:"
    echo "  Enter container: pct enter $CONTAINER_ID"
    echo "  Check services: pct exec $CONTAINER_ID -- systemctl status plex-gpu-collector"
    echo "  View logs: pct exec $CONTAINER_ID -- journalctl -u plex-gpu-collector -f"
    echo
    success "All services will start automatically when the container boots"
    success "GPU passthrough has been configured for both NVIDIA and Intel GPUs"
    echo
}

# Main installation flow
main() {
    echo "Plex GPU Balancer - Proxmox Container Installer"
    echo "================================================"
    
    # Check environment
    if ! command -v pct >/dev/null 2>&1; then
        error "This installer must be run on a Proxmox VE host"
        exit 1
    fi
    
    if [ "$EUID" -ne 0 ]; then
        error "This script must be run as root"
        exit 1
    fi
    
    # Run installation
    show_warning
    get_container_config
    get_network_config
    get_plex_config
    create_container
    setup_gpu_passthrough
    start_container
    install_dependencies
    download_project
    create_configs
    install_services
    show_completion
}

main "$@"
