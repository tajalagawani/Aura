"""
Aura Monitoring Service - Continuously monitors assets in real-time.

Runs sensors indefinitely with real-time updates.
"""

import asyncio
import logging
import signal
import socket
from pathlib import Path

from aura.core.aav import AAVFile
from aura.sensors import ComputeSensor, MemorySensor, StorageSensor, NetworkSensor

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AuraMonitoringService:
    """Continuous monitoring service for assets."""

    def __init__(self, assets_dir: str = "./assets", asset_id: str = None):
        """
        Initialize monitoring service.

        Args:
            assets_dir: Directory for AAV files
            asset_id: Asset ID (defaults to hostname)
        """
        self.assets_dir = Path(assets_dir)
        self.asset_id = asset_id or socket.gethostname()
        self.aav_file = self.assets_dir / f"{self.asset_id}.aav"
        self.running = False
        self.sensors = []

    async def initialize(self):
        """Initialize AAV file and sensors."""
        logger.info(f"Initializing Aura monitoring for: {self.asset_id}")

        # Create assets directory
        self.assets_dir.mkdir(parents=True, exist_ok=True)

        # Create or verify AAV file
        if not self.aav_file.exists():
            logger.info(f"Creating AAV file: {self.aav_file}")
            AAVFile.create_empty(
                file_path=self.aav_file,
                asset_id=self.asset_id,
                asset_type="server",
                asset_name=self.asset_id
            )
        else:
            logger.info(f"Using existing AAV file: {self.aav_file}")

        # Initialize sensors
        logger.info("Initializing sensors...")
        self.sensors = [
            ComputeSensor(self.asset_id, str(self.aav_file)),
            MemorySensor(self.asset_id, str(self.aav_file)),
            StorageSensor(self.asset_id, str(self.aav_file)),
            NetworkSensor(self.asset_id, str(self.aav_file)),
        ]

        logger.info(f"✅ Initialized {len(self.sensors)} sensors")

    async def start(self):
        """Start monitoring service."""
        await self.initialize()

        logger.info("🚀 Starting Aura monitoring service...")
        logger.info(f"   Asset ID: {self.asset_id}")
        logger.info(f"   AAV File: {self.aav_file}")
        logger.info(f"   Sensors: {len(self.sensors)}")
        logger.info("")
        logger.info("Press Ctrl+C to stop")
        logger.info("")

        self.running = True

        # Start all sensors
        tasks = [sensor.start() for sensor in self.sensors]

        try:
            await asyncio.gather(*tasks)
        except asyncio.CancelledError:
            logger.info("Monitoring service cancelled")
        finally:
            await self.stop()

    async def stop(self):
        """Stop monitoring service."""
        if not self.running:
            return

        logger.info("Stopping sensors...")
        self.running = False

        for sensor in self.sensors:
            try:
                await sensor.stop()
            except Exception as e:
                logger.error(f"Error stopping sensor: {e}")

        logger.info("✅ Monitoring service stopped")

    def handle_signal(self, signum, frame):
        """Handle shutdown signals."""
        logger.info(f"Received signal {signum}, shutting down...")
        raise KeyboardInterrupt


def main():
    """Run monitoring service."""
    import sys

    assets_dir = sys.argv[1] if len(sys.argv) > 1 else "./assets"
    asset_id = sys.argv[2] if len(sys.argv) > 2 else None

    service = AuraMonitoringService(assets_dir=assets_dir, asset_id=asset_id)

    # Setup signal handlers
    signal.signal(signal.SIGINT, service.handle_signal)
    signal.signal(signal.SIGTERM, service.handle_signal)

    try:
        asyncio.run(service.start())
    except KeyboardInterrupt:
        logger.info("\n✅ Service stopped by user")
    except Exception as e:
        logger.error(f"❌ Service error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
