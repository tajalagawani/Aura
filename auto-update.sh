#!/bin/bash
# Aura Auto-Update Script
# Checks for updates from GitHub and automatically updates the VPS installation

set -e

INSTALL_DIR="/opt/aura"
REPO_URL="https://github.com/tajalagawani/Aura.git"
LOG_FILE="/var/log/aura-update.log"

# Logging function
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
log "🔍 Checking for Aura updates..."

# Navigate to install directory
cd "$INSTALL_DIR" || exit 1

# Fetch latest changes
git fetch origin master &>/dev/null

# Check if updates are available
LOCAL=$(git rev-parse HEAD)
REMOTE=$(git rev-parse origin/master)

if [ "$LOCAL" = "$REMOTE" ]; then
    log "✅ Already up to date (commit: ${LOCAL:0:7})"
    exit 0
fi

log "📥 New updates available!"
log "   Current: ${LOCAL:0:7}"
log "   Latest:  ${REMOTE:0:7}"

# Pull changes
log "📦 Pulling updates..."
git pull origin master &>/dev/null

# Reinstall package
log "🔧 Reinstalling Aura package..."
python3 -m pip install -e . --break-system-packages --quiet &>/dev/null

# Restart services
log "🔄 Restarting services..."
systemctl restart aura-monitor.service
systemctl restart aura-dashboard.service

# Wait for services to start
sleep 3

# Check service status
if systemctl is-active --quiet aura-monitor.service; then
    log "✅ Monitor service: RUNNING"
else
    log "❌ Monitor service: FAILED"
fi

if systemctl is-active --quiet aura-dashboard.service; then
    log "✅ Dashboard service: RUNNING"
else
    log "❌ Dashboard service: FAILED"
fi

log "✅ Update complete! (now at ${REMOTE:0:7})"
log "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
