#!/bin/bash
# Pi-Guard Backup Script
# Creates backups of configuration files
#
# Usage:
#   ./scripts/backup.sh              # Create backup
#   ./scripts/backup.sh restore      # List available backups
#   ./scripts/backup.sh restore <backup_file>  # Restore from backup

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Configuration
BACKUP_DIR="./backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="${BACKUP_DIR}/pi-guard_backup_${TIMESTAMP}.tar.gz"

# Directories to backup
BACKUP_ITEMS=(
    "config/wireguard"
    "config/pihole"
    "config/tor"
    "config/nginx"
    "config/portainer"
    "config/ai-tools"
    ".env"
    "docker-compose.enhanced.yml"
    "docker-compose.bytehunter.yml"
)

# Directories to exclude (sensitive runtime data)
EXCLUDE_ITEMS=(
    "config/wireguard/coredns"
    "config/pihole/etc-pihole/pihole-FTL.db"
    "*.log"
    "*.tmp"
    "__pycache__"
)

create_backup() {
    log_info "Creating Pi-Guard backup..."
    echo ""

    # Create backup directory
    mkdir -p "$BACKUP_DIR"

    # Build exclude arguments
    EXCLUDE_ARGS=""
    for item in "${EXCLUDE_ITEMS[@]}"; do
        EXCLUDE_ARGS="$EXCLUDE_ARGS --exclude=$item"
    done

    # Build include list (only existing items)
    INCLUDE_ITEMS=()
    for item in "${BACKUP_ITEMS[@]}"; do
        if [ -e "$item" ]; then
            INCLUDE_ITEMS+=("$item")
        else
            log_warn "Skipping (not found): $item"
        fi
    done

    if [ ${#INCLUDE_ITEMS[@]} -eq 0 ]; then
        log_error "No items to backup!"
        exit 1
    fi

    # Create backup
    log_info "Backing up: ${INCLUDE_ITEMS[*]}"
    tar -czvf "$BACKUP_FILE" $EXCLUDE_ARGS "${INCLUDE_ITEMS[@]}" 2>/dev/null

    # Calculate size
    BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)

    echo ""
    log_info "Backup created successfully!"
    echo ""
    echo "================================================"
    echo "  Backup Details"
    echo "================================================"
    echo "  File: $BACKUP_FILE"
    echo "  Size: $BACKUP_SIZE"
    echo "  Date: $(date)"
    echo "================================================"
    echo ""

    # List recent backups
    echo "Recent backups:"
    ls -lht "$BACKUP_DIR"/*.tar.gz 2>/dev/null | head -5 || echo "  No backups found"
    echo ""

    # Cleanup old backups (keep last 5)
    BACKUP_COUNT=$(ls -1 "$BACKUP_DIR"/*.tar.gz 2>/dev/null | wc -l)
    if [ "$BACKUP_COUNT" -gt 5 ]; then
        log_info "Cleaning up old backups (keeping last 5)..."
        ls -1t "$BACKUP_DIR"/*.tar.gz | tail -n +6 | xargs rm -f
    fi
}

list_backups() {
    echo "================================================"
    echo "       Available Backups"
    echo "================================================"
    echo ""

    if [ -d "$BACKUP_DIR" ] && ls "$BACKUP_DIR"/*.tar.gz &> /dev/null; then
        ls -lht "$BACKUP_DIR"/*.tar.gz
        echo ""
        echo "To restore a backup:"
        echo "  $0 restore <backup_file>"
    else
        log_warn "No backups found in $BACKUP_DIR"
    fi
    echo ""
}

restore_backup() {
    local RESTORE_FILE="$1"

    if [ ! -f "$RESTORE_FILE" ]; then
        log_error "Backup file not found: $RESTORE_FILE"
        exit 1
    fi

    log_warn "This will overwrite current configuration!"
    echo ""
    echo "Backup file: $RESTORE_FILE"
    echo ""
    read -p "Are you sure you want to restore? (yes/N): " CONFIRM

    if [ "$CONFIRM" != "yes" ]; then
        log_info "Restore cancelled"
        exit 0
    fi

    # Stop containers before restore
    log_info "Stopping containers..."
    docker compose down 2>/dev/null || true

    # Create a safety backup of current config
    SAFETY_BACKUP="${BACKUP_DIR}/pre_restore_${TIMESTAMP}.tar.gz"
    log_info "Creating safety backup: $SAFETY_BACKUP"
    tar -czf "$SAFETY_BACKUP" config/ .env 2>/dev/null || true

    # Restore
    log_info "Restoring from backup..."
    tar -xzvf "$RESTORE_FILE"

    echo ""
    log_info "Restore completed!"
    echo ""
    echo "Next steps:"
    echo "  1. Review the restored configuration"
    echo "  2. Start containers: docker compose up -d"
    echo "  3. Verify services: ./scripts/health_check.sh"
    echo ""
    log_info "Safety backup created: $SAFETY_BACKUP"
}

show_usage() {
    echo "Pi-Guard Backup Script"
    echo ""
    echo "Usage:"
    echo "  $0              Create a new backup"
    echo "  $0 restore      List available backups"
    echo "  $0 restore <file>  Restore from a backup file"
    echo ""
    echo "Examples:"
    echo "  $0"
    echo "  $0 restore"
    echo "  $0 restore backups/pi-guard_backup_20240101_120000.tar.gz"
}

# Main
case "${1:-backup}" in
    backup)
        create_backup
        ;;
    restore)
        if [ -n "${2:-}" ]; then
            restore_backup "$2"
        else
            list_backups
        fi
        ;;
    -h|--help|help)
        show_usage
        ;;
    *)
        log_error "Unknown command: $1"
        show_usage
        exit 1
        ;;
esac
