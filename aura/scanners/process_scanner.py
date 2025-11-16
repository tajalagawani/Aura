"""
Process Scanner - Discovers running processes.

Automatically finds running processes and creates AAV files.
"""

import logging
import psutil
from typing import Dict, List, Any

from aura.scanners.base_scanner import BaseScanner

logger = logging.getLogger(__name__)


class ProcessScanner(BaseScanner):
    """
    Scanner for running processes.

    Discovers running processes and creates monitoring files.

    Example:
        >>> scanner = ProcessScanner(
        ...     assets_dir="./assets",
        ...     min_cpu_percent=1.0
        ... )
        >>> count = await scanner.discover_and_instrument()
    """

    def __init__(
        self,
        assets_dir: str = "./assets",
        min_cpu_percent: float = 1.0,
        min_memory_mb: float = 100.0,
        exclude_system: bool = True
    ):
        """
        Initialize Process scanner.

        Args:
            assets_dir: Directory for AAV files
            min_cpu_percent: Minimum CPU usage to include process
            min_memory_mb: Minimum memory usage (MB) to include process
            exclude_system: Exclude system processes
        """
        super().__init__(assets_dir)
        self.min_cpu_percent = min_cpu_percent
        self.min_memory_mb = min_memory_mb * 1024 * 1024  # Convert to bytes
        self.exclude_system = exclude_system

    async def scan(self) -> List[Dict[str, Any]]:
        """
        Scan for running processes.

        Returns:
            List of discovered processes
        """
        try:
            processes = []

            for proc in psutil.process_iter(['pid', 'name', 'username', 'cmdline', 'status']):
                try:
                    # Get process info
                    pinfo = proc.info

                    # Skip system processes if configured
                    if self.exclude_system and pinfo.get('username') == 'root':
                        continue

                    # Get CPU and memory usage
                    try:
                        cpu_percent = proc.cpu_percent(interval=0.1)
                        mem_info = proc.memory_info()
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue

                    # Filter by resource usage
                    if cpu_percent < self.min_cpu_percent and mem_info.rss < self.min_memory_mb:
                        continue

                    # Get command line
                    cmdline = pinfo.get('cmdline', [])
                    cmd_str = ' '.join(cmdline) if cmdline else pinfo.get('name', 'unknown')

                    asset = {
                        "id": f"process-{pinfo['pid']}",
                        "name": pinfo.get('name', 'unknown'),
                        "type": "process",
                        "metadata": {
                            "pid": pinfo['pid'],
                            "username": pinfo.get('username', 'unknown'),
                            "status": pinfo.get('status', 'unknown'),
                            "command": cmd_str[:200],  # Limit command length
                            "cpu_percent": round(cpu_percent, 2),
                            "memory_mb": round(mem_info.rss / 1024 / 1024, 2),
                        }
                    }
                    processes.append(asset)

                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
                except Exception as e:
                    logger.debug(f"Error processing process: {e}")
                    continue

            logger.info(f"Found {len(processes)} processes matching criteria")
            return processes

        except Exception as e:
            logger.error(f"Process scan failed: {e}")
            return []

    def get_process_details(self, pid: int) -> Dict[str, Any]:
        """
        Get detailed process information.

        Args:
            pid: Process ID

        Returns:
            Process details
        """
        try:
            proc = psutil.Process(pid)

            return {
                "pid": pid,
                "name": proc.name(),
                "username": proc.username(),
                "status": proc.status(),
                "cpu_percent": proc.cpu_percent(interval=0.1),
                "memory_percent": proc.memory_percent(),
                "num_threads": proc.num_threads(),
                "create_time": proc.create_time(),
                "cmdline": ' '.join(proc.cmdline()),
                "cwd": proc.cwd(),
                "connections": len(proc.connections()),
                "open_files": len(proc.open_files()),
            }

        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            logger.error(f"Failed to get details for process {pid}: {e}")
            return {}
        except Exception as e:
            logger.error(f"Error getting process details: {e}")
            return {}
