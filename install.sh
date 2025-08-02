#!/bin/bash

# Plex GPU Balancer - Proxmox Container Installer
# Clean, simple installer for Proxmox VE environments
# https://github.com/kotysoft/plex-gpu-balancer-public

set -e

# Colors for output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly CYAN='\033[0;36m'
readonly WHITE='\033[1;37m'
readonly GRAY='\033[0;37m'
readonly NC='\033[0m'

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

# Utility functions
log_info() {
    echo -e "${CYAN}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_step() {
    echo -e "\n${BLUE}▶${NC} ${WHITE}$1${NC}"
}

# Input functions that work with pipes
get_input() {
    local prompt="$1"
    local default="$2"
    local input=""
    
    if [ -t 0 ]; then
        # Interactive mode
        if [ -n "$default" ]; then
            echo -n "$prompt [$default]: "
        else
            echo -n "$prompt: "
        fi
        read -r input
        if [ -z "$input" ] && [ -n "$default" ]; then
            input="$default"
        fi
    else
        # Non-interactive mode - use defaults or exit
        if [ -n "$default" ]; then
            input="$default"
            log_info "$prompt: Using default '$default'"
        else
            log_error "$prompt: No default available in non-interactive mode"
            exit 1
        fi
    fi
    
    echo "$input"
}

