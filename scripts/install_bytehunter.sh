#!/bin/bash
# ByteHunter AI Security System Installation Script
# Multi-Agent Security Testing Framework
#
# Usage: ./scripts/install_bytehunter.sh

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

# Validate required directories exist
validate_paths() {
    local required_dirs=(
        "config/ai-tools"
        "config/ai-tools/shared"
    )

    for dir in "${required_dirs[@]}"; do
        if [ ! -d "$dir" ]; then
            log_info "Creating missing directory: $dir"
            mkdir -p "$dir"
        fi
    done
}

log_info "Installing ByteHunter AI Security System..."

# Validate paths first
validate_paths

# 1. Start Kali container
log_info "Starting Kali container..."
docker compose -f docker-compose.bytehunter.yml up -d kali

# Wait for container to be ready
log_info "Waiting for Kali container to start..."
for i in {1..30}; do
    if docker ps --format '{{.Names}}' | grep -q '^kali$'; then
        break
    fi
    sleep 1
done

if ! docker ps --format '{{.Names}}' | grep -q '^kali$'; then
    log_error "Kali container failed to start"
    exit 1
fi

# 2. Install comprehensive security tools in Kali
log_info "Installing security tools in Kali container..."
docker exec $DOCKER_OPTS kali bash -c "
apt-get update && apt-get install -y \
    python3-pip python3-venv \
    nmap nikto gobuster subfinder amass sqlmap whatweb \
    theHarvester dirb wfuzz sslscan \
    john hashcat hydra metasploit-framework \
    aircrack-ng wireshark-common ettercap-text-only \
    git curl wget unzip || true

pip3 install --break-system-packages \
    requests beautifulsoup4 lxml colorama tabulate \
    python-nmap paramiko scapy shodan || true
"

# 3. Setup ByteHunter environment
log_info "Setting up ByteHunter environment..."
docker exec $DOCKER_OPTS kali bash -c "
mkdir -p /opt/ai-tools/{agents,reports,logs,configs}
mkdir -p /shared/results/{recon,vulnerability,bugbounty,report,opsec}
chmod -R 755 /opt/ai-tools/
chmod -R 755 /shared/

# Install wordlists
mkdir -p /usr/share/wordlists/custom
if [ ! -f /usr/share/wordlists/custom/common.txt ]; then
    wget -q -O /usr/share/wordlists/custom/common.txt https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/Web-Content/common.txt || true
fi
if [ ! -f /usr/share/wordlists/custom/directory-list-2.3-medium.txt ]; then
    wget -q -O /usr/share/wordlists/custom/directory-list-2.3-medium.txt https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/Web-Content/directory-list-2.3-medium.txt || true
fi
"

# 4. Copy ByteHunter system (if files exist)
log_info "Copying ByteHunter AI system..."
if [ -f "config/ai-tools/bytehunter.py" ]; then
    docker cp config/ai-tools/bytehunter.py kali:/opt/ai-tools/
    log_info "Copied bytehunter.py"
else
    log_warn "bytehunter.py not found - skipping"
fi

if [ -d "config/ai-tools/shared" ]; then
    docker cp config/ai-tools/shared/. kali:/shared/ 2>/dev/null || true
    log_info "Copied shared directory contents"
fi

# 5. Start ByteHunter system
log_info "Starting ByteHunter AI Security System..."
docker compose -f docker-compose.bytehunter.yml up -d bytehunter

# 6. Create ByteHunter launcher
log_info "Creating ByteHunter launcher..."
docker exec $DOCKER_OPTS kali bash -c "
cat > /usr/local/bin/bytehunter << 'LAUNCHER_EOF'
#!/bin/bash
echo 'ByteHunter AI Security System'
echo 'Multi-Agent Security Testing Framework'
echo ''
echo 'Starting ByteHunter...'
cd /opt/ai-tools
if [ -f bytehunter.py ]; then
    python3 bytehunter.py
else
    echo 'Error: bytehunter.py not found'
    echo 'Please ensure the AI tools are properly installed'
    exit 1
fi
LAUNCHER_EOF
chmod +x /usr/local/bin/bytehunter

cat > /usr/local/bin/security-tools << 'MENU_EOF'
#!/bin/bash
echo 'AI Security Tools Menu:'
echo '1. ByteHunter (Multi-Agent System)'
echo '2. Kali Linux Terminal'
echo '3. Portainer Management'
echo ''
read -p 'Select option (1-3): ' choice

case \$choice in
    1)
        bytehunter
        ;;
    2)
        echo 'Entering Kali Linux environment...'
        /bin/bash
        ;;
    3)
        echo 'Portainer: https://YOUR_PI_IP:9443'
        echo 'Use Portainer for container management'
        ;;
    *)
        echo 'Invalid option'
        ;;
esac
MENU_EOF
chmod +x /usr/local/bin/security-tools
"

log_info "ByteHunter AI Security System Installation Complete!"
echo ""
log_info "Access Methods:"
echo "  1. ByteHunter System: docker exec -it kali bytehunter"
echo "  2. Kali Linux: docker exec -it kali bash"
echo "  3. Security Tools Menu: docker exec -it kali security-tools"
echo "  4. Portainer: https://YOUR_PI_IP:9443"
echo ""
log_info "ByteHunter Multi-Agent System:"
echo "  - ReconAgent: Information gathering and mapping"
echo "  - VulnerabilityAgent: Security weakness identification"
echo "  - BugBountyAgent: Business logic and application testing"
echo "  - ReportAgent: Comprehensive security reporting"
echo "  - OpSecAgent: Operational security assessment"
echo ""
log_info "Configure AI API Keys for enhanced features:"
echo "  export OPENAI_API_KEY=your_openai_key"
echo "  export ANTHROPIC_API_KEY=your_anthropic_key"
