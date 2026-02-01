#!/bin/bash
# Enhanced AI Security Tools Installation Script
# Installs and configures AI-powered security tools in Kali container
#
# Usage: ./scripts/install_ai_tools.sh

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# TTY detection for docker exec
DOCKER_OPTS=""
if [ -t 0 ]; then
    DOCKER_OPTS="-it"
fi

# Check if Kali container is running
if ! docker ps --format '{{.Names}}' | grep -q '^kali$'; then
    log_error "Kali container is not running"
    log_error "Start it first: docker compose -f docker-compose.enhanced.yml up -d kali"
    exit 1
fi

log_info "Installing AI Security Tools..."

# 1. Install Python dependencies in Kali container
log_info "Installing Python dependencies..."
docker exec $DOCKER_OPTS kali bash -c "
apt-get update && apt-get install -y \
    python3-pip \
    python3-requests \
    python3-numpy \
    git \
    nmap \
    nikto \
    gobuster \
    subfinder \
    amass \
    sqlmap \
    whatweb \
    theHarvester \
    dirb \
    wfuzz \
    sslscan

pip3 install --break-system-packages \
    requests \
    beautifulsoup4 \
    lxml \
    colorama \
    tabulate
"

# 2. Install additional security tools
log_info "Installing additional security tools..."
docker exec $DOCKER_OPTS kali bash -c "
apt-get install -y \
    john \
    hashcat \
    hydra \
    metasploit-framework \
    aircrack-ng \
    wireshark-common \
    ettercap-text-only \
    sqlmap || true

pip3 install --break-system-packages \
    shodan \
    python-nmap \
    paramiko \
    scapy || true
"

# 3. Setup directories and permissions
log_info "Setting up directories..."
docker exec $DOCKER_OPTS kali bash -c "
mkdir -p /opt/ai-tools/{recon,bugbounty,pentest}
mkdir -p /shared/results/{recon,bugbounty,pentest}
chmod -R 755 /opt/ai-tools/
chmod -R 755 /shared/
"

# 4. Copy AI tools to Kali container (if they exist)
log_info "Copying AI tools to container..."
for tool in recon/recon_ai.py bugbounty/bugbounty_assistant.py pentest/pentest_assistant.py ai_launcher.py; do
    if [ -f "config/ai-tools/$tool" ]; then
        docker cp "config/ai-tools/$tool" "kali:/opt/ai-tools/$tool"
        log_info "Copied: $tool"
    else
        log_warn "Skipping (not found): $tool"
    fi
done

# 5. Create executable scripts
log_info "Creating executable scripts..."
docker exec $DOCKER_OPTS kali bash -c "
find /opt/ai-tools -name '*.py' -exec chmod +x {} \;
"

# 6. Install wordlists
log_info "Installing wordlists..."
docker exec $DOCKER_OPTS kali bash -c "
mkdir -p /usr/share/wordlists/custom
if [ ! -f /usr/share/wordlists/custom/common.txt ]; then
    wget -q -O /usr/share/wordlists/custom/common.txt https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/Web-Content/common.txt || true
fi
if [ ! -f /usr/share/wordlists/custom/directory-list-2.3-medium.txt ]; then
    wget -q -O /usr/share/wordlists/custom/directory-list-2.3-medium.txt https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/Web-Content/directory-list-2.3-medium.txt || true
fi
"

log_info "AI Security Tools Installation Complete!"
echo ""
log_info "Access AI Security Tools:"
echo "  1. Kali Container: docker exec -it kali bash"
echo "  2. AI Tools: docker exec -it kali python3 /opt/ai-tools/ai_launcher.py"
echo ""
log_info "Configure API Keys for enhanced AI features:"
echo "  - OPENAI_API_KEY=your_openai_key"
echo "  - ANTHROPIC_API_KEY=your_anthropic_key"
