#!/bin/bash

# Plex GPU Balancer - Proxmox Container Installer
# Interactive installation script for Proxmox VE
# https://github.com/kotysoft/plex-gpu-balancer-public

set -e  # Exit on any error

# Color definitions for modern terminal interface
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly PURPLE='\033[0;35m'
readonly CYAN='\033[0;36m'
readonly WHITE='\033[1;37m'
readonly GRAY='\033[0;37m'
readonly BOLD='\033[1m'
readonly NC='\033[0m' # No Color

# Global variables
CONTAINER_ID=""
CONTAINER_IP=""
GATEWAY=""
DNS=""
STORAGE=""
PLEX_SERVER=""
PLEX_TOKEN=""
PLEX_SERVER_NAME=""
PROJECT_PATH="/opt/plex-gpu-balancer"

# Terminal interface functions
print_header() {
    clear
    echo -e "${CYAN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║              ${WHITE}PLEX GPU BALANCER INSTALLER${CYAN}              ║${NC}"
    echo -e "${CYAN}║                   ${GRAY}Proxmox Container Setup${CYAN}                 ║${NC}"
    echo -e "${CYAN}╚════════════════════════════════════════════════════════════╝${NC}"
    echo
}

print_warning() {
    echo -e "${YELLOW}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${YELLOW}║                      ${RED}⚠ WARNING ⚠${YELLOW}                       ║${NC}"
    echo -e "${YELLOW}║                                                            ║${NC}"
    echo -e "${YELLOW}║  ${WHITE}This is a WORK IN PROGRESS project - not fully tested${YELLOW}  ║${NC}"
    echo -e "${YELLOW}║                                                            ║${NC}"
    echo -e "${YELLOW}║  ${WHITE}Requirements:${YELLOW}                                           ║${NC}"
    echo -e "${YELLOW}║  ${GRAY}• Must run on Proxmox VE host${YELLOW}                          ║${NC}"
    echo -e "${YELLOW}║  ${GRAY}• Container MUST be PRIVILEGED to access GPU details${YELLOW}   ║${NC}"
    echo -e "${YELLOW}║  ${GRAY}• NVIDIA/Intel GPU hardware acceleration required${YELLOW}      ║${NC}"
    echo -e "${YELLOW}╚════════════════════════════════════════════════════════════╝${NC}"
    echo
    echo -e "${WHITE}Press ${GREEN}ENTER${WHITE} to continue or ${RED}Ctrl+C${WHITE} to cancel...${NC}"
    read
}

print_step() {
    echo -e "\n${BLUE}▶ ${WHITE}$1${NC}"
    echo -e "${GRAY}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ Error: $1${NC}"
}

print_info() {
    echo -e "${CYAN}ℹ $1${NC}"
}

# Validation functions
validate_container_id() {
    if [[ ! "$1" =~ ^[0-9]+$ ]] || [ "$1" -lt 100 ] || [ "$1" -gt 999999 ]; then
        return 1
    fi
    
    # Check if container ID already exists
    if pct status "$1" >/dev/null 2>&1; then
        return 1
    fi
    
    return 0
}

validate_ip() {
    local ip="$1"
    if [[ $ip =~ ^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$ ]]; then
        IFS='.' read -ra ADDR <<< "$ip"
        for i in "${ADDR[@]}"; do
            if [ "$i" -gt 255 ]; then
                return 1
            fi
        done
        return 0
    fi
    return 1
}

validate_plex_connection() {
    local server="$1"
    local token="$2"
    
    print_info "Validating Plex connection..."
    
    # Test connection and get server name
    local response
    response=$(curl -s -w "%{http_code}" -o /tmp/plex_test.json \
        "http://${server}/?X-Plex-Token=${token}" \
        --connect-timeout 10 \
        --max-time 15 2>/dev/null)
    
    local http_code="${response: -3}"
    
    if [ "$http_code" = "200" ]; then
        if [ -f /tmp/plex_test.json ]; then
            PLEX_SERVER_NAME=$(grep -o '"friendlyName":"[^"]*"' /tmp/plex_test.json | cut -d'"' -f4 2>/dev/null || echo "Unknown")
            rm -f /tmp/plex_test.json
            return 0
        fi
    fi
    
    rm -f /tmp/plex_test.json
    return 1
}

