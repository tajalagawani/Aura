"""
Network Sensor - Connection and Traffic Monitoring.

This sensor monitors:
- Active network connections (count and state)
- Network traffic (bytes sent/received)
- Connection states (ESTABLISHED, LISTEN, etc.)
- Failed connections
- Port usage

Updates .aav file when connections change by 10+ or traffic spike detected.
"""

import logging
from collections import Counter
from datetime import datetime, timezone
from typing import Any, Dict, List

import psutil

from aura.sensors.base import BaseSensor
from aura.core.exceptions import SensorError

logger = logging.getLogger(__name__)


class NetworkSensor(BaseSensor):
    """
    Sensor for network monitoring.

    Monitors network connections, traffic, and connection states.

    Example:
        >>> sensor = NetworkSensor(
        ...     asset_id="container-api",
        ...     aav_file_path="/assets/container-api.aav"
        ... )
        >>> await sensor.start()

    .aav Output:
        [network]
        last_updated = "2025-11-16T15:30:45.250Z"
        sensor = "NetworkSensor"
        sensor_status = "healthy"

        [network.real_time]
        active_connections = 127
        bytes_sent_per_sec = 1024000
        bytes_recv_per_sec = 2048000

        [network.connections]
        established = 127
        listen = 5
        time_wait = 12

        [network.thresholds]
        max_connections = 500
        update_threshold = 10

        [[network.connections.active]]
        local_port = 8080
        remote_host = "nginx-lb-01"
        state = "ESTABLISHED"
    """

    def __init__(
        self,
        asset_id: str,
        aav_file_path: str,
        max_connections_threshold: int = 500,
        monitor_ports: List[int] = None,
    ) -> None:
        """
        Initialize Network Sensor.

        Args:
            asset_id: Unique asset identifier
            aav_file_path: Path to .aav file
            max_connections_threshold: Maximum connections threshold
            monitor_ports: Specific ports to monitor (None = all ports)
        """
        super().__init__(
            asset_id=asset_id,
            aav_file_path=aav_file_path,
            section_name="network",
            sampling_interval=1.0,  # Sample every 1 second
        )

        self.max_connections_threshold = max_connections_threshold
        self.monitor_ports = monitor_ports or []

        # Track traffic for rate calculation
        self.previous_net_io: Dict[str, int] = {}
        self.previous_net_time: float = 0.0

        logger.info(f"NetworkSensor initialized for {asset_id}")

    async def collect(self) -> Dict[str, Any]:
        """
        Collect network metrics.

        Returns:
            Dictionary with network metrics

        Raises:
            SensorError: If collection fails
        """
        try:
            import time

            # Network connections
            connections = psutil.net_connections(kind='inet')

            # Filter by monitored ports if specified
            if self.monitor_ports:
                connections = [
                    conn for conn in connections
                    if conn.laddr.port in self.monitor_ports
                ]

            # Count connection states
            state_counts = Counter(conn.status for conn in connections)

            # Get active connections details (sample of ESTABLISHED)
            active_connections = [
                {
                    "local_port": conn.laddr.port,
                    "remote_host": conn.raddr.ip if conn.raddr else None,
                    "remote_port": conn.raddr.port if conn.raddr else None,
                    "state": conn.status,
                }
                for conn in connections[:10]  # Sample first 10
                if conn.status == "ESTABLISHED"
            ]

            # Network I/O
            net_io = psutil.net_io_counters()
            current_time = time.time()

            # Calculate traffic rates
            bytes_sent_per_sec = 0.0
            bytes_recv_per_sec = 0.0

            if self.previous_net_io and self.previous_net_time > 0:
                time_delta = current_time - self.previous_net_time

                if time_delta > 0:
                    sent_bytes = net_io.bytes_sent - self.previous_net_io['bytes_sent']
                    recv_bytes = net_io.bytes_recv - self.previous_net_io['bytes_recv']

                    bytes_sent_per_sec = sent_bytes / time_delta
                    bytes_recv_per_sec = recv_bytes / time_delta

            # Store current values
            self.previous_net_io = {
                'bytes_sent': net_io.bytes_sent,
                'bytes_recv': net_io.bytes_recv,
            }
            self.previous_net_time = current_time

            return {
                "connection_count": len(connections),
                "state_counts": dict(state_counts),
                "active_connections": active_connections,
                "bytes_sent_per_sec": bytes_sent_per_sec,
                "bytes_recv_per_sec": bytes_recv_per_sec,
                "total_packets_sent": net_io.packets_sent,
                "total_packets_recv": net_io.packets_recv,
                "errors_in": net_io.errin,
                "errors_out": net_io.errout,
                "drops_in": net_io.dropin,
                "drops_out": net_io.dropout,
            }

        except PermissionError:
            logger.warning("Permission denied accessing network connections, returning basic I/O stats only")
            # Return basic network I/O stats without connection details
            try:
                net_io = psutil.net_io_counters()
                current_time = time.time()

                bytes_sent_per_sec = 0.0
                bytes_recv_per_sec = 0.0

                if self.previous_net_io and self.previous_net_time > 0:
                    time_delta = current_time - self.previous_net_time
                    if time_delta > 0:
                        sent_bytes = net_io.bytes_sent - self.previous_net_io['bytes_sent']
                        recv_bytes = net_io.bytes_recv - self.previous_net_io['bytes_recv']
                        bytes_sent_per_sec = sent_bytes / time_delta
                        bytes_recv_per_sec = recv_bytes / time_delta

                self.previous_net_io = {
                    'bytes_sent': net_io.bytes_sent,
                    'bytes_recv': net_io.bytes_recv,
                }
                self.previous_net_time = current_time

                return {
                    "connection_count": 0,
                    "state_counts": {},
                    "active_connections": [],
                    "bytes_sent_per_sec": bytes_sent_per_sec,
                    "bytes_recv_per_sec": bytes_recv_per_sec,
                    "total_packets_sent": net_io.packets_sent,
                    "total_packets_recv": net_io.packets_recv,
                    "errors_in": net_io.errin,
                    "errors_out": net_io.errout,
                    "drops_in": net_io.dropin,
                    "drops_out": net_io.dropout,
                }
            except Exception as fallback_error:
                logger.error(f"Fallback network metrics failed: {fallback_error}")
                raise SensorError(f"Failed to collect network metrics: {fallback_error}")
        except Exception as e:
            logger.error(f"Network sensor collection failed: {e}")
            raise SensorError(f"Failed to collect network metrics: {e}")

    def process(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process raw network data into .aav format.

        Args:
            raw_data: Raw data from collect()

        Returns:
            Processed data for .aav file
        """
        # Build .aav structure
        processed = {
            "update_strategy": "change_driven",
            "real_time": {
                "active_connections": raw_data["connection_count"],
                "bytes_sent_per_sec": round(raw_data["bytes_sent_per_sec"], 2),
                "bytes_recv_per_sec": round(raw_data["bytes_recv_per_sec"], 2),
            },
            "connections": raw_data["state_counts"],
            "thresholds": {
                "max_connections": self.max_connections_threshold,
                "update_threshold": 10,  # 10 connection change
            },
            "errors": {
                "errors_in": raw_data["errors_in"],
                "errors_out": raw_data["errors_out"],
                "drops_in": raw_data["drops_in"],
                "drops_out": raw_data["drops_out"],
            }
        }

        # Add active connections sample
        if raw_data["active_connections"]:
            processed["connections"]["active"] = raw_data["active_connections"]

        # Add last significant change if detected
        if self.change_detector.should_update("active_connections", raw_data["connection_count"]):
            processed["real_time"]["last_significant_change"] = \
                datetime.now(timezone.utc).isoformat() + 'Z'

        return processed

    def get_network_status(self) -> str:
        """
        Get current network status based on connection count.

        Returns:
            "normal", "warning", or "critical"
        """
        try:
            connections = psutil.net_connections(kind='inet')
            conn_count = len(connections)

            if conn_count >= self.max_connections_threshold:
                return "critical"
            elif conn_count >= (self.max_connections_threshold * 0.8):
                return "warning"
            else:
                return "normal"

        except Exception:
            return "unknown"
