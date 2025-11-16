"""
Storage Sensor - Disk Usage and I/O Monitoring.

This sensor monitors:
- Disk usage percentage and free space
- I/O operations (read/write rates)
- IOPS (operations per second)
- Disk latency
- Mount points

Updates .aav file when disk usage changes by 1%+ or high I/O detected.
"""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List

import psutil

from aura.sensors.base import BaseSensor
from aura.core.exceptions import SensorError

logger = logging.getLogger(__name__)


class StorageSensor(BaseSensor):
    """
    Sensor for disk and storage monitoring.

    Monitors disk usage, I/O operations, and detects storage issues.

    Example:
        >>> sensor = StorageSensor(
        ...     asset_id="container-api",
        ...     aav_file_path="/assets/container-api.aav"
        ... )
        >>> await sensor.start()

    .aav Output:
        [storage]
        last_updated = "2025-11-16T15:30:45.200Z"
        sensor = "StorageSensor"
        sensor_status = "healthy"

        [storage.real_time]
        disk_usage_percent = 67.8
        free_gb = 15.6
        used_gb = 32.4
        total_gb = 48.0
        io_read_mb_per_sec = 2.3
        io_write_mb_per_sec = 1.8

        [storage.thresholds]
        warning = 80.0
        critical = 90.0
        update_threshold = 1.0

        [[storage.mount_points]]
        path = "/"
        usage_percent = 67.8
        free_gb = 15.6
    """

    def __init__(
        self,
        asset_id: str,
        aav_file_path: str,
        storage_warning_threshold: float = 80.0,
        storage_critical_threshold: float = 90.0,
        monitor_path: str = "/",
    ) -> None:
        """
        Initialize Storage Sensor.

        Args:
            asset_id: Unique asset identifier
            aav_file_path: Path to .aav file
            storage_warning_threshold: Storage warning threshold (default: 80%)
            storage_critical_threshold: Storage critical threshold (default: 90%)
            monitor_path: Path to monitor (default: "/")
        """
        super().__init__(
            asset_id=asset_id,
            aav_file_path=aav_file_path,
            section_name="storage",
            sampling_interval=2.0,  # Sample every 2 seconds
        )

        self.storage_warning_threshold = storage_warning_threshold
        self.storage_critical_threshold = storage_critical_threshold
        self.monitor_path = monitor_path

        # Track I/O for rate calculation
        self.previous_io_counters: Dict[str, int] = {}
        self.previous_io_time: float = 0.0

        logger.info(f"StorageSensor initialized for {asset_id} (path: {monitor_path})")

    def collect(self) -> Dict[str, Any]:
        """
        Collect storage and I/O metrics.

        Returns:
            Dictionary with storage metrics

        Raises:
            SensorError: If collection fails
        """
        try:
            import time

            # Disk usage
            usage = psutil.disk_usage(self.monitor_path)

            # I/O statistics
            io_counters = psutil.disk_io_counters()
            current_time = time.time()

            # Calculate I/O rates
            read_mb_per_sec = 0.0
            write_mb_per_sec = 0.0
            read_iops = 0.0
            write_iops = 0.0

            if self.previous_io_counters and self.previous_io_time > 0:
                time_delta = current_time - self.previous_io_time

                if time_delta > 0:
                    # Read/write rates in MB/s
                    read_bytes = io_counters.read_bytes - self.previous_io_counters['read_bytes']
                    write_bytes = io_counters.write_bytes - self.previous_io_counters['write_bytes']

                    read_mb_per_sec = (read_bytes / 1024 / 1024) / time_delta
                    write_mb_per_sec = (write_bytes / 1024 / 1024) / time_delta

                    # IOPS
                    read_ops = io_counters.read_count - self.previous_io_counters['read_count']
                    write_ops = io_counters.write_count - self.previous_io_counters['write_count']

                    read_iops = read_ops / time_delta
                    write_iops = write_ops / time_delta

            # Store current values for next iteration
            self.previous_io_counters = {
                'read_bytes': io_counters.read_bytes,
                'write_bytes': io_counters.write_bytes,
                'read_count': io_counters.read_count,
                'write_count': io_counters.write_count,
            }
            self.previous_io_time = current_time

            # Get all mount points
            mount_points = self._get_mount_points()

            return {
                "total_gb": usage.total / 1024 / 1024 / 1024,
                "used_gb": usage.used / 1024 / 1024 / 1024,
                "free_gb": usage.free / 1024 / 1024 / 1024,
                "usage_percent": usage.percent,
                "read_mb_per_sec": read_mb_per_sec,
                "write_mb_per_sec": write_mb_per_sec,
                "read_iops": read_iops,
                "write_iops": write_iops,
                "mount_points": mount_points,
            }

        except Exception as e:
            raise SensorError(f"Failed to collect storage metrics: {e}")

    def process(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process raw storage data into .aav format.

        Args:
            raw_data: Raw data from collect()

        Returns:
            Processed data for .aav file
        """
        # Build .aav structure
        processed = {
            "update_strategy": "change_driven",
            "real_time": {
                "disk_usage_percent": round(raw_data["usage_percent"], 2),
                "free_gb": round(raw_data["free_gb"], 2),
                "used_gb": round(raw_data["used_gb"], 2),
                "total_gb": round(raw_data["total_gb"], 2),
                "io_read_mb_per_sec": round(raw_data["read_mb_per_sec"], 2),
                "io_write_mb_per_sec": round(raw_data["write_mb_per_sec"], 2),
            },
            "io": {
                "read_iops": round(raw_data["read_iops"], 2),
                "write_iops": round(raw_data["write_iops"], 2),
            },
            "thresholds": {
                "warning": self.storage_warning_threshold,
                "critical": self.storage_critical_threshold,
                "update_threshold": 1.0,  # 1% change threshold
            }
        }

        # Add mount points
        if raw_data["mount_points"]:
            processed["mount_points"] = raw_data["mount_points"]

        # Add last significant change if detected
        if self.change_detector.should_update("disk_usage_percent", raw_data["usage_percent"]):
            processed["real_time"]["last_significant_change"] = \
                datetime.now(timezone.utc).isoformat() + 'Z'

        return processed

    def _get_mount_points(self) -> List[Dict[str, Any]]:
        """Get information about all mount points."""
        mount_points = []

        try:
            partitions = psutil.disk_partitions()

            for partition in partitions:
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    mount_points.append({
                        "path": partition.mountpoint,
                        "device": partition.device,
                        "fstype": partition.fstype,
                        "usage_percent": round(usage.percent, 2),
                        "free_gb": round(usage.free / 1024 / 1024 / 1024, 2),
                    })
                except (PermissionError, OSError):
                    # Skip inaccessible mount points
                    continue

        except Exception as e:
            logger.warning(f"Failed to get mount points: {e}")

        return mount_points

    def get_storage_status(self) -> str:
        """
        Get current storage status based on thresholds.

        Returns:
            "normal", "warning", or "critical"
        """
        try:
            usage = psutil.disk_usage(self.monitor_path)

            if usage.percent >= self.storage_critical_threshold:
                return "critical"
            elif usage.percent >= self.storage_warning_threshold:
                return "warning"
            else:
                return "normal"

        except Exception:
            return "unknown"
