#!/bin/bash

# Plex GPU Balancer - Proxmox Container Installer
# Full-screen BIOS-style interactive installer
# https://github.com/kotysoft/plex-gpu-balancer-public

# Terminal control
TERM_COLS=$(tput cols 2>/dev/null || echo 80)
TERM_ROWS=$(tput lines 2>/dev/null || echo 24)

# Colors for BIOS-like interface
readonly BLUE_BG='\033[44m'
readonly CYAN_BG='\033[46m'
readonly WHITE_BG='\033[47m'
readonly BLACK_BG='\033[40m'
readonly RED_BG='\033[41m'
readonly GREEN_BG='\033[42m'
readonly YELLOW_BG='\033[43m'

readonly WHITE_TEXT='\033[1;37m'
readonly BLACK_TEXT='\033[0;30m'
readonly BLUE_TEXT='\033[1;34m'
readonly CYAN_TEXT='\033[1;36m'
readonly YELLOW_TEXT='\033[1;33m'
readonly RED_TEXT='\033[1;31m'
readonly GREEN_TEXT='\033[1;32m'
readonly GRAY_TEXT='\033[0;37m'
readonly NC='\033[0m'

# Global variables
CONTAINER_ID=""
CPU_CORES=""
MEMORY=""
CONTAINER_IP=""
GATEWAY=""
DNS="8.8.8.8"
PLEX_SERVER=""
PLEX_TOKEN=""
PLEX_SERVER_NAME=""
PROJECT_PATH="/opt/plex-gpu-balancer"

# Terminal functions
clear_screen() {
    clear
    tput cup 0 0
}

goto_xy() {
    tput cup "$1" "$2"
}

print_at() {
    local row=$1
    local col=$2
    local text="$3"
    goto_xy "$row" "$col"
    echo -n "$text"
}

