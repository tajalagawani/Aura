"""
Intelligent Change Detection System.

This module implements threshold-based change detection to minimize unnecessary
updates. Only significant changes trigger file updates, reducing I/O and ensuring
efficient monitoring.

The change detector supports:
- Threshold-based detection (5% CPU, 5% memory, 1% disk, etc.)
- Spike detection for rapid changes
- Trend analysis for gradual changes
- Adaptive thresholds based on volatility
"""

import time
from collections import deque
from dataclasses import dataclass, field
from typing import Any, Deque, Dict, Optional


@dataclass
class ChangeThreshold:
    """Thresholds for detecting significant changes."""

    cpu_percent: float = 5.0  # 5% change
    memory_percent: float = 5.0  # 5% change
    storage_percent: float = 1.0  # 1% change (more sensitive)
    network_connections: int = 10  # 10 connection change
    response_time_multiplier: float = 2.0  # 2x response time change


@dataclass
class MetricHistory:
    """Historical metric values for trend analysis."""

    values: Deque[float] = field(default_factory=lambda: deque(maxlen=60))
    timestamps: Deque[float] = field(default_factory=lambda: deque(maxlen=60))

    def add(self, value: float) -> None:
        """Add a value to history."""
        self.values.append(value)
        self.timestamps.append(time.time())

    def get_trend(self) -> str:
        """
        Calculate trend direction.

        Returns:
            "increasing", "decreasing", or "stable"
        """
        if len(self.values) < 5:
            return "stable"

        recent = list(self.values)[-5:]
        increasing = sum(1 for i in range(1, len(recent)) if recent[i] > recent[i-1])

        if increasing >= 4:
            return "increasing"
        elif increasing <= 1:
            return "decreasing"
        else:
            return "stable"

    def get_average(self) -> Optional[float]:
        """Get average of historical values."""
        if not self.values:
            return None
        return sum(self.values) / len(self.values)

    def get_volatility(self) -> float:
        """
        Calculate volatility (standard deviation).

        Higher volatility might warrant lower thresholds.

        Returns:
            Standard deviation of values
        """
        if len(self.values) < 2:
            return 0.0

        avg = self.get_average()
        if avg is None:
            return 0.0

        variance = sum((x - avg) ** 2 for x in self.values) / len(self.values)
        return variance ** 0.5


