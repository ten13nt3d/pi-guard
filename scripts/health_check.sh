#!/bin/bash
# Pi-Guard Health Check Script
# Verifies all services are running properly
#
# Usage: ./scripts/health_check.sh

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Status indicators
PASS="${GREEN}[PASS]${NC}"
FAIL="${RED}[FAIL]${NC}"
WARN="${YELLOW}[WARN]${NC}"
INFO="${BLUE}[INFO]${NC}"

# Counters
CHECKS_PASSED=0
CHECKS_FAILED=0
CHECKS_WARNED=0

check_pass() {
    echo -e "$PASS $1"
    ((CHECKS_PASSED++))
}

check_fail() {
    echo -e "$FAIL $1"
    ((CHECKS_FAILED++))
}

check_warn() {
    echo -e "$WARN $1"
    ((CHECKS_WARNED++))
}

check_info() {
    echo -e "$INFO $1"
}

echo "================================================"
echo "        Pi-Guard System Health Check"
echo "================================================"
echo ""

# 1. Check Docker
echo "--- Docker Engine ---"
if command -v docker &> /dev/null; then
    if docker info &> /dev/null; then
        check_pass "Docker is running"
        DOCKER_VERSION=$(docker --version | cut -d' ' -f3 | tr -d ',')
        check_info "Docker version: $DOCKER_VERSION"
    else
        check_fail "Docker is installed but not running"
    fi
else
    check_fail "Docker is not installed"
fi
echo ""

# 2. Check Docker Compose
echo "--- Docker Compose ---"
if docker compose version &> /dev/null; then
    COMPOSE_VERSION=$(docker compose version --short 2>/dev/null || echo "unknown")
    check_pass "Docker Compose is available (v$COMPOSE_VERSION)"
else
    check_fail "Docker Compose is not available"
fi
echo ""

# 3. Check Containers
echo "--- Container Status ---"
EXPECTED_CONTAINERS=("portainer" "pihole" "wireguard" "kali" "tor" "nginx-hidden")

for container in "${EXPECTED_CONTAINERS[@]}"; do
    if docker ps --format '{{.Names}}' | grep -q "^${container}$"; then
        STATUS=$(docker inspect --format='{{.State.Health.Status}}' "$container" 2>/dev/null || echo "no-healthcheck")
        if [ "$STATUS" = "healthy" ]; then
            check_pass "$container is running (healthy)"
        elif [ "$STATUS" = "no-healthcheck" ]; then
            check_pass "$container is running"
        elif [ "$STATUS" = "starting" ]; then
            check_warn "$container is starting..."
        else
            check_warn "$container is running but unhealthy ($STATUS)"
        fi
    elif docker ps -a --format '{{.Names}}' | grep -q "^${container}$"; then
        check_fail "$container exists but is not running"
    else
        check_warn "$container not found (may not be deployed)"
    fi
done
echo ""

# 4. Check DNS (Pi-hole)
echo "--- DNS Service (Pi-hole) ---"
if docker ps --format '{{.Names}}' | grep -q '^pihole$'; then
    if docker exec pihole dig +short google.com @127.0.0.1 &> /dev/null; then
        check_pass "Pi-hole DNS resolution working"
    else
        check_fail "Pi-hole DNS resolution failed"
    fi

    # Check Pi-hole web interface
    PI_IP=$(hostname -I | awk '{print $1}')
    if curl -s -o /dev/null -w "%{http_code}" "http://${PI_IP}/admin/" | grep -q "200\|301\|302"; then
        check_pass "Pi-hole web interface accessible"
    else
        check_warn "Pi-hole web interface may not be accessible"
    fi
else
    check_warn "Pi-hole container not running - skipping DNS checks"
fi
echo ""