center_text() {
    local text="$1"
    local width=${2:-$TERM_COLS}
    local padding=$(( (width - ${#text}) / 2 ))
    printf "%*s%s" "$padding" "" "$text"
}

draw_box() {
    local top=$1
    local left=$2
    local height=$3
    local width=$4
    local color="$5"
    
    # Top border
    goto_xy "$top" "$left"
    echo -ne "${color}┌$(printf '─%.0s' $(seq 1 $((width-2))))┐${NC}"
    
    # Side borders
    for ((i=1; i<height-1; i++)); do
        goto_xy $((top+i)) "$left"
        echo -ne "${color}│$(printf ' %.0s' $(seq 1 $((width-2))))│${NC}"
    done
    
    # Bottom border
    goto_xy $((top+height-1)) "$left"
    echo -ne "${color}└$(printf '─%.0s' $(seq 1 $((width-2))))┘${NC}"
}

draw_title_bar() {
    goto_xy 0 0
    echo -ne "${BLUE_BG}${WHITE_TEXT}"
    printf "%-${TERM_COLS}s" " PLEX GPU BALANCER INSTALLER v1.0"
    echo -ne "${NC}"
    
    goto_xy 1 0
    echo -ne "${CYAN_BG}${BLACK_TEXT}"
    printf "%-${TERM_COLS}s" " Proxmox VE Container Setup Wizard"
    echo -ne "${NC}"
}

draw_status_bar() {
    local message="$1"
    goto_xy $((TERM_ROWS-1)) 0
    echo -ne "${BLUE_BG}${WHITE_TEXT}"
    printf "%-${TERM_COLS}s" " $message"
    echo -ne "${NC}"
}

draw_warning_screen() {
    clear_screen
    draw_title_bar
    
    local box_width=70
    local box_height=15
    local box_top=5
    local box_left=$(( (TERM_COLS - box_width) / 2 ))
    
    draw_box "$box_top" "$box_left" "$box_height" "$box_width" "${RED_BG}${WHITE_TEXT}"
    
    print_at $((box_top+2)) $((box_left+2)) "${RED_BG}${WHITE_TEXT}$(center_text "⚠ WARNING - WORK IN PROGRESS ⚠" $((box_width-4)))"
    print_at $((box_top+4)) $((box_left+2)) "${RED_BG}${WHITE_TEXT}This project is NOT fully tested and should be used with caution."
    print_at $((box_top+6)) $((box_left+2)) "${RED_BG}${WHITE_TEXT}REQUIREMENTS:"
    print_at $((box_top+7)) $((box_left+4)) "${RED_BG}${WHITE_TEXT}• Must run on Proxmox VE host (not in container)"
    print_at $((box_top+8)) $((box_left+4)) "${RED_BG}${WHITE_TEXT}• Container MUST be PRIVILEGED for GPU access"
    print_at $((box_top+9)) $((box_left+4)) "${RED_BG}${WHITE_TEXT}• NVIDIA/Intel GPU with hardware acceleration"
    print_at $((box_top+10)) $((box_left+4)) "${RED_BG}${WHITE_TEXT}• Plex Pass subscription required"
    
    print_at $((box_top+12)) $((box_left+2)) "${RED_BG}${WHITE_TEXT}$(center_text "Press ENTER to continue or Ctrl+C to exit" $((box_width-4)))"
    echo -ne "${NC}"
    
    draw_status_bar "WARNING: Read carefully before proceeding"
    read -r
}

draw_input_screen() {
    local title="$1"
    local fields=("${@:2}")
    
    clear_screen
    draw_title_bar
    
    local box_width=80
    local box_height=$((${#fields[@]} * 2 + 8))
    local box_top=4
    local box_left=$(( (TERM_COLS - box_width) / 2 ))
    
    draw_box "$box_top" "$box_left" "$box_height" "$box_width" "${WHITE_BG}${BLACK_TEXT}"
    
    print_at $((box_top+1)) $((box_left+2)) "${WHITE_BG}${BLUE_TEXT}$(center_text "$title" $((box_width-4)))"
    print_at $((box_top+2)) $((box_left+2)) "${WHITE_BG}${BLACK_TEXT}$(printf '─%.0s' $((box_width-4)))"
    
    local row=$((box_top+4))
    for field in "${fields[@]}"; do
        print_at "$row" $((box_left+4)) "${WHITE_BG}${BLACK_TEXT}$field"
        ((row+=2))
    done
    
    echo -ne "${NC}"
}

get_input() {
    local prompt="$1"
    local default="$2"
    local row="$3"
    local col="$4"
    local input=""
    
    print_at "$row" "$col" "${WHITE_BG}${BLACK_TEXT}$prompt"
    if [ -n "$default" ]; then
        print_at "$row" $((col + ${#prompt} + 1)) "${WHITE_BG}${GRAY_TEXT}[$default]"
    fi
    print_at "$row" $((col + ${#prompt} + ${#default} + 4)) "${WHITE_BG}${BLACK_TEXT}> "
    
    goto_xy "$row" $((col + ${#prompt} + ${#default} + 6))
    echo -ne "${WHITE_BG}${BLACK_TEXT}"
    read -r input
    echo -ne "${NC}"
    
    if [ -z "$input" ] && [ -n "$default" ]; then
        input="$default"
    fi
    
    echo "$input"
}

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
import json, sys
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

show_error() {
    local message="$1"
    local row="$2"
    local col="$3"
    
    print_at "$row" "$col" "${RED_BG}${WHITE_TEXT} ERROR: $message ${NC}"
    sleep 2
    print_at "$row" "$col" "$(printf ' %.0s' $((${#message} + 10)))"
}

container_config_screen() {
    while true; do
        draw_input_screen "CONTAINER CONFIGURATION" \
            "Container ID (100-999999):" \
            "CPU Cores:" \
            "Memory (MB):"
        
        draw_status_bar "Enter container configuration details"
        
        local box_left=$(( (TERM_COLS - 80) / 2 ))
        local base_row=8
        
        CONTAINER_ID=$(get_input "Container ID:" "" "$base_row" $((box_left + 4)))
        if ! validate_container_id "$CONTAINER_ID"; then
            show_error "Invalid ID or container exists" $((base_row + 1)) $((box_left + 4))
            continue
        fi
        
        CPU_CORES=$(get_input "CPU Cores:" "1" $((base_row + 2)) $((box_left + 4)))
        if [[ ! "$CPU_CORES" =~ ^[0-9]+$ ]] || [ "$CPU_CORES" -lt 1 ] || [ "$CPU_CORES" -gt 32 ]; then
            show_error "CPU cores must be 1-32" $((base_row + 3)) $((box_left + 4))
            continue
        fi
        
        MEMORY=$(get_input "Memory (MB):" "512" $((base_row + 4)) $((box_left + 4)))
        if [[ ! "$MEMORY" =~ ^[0-9]+$ ]] || [ "$MEMORY" -lt 128 ]; then
            show_error "Memory must be at least 128MB" $((base_row + 5)) $((box_left + 4))
            continue
        fi
        
        break
    done
}

network_config_screen() {
    draw_input_screen "NETWORK CONFIGURATION" \
        "Use DHCP? (y/n):" \
        "Static IP (if not DHCP):" \
        "Gateway (if static):" \
        "DNS Server:"
    
    draw_status_bar "Configure container network settings"
    
    local box_left=$(( (TERM_COLS - 80) / 2 ))
    local base_row=8
    
    local use_dhcp=$(get_input "Use DHCP?" "y" "$base_row" $((box_left + 4)))
    
    if [[ ! "$use_dhcp" =~ ^[Yy] ]]; then
        while true; do
            CONTAINER_IP=$(get_input "Static IP:" "" $((base_row + 2)) $((box_left + 4)))
            if ! validate_ip "$CONTAINER_IP"; then
                show_error "Invalid IP address" $((base_row + 3)) $((box_left + 4))
                continue
            fi
            break
        done
        
        while true; do
            GATEWAY=$(get_input "Gateway:" "" $((base_row + 4)) $((box_left + 4)))
            if ! validate_ip "$GATEWAY"; then
                show_error "Invalid gateway IP" $((base_row + 5)) $((box_left + 4))
                continue
            fi
            break
        done
    fi
    
    local dns_input=$(get_input "DNS Server:" "8.8.8.8" $((base_row + 6)) $((box_left + 4)))
    if validate_ip "$dns_input"; then
        DNS="$dns_input"
    fi
}

plex_config_screen() {
    while true; do
        draw_input_screen "PLEX SERVER CONFIGURATION" \
            "Plex Server (IP:PORT):" \
            "Plex Token:" \
            "" \
            "To get your token:" \
            "1. Open Plex in browser and login" \
            "2. Press F12, go to Console tab" \
            "3. Type: localStorage.getItem('myPlexAccessToken')" \
            "4. Copy the token (without quotes)"
        
        draw_status_bar "Configure Plex server connection"
        
        local box_left=$(( (TERM_COLS - 80) / 2 ))
        local base_row=8
        
        PLEX_SERVER=$(get_input "Server (IP:PORT):" "" "$base_row" $((box_left + 4)))
        if [ -z "$PLEX_SERVER" ]; then
            show_error "Server address required" $((base_row + 1)) $((box_left + 4))
            continue
        fi
        
        PLEX_TOKEN=$(get_input "Token:" "" $((base_row + 2)) $((box_left + 4)))
        if [ -z "$PLEX_TOKEN" ]; then
            show_error "Token required" $((base_row + 3)) $((box_left + 4))
            continue
        fi
        
        # Show validation message
        print_at $((base_row + 4)) $((box_left + 4)) "${WHITE_BG}${BLUE_TEXT}Validating connection...${NC}"
        
        if validate_plex "$PLEX_SERVER" "$PLEX_TOKEN"; then
            print_at $((base_row + 4)) $((box_left + 4)) "${GREEN_BG}${WHITE_TEXT}✓ Connected to: $PLEX_SERVER_NAME${NC}"
            sleep 2
            break
        else
            show_error "Cannot connect to Plex server" $((base_row + 4)) $((box_left + 4))
        fi
    done
}

show_progress() {
    local title="$1"
    local message="$2"
    local step="$3"
    local total="$4"
    
    clear_screen
    draw_title_bar
    
    local box_width=60
    local box_height=10
    local box_top=8
    local box_left=$(( (TERM_COLS - box_width) / 2 ))
    
    draw_box "$box_top" "$box_left" "$box_height" "$box_width" "${GREEN_BG}${WHITE_TEXT}"
    
    print_at $((box_top+1)) $((box_left+2)) "${GREEN_BG}${WHITE_TEXT}$(center_text "$title" $((box_width-4)))"
    print_at $((box_top+3)) $((box_left+2)) "${GREEN_BG}${WHITE_TEXT}$message"
    
    if [ -n "$step" ] && [ -n "$total" ]; then
        local percent=$(( step * 100 / total ))
        local bar_width=40
        local filled=$(( percent * bar_width / 100 ))
        
        print_at $((box_top+5)) $((box_left+2)) "${GREEN_BG}${WHITE_TEXT}Progress: [$percent%]"
        print_at $((box_top+6)) $((box_left+2)) "${GREEN_BG}${WHITE_TEXT}["
        print_at $((box_top+6)) $((box_left+3)) "${GREEN_BG}${WHITE_TEXT}$(printf '█%.0s' $(seq 1 $filled))"
        print_at $((box_top+6)) $((box_left+3+filled)) "${GREEN_BG}${WHITE_TEXT}$(printf '░%.0s' $(seq 1 $((bar_width-filled))))"
        print_at $((box_top+6)) $((box_left+3+bar_width)) "${GREEN_BG}${WHITE_TEXT}]"
    fi
    
    echo -ne "${NC}"
    draw_status_bar "$message"
}

create_container() {
    show_progress "CREATING CONTAINER" "Setting up Proxmox container..." 1 8
    
    local net_config="name=eth0,bridge=vmbr0"
    if [ -n "$CONTAINER_IP" ]; then
        net_config+=",ip=${CONTAINER_IP}/24,gw=${GATEWAY}"
    else
        net_config+=",ip=dhcp"
    fi
    
    # Fix: Use --unprivileged 0 instead of --privileged 1
    if ! pct create "$CONTAINER_ID" \
        local:vztmpl/ubuntu-22.04-standard_22.04-1_amd64.tar.zst \
        --memory "$MEMORY" \
        --cores "$CPU_CORES" \
        --rootfs "local:4" \
        --net0 "$net_config" \
        --nameserver "$DNS" \
        --hostname "plex-gpu-balancer" \
        --unprivileged 0 \
        --features nesting=1 \
        --onboot 1 >/dev/null 2>&1; then
        
        show_error "Failed to create container" 15 10
        exit 1
    fi
}

setup_gpu_passthrough() {
    show_progress "GPU PASSTHROUGH" "Configuring GPU access..." 2 8
    
    local config_file="/etc/pve/lxc/${CONTAINER_ID}.conf"
    
    # Add GPU passthrough configuration
    cat >> "$config_file" << EOF

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
}

start_container() {
    show_progress "STARTING CONTAINER" "Booting container..." 3 8
    
    if ! pct start "$CONTAINER_ID" >/dev/null 2>&1; then
        show_error "Failed to start container" 15 10
        exit 1
    fi
    
    sleep 10
}

install_dependencies() {
    show_progress "INSTALLING PACKAGES" "Updating and installing packages..." 4 8
    
    pct exec "$CONTAINER_ID" -- apt update >/dev/null 2>&1
    pct exec "$CONTAINER_ID" -- apt install -y \
        python3 python3-pip git curl wget unzip \
        intel-gpu-tools nvidia-utils-535 >/dev/null 2>&1
}

download_project() {
    show_progress "DOWNLOADING PROJECT" "Getting Plex GPU Balancer..." 5 8
    
    pct exec "$CONTAINER_ID" -- mkdir -p /tmp/download
    pct exec "$CONTAINER_ID" -- git clone \
        https://github.com/kotysoft/plex-gpu-balancer-public.git \
        /tmp/download >/dev/null 2>&1
    
    pct exec "$CONTAINER_ID" -- mkdir -p "$PROJECT_PATH"
    pct exec "$CONTAINER_ID" -- cp -r /tmp/download/* "$PROJECT_PATH/"
    pct exec "$CONTAINER_ID" -- rm -rf /tmp/download
    
    pct exec "$CONTAINER_ID" -- pip3 install -r "$PROJECT_PATH/requirements.txt" >/dev/null 2>&1
}

create_configs() {
    show_progress "CREATING CONFIGS" "Setting up configuration files..." 6 8
    
    pct exec "$CONTAINER_ID" -- bash -c "cat > $PROJECT_PATH/config.conf << EOF
[system]
project_path = $PROJECT_PATH

[plex]
server = $PLEX_SERVER
token = $PLEX_TOKEN
EOF"
    
    pct exec "$CONTAINER_ID" -- cp \
        "$PROJECT_PATH/balance.conf.template" \
        "$PROJECT_PATH/balance.conf"
}

install_services() {
    show_progress "INSTALLING SERVICES" "Setting up system services..." 7 8
    
    pct exec "$CONTAINER_ID" -- bash "$PROJECT_PATH/service-install.sh" >/dev/null 2>&1
}

show_completion() {
    show_progress "INSTALLATION COMPLETE" "Setup finished successfully!" 8 8
    
    sleep 3
    
    clear_screen
    draw_title_bar
    
    local box_width=70
    local box_height=20
    local box_top=3
    local box_left=$(( (TERM_COLS - box_width) / 2 ))
    
    draw_box "$box_top" "$box_left" "$box_height" "$box_width" "${GREEN_BG}${WHITE_TEXT}"
    
    print_at $((box_top+1)) $((box_left+2)) "${GREEN_BG}${WHITE_TEXT}$(center_text "INSTALLATION COMPLETED SUCCESSFULLY" $((box_width-4)))"
    print_at $((box_top+3)) $((box_left+2)) "${GREEN_BG}${WHITE_TEXT}Container ID: $CONTAINER_ID"
    print_at $((box_top+4)) $((box_left+2)) "${GREEN_BG}${WHITE_TEXT}Hostname: plex-gpu-balancer"
    print_at $((box_top+5)) $((box_left+2)) "${GREEN_BG}${WHITE_TEXT}Resources: ${CPU_CORES} CPU, ${MEMORY}MB RAM"
    
    if [ -n "$CONTAINER_IP" ]; then
        print_at $((box_top+6)) $((box_left+2)) "${GREEN_BG}${WHITE_TEXT}IP Address: $CONTAINER_IP"
    else
        print_at $((box_top+6)) $((box_left+2)) "${GREEN_BG}${WHITE_TEXT}Network: DHCP"
    fi
    
    print_at $((box_top+8)) $((box_left+2)) "${GREEN_BG}${WHITE_TEXT}Plex Server: $PLEX_SERVER"
    print_at $((box_top+9)) $((box_left+2)) "${GREEN_BG}${WHITE_TEXT}Server Name: $PLEX_SERVER_NAME"
    
    print_at $((box_top+11)) $((box_left+2)) "${GREEN_BG}${WHITE_TEXT}Dashboard: http://${CONTAINER_IP:-localhost}:8080"
    print_at $((box_top+12)) $((box_left+2)) "${GREEN_BG}${WHITE_TEXT}Project Path: $PROJECT_PATH"
    
    print_at $((box_top+14)) $((box_left+2)) "${GREEN_BG}${WHITE_TEXT}USEFUL COMMANDS:"
    print_at $((box_top+15)) $((box_left+2)) "${GREEN_BG}${WHITE_TEXT}pct enter $CONTAINER_ID"
    print_at $((box_top+16)) $((box_left+2)) "${GREEN_BG}${WHITE_TEXT}pct exec $CONTAINER_ID -- systemctl status plex-gpu-collector"
    
    print_at $((box_top+18)) $((box_left+2)) "${GREEN_BG}${WHITE_TEXT}$(center_text "Press ENTER to exit" $((box_width-4)))"
    
    echo -ne "${NC}"
    draw_status_bar "Installation completed - All services are running"
    read -r
}

main() {
    # Debug mode for troubleshooting
    echo "Starting Plex GPU Balancer installer..."
    echo "Terminal size: ${TERM_COLS}x${TERM_ROWS}"
    
    # Check environment
    if ! command -v pct >/dev/null 2>&1; then
        echo "ERROR: This installer must be run on a Proxmox VE host"
        exit 1
    fi
    
    if [ "$EUID" -ne 0 ]; then
        echo "ERROR: This script must be run as root"
        exit 1
    fi
    
    # Test tput functionality
    if ! tput smcup 2>/dev/null; then
        echo "Warning: Terminal doesn't support full-screen mode"
        echo "Running in simple mode..."
        simple_install
        return
    fi
    
    # Initialize terminal
    trap 'tput rmcup; exit' EXIT INT TERM
    
    # Run installation wizard
    draw_warning_screen
    container_config_screen
    network_config_screen
    plex_config_screen
    
    # Install
    create_container
    setup_gpu_passthrough
    start_container
    install_dependencies
    download_project
    create_configs
    install_services
    show_completion
}

simple_install() {
    echo "==============================================="
    echo "PLEX GPU BALANCER INSTALLER (Simple Mode)"
    echo "==============================================="
    echo
    echo "⚠ WARNING: Work in progress project"
    echo "Press Enter to continue..."
    read -r
    
    echo "Enter Container ID (100-999999):"
    read -r CONTAINER_ID
    
    echo "Enter CPU cores (default: 1):"
    read -r CPU_CORES
    CPU_CORES=${CPU_CORES:-1}
    
    echo "Enter Memory in MB (default: 512):"
    read -r MEMORY
    MEMORY=${MEMORY:-512}
    
    echo "Use DHCP? (y/n, default: y):"
    read -r use_dhcp
    use_dhcp=${use_dhcp:-y}
    
    if [[ ! "$use_dhcp" =~ ^[Yy] ]]; then
        echo "Enter static IP:"
        read -r CONTAINER_IP
        echo "Enter gateway:"
        read -r GATEWAY
    fi
    
    echo "Enter Plex server (IP:PORT):"
    read -r PLEX_SERVER
    
    echo "Enter Plex token:"
    read -r PLEX_TOKEN
    
    echo "Creating container..."
    create_container_simple
    
    echo "Installation complete!"
}

create_container_simple() {
    local net_config="name=eth0,bridge=vmbr0"
    if [ -n "$CONTAINER_IP" ]; then
        net_config+=",ip=${CONTAINER_IP}/24,gw=${GATEWAY}"
    else
        net_config+=",ip=dhcp"
    fi
    
    echo "Running: pct create $CONTAINER_ID ..."
    pct create "$CONTAINER_ID" \
        local:vztmpl/ubuntu-22.04-standard_22.04-1_amd64.tar.zst \
        --memory "$MEMORY" \
        --cores "$CPU_CORES" \
        --rootfs "local:4" \
        --net0 "$net_config" \
        --nameserver "8.8.8.8" \
        --hostname "plex-gpu-balancer" \
        --unprivileged 0 \
        --features nesting=1 \
        --onboot 1
    
    echo "Container created successfully!"
}

main "$@"
