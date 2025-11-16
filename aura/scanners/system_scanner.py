"""
System Scanner - Discovers the system itself as an asset.

Creates AAV file for the host system including hardware and OS details.
"""

import logging
import platform
import socket
import psutil
from typing import Dict, List, Any
from datetime import datetime

from aura.scanners.base_scanner import BaseScanner

logger = logging.getLogger(__name__)


class SystemScanner(BaseScanner):
    """
    Scanner for the host system.

    Discovers system information and creates monitoring file for the host.

    Example:
        >>> scanner = SystemScanner(assets_dir="./assets")
        >>> count = await scanner.discover_and_instrument()
    """

    async def scan(self) -> List[Dict[str, Any]]:
        """
        Scan system information.

        Returns:
            List containing single system asset
        """
        try:
            # Get hostname
            hostname = socket.gethostname()
            fqdn = socket.getfqdn()

            # Get system info
            uname = platform.uname()

            # Get CPU info
            cpu_count = psutil.cpu_count(logical=False)
            cpu_count_logical = psutil.cpu_count(logical=True)
            try:
                cpu_freq = psutil.cpu_freq()
                cpu_freq_max = cpu_freq.max if cpu_freq else 0
            except Exception:
                cpu_freq_max = 0

            # Get memory info
            mem = psutil.virtual_memory()
            mem_total_gb = round(mem.total / 1024 / 1024 / 1024, 2)

            # Get disk info
            disk = psutil.disk_usage('/')
            disk_total_gb = round(disk.total / 1024 / 1024 / 1024, 2)

            # Get network interfaces
            net_interfaces = []
            try:
                for interface, addrs in psutil.net_if_addrs().items():
                    for addr in addrs:
                        if addr.family == socket.AF_INET:
                            net_interfaces.append({
                                "interface": interface,
                                "ip": addr.address,
                            })
            except Exception as e:
                logger.debug(f"Error getting network interfaces: {e}")

            # Get boot time
            try:
                boot_time = datetime.fromtimestamp(psutil.boot_time())
                uptime_seconds = (datetime.now() - boot_time).total_seconds()
            except Exception:
                uptime_seconds = 0

            asset = {
                "id": f"system-{hostname}",
                "name": hostname,
                "type": "system",
                "metadata": {
                    "hostname": hostname,
                    "fqdn": fqdn,
                    "platform": uname.system,
                    "platform_version": uname.version,
                    "platform_release": uname.release,
                    "architecture": uname.machine,
                    "processor": uname.processor,
                    "cpu_cores_physical": cpu_count,
                    "cpu_cores_logical": cpu_count_logical,
                    "cpu_freq_max": cpu_freq_max,
                    "memory_total_gb": mem_total_gb,
                    "disk_total_gb": disk_total_gb,
                    "network_interfaces": net_interfaces,
                    "uptime_seconds": int(uptime_seconds),
                    "python_version": platform.python_version(),
                }
            }

            logger.info(f"Scanned system: {hostname}")
            return [asset]

        except Exception as e:
            logger.error(f"System scan failed: {e}")
            return []

    def get_system_metrics(self) -> Dict[str, Any]:
        """
        Get current system metrics.

        Returns:
            System metrics
        """
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            load_avg = psutil.getloadavg() if hasattr(psutil, 'getloadavg') else (0, 0, 0)

            # Memory metrics
            mem = psutil.virtual_memory()
            swap = psutil.swap_memory()

            # Disk metrics
            disk = psutil.disk_usage('/')
            disk_io = psutil.disk_io_counters()

            # Network metrics
            net_io = psutil.net_io_counters()

            return {
                "cpu": {
                    "percent": cpu_percent,
                    "count": cpu_count,
                    "load_average": list(load_avg),
                },
                "memory": {
                    "total": mem.total,
                    "available": mem.available,
                    "percent": mem.percent,
                    "used": mem.used,
                },
                "swap": {
                    "total": swap.total,
                    "used": swap.used,
                    "percent": swap.percent,
                },
                "disk": {
                    "total": disk.total,
                    "used": disk.used,
                    "free": disk.free,
                    "percent": disk.percent,
                    "read_bytes": disk_io.read_bytes if disk_io else 0,
                    "write_bytes": disk_io.write_bytes if disk_io else 0,
                },
                "network": {
                    "bytes_sent": net_io.bytes_sent,
                    "bytes_recv": net_io.bytes_recv,
                    "packets_sent": net_io.packets_sent,
                    "packets_recv": net_io.packets_recv,
                },
            }

        except Exception as e:
            logger.error(f"Failed to get system metrics: {e}")
            return {}

    def get_system_info(self) -> Dict[str, Any]:
        """
        Get detailed system information.

        Returns:
            Detailed system info
        """
        try:
            return {
                "hostname": socket.gethostname(),
                "platform": platform.system(),
                "platform_release": platform.release(),
                "platform_version": platform.version(),
                "architecture": platform.machine(),
                "processor": platform.processor(),
                "python_version": platform.python_version(),
                "cpu_count": psutil.cpu_count(),
                "memory_total": psutil.virtual_memory().total,
                "boot_time": datetime.fromtimestamp(psutil.boot_time()).isoformat(),
            }

        except Exception as e:
            logger.error(f"Failed to get system info: {e}")
            return {}
