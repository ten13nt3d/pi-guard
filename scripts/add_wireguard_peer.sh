#!/bin/bash
# WireGuard Peer Management Script
# Adds new peers to the WireGuard VPN server
#
# Usage: ./scripts/add_wireguard_peer.sh <peer_name>
# Example: ./scripts/add_wireguard_peer.sh laptop

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Check arguments
if [ $# -lt 1 ]; then
    echo "Usage: $0 <peer_name>"
    echo ""
    echo "Examples:"
    echo "  $0 laptop"
    echo "  $0 android-phone"
    echo "  $0 work-pc"
    echo ""
    echo "Peer names should be lowercase, alphanumeric with hyphens only."
    exit 1
fi

PEER_NAME="$1"

# Validate peer name
if ! [[ "$PEER_NAME" =~ ^[a-z0-9-]+$ ]]; then
    log_error "Invalid peer name: $PEER_NAME"
    log_error "Use only lowercase letters, numbers, and hyphens"
    exit 1
fi

# Check if WireGuard container is running
if ! docker ps --format '{{.Names}}' | grep -q '^wireguard$'; then
    log_error "WireGuard container is not running"
    log_error "Start it first: docker compose up -d wireguard"
    exit 1
fi

# Check if peer already exists
PEER_DIR="./config/wireguard/peer_${PEER_NAME}"
if [ -d "$PEER_DIR" ]; then
    log_warn "Peer '$PEER_NAME' already exists!"
    echo ""
    echo "Existing config location: $PEER_DIR"
    echo ""
    read -p "Do you want to regenerate this peer? (y/N): " CONFIRM
    if [ "$CONFIRM" != "y" ] && [ "$CONFIRM" != "Y" ]; then
        log_info "Aborted. Existing peer config preserved."
        exit 0
    fi
fi

log_info "Adding new WireGuard peer: $PEER_NAME"

# Get current PEERS list from the container
CURRENT_PEERS=$(docker exec wireguard printenv PEERS 2>/dev/null || echo "")
log_info "Current peers: $CURRENT_PEERS"

# Add new peer to the list if not already present
if echo "$CURRENT_PEERS" | grep -qw "$PEER_NAME"; then
    log_info "Peer already in PEERS list, regenerating config..."
else
    NEW_PEERS="${CURRENT_PEERS},${PEER_NAME}"
    log_info "New peers list: $NEW_PEERS"

    # Update the .env file if it exists
    if [ -f ".env" ]; then
        if grep -q "^PEERS=" .env; then
            log_warn "Note: Update PEERS in .env file to persist: PEERS=$NEW_PEERS"
        fi
    fi
fi

# Restart WireGuard to generate new peer
log_info "Regenerating WireGuard configuration..."

# The linuxserver/wireguard image regenerates peers on restart
# We need to update the PEERS environment variable
docker exec wireguard bash -c "
# Generate new peer keys
mkdir -p /config/peer_${PEER_NAME}
cd /config/peer_${PEER_NAME}

# Generate keys if they don't exist
if [ ! -f privatekey-peer_${PEER_NAME} ]; then
    wg genkey | tee privatekey-peer_${PEER_NAME} | wg pubkey > publickey-peer_${PEER_NAME}
fi

PRIVATE_KEY=\$(cat privatekey-peer_${PEER_NAME})
PUBLIC_KEY=\$(cat publickey-peer_${PEER_NAME})
SERVER_PUBLIC_KEY=\$(cat /config/server/publickey-server 2>/dev/null || cat /config/wg0.conf | grep 'PrivateKey' | cut -d'=' -f2 | tr -d ' ' | wg pubkey)

# Get server endpoint
ENDPOINT=\$(printenv SERVERURL || echo 'your-server.duckdns.org')
PORT=\$(printenv SERVERPORT || echo '51820')

# Get next available IP
SUBNET=\$(printenv INTERNAL_SUBNET || echo '10.13.13.0')
SUBNET_BASE=\${SUBNET%.*}

# Find next available peer number
PEER_NUM=2
for dir in /config/peer_*; do
    if [ -d \"\$dir\" ]; then
        ((PEER_NUM++))
    fi
done

PEER_IP=\"\${SUBNET_BASE}.\${PEER_NUM}\"

# Get DNS server
DNS=\$(printenv PEERDNS || echo '10.13.13.1')

# Create peer config
cat > peer_${PEER_NAME}.conf << CONF
[Interface]
PrivateKey = \$PRIVATE_KEY
Address = \$PEER_IP/32
DNS = \$DNS

[Peer]
PublicKey = \$SERVER_PUBLIC_KEY
AllowedIPs = 0.0.0.0/0, ::/0
Endpoint = \$ENDPOINT:\$PORT
PersistentKeepalive = 25
CONF

# Add peer to server config if not already present
if ! grep -q \"\$PUBLIC_KEY\" /config/wg0.conf 2>/dev/null; then
    cat >> /config/wg0.conf << PEER

[Peer]
# peer_${PEER_NAME}
PublicKey = \$PUBLIC_KEY
AllowedIPs = \$PEER_IP/32
PEER
fi

echo \"Peer IP: \$PEER_IP\"
"

# Reload WireGuard config
log_info "Reloading WireGuard configuration..."
docker exec wireguard wg syncconf wg0 <(docker exec wireguard wg-quick strip wg0) 2>/dev/null || \
    docker restart wireguard

log_info "Peer '$PEER_NAME' added successfully!"
echo ""
echo "================================================"
echo "          Peer Configuration"
echo "================================================"
echo ""
echo "Config file location:"
echo "  $PEER_DIR/peer_${PEER_NAME}.conf"
echo ""
echo "To view the config:"
echo "  cat $PEER_DIR/peer_${PEER_NAME}.conf"
echo ""
echo "To generate QR code (for mobile devices):"
echo "  docker exec wireguard cat /config/peer_${PEER_NAME}/peer_${PEER_NAME}.png"
echo "  # Or use qrencode:"
echo "  qrencode -t ansiutf8 < $PEER_DIR/peer_${PEER_NAME}.conf"
echo ""
echo "================================================"

# Show the config if it exists
if [ -f "$PEER_DIR/peer_${PEER_NAME}.conf" ]; then
    echo ""
    log_info "Generated configuration:"
    echo "----------------------------------------"
    cat "$PEER_DIR/peer_${PEER_NAME}.conf"
    echo "----------------------------------------"
fi
