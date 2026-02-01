# System Architecture Overview

This document provides a technical overview of the pi-guard HomeLab architecture, component relationships, and design decisions.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Internet                              │
└─────────────────────┬───────────────────────────────────────┘
                      │ UDP 51820 (WireGuard)
                      │ TCP 9443 (Portainer - LAN only)
┌─────────────────────▼───────────────────────────────────────┐
│                    Router/Firewall                           │
│  - Port Forwarding (51820 → Pi)                             │
│  - DHCP (DNS → Pi-hole)                                     │
│  - Network Isolation                                        │
└─────────────────────┬───────────────────────────────────────┘
                      │ 192.168.1.10
┌─────────────────────▼───────────────────────────────────────┐
│                Raspberry Pi 4 (Docker Host)                  │
├─────────────────────────────────────────────────────────────┤
│  Docker Engine                                              │
│  ├─ WireGuard (VPN Server)                                 │
│  ├─ Portainer (Web Management)                            │
│  ├─ Pi-hole (DNS + Ad Blocking)                           │
│  ├─ Kali Linux (Security Tools)                           │
│  └─ Tor Services (Hidden Services)                         │
├─────────────────────────────────────────────────────────────┤
│  Docker Networks                                            │
│  ├─ security_net (Isolated)                               │
│  ├─ tor_net (Isolated, Internal)                          │
│  └─ bridge (Default)                                       │
└─────────────────────┬───────────────────────────────────────┘
                      │ LAN Access
┌─────────────────────▼───────────────────────────────────────┐
│                    Home Network                              │
│  ├─ MacBook Pro (Target for remote access)                 │
│  ├─ Other Devices (Use Pi-hole for DNS)                    │
│  └─ Network Storage/File Servers                            │
└─────────────────────────────────────────────────────────────┘
```

## Component Architecture

### Core Services Layer

#### WireGuard VPN
- **Purpose**: Secure remote access tunnel
- **Protocol**: UDP 51820
- **Network**: 10.13.13.0/24 (VPN subnet)
- **Capabilities**: 
  - Site-to-site tunneling
  - Client authentication via public keys
  - Route LAN access
  - DNS assignment

#### Docker Orchestration
- **Engine**: Docker CE with compose plugin
- **Management**: Portainer web interface
- **Isolation**: Container-level security
- **Networking**: Multi-network architecture

### Service Layer Architecture

#### Portainer (Management Interface)
- **Port**: 9443/TCP (HTTPS)
- **Network**: Isolated security network
- **Access**: LAN only (recommended)
- **Features**: 
  - Container management
  - Volume management
  - Network visualization
  - User access control

#### Pi-hole (DNS & Ad Blocking)
- **Ports**: 53/UDP+TCP, 80/TCP (admin)
- **Role**: Network-wide DNS resolver
- **Features**:
  - Ad/tracker blocking
  - Custom DNS records
  - Query logging
  - DHCP integration
- **Integration**: Router DHCP DNS setting

#### Kali Linux Container
- **Purpose**: Security testing tools suite
- **Network**: Isolated security network
- **Tools Pre-installed**:
  - Nmap (port scanning)
  - Metasploit (exploitation)
  - Wireshark (packet analysis)
  - Nikto (web scanning)
  - SQLmap (SQL injection)
  - Gobuster (directory brute force)
- **Security**: No internet access by default

#### Tor Hidden Services
- **Purpose**: Anonymous web hosting
- **Network**: Isolated Tor network
- **Components**:
  - Tor SOCKS proxy (9050)
  - Hidden web service (nginx)
  - .onion hostname generation
- **Access**: Via Tor Browser only

## Network Architecture

### Docker Networks

```yaml
# security_net (Bridge Network - 172.20.0.0/16)
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Portainer     │    │    Pi-hole      │    │   Kali Linux    │
│     :9443       │    │     :53         │    │  172.20.0.10    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │  security_net   │
                    │ 172.20.0.0/16   │
                    └─────────────────┘

# tor_net (Internal/Isolated - 172.21.0.0/16)
┌─────────────────┐    ┌─────────────────┐
│      Tor        │    │  nginx-hidden   │
│     :9050       │    │   (web server)  │
└─────────────────┘    └─────────────────┘
         │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │    tor_net      │
                    │ 172.21.0.0/16   │
                    │   (internal)    │
                    └─────────────────┘
```

### IP Addressing Scheme

| Component | IP Range | Purpose |
|-----------|----------|---------|
| Router LAN | 192.168.1.0/24 | Home network |
| Raspberry Pi | 192.168.1.10 | Docker host |
| VPN Clients | 10.13.13.0/24 | WireGuard tunnel |
| security_net | 172.20.0.0/16 | Docker services |
| tor_net | 172.21.0.0/16 | Tor services (internal) |

## Data Flow Patterns

### Remote Access Flow
```
iPhone (Internet)
    ↓ [WireGuard Client]
