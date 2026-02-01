# pi-guard - HomeLab VPN on Raspberry Pi

A comprehensive HomeLab project featuring a secure VPN setup with Dockerized services including Portainer, Kali Linux container, Pi-hole, and Tor hidden services. The goal is to enable secure remote access from an iPhone to home network resources through a Raspberry Pi.

## Overview

### Core Services
- **WireGuard VPN** - Secure remote access tunnel
- **Docker & Portainer** - Containerized services with web management
- **Kali Linux Container** - Security testing tools suite
- **Pi-hole** - Network-wide ad blocking and DNS control
- **Tor Onion Service** - Anonymous web service hosting

### Hardware Requirements
- Raspberry Pi 4 (4GB+ recommended)
- 32GB+ microSD card
- Stable internet connection

## Quick Start

### 1. System Setup
```bash
# Flash Raspberry Pi OS Lite (64-bit) to SD card
# Enable SSH by creating empty 'ssh' file in boot partition
# Boot Pi and connect via SSH
ssh pi@raspberrypi.local
```

### 2. Install pi-guard
```bash
# Clone and setup
git clone <your-repo-url> ~/pi-guard
cd ~/pi-guard

# Run installation script
chmod +x scripts/install_enhanced_pi.sh
./scripts/install_enhanced_pi.sh
```

### 3. Start Services
```bash
# Launch all services
docker-compose -f docker-compose.enhanced.yml up -d

# Check status
docker ps
```

## Service Configuration

### WireGuard VPN
Edit `docker-compose.enhanced.yml`:
```yaml
# Update these values:
SERVERURL=your-subdomain.duckdns.org
PEERDNS=192.168.1.10  # Your Pi's IP
```

**Router Setup:**
- Forward UDP 51820 to Raspberry Pi
- Configure DDNS (DuckDNS recommended)

### Portainer (Docker Management)
- Access: `https://your-pi-ip:9443`
- Create admin account on first visit
- Manage all containers via web interface

### Kali Linux Container
```bash
# Access security tools
docker exec -it kali bash

# Update tools
apt update && apt install -y nmap metasploit-framework wireshark-common
```

### Pi-hole (DNS & Ad Blocking)
- Web interface: `http://your-pi-ip/admin`
- Default login: `admin/admin123`
- **Router Setup:** Set router DHCP DNS to Pi's IP address

### Tor Onion Service
```bash
# Find your .onion address
cat config/tor/hidden_service/hostname

# Access via Tor Browser when connected to VPN
```

## Network Architecture

```
Internet → Router → Raspberry Pi → Services
           │
    iPhone (WireGuard VPN)
           │
    MacBook Pro (Home LAN)
```

### Service Ports
| Service | Port | Purpose | Exposure |
|---------|------|---------|----------|
| WireGuard | 51820/UDP | VPN server | Internet |
| Portainer | 9443/TCP | Docker UI | LAN only |
| Pi-hole | 53/UDP+TCP | DNS | LAN |
| Pi-hole Web | 80/TCP | Admin interface | LAN |
| Tor | 9050/TCP | SOCKS proxy | LAN |
| Tor Hidden | 80/TCP | .onion service | Via Tor |

## Advanced Features

### Security Testing with Kali
```bash
# Port scanning
docker exec -it kali nmap -sS 192.168.1.0/24

# Web app testing
docker exec -it kali nikto -h http://target-site.com

# Metasploit framework
docker exec -it kali msfconsole
```

### AI Security Tools (Optional)
For advanced security testing, see [ByteHunter AI Security System](docs/security/bytehunter.md).

## Router Configuration

### Essential Port Forwards
- **UDP 51820** → Raspberry Pi (WireGuard VPN)
- **TCP 9443** → Raspberry Pi (Portainer - LAN access only)
- **TCP 80** → Raspberry Pi (Pi-hole admin - LAN only)

### DDNS Setup
1. Register with DuckDNS or similar service
2. Update `SERVERURL` in docker-compose.yml
3. Configure DDNS container for automatic updates

## Security Best Practices

### Firewall Setup (UFW)
```bash
sudo apt install ufw
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 51820/udp
sudo ufw enable
```

### Access Control
- **Portainer**: Only expose to LAN, not internet
- **Kali Container**: Isolated network, no internet access by default
- **Tor Service**: Anonymous by design
- **Pi-hole**: Should be primary DNS for network

## Operations

### Common Commands
```bash
# Start all services
docker-compose -f docker-compose.enhanced.yml up -d

# View logs
docker-compose -f docker-compose.enhanced.yml logs -f [service-name]

# Restart specific service
docker-compose -f docker-compose.enhanced.yml restart wireguard

# Update containers
docker-compose -f docker-compose.enhanced.yml pull
docker-compose -f docker-compose.enhanced.yml up -d

# System status
docker ps -a
docker system df
```

### Maintenance
```bash
# Clean up unused containers
docker system prune -a

# Update Pi-hole ad lists
docker exec -it pihole pihole -g

# Rotate WireGuard keys (if needed)
docker exec -it wireguard /config/add-peer.sh
```

## Installation Scripts

### Basic VPN Setup
For WireGuard-only installation, see [docs/setup/basic-setup.md](docs/setup/basic-setup.md).

### Enhanced Setup (Full Stack)
For comprehensive installation with all services, see [docs/setup/enhanced-setup.md](docs/setup/enhanced-setup.md).

## Troubleshooting

### Common Issues

#### WireGuard Not Connecting
```bash
# Check port forwarding
docker logs wireguard

# Verify DDNS resolution
nslookup your-subdomain.duckdns.org

# Check WireGuard status
docker exec -it wireguard wg
```

#### Pi-hole Not Blocking Ads
```bash
# Verify router DNS settings point to Pi
# Check Pi-hole status
docker logs pihole

# Force gravity update
docker exec -it pihole pihole -g
```

#### Container Not Starting
```bash
# Check system resources
docker system df
free -h

# View detailed logs
docker-compose -f docker-compose.enhanced.yml logs [service-name]

# Reset to defaults
docker-compose -f docker-compose.enhanced.yml down -v
docker-compose -f docker-compose.enhanced.yml up -d
```

### Debug Commands
```bash
# Network connectivity test
docker exec -it [container] ping google.com

# Check port bindings
netstat -tlnp | grep :[port]

# Monitor system resources
htop
docker stats
```

## Alternative Configurations

### Tailscale/Headscale Alternative
If you prefer zero-config networking over WireGuard:

**Tailscale (Hosted)**:
- No port forwarding required
- Easiest setup, SaaS control plane
- Connect via 100.x.x.x IP addresses

**Headscale (Self-hosted)**:
- Same UX as Tailscale, but self-hosted control plane
- Full control, no SaaS dependency
- More setup work required

See [VPN Alternatives](docs/architecture/system-overview.md) for detailed comparison.

### DNS Options
- **Pi-hole**: Network-wide ad blocking (default)
- **AdGuard Home**: Alternative with more features
- **Cloudflare/Google**: Public resolvers (fallback)

## Documentation

- [Basic VPN Setup](docs/setup/basic-setup.md) - WireGuard-only installation
- [Enhanced Setup](docs/setup/enhanced-setup.md) - Full stack with all services
- [ByteHunter Security Tools](docs/security/bytehunter.md) - AI-powered security testing
- [System Architecture](docs/architecture/system-overview.md) - Technical overview
- [AGENTS.md](AGENTS.md) - Project conventions and development guidelines


