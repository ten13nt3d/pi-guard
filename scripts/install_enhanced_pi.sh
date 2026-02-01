#!/bin/bash
# Enhanced Pi-Guard Installation Script
# Sets up Raspberry Pi with Docker, Portainer, and security tools
#
# Usage: ./scripts/install_enhanced_pi.sh

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging functions
log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Error handler
error_handler() {
    log_error "Installation failed at line $1"
    log_error "Please check the error above and try again"
    exit 1
}
trap 'error_handler $LINENO' ERR

# Check if running as root
check_not_root() {
    if [ "$EUID" -eq 0 ]; then
        log_error "Please do not run this script as root"
        log_error "Run as regular user: ./scripts/install_enhanced_pi.sh"
        exit 1
    fi
}

# Check for required commands
check_dependencies() {
    local missing=()
    for cmd in curl sudo; do
        if ! command -v "$cmd" &> /dev/null; then
            missing+=("$cmd")
        fi
    done

    if [ ${#missing[@]} -ne 0 ]; then
        log_error "Missing required commands: ${missing[*]}"
        exit 1
    fi
}

# Validate .env file exists
check_env_file() {
    if [ ! -f ".env" ]; then
        log_warn ".env file not found"
        if [ -f ".env.template" ]; then
            log_info "Creating .env from template..."
            cp .env.template .env
            log_warn "Please edit .env with your configuration before starting services"
            log_warn "Required: SERVERURL, PIHOLE_PASSWORD"
        else
            log_error ".env.template not found. Please create .env file manually."
            exit 1
        fi
    fi
}

echo "=== Enhanced Pi-Guard Installation ==="
echo ""

check_not_root
check_dependencies

# 1. System Update
log_info "Updating system packages..."
sudo apt-get update && sudo apt-get upgrade -y

# 2. Install Docker
if command -v docker &> /dev/null; then
    log_info "Docker already installed: $(docker --version)"
else
    log_info "Installing Docker..."
    curl -fsSL https://get.docker.com -o /tmp/get-docker.sh
    sudo sh /tmp/get-docker.sh
    rm /tmp/get-docker.sh
    sudo usermod -aG docker "$USER"
    log_warn "Added $USER to docker group. You may need to log out and back in."
fi

# 3. Install Docker Compose
if docker compose version &> /dev/null; then
    log_info "Docker Compose already installed: $(docker compose version)"
else
    log_info "Installing Docker Compose plugin..."
    sudo apt-get install -y docker-compose-plugin
fi

# 4. Enable Required Kernel Modules
log_info "Enabling kernel modules..."
for module in iptables ip6table_filter xt_MASQUERADE; do
    if ! grep -q "^$module$" /etc/modules 2>/dev/null; then
        echo "$module" | sudo tee -a /etc/modules > /dev/null
        log_info "Added module: $module"
    fi
done

# 5. Create Directory Structure
log_info "Creating configuration directories..."
mkdir -p config/{wireguard,pihole/{etc-pihole,etc-dnsmasq.d},kali,tor,nginx/html,portainer/data}
mkdir -p config/ai-tools/{recon,bugbounty,pentest,shared/results/{recon,vulnerability,bugbounty,report,opsec}}

# 6. Set Permissions
log_info "Setting permissions..."
sudo chown -R "$USER:$USER" config/

# 7. Check/Create .env file
check_env_file

# 8. Create Tor Configuration
log_info "Creating Tor configuration..."
cat > config/tor/torrc << 'EOF'
HiddenServiceDir /config/hidden_service
HiddenServicePort 80 nginx-hidden:80
EOF

# 9. Create Nginx Configuration for Hidden Service
log_info "Creating Nginx configuration..."
cat > config/nginx/nginx.conf << 'EOF'
events {
    worker_connections 1024;
}

http {
    server {
        listen 80;
        server_name localhost;

        location / {
            root /usr/share/nginx/html;
            index index.html;
        }

        # Security headers
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;
    }
}
EOF

# 10. Create Hidden Service Web Page
log_info "Creating hidden service page..."
cat > config/nginx/html/index.html << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <title>Pi-Guard Hidden Service</title>
    <style>
        body { font-family: monospace; background: #1a1a2e; color: #0f0; padding: 40px; }
        h1 { border-bottom: 1px solid #0f0; padding-bottom: 10px; }
        .status { color: #0ff; }
    </style>
</head>
<body>
    <h1>Pi-Guard Hidden Service</h1>
    <p>This is a secure hidden service running on your Raspberry Pi.</p>
    <p class="status">Status: Online</p>
</body>
</html>
EOF

# 11. Validate compose file syntax
log_info "Validating Docker Compose configuration..."
if docker compose -f docker-compose.enhanced.yml config > /dev/null 2>&1; then
    log_info "Docker Compose configuration is valid"
else
    log_error "Docker Compose configuration has errors:"
    docker compose -f docker-compose.enhanced.yml config
    exit 1
fi

# 12. Start Docker Services
log_info "Starting Docker services..."
docker compose -f docker-compose.enhanced.yml up -d

# 13. Wait for services to start
log_info "Waiting for services to initialize..."
sleep 10

# 14. Verify services
log_info "Verifying services..."
running_containers=$(docker ps --format "{{.Names}}" | wc -l)
log_info "Running containers: $running_containers"

echo ""
echo "=== Installation Complete ==="
echo ""
log_info "Access URLs:"
PI_IP=$(hostname -I | awk '{print $1}')
echo "  - Portainer: https://${PI_IP}:9443"
echo "  - Pi-hole:   http://${PI_IP}/admin"
echo "  - VPN:       Configure WireGuard with config in ./config/wireguard"
echo "  - Tor:       Check .onion address: ./scripts/get_onion_address.sh"
echo ""
log_info "Next steps:"
echo "  1. Edit .env with your DuckDNS subdomain and Pi-hole password"
echo "  2. Set up port forwarding on your router (UDP 51820)"
echo "  3. Import WireGuard config to your devices"
echo "  4. Access hidden service via Tor browser with .onion address"
echo ""
log_info "Useful commands:"
echo "  - Check status:    ./scripts/health_check.sh"
echo "  - Add VPN peer:    ./scripts/add_wireguard_peer.sh <peer_name>"
echo "  - Get onion addr:  ./scripts/get_onion_address.sh"
echo "  - Backup config:   ./scripts/backup.sh"