# Configuration input functions
get_container_config() {
    print_step "Container Configuration"
    
    while true; do
        echo -e "${WHITE}Enter Container ID ${GRAY}(100-999999):${NC}"
        read -p "> " CONTAINER_ID
        
        if validate_container_id "$CONTAINER_ID"; then
            print_success "Container ID $CONTAINER_ID is available"
            break
        else
            print_error "Invalid ID or container already exists"
        fi
    done
    
    echo -e "\n${WHITE}Select CPU cores ${GRAY}(default: 1):${NC}"
    echo -e "${GRAY}1) 1 core   2) 2 cores   3) 4 cores${NC}"
    read -p "> " cpu_choice
    case $cpu_choice in
        2) CPU_CORES=2 ;;
        3) CPU_CORES=4 ;;
        *) CPU_CORES=1 ;;
    esac
    
    echo -e "\n${WHITE}Select RAM ${GRAY}(default: 512MB):${NC}"
    echo -e "${GRAY}1) 512MB   2) 1GB   3) 2GB   4) 4GB${NC}"
    read -p "> " ram_choice
    case $ram_choice in
        2) MEMORY=1024 ;;
        3) MEMORY=2048 ;;
        4) MEMORY=4096 ;;
        *) MEMORY=512 ;;
    esac
}

