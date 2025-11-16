#!/bin/bash
# Aura VPS Deployment Script
# Fully automated deployment with monitoring service and web dashboard

set -e

echo "🚀 Aura VPS Deployment"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Configuration
INSTALL_DIR="/opt/aura"
ASSETS_DIR="/var/lib/aura/assets"
SERVICE_USER="aura"
WEB_PORT=8080

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

step() {
    echo -e "${BLUE}▶${NC} $1"
}

success() {
    echo -e "${GREEN}✅${NC} $1"
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Please run as root: sudo $0"
    exit 1
fi

step "Checking Python version..."
if ! python3 --version | grep -E "Python 3\.(11|12|13)" > /dev/null 2>&1; then
    echo "❌ Python 3.11+ required"
    echo "Installing Python 3.11..."
    apt-get update
    apt-get install -y python3.11 python3.11-venv python3-pip
fi
success "Python $(python3 --version | cut -d' ' -f2) detected"
echo ""

step "Creating aura user..."
if ! id "$SERVICE_USER" &>/dev/null; then
    useradd -r -m -s /bin/bash $SERVICE_USER
    success "Created user: $SERVICE_USER"
else
    success "User already exists: $SERVICE_USER"
fi
echo ""

step "Creating directories..."
mkdir -p $INSTALL_DIR
mkdir -p $ASSETS_DIR
chown -R $SERVICE_USER:$SERVICE_USER $INSTALL_DIR
chown -R $SERVICE_USER:$SERVICE_USER $ASSETS_DIR
success "Created directories"
echo ""

step "Copying Aura files..."
cp -r . $INSTALL_DIR/
chown -R $SERVICE_USER:$SERVICE_USER $INSTALL_DIR
success "Files copied to $INSTALL_DIR"
echo ""

step "Installing Aura package..."
cd $INSTALL_DIR
sudo -u $SERVICE_USER python3 -m pip install --user -e . --quiet
success "Package installed"
echo ""

step "Creating systemd service for monitoring..."
cat > /etc/systemd/system/aura-monitor.service << EOF
[Unit]
Description=Aura Monitoring Service
After=network.target

[Service]
Type=simple
User=$SERVICE_USER
WorkingDirectory=$INSTALL_DIR
Environment="PATH=/home/$SERVICE_USER/.local/bin:/usr/bin:/bin"
ExecStart=/usr/bin/python3 -m aura.service.monitor $ASSETS_DIR
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF
success "Created aura-monitor.service"
echo ""

step "Creating systemd service for web dashboard..."
cat > /etc/systemd/system/aura-dashboard.service << EOF
[Unit]
Description=Aura Web Dashboard
After=network.target aura-monitor.service

[Service]
Type=simple
User=$SERVICE_USER
WorkingDirectory=$INSTALL_DIR
Environment="PATH=/home/$SERVICE_USER/.local/bin:/usr/bin:/bin"
ExecStart=/usr/bin/python3 -m aura.web.dashboard $ASSETS_DIR $WEB_PORT
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF
success "Created aura-dashboard.service"
echo ""

step "Enabling and starting services..."
systemctl daemon-reload
systemctl enable aura-monitor.service
systemctl enable aura-dashboard.service
systemctl start aura-monitor.service
systemctl start aura-dashboard.service
success "Services started"
echo ""

step "Waiting for initial metrics (10 seconds)..."
sleep 10
success "Initial metrics collected"
echo ""

step "Checking service status..."
if systemctl is-active --quiet aura-monitor.service; then
    success "✅ Monitoring service: RUNNING"
else
    echo "❌ Monitoring service: FAILED"
    systemctl status aura-monitor.service --no-pager
fi

if systemctl is-active --quiet aura-dashboard.service; then
    success "✅ Dashboard service: RUNNING"
else
    echo "❌ Dashboard service: FAILED"
    systemctl status aura-dashboard.service --no-pager
fi
echo ""

# Get server IP
SERVER_IP=$(hostname -I | awk '{print $1}')

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Aura VPS Deployment Complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📊 Web Dashboard:"
echo "   http://$SERVER_IP:$WEB_PORT"
echo ""
echo "📁 Assets Directory:"
echo "   $ASSETS_DIR"
echo ""
echo "🔧 Service Management:"
echo "   sudo systemctl status aura-monitor"
echo "   sudo systemctl status aura-dashboard"
echo "   sudo systemctl restart aura-monitor"
echo "   sudo systemctl restart aura-dashboard"
echo "   sudo journalctl -u aura-monitor -f"
echo "   sudo journalctl -u aura-dashboard -f"
echo ""
echo "📝 View AAV Files:"
echo "   cat $ASSETS_DIR/*.aav"
echo ""
echo "🌐 Access Dashboard:"
echo "   Open in browser: http://$SERVER_IP:$WEB_PORT"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
