# Basic VPN Setup

This guide covers the core WireGuard VPN setup without additional services. Perfect for those who want a simple, secure VPN tunnel to their home network.

## Hardware Requirements
- Raspberry Pi 3B+ or newer
- 16GB+ microSD card
- Stable internet connection

## Step 1: System Setup

### Flash OS
1. Download **Raspberry Pi OS Lite (64-bit)**
2. Flash using Raspberry Pi Imager
3. Enable SSH: Create empty file named `ssh` in boot partition

### Initial Setup
```bash
ssh pi@raspberrypi.local
sudo raspi-config
# - Expand filesystem
# - Set static IP or DHCP reservation (recommended: 192.168.1.10)
# - Update system
sudo apt update && sudo apt upgrade -y
```

## Step 2: Docker Installation
```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker pi

# Install docker-compose
sudo apt install -y docker-compose-plugin

# Reboot for group changes to take effect
sudo reboot
```

## Step 3: Clone Repository
```bash
git clone <your-repo-url> ~/pi-guard
cd ~/pi-guard
```

## Step 4: WireGuard Configuration

### Create docker-compose.yml
```yaml
services:
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

  duckdns:
    image: lscr.io/linuxserver/duckdns:latest
    container_name: duckdns
    environment:
      - PUID=1000
      - PGID=1000
      - TZ=Etc/UTC
      - SUBDOMAINS=your-subdomain
      - TOKEN=your-duckdns-token
    restart: unless-stopped
```

### Configuration Required
1. **DuckDNS Setup**:
   - Register at [duckdns.org](https://www.duckdns.org)
   - Create subdomain (e.g., `mypi.duckdns.org`)
   - Update `SERVERURL` and `SUBDOMAINS` in docker-compose.yml
   - Add your DuckDNS token

2. **Router Port Forwarding**:
   - Forward UDP port 51820 to your Raspberry Pi IP (192.168.1.10)

## Step 5: Start VPN Service
```bash
# Start WireGuard
docker compose up -d

# Check status
docker ps
docker logs wireguard

# View generated config
ls -la config/
cat config/peer/iphone/peer.conf
```

## Step 6: Client Setup (iPhone)

### Install WireGuard App
1. Download WireGuard from App Store
2. Scan QR code or import config:
   ```bash
   # Display QR code
   docker exec -it wireguard qrencode -t ansiutf8 < config/peer/iphone/peer.conf
   ```
3. Connect to VPN

### Test Connection
```bash
# From iPhone (when connected to VPN)
ssh pi@192.168.1.10
# Or connect to other LAN devices
ssh user@192.168.1.20  # MacBook Pro
```

## Step 7: Security & Maintenance

### Basic Firewall
```bash
sudo apt install -y ufw
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 51820/udp
sudo ufw enable
```

### Maintenance Commands
```bash
# View logs
docker logs -f wireguard

# Check WireGuard status
docker exec -it wireguard wg

# Restart service
docker compose restart wireguard

# Add new peer
docker exec -it wireguard /config/add-peer.sh
```

## Troubleshooting

### Common Issues

#### VPN Not Connecting
1. Check port forwarding is active
2. Verify DDNS resolves: `nslookup your-subdomain.duckdns.org`
3. Check container logs: `docker logs wireguard`
4. Verify UDP 51820 is not blocked

#### Can't Access LAN Devices
1. Check `PEERDNS` is set to Pi's IP
2. Ensure target devices have SSH enabled
3. Verify local IP addresses are correct

#### Container Won't Start
```bash
# Check kernel modules
lsmod | grep wireguard

# Install missing modules if needed
sudo modprobe wireguard
```

## Network Flow

```
iPhone (Internet) 
    ↓ UDP 51820
Raspberry Pi (WireGuard Server)
    ↓ Routes to LAN
MacBook Pro (192.168.1.20)
```

## Next Steps

After basic VPN is working, you can enhance your setup with:
- **Enhanced Services**: Portainer, Pi-hole, Kali container
- **Advanced Security**: ByteHunter AI security tools
- **Monitoring**: Uptime Kuma, Grafana

See [Enhanced Setup](enhanced-setup.md) for comprehensive HomeLab setup.