get_storage_config() {
    print_step "Storage Configuration"
    
    echo -e "${WHITE}Available storage locations:${NC}"
    local i=1
    local storages=()
    
    # Get available storages
    while IFS= read -r line; do
        if [[ $line =~ ^[a-zA-Z0-9_-]+[[:space:]]+[a-zA-Z0-9_-]+[[:space:]]+[0-9]+[[:space:]]+[0-9]+ ]]; then
            local storage_name=$(echo "$line" | awk '{print $1}')
            local storage_type=$(echo "$line" | awk '{print $2}')
            local storage_size=$(echo "$line" | awk '{print $4}')
            
            if [[ "$storage_type" =~ (dir|zfspool|lvm|lvmthin) ]]; then
                storages+=("$storage_name")
                echo -e "${GRAY}$i) $storage_name ${CYAN}($storage_type, ${storage_size}GB)${NC}"
                ((i++))
            fi
        fi
    done < <(pvesm status 2>/dev/null || echo "local dir 0 100")
    
    if [ ${#storages[@]} -eq 0 ]; then
        storages=("local")
        echo -e "${GRAY}1) local ${CYAN}(default)${NC}"
    fi
    
    echo -e "\n${WHITE}Select storage ${GRAY}(default: 1):${NC}"
    read -p "> " storage_choice
    
    if [[ "$storage_choice" =~ ^[0-9]+$ ]] && [ "$storage_choice" -le "${#storages[@]}" ] && [ "$storage_choice" -gt 0 ]; then
        STORAGE="${storages[$((storage_choice-1))]}"
    else
        STORAGE="${storages[0]}"
    fi
    
    print_success "Selected storage: $STORAGE"
}

get_network_config() {
    print_step "Network Configuration"
    
    echo -e "${WHITE}Network Configuration:${NC}"
    echo -e "${GRAY}1) DHCP (automatic)${NC}"
    echo -e "${GRAY}2) Static IP${NC}"
    read -p "> " net_choice
    
    if [ "$net_choice" = "2" ]; then
        while true; do
            echo -e "\n${WHITE}Enter static IP address:${NC}"
            read -p "> " CONTAINER_IP
            if validate_ip "$CONTAINER_IP"; then
                break
            else
                print_error "Invalid IP address format"
            fi
        done
        
        while true; do
            echo -e "\n${WHITE}Enter gateway IP:${NC}"
            read -p "> " GATEWAY
            if validate_ip "$GATEWAY"; then
                break
            else
                print_error "Invalid gateway address format"
            fi
        done
        
        while true; do
            echo -e "\n${WHITE}Enter DNS server IP ${GRAY}(default: 8.8.8.8):${NC}"
            read -p "> " DNS
            if [ -z "$DNS" ]; then
                DNS="8.8.8.8"
                break
            elif validate_ip "$DNS"; then
                break
            else
                print_error "Invalid DNS address format"
            fi
        done
    fi
}

get_plex_config() {
    print_step "Plex Server Configuration"
    
    echo -e "${WHITE}Enter your Plex server address ${GRAY}(IP:PORT):${NC}"
    echo -e "${GRAY}Example: 192.168.1.100:32400${NC}"
    read -p "> " PLEX_SERVER
    
    echo -e "\n${CYAN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║                    ${WHITE}Getting Plex Token${CYAN}                     ║${NC}"
    echo -e "${CYAN}╚════════════════════════════════════════════════════════════╝${NC}"
    echo -e "${WHITE}1. Open Plex in your browser and log in${NC}"
    echo -e "${WHITE}2. Press ${YELLOW}F12${WHITE} to open Developer Tools${NC}"
    echo -e "${WHITE}3. Go to ${YELLOW}Console${WHITE} tab${NC}"
    echo -e "${WHITE}4. Paste this command and press Enter:${NC}"
    echo
    echo -e "${GREEN}   localStorage.getItem('myPlexAccessToken')${NC}"
    echo
    echo -e "${WHITE}5. Copy the token (without quotes) and paste it below${NC}"
    echo
    
    while true; do
        echo -e "${WHITE}Enter your Plex token:${NC}"
        read -p "> " PLEX_TOKEN
        
        if [ -n "$PLEX_TOKEN" ]; then
            if validate_plex_connection "$PLEX_SERVER" "$PLEX_TOKEN"; then
                print_success "Connected to Plex server: $PLEX_SERVER_NAME"
                echo -e "${WHITE}Is this correct? ${GRAY}(y/n):${NC}"
                read -p "> " confirm
                if [[ "$confirm" =~ ^[Yy] ]]; then
                    break
                fi
            else
                print_error "Could not connect to Plex server. Please check server address and token."
            fi
        else
            print_error "Token cannot be empty"
        fi
    done
}

# Container creation and setup functions
create_container() {
    print_step "Creating Proxmox Container"
    
    # Build network config
    local net_config="name=eth0,bridge=vmbr0"
    if [ -n "$CONTAINER_IP" ]; then
        net_config+=",ip=${CONTAINER_IP}/24,gw=${GATEWAY}"
    else
        net_config+=",ip=dhcp"
    fi
    
    # Create container
    print_info "Creating container $CONTAINER_ID..."
    
    pct create "$CONTAINER_ID" \
        local:vztmpl/ubuntu-22.04-standard_22.04-1_amd64.tar.zst \
        --storage "$STORAGE" \
        --memory "$MEMORY" \
        --cores "$CPU_CORES" \
        --rootfs "$STORAGE:4" \
        --net0 "$net_config" \
        --nameserver "$DNS" \
        --hostname "plex-gpu-balancer" \
        --privileged 1 \
        --features nesting=1 \
        --onboot 1 \
        --unprivileged 0
    
    print_success "Container created successfully"
}

setup_gpu_passthrough() {
    print_step "Configuring GPU Passthrough"
    
    # Add GPU devices to container config
    local config_file="/etc/pve/lxc/${CONTAINER_ID}.conf"
    
    print_info "Configuring NVIDIA GPU passthrough..."
    {
        echo "# NVIDIA GPU passthrough"
        echo "lxc.cgroup2.devices.allow: c 195:* rwm"
        echo "lxc.cgroup2.devices.allow: c 509:* rwm"
        echo "lxc.mount.entry: /dev/nvidia0 dev/nvidia0 none bind,optional,create=file"
        echo "lxc.mount.entry: /dev/nvidiactl dev/nvidiactl none bind,optional,create=file"
        echo "lxc.mount.entry: /dev/nvidia-uvm dev/nvidia-uvm none bind,optional,create=file"
        echo "lxc.mount.entry: /dev/nvidia-modeset dev/nvidia-modeset none bind,optional,create=file"
        echo "lxc.mount.entry: /dev/nvidia-uvm-tools dev/nvidia-uvm-tools none bind,optional,create=file"
    } >> "$config_file"
    
    print_info "Configuring Intel GPU passthrough..."
    {
        echo "# Intel GPU passthrough"
        echo "lxc.cgroup2.devices.allow: c 226:* rwm"
        echo "lxc.mount.entry: /dev/dri dev/dri none bind,optional,create=dir"
    } >> "$config_file"
    
    print_success "GPU passthrough configured"
}

start_container() {
    print_step "Starting Container"
    
    print_info "Starting container $CONTAINER_ID..."
    pct start "$CONTAINER_ID"
    
    print_info "Waiting for container to be ready..."
    sleep 10
    
    print_success "Container started successfully"
}

install_dependencies() {
    print_step "Installing Dependencies"
    
    print_info "Updating package lists..."
    pct exec "$CONTAINER_ID" -- apt update
    
    print_info "Installing system packages..."
    pct exec "$CONTAINER_ID" -- apt install -y \
        python3 \
        python3-pip \
        git \
        curl \
        wget \
        unzip \
        intel-gpu-tools \
        nvidia-utils-535
    
    print_success "Dependencies installed"
}

download_project() {
    print_step "Downloading Plex GPU Balancer"
    
    print_info "Creating temporary directory..."
    pct exec "$CONTAINER_ID" -- mkdir -p /tmp/plex-gpu-balancer-download
    
    print_info "Downloading latest release..."
    pct exec "$CONTAINER_ID" -- git clone \
        https://github.com/kotysoft/plex-gpu-balancer-public.git \
        /tmp/plex-gpu-balancer-download
    
    print_info "Moving files to project directory..."
    pct exec "$CONTAINER_ID" -- mkdir -p "$PROJECT_PATH"
    pct exec "$CONTAINER_ID" -- cp -r /tmp/plex-gpu-balancer-download/* "$PROJECT_PATH/"
    pct exec "$CONTAINER_ID" -- rm -rf /tmp/plex-gpu-balancer-download
    
    print_info "Installing Python dependencies..."
    pct exec "$CONTAINER_ID" -- pip3 install -r "$PROJECT_PATH/requirements.txt"
    
    print_success "Project downloaded and dependencies installed"
}

create_config_files() {
    print_step "Creating Configuration Files"
    
    # Create main config
    print_info "Creating main configuration..."
    pct exec "$CONTAINER_ID" -- bash -c "cat > $PROJECT_PATH/config.conf << EOF
# Plex GPU Balancer Main Configuration

[system]
project_path = $PROJECT_PATH

[plex]
server = $PLEX_SERVER
token = $PLEX_TOKEN
EOF"
    
    # Create balance config from template
    print_info "Creating balance configuration..."
    pct exec "$CONTAINER_ID" -- cp \
        "$PROJECT_PATH/balance.conf.template" \
        "$PROJECT_PATH/balance.conf"
    
    print_success "Configuration files created"
}

install_services() {
    print_step "Installing System Services"
    
    print_info "Running service installer..."
    pct exec "$CONTAINER_ID" -- bash "$PROJECT_PATH/service-install.sh"
    
    print_success "System services installed and started"
}

print_summary() {
    clear
    print_header
    
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                  ${WHITE}INSTALLATION COMPLETE!${GREEN}                 ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
    echo
    
    echo -e "${WHITE}Container Information:${NC}"
    echo -e "${GRAY}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${CYAN}Container ID:${NC} $CONTAINER_ID"
    echo -e "${CYAN}Hostname:${NC} plex-gpu-balancer"
    echo -e "${CYAN}Resources:${NC} ${CPU_CORES} CPU cores, ${MEMORY}MB RAM"
    echo -e "${CYAN}Storage:${NC} $STORAGE"
    
    if [ -n "$CONTAINER_IP" ]; then
        echo -e "${CYAN}IP Address:${NC} $CONTAINER_IP"
        echo -e "${CYAN}Gateway:${NC} $GATEWAY"
        echo -e "${CYAN}DNS:${NC} $DNS"
    else
        echo -e "${CYAN}Network:${NC} DHCP"
    fi
    
    echo
    echo -e "${WHITE}Plex Configuration:${NC}"
    echo -e "${GRAY}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${CYAN}Server:${NC} $PLEX_SERVER"
    echo -e "${CYAN}Server Name:${NC} $PLEX_SERVER_NAME"
    
    echo
    echo -e "${WHITE}Service Information:${NC}"
    echo -e "${GRAY}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${CYAN}Dashboard URL:${NC} http://${CONTAINER_IP:-localhost}:8080"
    echo -e "${CYAN}Project Path:${NC} $PROJECT_PATH"
    echo -e "${CYAN}Services:${NC} plex-gpu-collector, plex-dashboard, plex-balancer"
    
    echo
    echo -e "${WHITE}Useful Commands:${NC}"
    echo -e "${GRAY}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${CYAN}Enter container:${NC} pct enter $CONTAINER_ID"
    echo -e "${CYAN}Check services:${NC} pct exec $CONTAINER_ID -- systemctl status plex-gpu-collector"
    echo -e "${CYAN}View logs:${NC} pct exec $CONTAINER_ID -- journalctl -u plex-gpu-collector -f"
    echo -e "${CYAN}Stop container:${NC} pct stop $CONTAINER_ID"
    echo -e "${CYAN}Start container:${NC} pct start $CONTAINER_ID"
    
    echo
    echo -e "${YELLOW}Note: All services will start automatically when the container boots.${NC}"
    echo -e "${YELLOW}GPU passthrough has been configured for both NVIDIA and Intel GPUs.${NC}"
    echo
}

# Main installation flow
main() {
    print_header
    print_warning
    
    # Check if running on Proxmox
    if ! command -v pct >/dev/null 2>&1; then
        print_error "This installer must be run on a Proxmox VE host"
        exit 1
    fi
    
    # Check if running as root
    if [ "$EUID" -ne 0 ]; then
        print_error "This script must be run as root"
        echo -e "${WHITE}Please run: ${GREEN}curl -sSL https://raw.githubusercontent.com/kotysoft/plex-gpu-balancer-public/main/install.sh | sudo bash${NC}"
        exit 1
    fi
    
    # Interactive configuration
    get_container_config
    get_storage_config
    get_network_config
    get_plex_config
    
    # Container creation and setup
    create_container
    setup_gpu_passthrough
    start_container
    install_dependencies
    download_project
    create_config_files
    install_services
    
    # Show final summary
    print_summary
}

# Run main function
main "$@"
