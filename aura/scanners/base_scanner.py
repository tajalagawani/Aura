"""
Base Scanner - Abstract base class for all scanners.

Scanners discover computational assets and create AAV files for monitoring.
"""

import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Any

from aura.core.aav import AAVFile

logger = logging.getLogger(__name__)


class BaseScanner(ABC):
    """
    Abstract base class for asset scanners.

    Scanners discover computational assets (containers, VMs, processes)
    and automatically create AAV files for monitoring.
    """

    def __init__(self, assets_dir: str = "./assets"):
        """
        Initialize scanner.

        Args:
            assets_dir: Directory to store discovered AAV files
        """
        self.assets_dir = Path(assets_dir)
        self.assets_dir.mkdir(parents=True, exist_ok=True)
        self.discovered_assets: List[Dict[str, Any]] = []

        logger.info(f"{self.__class__.__name__} initialized")

    @abstractmethod
    async def scan(self) -> List[Dict[str, Any]]:
        """
        Scan for assets.

        Returns:
            List of discovered assets with metadata

        Each asset dict should contain:
            - id: Unique identifier
            - name: Human-readable name
            - type: Asset type (container, vm, pod, etc)
            - metadata: Additional metadata
        """
        pass

    async def discover_and_instrument(self) -> int:
        """
        Discover assets and create AAV files.

        Returns:
            Number of assets discovered and instrumented
        """
        logger.info(f"Starting {self.__class__.__name__} discovery...")

        # Scan for assets
        assets = await self.scan()
        self.discovered_assets = assets

        logger.info(f"Discovered {len(assets)} assets")

        # Create AAV files for each asset
        instrumented = 0
        for asset in assets:
            try:
                self._create_aav_file(asset)
                instrumented += 1
            except Exception as e:
                logger.error(f"Failed to instrument {asset.get('id')}: {e}")

        logger.info(f"Instrumented {instrumented}/{len(assets)} assets")
        return instrumented

    def _create_aav_file(self, asset: Dict[str, Any]) -> None:
        """
        Create AAV file for discovered asset.

        Args:
            asset: Asset metadata
        """
        asset_id = asset.get('id')
        asset_type = asset.get('type', 'unknown')
        asset_name = asset.get('name', asset_id)

        aav_file = self.assets_dir / f"{asset_id}.aav"

        # Skip if already exists
        if aav_file.exists():
            logger.debug(f"AAV file already exists for {asset_id}")
            return

        # Create AAV file
        AAVFile.create_empty(
            file_path=aav_file,
            asset_id=asset_id,
            asset_type=asset_type,
            asset_name=asset_name
        )

        logger.info(f"Created AAV file: {aav_file}")

    def get_discovered_assets(self) -> List[Dict[str, Any]]:
        """
        Get list of discovered assets.

        Returns:
            List of discovered assets
        """
        return self.discovered_assets

    def get_summary(self) -> Dict[str, Any]:
        """
        Get discovery summary.

        Returns:
            Summary statistics
        """
        return {
            "scanner": self.__class__.__name__,
            "total_discovered": len(self.discovered_assets),
            "assets_dir": str(self.assets_dir),
        }
