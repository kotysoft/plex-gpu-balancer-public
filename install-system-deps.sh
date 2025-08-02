#!/bin/bash

echo "🚀 Installing Plex GPU Balancer system dependencies..."

# Update package list
echo "📦 Updating package list..."
sudo apt update

# Install packages from system-requirements.txt
echo "🔧 Installing system packages..."
sudo apt install -y $(cat system-requirements.txt | grep -v '^#' | grep -v '^$' | tr '\n' ' ')

echo "✅ System dependencies installation complete!"
echo ""