VPN Tunnel (10.13.13.x)
    ↓ [Route via Pi]
Home Network (192.168.1.x)
    ↓ [Direct access]
MacBook Pro (192.168.1.20)
```

### DNS Resolution Flow
```
Client Device
    ↓ [DNS Query]
Router DHCP
    ↓ [Forward to DNS]
Pi-hole (192.168.1.10)
    ↓ [Block/Allow Lists]
Upstream DNS (if needed)
    ↓ [Response]
Client Device
```

### Security Testing Flow
```
Security Analyst
    ↓ [Access container]
Kali Container
    ↓ [Isolated scanning]
Target Networks
    ↓ [Results]
Analysis/Reporting
```

## Security Architecture

### Defense in Depth

#### Network Layer
- **Firewall**: UFW with minimal port exposure
- **Network Isolation**: Docker networks segment services
- **Access Control**: LAN-only for management interfaces

#### Application Layer
- **Container Isolation**: Each service isolated in containers
- **Principle of Least Privilege**: Minimal permissions per container
- **Encryption**: WireGuard for VPN, HTTPS for Portainer

#### Operational Security
- **Access Logging**: Container and system logs
- **Regular Updates**: Automated container updates
- **Monitoring**: Health checks and alerting

### Threat Model

#### External Threats
- **VPN Brute Force**: Mitigated by WireGuard's key-based auth
- **Port Scanning**: Minimal attack surface via firewall
- **DDoS**: Rate limiting at firewall level

#### Internal Threats
- **Container Escape**: Mitigated by Docker isolation
- **Resource Exhaustion**: Resource limits per container
- **Data Exfiltration**: Network segmentation prevents lateral movement

## Performance Considerations

### Resource Allocation
- **CPU**: Time-sharing between containers
- **Memory**: Minimum 2GB, 4GB+ recommended for full stack
- **Storage**: SSD preferred for I/O intensive operations
- **Network**: Gigabit recommended for multiple services

### Bottlenecks
- **SD Card Speed**: Primary storage bottleneck
- **CPU Contention**: During intensive security scans
- **Network Bandwidth**: Multiple concurrent connections
- **Memory Pressure**: Running all services simultaneously

## Scaling Architecture

### Horizontal Scaling
- **Additional Docker Nodes**: Swarm mode for load distribution
- **Service Replication**: Multiple instances of critical services
- **Load Balancing**: HAProxy/Nginx for web services

### Vertical Scaling
- **Hardware Upgrades**: Pi 4 8GB, external SSD
- **Resource Optimization**: Container limits and reservations
- **Service Prioritization**: CPU/memory prioritization

## Integration Points

### External Services
- **DDNS Providers**: DuckDNS for dynamic IP resolution
- **Certificate Authorities**: Let's Encrypt for HTTPS certificates
- **Monitoring**: Optional external monitoring services
- **Backup**: Cloud storage for configuration backups

### API Endpoints
- **Docker API**: Portainer integration
- **WireGuard API**: Configuration management
- **Pi-hole API**: DNS management
- **Tor Control**: Hidden service management

## Configuration Management

### Environment Variables
- **WireGuard**: SERVERURL, PEERDNS, INTERNAL_SUBNET
- **Pi-hole**: WEBPASSWORD, TZ
- **Portainer**: Admin password via web interface
- **Tor**: Service configuration files

### Persistent Data
- **Configuration**: /config, /pihole, /portainer volumes
- **Logs**: Centralized logging via Docker
- **Certificates**: SSL certificates for HTTPS
- **Security Keys**: WireGuard key pairs

## Failure Modes & Recovery

### Service Failures
- **Automatic Restart**: Docker restart policies
- **Health Checks**: Container health monitoring
- **Fallback DNS**: Secondary DNS resolvers
- **VPN Redundancy**: Multiple peer configurations

### Data Recovery
- **Configuration Backups**: Regular config directory backups
- **Container Images**: Local image caching
- **Network Configuration**: Router configuration backup
- **State Recovery**: Service state persistence

## Future Architecture Extensions

### Additional Services
- **SIEM Integration**: ELK stack for log analysis
- **File Storage**: Nextcloud for personal cloud
- **Media Server**: Plex/Jellyfin for media streaming
- **Home Automation**: Home Assistant integration

### Advanced Security
- **IDS/IPS**: Suricata for intrusion detection
- **Honeypots**: Cowrie for threat intelligence
- **Certificate Authority**: Local PKI management
- **Zero Trust**: Service mesh implementation

This architecture provides a secure, scalable foundation for HomeLab services while maintaining operational simplicity and strong security boundaries.