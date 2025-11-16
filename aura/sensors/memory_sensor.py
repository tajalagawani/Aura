"""
Memory Sensor - RAM Usage and Leak Detection.

This sensor monitors:
- RAM usage percentage and absolute values
- Available memory
- Swap usage
- Memory leak detection
- Memory growth rate
- Per-process memory usage

The sensor detects memory leaks by tracking growth rate and trend analysis.
Updates .aav file when memory changes by 5%+ or leak detected.
"""

import logging
from datetime import datetime, timezone
from typing import Any, Dict

import psutil

from aura.sensors.base import BaseSensor
from aura.core.exceptions import SensorError

logger = logging.getLogger(__name__)


class MemorySensor(BaseSensor):
    """
    Sensor for memory monitoring and leak detection.

    Monitors RAM usage and detects potential memory leaks through
    trend analysis and growth rate tracking.

    Example:
        >>> sensor = MemorySensor(
        ...     asset_id="container-api",
        ...     aav_file_path="/assets/container-api.aav"
        ... )
        >>> await sensor.start()

    .aav Output:
        [memory]
        last_updated = "2025-11-16T15:30:45.150Z"
        sensor = "MemorySensor"
        sensor_status = "healthy"
        update_strategy = "change_driven"

        [memory.real_time]
        usage_percent = 68.1
        available_mb = 2048
        used_mb = 4352
        total_mb = 6400

        [memory.analysis]
        leak_detection = "stable"
        growth_rate_mb_per_hour = 12.5
        trend = "stable"

        [memory.thresholds]
        warning = 80.0
        critical = 90.0
        update_threshold = 5.0

        [memory.swap]
        usage_percent = 15.2
        used_mb = 512
        total_mb = 3200
    """

    def __init__(
        self,
        asset_id: str,
        aav_file_path: str,
        memory_warning_threshold: float = 80.0,
        memory_critical_threshold: float = 90.0,
        leak_detection_enabled: bool = True,
    ) -> None:
        """
        Initialize Memory Sensor.

        Args:
            asset_id: Unique asset identifier
            aav_file_path: Path to .aav file
            memory_warning_threshold: Memory warning threshold (default: 80%)
            memory_critical_threshold: Memory critical threshold (default: 90%)
            leak_detection_enabled: Enable memory leak detection
        """
        super().__init__(
            asset_id=asset_id,
            aav_file_path=aav_file_path,
            section_name="memory",
            sampling_interval=1.0,  # Sample every 1 second
        )

        self.memory_warning_threshold = memory_warning_threshold
        self.memory_critical_threshold = memory_critical_threshold
        self.leak_detection_enabled = leak_detection_enabled

        # Leak detection tracking
        self.memory_history: list[float] = []
        self.max_history = 60  # Keep 60 samples for trend analysis

        logger.info(f"MemorySensor initialized for {asset_id}")

    def collect(self) -> Dict[str, Any]:
        """
        Collect memory metrics.

        Returns:
            Dictionary with memory metrics

        Raises:
            SensorError: If collection fails
        """
        try:
            # Virtual memory (RAM)
            vmem = psutil.virtual_memory()

            # Swap memory
            swap = psutil.swap_memory()

            # Track memory for leak detection
            if self.leak_detection_enabled:
                self.memory_history.append(vmem.used / 1024 / 1024)  # MB
                if len(self.memory_history) > self.max_history:
                    self.memory_history.pop(0)

            return {
                "total_mb": vmem.total / 1024 / 1024,
                "available_mb": vmem.available / 1024 / 1024,
                "used_mb": vmem.used / 1024 / 1024,
                "usage_percent": vmem.percent,
                "swap_total_mb": swap.total / 1024 / 1024,
                "swap_used_mb": swap.used / 1024 / 1024,
                "swap_percent": swap.percent,
            }

        except Exception as e:
            raise SensorError(f"Failed to collect memory metrics: {e}")

    def process(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process raw memory data into .aav format.

        Args:
            raw_data: Raw data from collect()

        Returns:
            Processed data for .aav file
        """
        # Detect memory leak
        leak_status = "stable"
        growth_rate = 0.0

        if self.leak_detection_enabled and len(self.memory_history) >= 10:
            leak_status = self._detect_leak()
            growth_rate = self._calculate_growth_rate()

        # Get trend
        trend = self.change_detector.get_trend("usage_percent")

        # Build .aav structure
        processed = {
            "update_strategy": "change_driven",
            "real_time": {
                "usage_percent": round(raw_data["usage_percent"], 2),
                "available_mb": round(raw_data["available_mb"], 2),
                "used_mb": round(raw_data["used_mb"], 2),
                "total_mb": round(raw_data["total_mb"], 2),
            },
            "analysis": {
                "leak_detection": leak_status,
                "growth_rate_mb_per_hour": round(growth_rate, 2),
                "trend": trend,
            },
            "thresholds": {
                "warning": self.memory_warning_threshold,
                "critical": self.memory_critical_threshold,
                "update_threshold": 5.0,
            },
            "swap": {
                "usage_percent": round(raw_data["swap_percent"], 2),
                "used_mb": round(raw_data["swap_used_mb"], 2),
                "total_mb": round(raw_data["swap_total_mb"], 2),
            }
        }

        # Add last significant change if detected
        if self.change_detector.should_update("usage_percent", raw_data["usage_percent"]):
            processed["real_time"]["last_significant_change"] = \
                datetime.now(timezone.utc).isoformat() + 'Z'

        return processed

    def _detect_leak(self) -> str:
        """
        Detect potential memory leak.

        A leak is suspected if:
        - Memory usage is consistently increasing
        - Growth rate is above threshold

        Returns:
            "stable", "possible_leak", or "leak_detected"
        """
        if len(self.memory_history) < 10:
            return "stable"

        # Check if memory is consistently increasing
        recent = self.memory_history[-10:]
        increases = sum(1 for i in range(1, len(recent)) if recent[i] > recent[i-1])

        # If increasing in 8+ out of 10 samples
        if increases >= 8:
            growth_rate = self._calculate_growth_rate()

            # Significant growth (>100 MB/hour)
            if growth_rate > 100:
                return "leak_detected"
            # Moderate growth (>50 MB/hour)
            elif growth_rate > 50:
                return "possible_leak"

        return "stable"

    def _calculate_growth_rate(self) -> float:
        """
        Calculate memory growth rate in MB/hour.

        Uses linear regression on recent history.

        Returns:
            Growth rate in MB/hour
        """
        if len(self.memory_history) < 5:
            return 0.0

        # Simple linear regression
        n = len(self.memory_history)
        x = list(range(n))
        y = self.memory_history

        x_mean = sum(x) / n
        y_mean = sum(y) / n

        numerator = sum((x[i] - x_mean) * (y[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))

        if denominator == 0:
            return 0.0

        # Slope in MB per sample
        slope = numerator / denominator

        # Convert to MB per hour (assuming 1 sample/second)
        mb_per_hour = slope * 3600

        return mb_per_hour

    def get_memory_status(self) -> str:
        """
        Get current memory status based on thresholds.

        Returns:
            "normal", "warning", or "critical"
        """
        try:
            mem = psutil.virtual_memory()

            if mem.percent >= self.memory_critical_threshold:
                return "critical"
            elif mem.percent >= self.memory_warning_threshold:
                return "warning"
            else:
                return "normal"

        except Exception:
            return "unknown"
