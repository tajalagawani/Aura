#!/bin/bash
# COPY AND PASTE THIS ENTIRE SCRIPT INTO YOUR VPS TERMINAL
#
# Usage:
#   1. SSH to your VPS: ssh root@92.112.181.127
#   2. Copy this entire file
#   3. Paste into terminal and press Enter
#   4. Wait ~1 minute
#   5. Open http://92.112.181.127:8080 in browser

set -e

echo "🚀 Deploying Aura to VPS..."
echo ""

# Clone repository
echo "📥 Cloning Aura repository..."
cd /root
rm -rf Aura 2>/dev/null || true
git clone https://github.com/tajalagawani/Aura.git
cd Aura

# Make deploy script executable
chmod +x deploy-vps.sh

# Run deployment
echo ""
echo "🔧 Running automated deployment..."
./deploy-vps.sh

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ DEPLOYMENT COMPLETE!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🌐 Open in your browser:"
echo "   http://92.112.181.127:8080"
echo ""
echo "🔍 Quick checks:"
echo "   sudo systemctl status aura-monitor"
echo "   sudo systemctl status aura-dashboard"
echo "   curl http://localhost:8080"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
