"""
Docker Scanner - Discovers Docker containers.

Automatically finds running Docker containers and creates AAV files.
"""

import logging
from typing import Dict, List, Any

from aura.scanners.base_scanner import BaseScanner

logger = logging.getLogger(__name__)


class DockerScanner(BaseScanner):
    """
    Scanner for Docker containers.

    Discovers running Docker containers and creates monitoring files.

    Example:
        >>> scanner = DockerScanner(assets_dir="./assets")
        >>> count = await scanner.discover_and_instrument()
        >>> print(f"Discovered {count} containers")
    """

    async def scan(self) -> List[Dict[str, Any]]:
        """
        Scan for Docker containers.

        Returns:
            List of discovered containers
        """
        try:
            import docker
            client = docker.from_env()

            containers = []
            for container in client.containers.list():
                asset = {
                    "id": f"container-{container.id[:12]}",
                    "name": container.name,
                    "type": "container",
                    "metadata": {
                        "container_id": container.id,
                        "image": container.image.tags[0] if container.image.tags else "unknown",
                        "status": container.status,
                        "labels": container.labels,
                    }
                }
                containers.append(asset)

            logger.info(f"Found {len(containers)} Docker containers")
            return containers

        except ImportError:
            logger.warning("Docker library not installed. Install with: pip install docker")
            return []
        except Exception as e:
            logger.error(f"Docker scan failed: {e}")
            return []


    def get_container_stats(self, container_id: str) -> Dict[str, Any]:
        """
        Get container statistics.

        Args:
            container_id: Container ID

        Returns:
            Container stats
        """
        try:
            import docker
            client = docker.from_env()
            container = client.containers.get(container_id)
            stats = container.stats(stream=False)

            return {
                "cpu_percent": self._calculate_cpu_percent(stats),
                "memory_usage": stats['memory_stats'].get('usage', 0),
                "memory_limit": stats['memory_stats'].get('limit', 0),
                "network_rx": stats['networks'].get('eth0', {}).get('rx_bytes', 0),
                "network_tx": stats['networks'].get('eth0', {}).get('tx_bytes', 0),
            }

        except Exception as e:
            logger.error(f"Failed to get stats for container {container_id}: {e}")
            return {}

    def _calculate_cpu_percent(self, stats: Dict) -> float:
        """Calculate CPU percentage from Docker stats."""
        try:
            cpu_delta = stats['cpu_stats']['cpu_usage']['total_usage'] - \
                       stats['precpu_stats']['cpu_usage']['total_usage']
            system_delta = stats['cpu_stats']['system_cpu_usage'] - \
                          stats['precpu_stats']['system_cpu_usage']

            if system_delta > 0:
                cpu_count = stats['cpu_stats'].get('online_cpus', 1)
                return (cpu_delta / system_delta) * cpu_count * 100.0

            return 0.0
        except (KeyError, ZeroDivisionError):
            return 0.0