class ChangeDetector:
    """
    Intelligent change detector with adaptive thresholds.

    This class determines whether metric changes are significant enough
    to warrant updating the .aav file, reducing unnecessary I/O while
    ensuring important changes are captured.

    Example:
        >>> detector = ChangeDetector()
        >>> # First reading
        >>> detector.update('cpu_percent', 45.0)
        >>> # Small change - not significant
        >>> detector.should_update('cpu_percent', 47.0)
        False
        >>> # Large change - significant
        >>> detector.should_update('cpu_percent', 55.0)
        True
    """

    def __init__(self, thresholds: Optional[ChangeThreshold] = None) -> None:
        """
        Initialize change detector.

        Args:
            thresholds: Custom thresholds (uses defaults if not provided)
        """
        self.thresholds = thresholds or ChangeThreshold()
        self.previous_values: Dict[str, Any] = {}
        self.history: Dict[str, MetricHistory] = {}
        self.last_update_time: Dict[str, float] = {}

    def should_update(
        self,
        metric_name: str,
        current_value: Any,
        force: bool = False
    ) -> bool:
        """
        Determine if metric change is significant enough to update file.

        Args:
            metric_name: Name of the metric (e.g., 'cpu_percent')
            current_value: Current metric value
            force: Force update regardless of change

        Returns:
            True if file should be updated
        """
        if force:
            return True

        # First reading - always update
        if metric_name not in self.previous_values:
            self._record_value(metric_name, current_value)
            return True

        previous_value = self.previous_values[metric_name]

        # Detect significant change based on metric type
        is_significant = self._is_significant_change(
            metric_name,
            previous_value,
            current_value
        )

        if is_significant:
            self._record_value(metric_name, current_value)
            return True

        # Check time-based update (fallback if no changes for 5 minutes)
        if self._should_update_by_time(metric_name, max_age=300):
            self._record_value(metric_name, current_value)
            return True

        return False

    def _is_significant_change(
        self,
        metric_name: str,
        previous: Any,
        current: Any
    ) -> bool:
        """Check if change exceeds threshold for this metric type."""
        # Handle None values
        if previous is None or current is None:
            return previous != current

        # CPU percentage change
        if 'cpu' in metric_name.lower() and 'percent' in metric_name.lower():
            return abs(current - previous) >= self.thresholds.cpu_percent

        # Memory percentage change
        if 'memory' in metric_name.lower() and 'percent' in metric_name.lower():
            return abs(current - previous) >= self.thresholds.memory_percent

        # Storage/disk percentage change
        if ('storage' in metric_name.lower() or 'disk' in metric_name.lower()) and \
           'percent' in metric_name.lower():
            return abs(current - previous) >= self.thresholds.storage_percent

        # Network connections change
        if 'connection' in metric_name.lower():
            return abs(current - previous) >= self.thresholds.network_connections

        # Response time change (2x increase)
        if 'response_time' in metric_name.lower() or 'latency' in metric_name.lower():
            if previous == 0:
                return current > 0
            return (current / previous) >= self.thresholds.response_time_multiplier

        # Status/state changes (always significant)
        if 'status' in metric_name.lower() or 'state' in metric_name.lower():
            return previous != current

        # Health changes (always significant)
        if 'health' in metric_name.lower():
            return previous != current

        # Default: any change for non-numeric values
        if not isinstance(current, (int, float)):
            return previous != current

        # Default: 10% change for other numeric values
        if previous == 0:
            return current != 0
        percent_change = abs((current - previous) / previous * 100)
        return percent_change >= 10.0

    def _should_update_by_time(self, metric_name: str, max_age: int = 300) -> bool:
        """Check if metric should be updated based on time since last update."""
        if metric_name not in self.last_update_time:
            return True

        age = time.time() - self.last_update_time[metric_name]
        return age >= max_age

    def _record_value(self, metric_name: str, value: Any) -> None:
        """Record metric value and timestamp."""
        self.previous_values[metric_name] = value
        self.last_update_time[metric_name] = time.time()

        # Add to history for numeric values
        if isinstance(value, (int, float)):
            if metric_name not in self.history:
                self.history[metric_name] = MetricHistory()
            self.history[metric_name].add(float(value))

    def update(self, metric_name: str, value: Any) -> None:
        """
        Update stored value without triggering change detection.

        Use this to record a value without determining if it should
        trigger a file update.

        Args:
            metric_name: Metric name
            value: Current value
        """
        self._record_value(metric_name, value)

    def detect_spike(self, metric_name: str, current_value: float) -> bool:
        """
        Detect sudden spikes in metrics.

        A spike is defined as a value significantly higher than recent average.

        Args:
            metric_name: Metric name
            current_value: Current value

        Returns:
            True if spike detected
        """
        if metric_name not in self.history:
            return False

        history = self.history[metric_name]
        avg = history.get_average()

        if avg is None or avg == 0:
            return False

        # Spike is 2x average
        return current_value >= (avg * 2.0)

    def get_trend(self, metric_name: str) -> str:
        """
        Get trend for a metric.

        Args:
            metric_name: Metric name

        Returns:
            "increasing", "decreasing", or "stable"
        """
        if metric_name not in self.history:
            return "stable"

        return self.history[metric_name].get_trend()

    def get_volatility(self, metric_name: str) -> float:
        """
        Get volatility for a metric.

        Args:
            metric_name: Metric name

        Returns:
            Standard deviation
        """
        if metric_name not in self.history:
            return 0.0

        return self.history[metric_name].get_volatility()

    def adjust_thresholds_for_volatility(self, metric_name: str) -> float:
        """
        Adjust threshold based on metric volatility.

        Higher volatility = lower threshold to catch important changes.

        Args:
            metric_name: Metric name

        Returns:
            Adjusted threshold
        """
        base_threshold = self.thresholds.cpu_percent  # Default

        if 'cpu' in metric_name.lower():
            base_threshold = self.thresholds.cpu_percent
        elif 'memory' in metric_name.lower():
            base_threshold = self.thresholds.memory_percent
        elif 'storage' in metric_name.lower():
            base_threshold = self.thresholds.storage_percent

        volatility = self.get_volatility(metric_name)

        # Higher volatility = lower threshold (more sensitive)
        # Volatility > 10 = halve threshold
        if volatility > 10:
            return base_threshold * 0.5
        elif volatility > 5:
            return base_threshold * 0.75
        else:
            return base_threshold

    def reset(self) -> None:
        """Reset all stored values and history."""
        self.previous_values.clear()
        self.history.clear()
        self.last_update_time.clear()
