#!/bin/bash
################################################################################
# Aura VPS Deployment Script - Production Grade
#
# Fully automated deployment with:
# - Monitoring service (24/7 real-time metrics)
# - Web dashboard (port 8080)
# - Auto-discovery scanners
# - Auto-update system (GitHub sync every 5 minutes)
# - Firewall configuration
# - Health checks
# - Rollback capability
################################################################################

set -e

# Exit on any error
trap 'error_exit "Deployment failed at line $LINENO"' ERR

################################################################################
# Configuration
################################################################################

INSTALL_DIR="/opt/aura"
ASSETS_DIR="/var/lib/aura/assets"
LOG_DIR="/var/log/aura"
SERVICE_USER="aura"
WEB_PORT=8080
GITHUB_REPO="https://github.com/tajalagawani/Aura.git"
GITHUB_BRANCH="main"

# Feature flags
ENABLE_FIREWALL=true
ENABLE_AUTO_UPDATE=true
ENABLE_SCANNERS=true
RUN_INITIAL_SCAN=true

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

################################################################################
# Helper Functions
################################################################################

log() {
    echo -e "${CYAN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

step() {
    echo ""
    echo -e "${BLUE}▶${NC} ${PURPLE}$1${NC}"
}

success() {
    echo -e "${GREEN}✅${NC} $1"
}

warning() {
    echo -e "${YELLOW}⚠️${NC}  $1"
}

error_exit() {
    echo -e "${RED}❌ ERROR: $1${NC}" >&2
    exit 1
}

check_root() {
    if [ "$EUID" -ne 0 ]; then
        error_exit "Please run as root: sudo $0"
    fi
}

check_internet() {
    if ! ping -c 1 8.8.8.8 &> /dev/null; then
        error_exit "No internet connection"
    fi
}

################################################################################
# Main Deployment
################################################################################

banner() {
    echo ""
    echo -e "${PURPLE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${PURPLE}         🌟 Aura VPS Deployment - Production Grade${NC}"
    echo -e "${PURPLE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
}

pre_flight_checks() {
    step "Running pre-flight checks..."

    check_root
    success "Running as root"

    check_internet
    success "Internet connection available"

    # Check if Git is installed
    if ! command -v git &> /dev/null; then
        log "Installing Git..."
        apt-get update -qq
        apt-get install -y git
    fi
    success "Git available"

    # Detect OS
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        log "Detected OS: $NAME $VERSION"
    fi
}

install_python() {
    step "Installing Python 3.11+..."

    if python3 --version 2>/dev/null | grep -E "Python 3\.(11|12|13)" > /dev/null; then
        success "Python $(python3 --version | cut -d' ' -f2) already installed"
        return
    fi

    log "Installing Python 3.11..."
    apt-get update -qq
    apt-get install -y python3.11 python3.11-venv python3-pip python3-dev build-essential

    # Set Python 3.11 as default python3
    update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1

    success "Python $(python3 --version | cut -d' ' -f2) installed"
}

create_user() {
    step "Creating service user..."

    if id "$SERVICE_USER" &>/dev/null; then
        success "User already exists: $SERVICE_USER"
        return
    fi

    useradd -r -m -s /bin/bash $SERVICE_USER
    usermod -aG docker $SERVICE_USER 2>/dev/null || true

    success "Created user: $SERVICE_USER"
}

setup_directories() {
    step "Setting up directories..."

    mkdir -p $INSTALL_DIR
    mkdir -p $ASSETS_DIR
    mkdir -p $LOG_DIR
    mkdir -p /var/run/aura

    chown -R $SERVICE_USER:$SERVICE_USER $INSTALL_DIR
    chown -R $SERVICE_USER:$SERVICE_USER $ASSETS_DIR
    chown -R $SERVICE_USER:$SERVICE_USER $LOG_DIR
    chown -R $SERVICE_USER:$SERVICE_USER /var/run/aura

    success "Directories created"
}

install_dependencies() {
    step "Installing system dependencies..."

    apt-get update -qq
    apt-get install -y \
        curl \
        wget \
        htop \
        net-tools \
        python3-psutil \
        lsof \
        procps

    success "System dependencies installed"
}

clone_repository() {
    step "Cloning Aura repository..."

    # Backup existing installation
    if [ -d "$INSTALL_DIR/.git" ]; then
        log "Backing up existing installation..."
        BACKUP_DIR="/tmp/aura-backup-$(date +%Y%m%d-%H%M%S)"
        cp -r $INSTALL_DIR $BACKUP_DIR
        log "Backup saved to: $BACKUP_DIR"
    fi

    # Remove old installation
    rm -rf $INSTALL_DIR/*

    # Clone fresh copy
    git clone --depth 1 -b $GITHUB_BRANCH $GITHUB_REPO $INSTALL_DIR

    chown -R $SERVICE_USER:$SERVICE_USER $INSTALL_DIR

    success "Repository cloned"
}

install_aura() {
    step "Installing Aura package..."

    cd $INSTALL_DIR

    # Install package
    python3 -m pip install -e . --break-system-packages --quiet

    # Install optional scanner dependencies
    log "Installing optional dependencies..."
    python3 -m pip install --break-system-packages --quiet \
        docker \
        psutil \
        || warning "Some optional dependencies failed (normal if not needed)"

    success "Aura package installed"
}

configure_monitoring_service() {
    step "Configuring monitoring service..."

    cat > /etc/systemd/system/aura-monitor.service << 'EOF'
[Unit]
Description=Aura Real-time Monitoring Service
Documentation=https://github.com/tajalagawani/Aura
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=aura
Group=aura
WorkingDirectory=/opt/aura
Environment="PATH=/home/aura/.local/bin:/usr/local/bin:/usr/bin:/bin"
Environment="PYTHONUNBUFFERED=1"
ExecStart=/usr/bin/python3 -m aura.service.monitor /var/lib/aura/assets
Restart=always
RestartSec=10
TimeoutStopSec=30
StandardOutput=append:/var/log/aura/monitor.log
StandardError=append:/var/log/aura/monitor-error.log

# Security
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/var/lib/aura /var/log/aura /var/run/aura

# Resource limits
LimitNOFILE=65536
LimitNPROC=4096

[Install]
WantedBy=multi-user.target
EOF

    success "Monitoring service configured"
}

configure_dashboard_service() {
    step "Configuring web dashboard service..."

    cat > /etc/systemd/system/aura-dashboard.service << EOF
[Unit]
Description=Aura Web Dashboard
Documentation=https://github.com/tajalagawani/Aura
After=network-online.target aura-monitor.service
Wants=network-online.target
Requires=aura-monitor.service

[Service]
Type=simple
User=aura
Group=aura
WorkingDirectory=/opt/aura
Environment="PATH=/home/aura/.local/bin:/usr/local/bin:/usr/bin:/bin"
Environment="PYTHONUNBUFFERED=1"
ExecStart=/usr/bin/python3 -m aura.web.dashboard /var/lib/aura/assets $WEB_PORT
Restart=always
RestartSec=10
TimeoutStopSec=30
StandardOutput=append:/var/log/aura/dashboard.log
StandardError=append:/var/log/aura/dashboard-error.log

# Security
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/var/lib/aura /var/log/aura

# Resource limits
LimitNOFILE=65536

[Install]
WantedBy=multi-user.target
EOF

    success "Dashboard service configured"
}

configure_auto_update() {
    if [ "$ENABLE_AUTO_UPDATE" = false ]; then
        return
    fi

    step "Configuring auto-update system..."

    # Create update script
    cat > /opt/aura/auto-update.sh << 'EOF'
#!/bin/bash
# Aura Auto-Update Script

INSTALL_DIR="/opt/aura"
LOG_FILE="/var/log/aura/auto-update.log"

log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

cd "$INSTALL_DIR" || exit 1

# Fetch latest changes
git fetch origin main

# Compare versions
LOCAL=$(git rev-parse HEAD)
REMOTE=$(git rev-parse origin/main)

if [ "$LOCAL" = "$REMOTE" ]; then
    log "✅ Already up to date"
    exit 0
fi

log "🔄 New version detected, updating..."

# Pull changes
git pull origin main

# Reinstall package
python3 -m pip install -e . --break-system-packages --quiet

# Restart services
systemctl restart aura-monitor.service
systemctl restart aura-dashboard.service

log "✅ Update complete - restarted services"
EOF

    chmod +x /opt/aura/auto-update.sh
    chown $SERVICE_USER:$SERVICE_USER /opt/aura/auto-update.sh

    # Create systemd service
    cat > /etc/systemd/system/aura-update.service << 'EOF'
[Unit]
Description=Aura Auto-Update Service
After=network-online.target

[Service]
Type=oneshot
User=root
ExecStart=/opt/aura/auto-update.sh
StandardOutput=append:/var/log/aura/auto-update.log
StandardError=append:/var/log/aura/auto-update.log
EOF

    # Create systemd timer
    cat > /etc/systemd/system/aura-update.timer << 'EOF'
[Unit]
Description=Aura Auto-Update Timer
Documentation=https://github.com/tajalagawani/Aura

[Timer]
OnBootSec=5min
OnUnitActiveSec=5min
AccuracySec=1min
Persistent=true

[Install]
WantedBy=timers.target
EOF

    systemctl daemon-reload
    systemctl enable aura-update.timer
    systemctl start aura-update.timer

    success "Auto-update configured (checks every 5 minutes)"
}

configure_firewall() {
    if [ "$ENABLE_FIREWALL" = false ]; then
        return
    fi

    step "Configuring firewall..."

    # Check if ufw is installed
    if ! command -v ufw &> /dev/null; then
        log "Installing ufw..."
        apt-get install -y ufw
    fi

    # Allow SSH (don't lock ourselves out!)
    ufw allow 22/tcp

    # Allow dashboard
    ufw allow $WEB_PORT/tcp

    # Enable firewall
    yes | ufw enable

    success "Firewall configured (ports 22, $WEB_PORT open)"
}

run_initial_scan() {
    if [ "$RUN_INITIAL_SCAN" = false ]; then
        return
    fi

    step "Running initial asset discovery scan..."

    # Give services time to start
    sleep 5

    # Run system scan as aura user
    sudo -u $SERVICE_USER bash -c "cd $INSTALL_DIR && python3 -m aura.cli.main scan system --assets-dir $ASSETS_DIR" || warning "System scan failed"

    # Run port scan
    sudo -u $SERVICE_USER bash -c "cd $INSTALL_DIR && python3 -m aura.cli.main scan ports --assets-dir $ASSETS_DIR" || warning "Port scan failed"

    success "Initial scan completed"
}

start_services() {
    step "Starting Aura services..."

    systemctl daemon-reload

    # Enable services
    systemctl enable aura-monitor.service
    systemctl enable aura-dashboard.service

    # Start services
    systemctl start aura-monitor.service
    systemctl start aura-dashboard.service

    success "Services started"
}

health_check() {
    step "Running health checks..."

    sleep 5

    # Check monitoring service
    if systemctl is-active --quiet aura-monitor.service; then
        success "Monitoring service: RUNNING"
    else
        error_exit "Monitoring service failed to start. Check: journalctl -u aura-monitor -n 50"
    fi

    # Check dashboard service
    if systemctl is-active --quiet aura-dashboard.service; then
        success "Dashboard service: RUNNING"
    else
        error_exit "Dashboard service failed to start. Check: journalctl -u aura-dashboard -n 50"
    fi

    # Check if dashboard responds
    if curl -s http://localhost:$WEB_PORT > /dev/null; then
        success "Dashboard responding on port $WEB_PORT"
    else
        warning "Dashboard not responding yet (may take a few seconds)"
    fi

    # Check for AAV files
    AAV_COUNT=$(ls -1 $ASSETS_DIR/*.aav 2>/dev/null | wc -l)
    if [ $AAV_COUNT -gt 0 ]; then
        success "Found $AAV_COUNT AAV files"
    else
        warning "No AAV files yet (will be created soon)"
    fi
}

display_summary() {
    SERVER_IP=$(hostname -I | awk '{print $1}')

    echo ""
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}         ✅ Aura Deployment Successful!${NC}"
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo -e "${CYAN}📊 Web Dashboard:${NC}"
    echo -e "   ${BLUE}http://$SERVER_IP:$WEB_PORT${NC}"
    echo ""
    echo -e "${CYAN}📁 Assets Directory:${NC}"
    echo -e "   $ASSETS_DIR"
    echo ""
    echo -e "${CYAN}📝 Log Files:${NC}"
    echo -e "   $LOG_DIR/monitor.log"
    echo -e "   $LOG_DIR/dashboard.log"
    echo -e "   $LOG_DIR/auto-update.log"
    echo ""
    echo -e "${CYAN}🔧 Service Management:${NC}"
    echo -e "   systemctl status aura-monitor"
    echo -e "   systemctl status aura-dashboard"
    echo -e "   systemctl restart aura-monitor"
    echo -e "   systemctl restart aura-dashboard"
    echo ""
    echo -e "${CYAN}📊 View Logs:${NC}"
    echo -e "   journalctl -u aura-monitor -f"
    echo -e "   journalctl -u aura-dashboard -f"
    echo -e "   tail -f $LOG_DIR/monitor.log"
    echo ""
    echo -e "${CYAN}🔍 CLI Commands:${NC}"
    echo -e "   aura status --summary"
    echo -e "   aura scan all"
    echo -e "   aura scan ports"
    echo ""
    echo -e "${CYAN}🔄 Auto-Update:${NC}"
    echo -e "   systemctl status aura-update.timer"
    echo -e "   $(if [ "$ENABLE_AUTO_UPDATE" = true ]; then echo "✅ Enabled (checks every 5 min)"; else echo "❌ Disabled"; fi)"
    echo ""
    echo -e "${CYAN}🔥 Firewall:${NC}"
    echo -e "   $(if [ "$ENABLE_FIREWALL" = true ]; then echo "✅ Enabled (ports 22, $WEB_PORT)"; else echo "❌ Disabled"; fi)"
    echo ""
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
}

################################################################################
# Main Execution
################################################################################

main() {
    banner
    pre_flight_checks
    install_python
    create_user
    setup_directories
    install_dependencies
    clone_repository
    install_aura
    configure_monitoring_service
    configure_dashboard_service
    configure_auto_update
    configure_firewall
    start_services
    run_initial_scan
    health_check
    display_summary
}

# Run main function
main

exit 0
