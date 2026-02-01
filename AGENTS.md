# Project Guidelines & Conventions

## Project Overview

**pi-guard** is a comprehensive HomeLab project that provides secure remote access through a Raspberry Pi VPN tunnel with optional advanced security services. The project has evolved from a simple VPN setup to include Docker management, security testing, and privacy services.

## Project Scope

### Core Services
- **WireGuard VPN** - Secure remote access tunnel
- **Docker Orchestration** - Container-based service management
- **Portainer** - Web-based Docker management interface

### Extended Services
- **Pi-hole** - Network-wide ad blocking and DNS control
- **Kali Linux Container** - Security testing tools suite
- **Tor Hidden Services** - Anonymous web service hosting
- **ByteHunter AI** - Advanced security testing with AI agents

## Documentation Structure

```
pi-guard/
├── README.md                    # Project overview and quick start
├── AGENTS.md                    # This file - project conventions
└── docs/
    ├── setup/
    │   ├── basic-setup.md       # Core VPN installation
    │   └── enhanced-setup.md    # Full stack with all services
    ├── security/
    │   └── bytehunter.md        # AI security tools documentation
    └── architecture/
        └── system-overview.md   # Technical architecture
```

## Development Conventions

### Documentation Standards
- **Concise ASCII-only** documentation unless visual elements are essential
- **Clear separation** between basic and enhanced features
- **Progressive disclosure** - start simple, build complexity gradually
- **Working examples** - all code snippets tested and functional

### Code Organization
- **Docker-first approach** - all services containerized
- **Separate networks** for different security zones
- **Environment-based configuration** - avoid hardcoded values
- **Composable services** - each service should work independently

### Security Principles
- **Principle of least privilege** - minimal permissions per service
- **Network isolation** - Docker networks for service segmentation
- **Defense in depth** - multiple security layers
- **Privacy by design** - local processing, minimal data exposure

## Common Commands

### Service Management
```bash
# Start core VPN services
docker-compose up -d

# Start enhanced services
docker-compose -f docker-compose.enhanced.yml up -d

# Start AI security tools
docker-compose -f docker-compose.bytehunter.yml up -d

# View logs
docker-compose logs -f [service-name]

# Restart specific service
docker-compose restart [service-name]
```

### System Maintenance
```bash
# Update all containers
docker-compose pull && docker-compose up -d

# Clean up unused resources
docker system prune -a

# Backup configurations
./scripts/backup-config.sh

# Monitor system resources
docker stats
```

### Security Tools Access
```bash
# Access Kali container
docker exec -it kali bash

# Access ByteHunter AI
docker exec -it kali bytehunter

# Check WireGuard status
docker exec -it wireguard wg

# Portainer web interface
https://your-pi-ip:9443
```

## Configuration Management

### Environment Variables
- `SERVERURL`: Dynamic DNS hostname for VPN
- `PEERDNS`: Pi's IP address for DNS resolution
- `WEBPASSWORD`: Pi-hole admin password
- `OPENAI_API_KEY`: Optional AI enhancement for security tools

### Required Files
- `docker-compose.yml`: Core services configuration
- `docker-compose.enhanced.yml`: Extended services
- `config/`: WireGuard and Tor configurations
- `scripts/`: Installation and maintenance scripts

### Network Configuration
- Static IP or DHCP reservation for Raspberry Pi
- Router port forwarding: UDP 51820 for WireGuard
- Router DNS settings pointing to Pi-hole (192.168.1.10)

## Installation Scripts

### Basic Setup
```bash
# WireGuard VPN only
./scripts/install_wireguard_pi.sh
```

### Enhanced Setup
```bash
# Full service stack
./scripts/install_enhanced_pi.sh
```

### AI Security Tools
```bash
# ByteHunter security suite
./scripts/install_bytehunter.sh
```

## Testing & Validation

### Basic VPN Testing
```bash
# Test WireGuard connection
docker exec -it wireguard wg

# Test DNS resolution
nslookup google.com

# Test LAN access from VPN client
ping 192.168.1.10
```

### Service Health Checks
```bash
# Check all containers
docker ps

# Check service connectivity
curl -k https://localhost:9443  # Portainer
curl http://localhost/admin      # Pi-hole
```

### Security Testing
```bash
# Port scan from Kali container
docker exec -it kali nmap -sS localhost

# Test DNS blocking
dig doubleclick.net  # Should resolve to 0.0.0.0
```

## Troubleshooting Guidelines

### Common Issues
1. **VPN not connecting**: Check port forwarding and DDNS
2. **Pi-hole not blocking ads**: Verify router DNS settings
3. **Container won't start**: Check resource availability
4. **Kali no internet**: Intentional for security, enable if needed

### Debug Commands
```bash
# System resources
free -h
df -h
docker system df

# Network diagnostics
netstat -tlnp
docker network ls
docker exec -it [container] ip route

# Service logs
docker logs -f [service-name]
journalctl -u docker.service
```

## Contribution Guidelines

### Adding New Services
1. Create isolated Docker network
2. Follow existing service configuration patterns
3. Update documentation in appropriate `docs/` subdirectory
4. Test basic functionality before integration
5. Add installation script if complex setup required

### Documentation Updates
- Keep README.md focused on overview and quick start
- Put detailed setup instructions in `docs/setup/`
- Add architecture changes to `docs/architecture/`
- Update this file for new conventions

### Security Considerations
- Never expose management interfaces to internet
- Use environment variables for sensitive data
- Implement proper access controls
- Document security implications of new services

## Version Control

### Branch Structure
- `main`: Stable production configurations
- `develop`: Development and testing
- `feature/*`: New services or major changes

### Commit Messages
- Use conventional commit format
- Reference relevant documentation files
- Include security considerations for service changes

### Release Process
1. Update documentation
2. Test all service configurations
3. Update version numbers in docker-compose files
4. Tag release with semantic version
5. Update CHANGELOG with breaking changes

## Performance Guidelines

### Resource Management
- Monitor Docker resource usage with `docker stats`
- Set appropriate memory limits for containers
- Use SSD for better I/O performance
- Consider Pi 4 8GB for full stack deployment

### Optimization Tips
- Use .dockerignore to reduce image sizes
- Implement health checks for critical services
- Use restart policies for service reliability
- Regular system updates and container image updates

This project follows HomeLab best practices while maintaining simplicity and security. Contributions should align with these conventions to ensure consistency and reliability.
