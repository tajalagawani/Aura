#!/bin/bash
# Aura Installation Script
# Usage: ./install.sh

set -e

echo "🚀 Installing Aura - Universal AI Asset Authority"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check Python version
echo "📋 Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
REQUIRED_VERSION="3.11"

if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 11) else 1)" 2>/dev/null; then
    echo "❌ Error: Python 3.11+ required. Current version: $PYTHON_VERSION"
    echo "   Please install Python 3.11 or higher."
    exit 1
fi

echo "✅ Python $PYTHON_VERSION detected"
echo ""

# Install package
echo "📦 Installing Aura package..."
pip install -e . --quiet

if [ $? -eq 0 ]; then
    echo "✅ Aura package installed successfully"
else
    echo "❌ Failed to install Aura package"
    exit 1
fi
echo ""

# Create assets directory
echo "📁 Creating assets directory..."
mkdir -p ./assets
echo "✅ Created ./assets directory"
echo ""

# Create initial AAV file for this machine
echo "🔧 Initializing monitoring for this machine..."
python3 -c "
from aura.core.aav import AAVFile
import socket

# Get hostname
hostname = socket.gethostname()

# Create AAV file
AAVFile.create_empty(
    file_path='./assets/$(hostname).aav',
    asset_id='$(hostname)',
    asset_type='machine',
    asset_name='$(hostname)'
)
print('✅ Created AAV file: ./assets/$(hostname).aav')
"
echo ""

# Start sensors for 5 seconds to populate initial data
echo "📊 Collecting initial metrics (5 seconds)..."
python3 -c "
import asyncio
import socket
from aura.sensors import ComputeSensor, MemorySensor, StorageSensor

async def collect_initial_data():
    hostname = socket.gethostname()
    aav_path = f'./assets/{hostname}.aav'

    sensors = [
        ComputeSensor(hostname, aav_path),
        MemorySensor(hostname, aav_path),
        StorageSensor(hostname, aav_path),
    ]

    tasks = [sensor.start() for sensor in sensors]

    try:
        await asyncio.wait_for(asyncio.gather(*tasks), timeout=5.0)
    except asyncio.TimeoutError:
        for sensor in sensors:
            await sensor.stop()

asyncio.run(collect_initial_data())
print('✅ Initial metrics collected')
"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Aura installation complete!"
echo ""
echo "📊 Try these commands:"
echo ""
echo "   # View status"
echo "   aura status $(hostname) --assets-dir ./assets"
echo ""
echo "   # View summary"
echo "   aura status --summary --assets-dir ./assets"
echo ""
echo "   # Query assets"
echo "   aura query --filter \"memory > 70\" --assets-dir ./assets"
echo ""
echo "   # Watch live updates"
echo "   aura watch $(hostname) --assets-dir ./assets"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
