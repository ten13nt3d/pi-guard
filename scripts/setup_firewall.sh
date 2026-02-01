#!/bin/bash
# Pi-Guard Firewall Configuration Script
# Sets up UFW rules for Pi-Guard services
#
# Usage: sudo ./scripts/setup_firewall.sh

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    log_error "Please run this script as root: sudo ./scripts/setup_firewall.sh"
    exit 1
fi

# Check if UFW is installed
if ! command -v ufw &> /dev/null; then
    log_info "Installing UFW..."
    apt-get update && apt-get install -y ufw
fi

log_info "Configuring Pi-Guard firewall rules..."

# Reset UFW to defaults (optional, uncomment if needed)
# log_warn "Resetting UFW to defaults..."
# ufw --force reset

# Set default policies
log_info "Setting default policies..."
ufw default deny incoming
ufw default allow outgoing

# Allow SSH (important: don't lock yourself out!)
log_info "Allowing SSH (port 22)..."
ufw allow ssh

# WireGuard VPN
log_info "Allowing WireGuard VPN (UDP 51820)..."
ufw allow 51820/udp comment 'WireGuard VPN'

# Pi-hole DNS
log_info "Allowing DNS (port 53)..."
ufw allow 53/tcp comment 'Pi-hole DNS TCP'
ufw allow 53/udp comment 'Pi-hole DNS UDP'

# Pi-hole Web Interface (HTTP)
log_info "Allowing Pi-hole Web (port 80)..."
ufw allow 80/tcp comment 'Pi-hole Web Interface'

# Portainer HTTPS (restrict to LAN only)
log_info "Allowing Portainer (port 9443) from LAN only..."
ufw allow from 192.168.0.0/16 to any port 9443 proto tcp comment 'Portainer HTTPS (LAN)'
ufw allow from 10.13.13.0/24 to any port 9443 proto tcp comment 'Portainer HTTPS (VPN)'

# Portainer Agent (restrict to LAN only)
log_info "Allowing Portainer Agent (port 8000) from LAN only..."
ufw allow from 192.168.0.0/16 to any port 8000 proto tcp comment 'Portainer Agent (LAN)'
ufw allow from 10.13.13.0/24 to any port 8000 proto tcp comment 'Portainer Agent (VPN)'

# Tor SOCKS proxy (localhost only by default, but allow from VPN)
log_info "Allowing Tor SOCKS (port 9050) from VPN..."
ufw allow from 10.13.13.0/24 to any port 9050 proto tcp comment 'Tor SOCKS (VPN)'

# Optional: Tor hidden service web port (usually proxied through Tor)
# Uncomment if you need direct access for testing
# log_info "Allowing Tor hidden service (port 8080)..."
# ufw allow 8080/tcp comment 'Tor Hidden Service'

# Enable UFW
log_info "Enabling UFW..."
ufw --force enable

# Show status
log_info "Firewall status:"
ufw status verbose

echo ""
log_info "Firewall configuration complete!"
echo ""
log_warn "Important notes:"
echo "  1. SSH access is allowed - don't modify this rule without console access"
echo "  2. Portainer is restricted to LAN (192.168.x.x) and VPN (10.13.13.x)"
echo "  3. DNS is open for all devices to use Pi-hole"
echo "  4. WireGuard is open for VPN connections"
echo ""
log_info "To check firewall status: sudo ufw status"
log_info "To disable firewall: sudo ufw disable"
log_info "To see numbered rules: sudo ufw status numbered"
log_info "To delete a rule: sudo ufw delete <rule_number>"
