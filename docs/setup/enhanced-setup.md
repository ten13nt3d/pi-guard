# Enhanced Setup Guide

This guide covers the complete HomeLab setup with Docker, Portainer, Kali Linux container, Pi-hole, and Tor services in addition to the core WireGuard VPN.

## Prerequisites
- Complete [Basic VPN Setup](basic-setup.md) first, or start fresh with this guide
- Raspberry Pi 4 (4GB+ recommended)
- 32GB+ microSD card

## Step 1: System Preparation

### Install Enhanced Stack
```bash
# Clone repo (if not already done)
git clone <your-repo-url> ~/pi-guard
cd ~/pi-guard

# Run enhanced installation script
chmod +x scripts/install_enhanced_pi.sh
./scripts/install_enhanced_pi.sh
```

### Manual Installation (Alternative)
If you prefer manual setup:

```bash
# Install Docker and utilities
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker pi
sudo apt install -y docker-compose-plugin

# Create docker networks
docker network create pi-guard_security_net
docker network create pi-guard_tor_net

# Reboot for group changes
sudo reboot
```

## Step 2: Services Configuration

### Enhanced Docker Compose Setup

Create `docker-compose.enhanced.yml`:

```yaml
services:
  # Core VPN Service
  wireguard:
    image: lscr.io/linuxserver/wireguard:latest
    container_name: wireguard
    cap_add:
      - NET_ADMIN
      - SYS_MODULE
    environment:
      - PUID=1000
      - PGID=1000
      - TZ=Etc/UTC
      - SERVERURL=your-subdomain.duckdns.org
      - SERVERPORT=51820
      - PEERS=iphone
      - PEERDNS=192.168.1.10
      - INTERNAL_SUBNET=10.13.13.0
    volumes:
      - ./config:/config
      - /lib/modules:/lib/modules:ro
    ports:
      - "51820:51820/udp"
    sysctls:
      - net.ipv4.conf.all.src_valid_mark=1
    restart: unless-stopped

  # Docker Management
  portainer:
    image: portainer/portainer-ce:latest
    container_name: portainer
    command: -H unix:///var/run/docker.sock
    ports:
      - "9443:9443"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - ./portainer:/data
    restart: unless-stopped
    networks:
      - pi-guard_security_net

  # DNS & Ad Blocking
  pihole:
    image: pihole/pihole:latest
    container_name: pihole
    environment:
      - TZ=Etc/UTC
      - WEBPASSWORD=admin123
    volumes:
      - ./pihole:/etc/pihole
      - ./dnsmasq.d:/etc/dnsmasq.d
    ports:
      - "53:53/tcp"
      - "53:53/udp"
      - "80:80/tcp"
    restart: unless-stopped
    networks:
      - pi-guard_security_net

  # Security Testing Container
  kali:
    image: kalilinux/kali-rolling:latest
    container_name: kali
    command: tail -f /dev/null
    volumes:
      - ./kali-tools:/tools
    restart: unless-stopped
    networks:
      - pi-guard_security_net

  # Tor Hidden Service
  tor:
    image: lscr.io/linuxserver/tor:latest
    container_name: tor
    environment:
      - PUID=1000
      - PGID=1000
      - TZ=Etc/UTC
    volumes:
      - ./config/tor:/config
    ports:
      - "9050:9050"
    restart: unless-stopped
    networks:
      - pi-guard_tor_net

  # Tor Hidden Web Service
  tor-hidden:
    image: nginx:alpine
    container_name: tor-hidden
    volumes:
      - ./tor-web:/usr/share/nginx/html
    restart: unless-stopped
    networks:
      - pi-guard_tor_net

networks:
  pi-guard_security_net:
    driver: bridge
  pi-guard_tor_net:
    driver: bridge
```

## Step 3: Service Configuration

### 3.1 WireGuard Configuration
Same as basic setup - update `SERVERURL` and `PEERDNS` with your values.

### 3.2 Portainer Setup
```bash
# Start services
docker-compose -f docker-compose.enhanced.yml up -d

# Access Portainer
# URL: https://your-pi-ip:9443
# Create admin account on first visit
```

### 3.3 Pi-hole Configuration
```bash
# Access Pi-hole admin
# URL: http://your-pi-ip/admin
# Default password: admin123

# Change router DHCP DNS to your Pi's IP
# Recommended: 192.168.1.10 (your Pi's IP)
```

### 3.4 Kali Linux Container Setup
```bash
# Enter container
docker exec -it kali bash

# Update and install tools
apt update
apt install -y nmap metasploit-framework wireshark-common nikto sqlmap gobuster

# Create tools directory for persistent scripts
mkdir -p /tools
```

### 3.5 Tor Hidden Service Configuration
```bash
# Create web content directory
mkdir -p tor-web
echo "<h1>Welcome to My Tor Hidden Service</h1>" > tor-web/index.html

# Find your .onion address
cat config/tor/hidden_service/hostname

# Restart Tor service
docker-compose -f docker-compose.enhanced.yml restart tor
```

## Step 4: Router Configuration

### Port Forwarding Setup
| Port | Protocol | Service | Exposure |
|------|----------|---------|----------|
| 51820 | UDP | WireGuard | Internet |
| 9443 | TCP | Portainer | LAN only |
| 80 | TCP | Pi-hole Admin | LAN only |

