#!/bin/bash
# Get Tor Onion Address Script
# Retrieves the .onion address for the Pi-Guard hidden service
#
# Usage: ./scripts/get_onion_address.sh

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

HOSTNAME_FILE="./config/tor/hidden_service/hostname"

echo "================================================"
echo "       Pi-Guard Tor Hidden Service"
echo "================================================"
echo ""

# Check if Tor container is running
if ! docker ps --format '{{.Names}}' | grep -q '^tor$'; then
    log_warn "Tor container is not running"
    echo ""
    echo "Start it with:"
    echo "  docker compose up -d tor-hidden-service"
    echo ""

    # Check if hostname file exists anyway
    if [ -f "$HOSTNAME_FILE" ]; then
        log_info "Previous onion address found:"
        echo ""
        echo "  $(cat "$HOSTNAME_FILE")"
        echo ""
        log_warn "Note: Service is offline until Tor container starts"
    fi
    exit 1
fi

# Wait for Tor to initialize (if just started)
if [ ! -f "$HOSTNAME_FILE" ]; then
    log_info "Waiting for Tor to initialize hidden service..."
    for i in {1..30}; do
        if [ -f "$HOSTNAME_FILE" ]; then
            break
        fi
        echo -n "."
        sleep 2
    done
    echo ""
fi

# Check if hostname file exists
if [ -f "$HOSTNAME_FILE" ]; then
    ONION_ADDRESS=$(cat "$HOSTNAME_FILE")

    if [ -n "$ONION_ADDRESS" ]; then
        log_info "Hidden service is active!"
        echo ""
        echo "================================================"
        echo ""
        echo "  Onion Address:"
        echo ""
        echo "  $ONION_ADDRESS"
        echo ""
        echo "================================================"
        echo ""
        log_info "Access via Tor Browser:"
        echo "  http://$ONION_ADDRESS"
        echo ""
        log_info "Test with curl (requires Tor SOCKS proxy):"
        echo "  curl --socks5 localhost:9050 http://$ONION_ADDRESS"
        echo ""

        # Check if nginx-hidden is running
        if docker ps --format '{{.Names}}' | grep -q '^nginx-hidden$'; then
            log_info "Web server (nginx-hidden) is running"
        else
            log_warn "Web server (nginx-hidden) is not running!"
            echo "  Start it: docker compose up -d nginx-hidden"
        fi
    else
        log_error "Hostname file is empty"
        log_info "Tor may still be initializing. Try again in a moment."
    fi
else
    log_error "Hidden service hostname not found"
    echo ""
    echo "Possible causes:"
    echo "  1. Tor container just started - wait a few seconds"
    echo "  2. Tor configuration error - check docker logs tor"
    echo "  3. Missing torrc configuration"
    echo ""
    echo "To check Tor logs:"
    echo "  docker logs tor"
    echo ""
    echo "To restart Tor:"
    echo "  docker compose restart tor-hidden-service"
    exit 1
fi
