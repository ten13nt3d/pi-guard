#!/usr/bin/env bash
set -euo pipefail

# Basic packages and updates
sudo apt-get update
sudo apt-get install -y \
  ca-certificates \
  curl \
  gnupg \
  lsb-release \
  iproute2

# Install Docker (official repo)
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/debian/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
  https://download.docker.com/linux/debian $(. /etc/os-release && echo "$VERSION_CODENAME") stable" \
  | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Allow non-root docker usage
if ! getent group docker >/dev/null; then
  sudo groupadd docker
fi
sudo usermod -aG docker "$USER"

# Enable IP forwarding
if ! grep -q "^net.ipv4.ip_forward=1" /etc/sysctl.conf; then
  echo "net.ipv4.ip_forward=1" | sudo tee -a /etc/sysctl.conf > /dev/null
fi
sudo sysctl -p

# Load WireGuard kernel module at boot
if ! grep -q "^wireguard$" /etc/modules; then
  echo "wireguard" | sudo tee -a /etc/modules > /dev/null
fi
sudo modprobe wireguard || true

echo "Checking port 53 usage (for AdGuard Home)..."
sudo ss -lunpt | grep ':53 ' || true
sudo ss -ltnp | grep ':53 ' || true

echo "Done. Reboot recommended, then run: docker compose up -d"