### DNS Configuration
1. Set router DHCP primary DNS to Pi's IP (192.168.1.10)
2. Optionally set secondary DNS to 1.1.1.1 or 8.8.8.8

## Step 5: Usage Examples

### Remote Access Workflow
```bash
# 1. Connect iPhone to WireGuard VPN
# 2. Access home network resources:
#    - SSH: ssh pi@192.168.1.10
#    - MacBook: ssh user@192.168.1.20
#    - Portainer: https://192.168.1.10:9443
# 3. Browse .onion site via Tor Browser
```

### Security Testing with Kali
```bash
# Port scanning
docker exec -it kali nmap -sS 192.168.1.0/24

# Web application testing
docker exec -it kali nikto -h http://target-site.com

# DNS enumeration
docker exec -it kali dnsenum domain.com

# Directory brute force
docker exec -it kali gobuster dir -u http://target-site.com -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt
```

### Pi-hole Management
```bash
# Update ad lists
docker exec -it pihole pihole -g

# View statistics
docker exec -it pihole pihole -c

# Whitelist domain
docker exec -it pihole pihole -w example.com

# Blacklist domain
docker exec -it pihole pihole -b example.com
```

### Tor Hidden Service Access
```bash
# View .onion address
cat config/tor/hidden_service/hostname

# Test locally through Tor
docker exec -it tor curl --socks5 127.0.0.1:9050 http://[your-onion-address].onion
```

## Step 6: Security Hardening

### Firewall Configuration
```bash
sudo apt install -y ufw

# Default policies
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Allow essential services
sudo ufw allow ssh
sudo ufw allow 51820/udp  # WireGuard

# Allow LAN services (adjust subnet if needed)
sudo ufw allow from 192.168.1.0/24 to any port 9443  # Portainer
sudo ufw allow from 192.168.1.0/24 to any port 80    # Pi-hole

# Enable firewall
sudo ufw enable
```

### Access Control
1. **Portainer**: Only expose to LAN, never to internet
2. **Kali Container**: Isolated network, no internet access by default
3. **Tor Service**: Anonymous by design, minimal exposure
4. **SSH**: Use key-based authentication only

## Step 7: Monitoring & Maintenance

### System Status Dashboard
```bash
# Check all containers
docker-compose -f docker-compose.enhanced.yml ps

# View resource usage
docker stats

# Check logs
docker-compose -f docker-compose.enhanced.yml logs -f [service-name]
```

### Backup Configuration
```bash
# Create backup script
cat > backup-config.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/home/pi/pi-guard-backups/$(date +%Y%m%d)"
mkdir -p "$BACKUP_DIR"

# Backup configurations
cp -r config/ "$BACKUP_DIR/"
cp -r pihole/ "$BACKUP_DIR/"
cp -r portainer/ "$BACKUP_DIR/"
cp docker-compose.enhanced.yml "$BACKUP_DIR/"

echo "Backup completed: $BACKUP_DIR"
EOF

chmod +x backup-config.sh
```

### Update Procedure
```bash
# Update all containers
docker-compose -f docker-compose.enhanced.yml pull
docker-compose -f docker-compose.enhanced.yml up -d

# Update Kali tools
docker exec -it kali apt update && apt upgrade -y
```

## Troubleshooting

### Common Issues

#### Portainer Not Accessible
1. Check if container is running: `docker ps | grep portainer`
2. Verify firewall allows port 9443 from LAN
3. Check logs: `docker logs portainer`

#### Pi-hole Not Blocking Ads
1. Ensure router DNS is set to Pi's IP
2. Check Pi-hole status: `docker exec -it pihole pihole status`
3. Force gravity update: `docker exec -it pihole pihole -g`

#### Kali Container No Internet
This is intentional for security. If needed:
```bash
# Add internet access temporarily
docker network connect bridge kali
docker network disconnect pi-guard_security_net kali

# Remember to re-isolate after use
docker network connect pi-guard_security_net kali
docker network disconnect bridge kali
```

#### Tor Service Issues
```bash
# Check Tor logs
docker logs tor

# Verify .onion address exists
ls -la config/tor/hidden_service/

# Restart Tor service
docker-compose -f docker-compose.enhanced.yml restart tor
```

## Network Architecture

```
Internet
    ↓
Router (Port Forwarding: 51820/UDP, 9443/TCP)
    ↓
Raspberry Pi
├── WireGuard (10.13.13.x) → iPhone VPN
├── Portainer (9443) → Docker Management
├── Pi-hole (53) → DNS/Ad Blocking
├── Kali Container → Security Tools (Isolated)
└── Tor Services (.onion) → Anonymous Hosting
```

## Performance Considerations

- **RAM Usage**: Monitor with `free -h`, consider 4GB+ Pi for all services
- **Storage**: Use high-quality SD card, consider external SSD
- **Network**: Gigabit switch recommended for multiple services
- **CPU**: CPU intensive tasks in Kali may affect other services

## Advanced Configuration

For security testing with AI assistance, see [ByteHunter Security Tools](../security/bytehunter.md).

For technical architecture details, see [System Overview](../architecture/system-overview.md).