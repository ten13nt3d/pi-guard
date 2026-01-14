# pi-guard - HomeLab VPN on Raspberry Pi

Project specs for a HomeLab-style VPN on a Raspberry Pi using Dockerized apps. The goal is to let an iPhone connect from outside the home network and reach a MacBook Pro on the home LAN through the Raspberry Pi tunnel.

## Goals

- Remote access from iPhone to MacBook Pro via Raspberry Pi VPN.
- Access works from any external network.
- Dockerized services on the Pi, headless operation.
- Simple to maintain with minimal moving parts.

## Recommended Architecture

- Raspberry Pi runs the VPN server in Docker.
- iPhone connects to the VPN from the internet.
- MacBook Pro stays on the home LAN and is reached by its LAN IP once the VPN is up.
- Router forwards one UDP port to the Pi if using WireGuard directly.

## Choose the System (OS) for the Raspberry Pi

Recommended:
- Raspberry Pi OS Lite (64-bit, Debian-based). Small, stable, and well supported.

Also acceptable:
- Debian Bookworm ARM64 (headless), if you want a stock Debian base.

Notes:
- Use a static DHCP lease for the Pi (e.g., 192.168.1.10).
- Enable SSH on first boot and update packages.

## Git + Repo Clone (Raspberry Pi)

Use this section to confirm Git is installed on the Pi and clone the repo.

1. Check if Git is installed:

```sh
git --version
```

If it is missing, install it:

```sh
sudo apt-get update
sudo apt-get install -y git
```

2. Clone the repo (replace the URL if needed):

```sh
git clone <REPO_URL> ~/pi-guard
cd ~/pi-guard
```

3. Optional: confirm you are in the repo:

```sh
git status -sb
```

## VPN Options Summary

WireGuard (self-hosted):
- Fast, minimal, full control.
- Requires port forwarding and DDNS.

Tailscale (SaaS) or Headscale (self-hosted control plane):
- No port forwarding.
- Easiest setup, but depends on Tailscale control plane unless you run Headscale.

This README focuses on WireGuard as requested.

## Docker Compose (WireGuard)

Create a `docker-compose.yml` in the project root. A template is provided in `docker-compose.yml.template`.

```yaml
version: "3.8"

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
      - SERVERURL=your-ddns-hostname.example.com
      - SERVERPORT=51820
      - PEERS=iphone
      - PEERDNS=auto
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
      - SUBDOMAINS=your-duckdns-subdomain
      - TOKEN=your-duckdns-token
    restart: unless-stopped
```

Notes:
- Replace `SERVERURL` with your DDNS hostname.
- If you use another DDNS provider, swap the service.
- The WireGuard container will create configs in `./config`.

Optional helper:

```sh
make compose-init
make compose-up
```

## Ops (Make Targets)

Common operational commands:

```sh
make compose-up
make compose-down
make restart
make ps
make logs
```

## Network Flow

- iPhone -> WireGuard on Raspberry Pi (UDP 51820).
- WireGuard routes to LAN.
- iPhone -> MacBook Pro (e.g., 192.168.1.20:22).

## Detailed Plan

1. Hardware + OS
   - Flash Raspberry Pi OS Lite (64-bit) to SD card.
   - Enable SSH (create empty `ssh` file in boot partition).
   - Boot the Pi and update packages.

2. Network Setup
   - Reserve a static DHCP lease for the Pi (e.g., 192.168.1.10).
   - Set router port forward: UDP 51820 -> 192.168.1.10.

3. DDNS
   - Create a DuckDNS (or similar) hostname.
   - Add the DDNS container to docker-compose.

4. Docker + Compose
   - Install Docker and docker-compose plugin.
   - Place the `docker-compose.yml` in the project root.
   - Start services: `docker compose up -d`.

5. WireGuard Client (iPhone)
   - Install WireGuard app on iOS.
   - Import the generated config from `./config`.
   - Connect and verify tunnel.

6. MacBook Pro
   - Enable SSH (System Settings -> Remote Login).
   - Confirm LAN IP (e.g., 192.168.1.20).
   - From iPhone, connect: `ssh user@192.168.1.20`.

7. Validate
   - Test from an external network (cellular).
   - Confirm iPhone can reach MacBook via SSH.

## Step-by-step install script (Docker + WireGuard)

Use this script on a fresh Raspberry Pi OS Lite 64-bit install. It installs Docker, enables required kernel modules, and prepares the WireGuard compose stack.

Script: `scripts/install_wireguard_pi.sh`

```sh
sudo bash scripts/install_wireguard_pi.sh
```

## Security Notes

- Use strong SSH keys on the MacBook.
- Keep the Pi updated.
- Avoid exposing other services directly to the internet.

## Hardened Firewall (UFW or nftables)

Pick one. UFW is simpler; nftables is more explicit and production-grade.

### UFW (simple)

1. Install and enable:

```sh
sudo apt-get install -y ufw
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp
sudo ufw allow 51820/udp
sudo ufw enable
```

2. If your VPN clients need LAN access through the Pi, allow forwarding:

```sh
sudo sed -i 's/^DEFAULT_FORWARD_POLICY=.*/DEFAULT_FORWARD_POLICY="ACCEPT"/' /etc/default/ufw
sudo ufw reload
```

### nftables (explicit rules)

1. Install and enable:

```sh
sudo apt-get install -y nftables
sudo systemctl enable nftables
```

2. Create ruleset:

```sh
sudo tee /etc/nftables.conf > /dev/null <<'EOF'
#!/usr/sbin/nft -f

flush ruleset

table inet filter {
  chain input {
    type filter hook input priority 0; policy drop;
    ct state established,related accept
    iif "lo" accept
    tcp dport 22 accept
    udp dport 51820 accept
  }
  chain forward {
    type filter hook forward priority 0; policy drop;
    ct state established,related accept
    iif "wg0" accept
  }
  chain output {
    type filter hook output priority 0; policy accept;
  }
}
EOF
```

3. Apply:

```sh
sudo nft -f /etc/nftables.conf
```

## Optional Add-ons

- Portainer for Docker management.
- Uptime Kuma for basic monitoring.
- Caddy or Traefik if you add web services later.

## Tailscale / Headscale Alternative (Comparison)

Use this path if you want zero router changes or are behind CGNAT.

Tailscale (hosted control plane):
- Easiest: install on Pi, Mac, and iPhone.
- No port forwarding or DDNS.
- SSH to Mac via Tailscale IP (100.x.x.x).

Headscale (self-hosted control plane):
- Same UX as Tailscale but you host the control server.
- More setup work; still no router port forwarding in most cases.
- Good when you want full control and no SaaS dependency.

When to choose:
- Choose WireGuard if you want maximum control and can port forward.
- Choose Tailscale if you want the simplest setup and fast results.
- Choose Headscale if you want Tailscale-style ease but self-hosted.
