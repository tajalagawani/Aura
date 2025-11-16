"""
Port Scanner - Discovers open ports and services.

Scans for listening ports and identifies running services with statistics.
"""

import logging
import socket
import psutil
from typing import Dict, List, Any
from collections import defaultdict

from aura.scanners.base_scanner import BaseScanner

logger = logging.getLogger(__name__)


class PortScanner(BaseScanner):
    """
    Scanner for open ports and services.

    Discovers listening ports, identifies services, and tracks connection stats.

    Example:
        >>> scanner = PortScanner(
        ...     assets_dir="./assets",
        ...     include_stats=True
        ... )
        >>> count = await scanner.discover_and_instrument()
    """

    # Common port to service mapping
    COMMON_SERVICES = {
        20: "ftp-data",
        21: "ftp",
        22: "ssh",
        23: "telnet",
        25: "smtp",
        53: "dns",
        80: "http",
        110: "pop3",
        143: "imap",
        443: "https",
        465: "smtps",
        587: "smtp-submission",
        993: "imaps",
        995: "pop3s",
        3000: "dev-server",
        3306: "mysql",
        5432: "postgresql",
        5672: "rabbitmq",
        6379: "redis",
        8000: "http-alt",
        8080: "http-proxy",
        8443: "https-alt",
        9090: "prometheus",
        9200: "elasticsearch",
        11211: "memcached",
        27017: "mongodb",
        50000: "db2",
    }

    def __init__(
        self,
        assets_dir: str = "./assets",
        include_stats: bool = True,
        track_connections: bool = True
    ):
        """
        Initialize Port scanner.

        Args:
            assets_dir: Directory for AAV files
            include_stats: Include connection statistics
            track_connections: Track active connections per port
        """
        super().__init__(assets_dir)
        self.include_stats = include_stats
        self.track_connections = track_connections

    async def scan(self) -> List[Dict[str, Any]]:
        """
        Scan for listening ports and services.

        Returns:
            List of discovered ports/services
        """
        try:
            ports = []
            port_stats = defaultdict(lambda: {
                "connections": 0,
                "established": 0,
                "listen": 0,
                "time_wait": 0,
            })

            # Get all listening connections
            try:
                connections = psutil.net_connections(kind='inet')
            except psutil.AccessDenied:
                logger.warning("Permission denied accessing network connections. Run as root for full scanning.")
                connections = []

            # Track listening ports
            listening_ports = {}

            for conn in connections:
                if conn.status == psutil.CONN_LISTEN:
                    port = conn.laddr.port
                    addr = conn.laddr.ip

                    # Get process info if available
                    process_name = "unknown"
                    process_pid = conn.pid
                    if process_pid:
                        try:
                            proc = psutil.Process(process_pid)
                            process_name = proc.name()
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            pass

                    # Identify service
                    service_name = self._identify_service(port, process_name)

                    key = (addr, port)
                    if key not in listening_ports:
                        listening_ports[key] = {
                            "address": addr,
                            "port": port,
                            "service": service_name,
                            "process": process_name,
                            "pid": process_pid,
                        }

                # Collect connection stats
                if self.include_stats and conn.laddr:
                    port = conn.laddr.port
                    port_stats[port]["connections"] += 1

                    if conn.status == psutil.CONN_ESTABLISHED:
                        port_stats[port]["established"] += 1
                    elif conn.status == psutil.CONN_LISTEN:
                        port_stats[port]["listen"] += 1
                    elif conn.status == psutil.CONN_TIME_WAIT:
                        port_stats[port]["time_wait"] += 1

            # Create assets for each listening port
            for (addr, port), info in listening_ports.items():
                stats = port_stats.get(port, {})

                asset = {
                    "id": f"port-{addr.replace('.', '-').replace(':', '-')}-{port}",
                    "name": f"{info['service']}:{port}",
                    "type": "port",
                    "metadata": {
                        "address": addr,
                        "port": port,
                        "service": info['service'],
                        "process": info['process'],
                        "pid": info['pid'],
                        "protocol": "tcp",
                        "stats": {
                            "total_connections": stats.get("connections", 0),
                            "established": stats.get("established", 0),
                            "listening": stats.get("listen", 0),
                            "time_wait": stats.get("time_wait", 0),
                        } if self.include_stats else {},
                    }
                }
                ports.append(asset)

            logger.info(f"Found {len(ports)} listening ports")
            return ports

        except Exception as e:
            logger.error(f"Port scan failed: {e}")
            return []

    def _identify_service(self, port: int, process_name: str) -> str:
        """
        Identify service by port and process name.

        Args:
            port: Port number
            process_name: Process name

        Returns:
            Service name
        """
        # Check common ports first
        if port in self.COMMON_SERVICES:
            return self.COMMON_SERVICES[port]

        # Try to identify from process name
        process_lower = process_name.lower()

        if "nginx" in process_lower:
            return "nginx"
        elif "apache" in process_lower or "httpd" in process_lower:
            return "apache"
        elif "postgres" in process_lower:
            return "postgresql"
        elif "mysql" in process_lower or "mariadb" in process_lower:
            return "mysql"
        elif "redis" in process_lower:
            return "redis"
        elif "mongo" in process_lower:
            return "mongodb"
        elif "docker" in process_lower:
            return "docker"
        elif "ssh" in process_lower:
            return "ssh"
        elif "python" in process_lower or "gunicorn" in process_lower or "uwsgi" in process_lower:
            return "python-app"
        elif "node" in process_lower or "npm" in process_lower:
            return "node-app"
        elif "java" in process_lower:
            return "java-app"
        else:
            return f"unknown-{port}"

    def get_port_details(self, port: int, address: str = "0.0.0.0") -> Dict[str, Any]:
        """
        Get detailed port information and statistics.

        Args:
            port: Port number
            address: Bind address

        Returns:
            Port details
        """
        try:
            details = {
                "port": port,
                "address": address,
                "service": self.COMMON_SERVICES.get(port, f"unknown-{port}"),
                "connections": [],
                "stats": {
                    "total": 0,
                    "established": 0,
                    "listen": 0,
                    "time_wait": 0,
                    "close_wait": 0,
                },
            }

            # Get connections for this port
            try:
                connections = psutil.net_connections(kind='inet')
            except psutil.AccessDenied:
                logger.warning("Permission denied accessing connections")
                return details

            for conn in connections:
                if conn.laddr and conn.laddr.port == port:
                    details["stats"]["total"] += 1

                    # Count by status
                    if conn.status == psutil.CONN_ESTABLISHED:
                        details["stats"]["established"] += 1
                    elif conn.status == psutil.CONN_LISTEN:
                        details["stats"]["listen"] += 1
                    elif conn.status == psutil.CONN_TIME_WAIT:
                        details["stats"]["time_wait"] += 1
                    elif conn.status == psutil.CONN_CLOSE_WAIT:
                        details["stats"]["close_wait"] += 1

                    # Add connection details
                    if self.track_connections:
                        conn_info = {
                            "local": f"{conn.laddr.ip}:{conn.laddr.port}",
                            "status": conn.status,
                        }
                        if conn.raddr:
                            conn_info["remote"] = f"{conn.raddr.ip}:{conn.raddr.port}"
                        if conn.pid:
                            try:
                                proc = psutil.Process(conn.pid)
                                conn_info["process"] = proc.name()
                            except (psutil.NoSuchProcess, psutil.AccessDenied):
                                pass

                        details["connections"].append(conn_info)

            return details

        except Exception as e:
            logger.error(f"Failed to get port details for {port}: {e}")
            return {}

    def get_service_stats(self, service_name: str) -> Dict[str, Any]:
        """
        Get statistics for a specific service across all ports.

        Args:
            service_name: Service name to query

        Returns:
            Service statistics
        """
        try:
            stats = {
                "service": service_name,
                "ports": [],
                "total_connections": 0,
                "processes": set(),
            }

            # Find all ports running this service
            for port, svc_name in self.COMMON_SERVICES.items():
                if svc_name == service_name:
                    port_details = self.get_port_details(port)
                    if port_details.get("stats", {}).get("total", 0) > 0:
                        stats["ports"].append(port)
                        stats["total_connections"] += port_details["stats"]["total"]

            # Convert set to list for serialization
            stats["processes"] = list(stats["processes"])

            return stats

        except Exception as e:
            logger.error(f"Failed to get stats for service {service_name}: {e}")
            return {}

    def check_port_open(self, host: str, port: int, timeout: float = 1.0) -> bool:
        """
        Check if a port is open on a host.

        Args:
            host: Host to check
            port: Port number
            timeout: Connection timeout in seconds

        Returns:
            True if port is open
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((host, port))
            sock.close()
            return result == 0

        except Exception as e:
            logger.debug(f"Port check failed for {host}:{port}: {e}")
            return False

    def get_all_port_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive port statistics.

        Returns:
            All port statistics
        """
        try:
            stats = {
                "total_ports": 0,
                "by_service": defaultdict(int),
                "by_status": defaultdict(int),
                "top_ports": [],
            }

            try:
                connections = psutil.net_connections(kind='inet')
            except psutil.AccessDenied:
                logger.warning("Permission denied accessing connections")
                return stats

            port_connection_count = defaultdict(int)

            for conn in connections:
                if conn.laddr:
                    port = conn.laddr.port
                    port_connection_count[port] += 1
                    stats["by_status"][conn.status] += 1

                    if conn.status == psutil.CONN_LISTEN:
                        service = self.COMMON_SERVICES.get(port, "other")
                        stats["by_service"][service] += 1

            stats["total_ports"] = len(port_connection_count)

            # Top 10 ports by connection count
            top_ports = sorted(
                port_connection_count.items(),
                key=lambda x: x[1],
                reverse=True
            )[:10]

            stats["top_ports"] = [
                {
                    "port": port,
                    "connections": count,
                    "service": self.COMMON_SERVICES.get(port, f"unknown-{port}")
                }
                for port, count in top_ports
            ]

            # Convert defaultdict to regular dict
            stats["by_service"] = dict(stats["by_service"])
            stats["by_status"] = dict(stats["by_status"])

            return stats

        except Exception as e:
            logger.error(f"Failed to get port stats: {e}")
            return {}