# 5. Check WireGuard
echo "--- VPN Service (WireGuard) ---"
if docker ps --format '{{.Names}}' | grep -q '^wireguard$'; then
    if docker exec wireguard wg show &> /dev/null; then
        check_pass "WireGuard interface is up"
        PEERS=$(docker exec wireguard wg show wg0 peers 2>/dev/null | wc -l || echo "0")
        check_info "Configured peers: $PEERS"
    else
        check_fail "WireGuard interface not configured"
    fi

    # Check if config files exist
    if [ -d "./config/wireguard/peer_iphone" ]; then
        check_pass "WireGuard peer configs generated"
    else
        check_warn "WireGuard peer configs not yet generated"
    fi
else
    check_warn "WireGuard container not running - skipping VPN checks"
fi
echo ""

# 6. Check Tor
echo "--- Tor Hidden Service ---"
if docker ps --format '{{.Names}}' | grep -q '^tor$'; then
    if [ -f "./config/tor/hidden_service/hostname" ]; then
        ONION_ADDR=$(cat ./config/tor/hidden_service/hostname 2>/dev/null || echo "")
        if [ -n "$ONION_ADDR" ]; then
            check_pass "Tor hidden service configured"
            check_info "Onion address: $ONION_ADDR"
        else
            check_warn "Tor hidden service hostname file is empty"
        fi
    else
        check_warn "Tor hidden service not yet initialized"
    fi
else
    check_warn "Tor container not running - skipping Tor checks"
fi
echo ""

# 7. Check Portainer
echo "--- Portainer Management ---"
if docker ps --format '{{.Names}}' | grep -q '^portainer$'; then
    PI_IP=$(hostname -I | awk '{print $1}')
    if curl -sk -o /dev/null -w "%{http_code}" "https://${PI_IP}:9443" | grep -q "200\|301\|302"; then
        check_pass "Portainer web interface accessible"
        check_info "URL: https://${PI_IP}:9443"
    else
        check_warn "Portainer may need initial setup (first access)"
    fi
else
    check_warn "Portainer container not running"
fi
echo ""

# 8. Check disk space
echo "--- System Resources ---"
DISK_USAGE=$(df -h / | awk 'NR==2 {print $5}' | tr -d '%')
if [ "$DISK_USAGE" -lt 80 ]; then
    check_pass "Disk usage: ${DISK_USAGE}%"
elif [ "$DISK_USAGE" -lt 90 ]; then
    check_warn "Disk usage: ${DISK_USAGE}% (getting high)"
else
    check_fail "Disk usage: ${DISK_USAGE}% (critical!)"
fi

# Check memory
MEM_AVAILABLE=$(free -m | awk 'NR==2 {print $7}')
if [ "$MEM_AVAILABLE" -gt 500 ]; then
    check_pass "Available memory: ${MEM_AVAILABLE}MB"
elif [ "$MEM_AVAILABLE" -gt 200 ]; then
    check_warn "Available memory: ${MEM_AVAILABLE}MB (low)"
else
    check_fail "Available memory: ${MEM_AVAILABLE}MB (critical!)"
fi
echo ""

# 9. Check .env configuration
echo "--- Configuration ---"
if [ -f ".env" ]; then
    check_pass ".env file exists"

    # Check for placeholder values
    if grep -q "your-subdomain.duckdns.org" .env 2>/dev/null; then
        check_warn "SERVERURL still has placeholder value"
    fi
    if grep -q "CHANGE_ME" .env 2>/dev/null; then
        check_warn "PIHOLE_PASSWORD still has placeholder value"
    fi
else
    check_fail ".env file not found"
fi
echo ""

# Summary
echo "================================================"
echo "                   Summary"
echo "================================================"
echo -e "Passed:  ${GREEN}${CHECKS_PASSED}${NC}"
echo -e "Failed:  ${RED}${CHECKS_FAILED}${NC}"
echo -e "Warnings: ${YELLOW}${CHECKS_WARNED}${NC}"
echo ""

if [ "$CHECKS_FAILED" -eq 0 ]; then
    if [ "$CHECKS_WARNED" -eq 0 ]; then
        echo -e "${GREEN}All checks passed! Pi-Guard is healthy.${NC}"
    else
        echo -e "${YELLOW}System operational with warnings.${NC}"
    fi
    exit 0
else
    echo -e "${RED}Some checks failed. Review issues above.${NC}"
    exit 1
fi