get_required_input() {
    local prompt="$1"
    local input=""
    
    if [ -t 0 ]; then
        # Interactive mode
        while [ -z "$input" ]; do
            echo -n "$prompt: "
            read -r input
            if [ -z "$input" ]; then
                log_error "This field is required"
            fi
        done
    else
        # Non-interactive mode - exit with error
        log_error "$prompt: Required input not available in non-interactive mode"
        log_error "Please run this installer interactively or set environment variables"
        exit 1
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
    
    log_info "Testing Plex connection to $server..."
    
    local response
    response=$(curl -s -w "%{http_code}" -o /tmp/plex_test.json \
        "http://${server}/?X-Plex-Token=${token}" \
        --connect-timeout 10 \
        --max-time 15 2>/dev/null || echo "000")
    
    local http_code="${response: -3}"
    
    if [ "$http_code" = "200" ] && [ -f /tmp/plex_test.json ]; then
        # Parse JSON to get friendlyName
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

# Main configuration functions
show_warning() {
    echo -e "${YELLOW}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                        ⚠ WARNING ⚠                         ║"
    echo "║                                                              ║"
    echo "║  This is a WORK IN PROGRESS project - not fully tested      ║"
    echo "║                                                              ║"
    echo "║  Requirements:                                               ║"
    echo "║  • Must run on Proxmox VE host (not in container)           ║"
    echo "║  • Container MUST be PRIVILEGED for GPU access              ║"
    echo "║  • NVIDIA/Intel GPU with hardware acceleration              ║"
    echo "║  • Plex Pass subscription required                          ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    
    if [ -t 0 ]; then
        echo -n "Press Enter to continue or Ctrl+C to cancel..."
        read -r
    else
        log_info "Non-interactive mode: Continuing automatically"
    fi
}

get_container_config() {
    log_step "Container Configuration"
    
    # Container ID
    while true; do
        CONTAINER_ID=$(get_required_input "Container ID (100-999999)")
        if validate_container_id "$CONTAINER_ID"; then
            log_success "Container ID $CONTAINER_ID is available"
            break
        else
            log_error "Invalid ID or container already exists"
            if [ ! -t 0 ]; then
                exit 1
            fi
        fi
    done
    
    # CPU Cores
    CPU_CORES=$(get_input "CPU cores" "1")
    if [[ ! "$CPU_CORES" =~ ^[0-9]+$ ]] || [ "$CPU_CORES" -lt 1 ] || [ "$CPU_CORES" -gt 32 ]; then
        log_warning "Invalid CPU cores, using default: 1"
        CPU_CORES="1"
    fi
    
    # Memory
    MEMORY=$(get_input "Memory (MB)" "512")
    if [[ ! "$MEMORY" =~ ^[0-9]+$ ]] || [ "$MEMORY" -lt 128 ]; then
        log_warning "Invalid memory, using default: 512MB"
        MEMORY="512"
    fi
    
    log_info "Container config: ID=$CONTAINER_ID, CPU=$CPU_CORES, RAM=${MEMORY}MB"
}

get_network_config() {
    log_step "Network Configuration"
    
    local use_dhcp=$(get_input "Use DHCP" "y")
    
    if [[ ! "$use_dhcp" =~ ^[Yy] ]]; then
        while true; do
            CONTAINER_IP=$(get_required_input "Static IP address")
            if validate_ip "$CONTAINER_IP"; then
                break
            else
                log_error "Invalid IP address format"
                if [ ! -t 0 ]; then
                    exit 1
                fi
            fi
        done
        
        while true; do
            GATEWAY=$(get_required_input "Gateway IP address")
            if validate_ip "$GATEWAY"; then
                break
            else
                log_error "Invalid gateway IP address format"
                if [ ! -t 0 ]; then
                    exit 1
                fi
            fi
        done
        
        local dns_input=$(get_input "DNS server" "8.8.8.8")
        if validate_ip "$dns_input"; then
            DNS="$dns_input"
        fi
        
        log_info "Network config: Static IP=$CONTAINER_IP, Gateway=$GATEWAY, DNS=$DNS"
    else
        log_info "Network config: DHCP enabled"
    fi
}

get_plex_config() {
    log_step "Plex Server Configuration"
    
    echo
    log_info "To get your Plex token:"
    echo "  1. Open Plex in your browser and log in"
    echo "  2. Press F12 to open Developer Tools"
    echo "  3. Go to Console tab"
    echo "  4. Type: localStorage.getItem('myPlexAccessToken')"
    echo "  5. Copy the token (without quotes)"
    echo
    
    while true; do
        PLEX_SERVER=$(get_required_input "Plex server (IP:PORT, e.g., 192.168.1.100:32400)")
        PLEX_TOKEN=$(get_required_input "Plex token")
        
        if validate_plex "$PLEX_SERVER" "$PLEX_TOKEN"; then
            log_success "Connected to Plex server: $PLEX_SERVER_NAME"
            break
        else
            log_error "Cannot connect to Plex server. Please check server address and token."
            if [ ! -t 0 ]; then
                exit 1
            fi
        fi
    done
}

# Installation functions
create_container() {
    log_step "Creating Proxmox Container"
    
    local net_config="name=eth0,bridge=vmbr0"
    if [ -n "$CONTAINER_IP" ]; then
        net_config+=",ip=${CONTAINER_IP}/24,gw=${GATEWAY}"
    else
        net_config+=",ip=dhcp"
    fi
    
    log_info "Creating container with ID $CONTAINER_ID..."
    
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
        
        log_success "Container created successfully"
    else
        log_error "Failed to create container"
        exit 1
    fi
}

setup_gpu_passthrough() {
    log_step "Configuring GPU Passthrough"
    
    local config_file="/etc/pve/lxc/${CONTAINER_ID}.conf"
    
    log_info "Adding GPU passthrough configuration..."
    
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
    
    log_success "GPU passthrough configured"
}

start_container() {
    log_step "Starting Container"
    
    log_info "Starting container $CONTAINER_ID..."
    if pct start "$CONTAINER_ID"; then
        log_success "Container started"
        log_info "Waiting for container to initialize..."
        sleep 10
    else
        log_error "Failed to start container"
        exit 1
    fi
}

install_dependencies() {
    log_step "Installing Dependencies"
    
    log_info "Updating package lists..."
    pct exec "$CONTAINER_ID" -- apt update
    
    log_info "Installing system packages..."
    pct exec "$CONTAINER_ID" -- apt install -y \
        python3 python3-pip git curl wget unzip \
        intel-gpu-tools nvidia-utils-535
    
    log_success "Dependencies installed"
}

download_project() {
    log_step "Downloading Plex GPU Balancer"
    
    log_info "Cloning project repository..."
    pct exec "$CONTAINER_ID" -- mkdir -p /tmp/download
    pct exec "$CONTAINER_ID" -- git clone \
        https://github.com/kotysoft/plex-gpu-balancer-public.git \
        /tmp/download
    
    log_info "Installing project files..."
    pct exec "$CONTAINER_ID" -- mkdir -p "$PROJECT_PATH"
    pct exec "$CONTAINER_ID" -- cp -r /tmp/download/* "$PROJECT_PATH/"
    pct exec "$CONTAINER_ID" -- rm -rf /tmp/download
    
    log_info "Installing Python dependencies..."
    pct exec "$CONTAINER_ID" -- pip3 install -r "$PROJECT_PATH/requirements.txt"
    
    log_success "Project downloaded and installed"
}

create_configs() {
    log_step "Creating Configuration Files"
    
    log_info "Creating main configuration..."
    pct exec "$CONTAINER_ID" -- bash -c "cat > $PROJECT_PATH/config.conf << EOF
[system]
project_path = $PROJECT_PATH

[plex]
server = $PLEX_SERVER
token = $PLEX_TOKEN
EOF"
    
    log_info "Creating balance configuration..."
    pct exec "$CONTAINER_ID" -- cp \
        "$PROJECT_PATH/balance.conf.template" \
        "$PROJECT_PATH/balance.conf"
    
    log_success "Configuration files created"
}

install_services() {
    log_step "Installing System Services"
    
    log_info "Running service installer..."
    pct exec "$CONTAINER_ID" -- bash "$PROJECT_PATH/service-install.sh"
    
    log_success "System services installed and started"
}

show_completion() {
    echo
    log_success "Installation completed successfully!"
    echo
    echo -e "${GREEN}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                    INSTALLATION COMPLETE                    ║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo
    echo -e "${WHITE}Container Information:${NC}"
    echo -e "  Container ID: ${CYAN}$CONTAINER_ID${NC}"
    echo -e "  Hostname: ${CYAN}plex-gpu-balancer${NC}"
    echo -e "  Resources: ${CYAN}${CPU_CORES} CPU cores, ${MEMORY}MB RAM${NC}"
    if [ -n "$CONTAINER_IP" ]; then
        echo -e "  IP Address: ${CYAN}$CONTAINER_IP${NC}"
        echo -e "  Gateway: ${CYAN}$GATEWAY${NC}"
        echo -e "  DNS: ${CYAN}$DNS${NC}"
    else
        echo -e "  Network: ${CYAN}DHCP${NC}"
    fi
    echo
    echo -e "${WHITE}Plex Configuration:${NC}"
    echo -e "  Server: ${CYAN}$PLEX_SERVER${NC}"
    echo -e "  Server Name: ${CYAN}$PLEX_SERVER_NAME${NC}"
    echo
    echo -e "${WHITE}Service Information:${NC}"
    echo -e "  Dashboard: ${CYAN}http://${CONTAINER_IP:-localhost}:8080${NC}"
    echo -e "  Project Path: ${CYAN}$PROJECT_PATH${NC}"
    echo -e "  Services: ${CYAN}plex-gpu-collector, plex-dashboard, plex-balancer${NC}"
    echo
    echo -e "${WHITE}Useful Commands:${NC}"
    echo -e "  ${GRAY}Enter container:${NC} pct enter $CONTAINER_ID"
    echo -e "  ${GRAY}Check services:${NC} pct exec $CONTAINER_ID -- systemctl status plex-gpu-collector"
    echo -e "  ${GRAY}View logs:${NC} pct exec $CONTAINER_ID -- journalctl -u plex-gpu-collector -f"
    echo
    log_info "All services will start automatically when the container boots"
    log_info "GPU passthrough has been configured for both NVIDIA and Intel GPUs"
    echo
}

# Environment variable support for non-interactive mode
load_env_vars() {
    if [ -n "$PLEX_GPU_CONTAINER_ID" ]; then
        CONTAINER_ID="$PLEX_GPU_CONTAINER_ID"
    fi
    if [ -n "$PLEX_GPU_CPU_CORES" ]; then
        CPU_CORES="$PLEX_GPU_CPU_CORES"
    fi
    if [ -n "$PLEX_GPU_MEMORY" ]; then
        MEMORY="$PLEX_GPU_MEMORY"
    fi
    if [ -n "$PLEX_GPU_CONTAINER_IP" ]; then
        CONTAINER_IP="$PLEX_GPU_CONTAINER_IP"
    fi
    if [ -n "$PLEX_GPU_GATEWAY" ]; then
        GATEWAY="$PLEX_GPU_GATEWAY"
    fi
    if [ -n "$PLEX_GPU_DNS" ]; then
        DNS="$PLEX_GPU_DNS"
    fi
    if [ -n "$PLEX_GPU_SERVER" ]; then
        PLEX_SERVER="$PLEX_GPU_SERVER"
    fi
    if [ -n "$PLEX_GPU_TOKEN" ]; then
        PLEX_TOKEN="$PLEX_GPU_TOKEN"
    fi
}

# Main installation flow
main() {
    echo -e "${CYAN}Plex GPU Balancer - Proxmox Container Installer${NC}"
    echo -e "${GRAY}=================================================${NC}"
    echo
    
    # Check environment
    if ! command -v pct >/dev/null 2>&1; then
        log_error "This installer must be run on a Proxmox VE host"
        exit 1
    fi
    
    if [ "$EUID" -ne 0 ]; then
        log_error "This script must be run as root"
        exit 1
    fi
    
    # Load environment variables for non-interactive mode
    load_env_vars
    
    # Show warning
    show_warning
    
    # Check if we have required values for non-interactive mode
    if [ ! -t 0 ]; then
        log_info "Running in non-interactive mode"
        if [ -z "$CONTAINER_ID" ] || [ -z "$PLEX_SERVER" ] || [ -z "$PLEX_TOKEN" ]; then
            log_error "Non-interactive mode requires environment variables:"
            echo "  PLEX_GPU_CONTAINER_ID - Container ID (required)"
            echo "  PLEX_GPU_SERVER - Plex server IP:PORT (required)"
            echo "  PLEX_GPU_TOKEN - Plex token (required)"
            echo "  PLEX_GPU_CPU_CORES - CPU cores (optional, default: 1)"
            echo "  PLEX_GPU_MEMORY - Memory in MB (optional, default: 512)"
            echo "  PLEX_GPU_CONTAINER_IP - Static IP (optional, uses DHCP if not set)"
            echo "  PLEX_GPU_GATEWAY - Gateway IP (required if static IP set)"
            echo "  PLEX_GPU_DNS - DNS server (optional, default: 8.8.8.8)"
            exit 1
        fi
        
        # Validate required non-interactive values
        if ! validate_container_id "$CONTAINER_ID"; then
            log_error "Invalid container ID or container already exists: $CONTAINER_ID"
            exit 1
        fi
        
        if ! validate_plex "$PLEX_SERVER" "$PLEX_TOKEN"; then
            log_error "Cannot connect to Plex server: $PLEX_SERVER"
            exit 1
        fi
        
        log_info "Non-interactive configuration validated"
    else
        # Interactive configuration
        get_container_config
        get_network_config
        get_plex_config
    fi
    
    # Installation steps
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
