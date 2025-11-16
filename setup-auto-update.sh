#!/bin/bash
# Setup Auto-Update System for Aura
# Run this script on your VPS to enable automatic updates

set -e

if [ "$EUID" -ne 0 ]; then
    echo "❌ Please run as root: sudo $0"
    exit 1
fi

echo "🔧 Setting up Aura auto-update system..."
echo ""

# Copy auto-update script
echo "📋 Installing auto-update script..."
cp auto-update.sh /opt/aura/auto-update.sh
chmod +x /opt/aura/auto-update.sh
echo "✅ Script installed to /opt/aura/auto-update.sh"
echo ""

# Create systemd service
echo "🔧 Creating systemd service..."
cat > /etc/systemd/system/aura-update.service << 'EOF'
[Unit]
Description=Aura Auto-Update Service
After=network.target

[Service]
Type=oneshot
ExecStart=/opt/aura/auto-update.sh
StandardOutput=journal
StandardError=journal
EOF

echo "✅ Created aura-update.service"
echo ""

# Create systemd timer
echo "⏰ Creating systemd timer..."
cat > /etc/systemd/system/aura-update.timer << 'EOF'
[Unit]
Description=Aura Auto-Update Timer
Requires=aura-update.service

[Timer]
# Check for updates every 5 minutes
OnBootSec=2min
OnUnitActiveSec=5min

[Install]
WantedBy=timers.target
EOF

echo "✅ Created aura-update.timer (checks every 5 minutes)"
echo ""

# Create log directory
mkdir -p /var/log
touch /var/log/aura-update.log
chmod 644 /var/log/aura-update.log

# Enable and start timer
echo "🚀 Enabling auto-update timer..."
systemctl daemon-reload
systemctl enable aura-update.timer
systemctl start aura-update.timer

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Auto-update system installed!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📊 Configuration:"
echo "   Update check interval: Every 5 minutes"
echo "   Auto-restart services: Yes"
echo "   Update log: /var/log/aura-update.log"
echo ""
echo "🔧 Management commands:"
echo "   sudo systemctl status aura-update.timer"
echo "   sudo systemctl status aura-update.service"
echo "   sudo journalctl -u aura-update.service -f"
echo "   tail -f /var/log/aura-update.log"
echo ""
echo "✋ To disable auto-updates:"
echo "   sudo systemctl stop aura-update.timer"
echo "   sudo systemctl disable aura-update.timer"
echo ""
echo "🔄 To manually trigger update now:"
echo "   sudo systemctl start aura-update.service"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
