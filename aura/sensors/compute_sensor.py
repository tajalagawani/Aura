"""
Compute Sensor - CPU and Process Monitoring.

This sensor monitors:
- CPU usage percentage
- Load average (1, 5, 15 minutes)
- Process count and lifecycle
- Critical process monitoring
- CPU events (spikes, process starts/stops)

The sensor uses intelligent change detection to only update the .aav file
when CPU changes by 5%+ or processes start/stop.
"""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import psutil

from aura.sensors.base import BaseSensor
from aura.core.exceptions import SensorError

logger = logging.getLogger(__name__)


class ProcessInfo:
    """Information about a process."""

    def __init__(self, proc: psutil.Process) -> None:
        """
        Initialize from psutil Process.

        Args:
            proc: psutil.Process instance
        """
        try:
            self.pid = proc.pid
            self.name = proc.name()
            self.cpu_percent = proc.cpu_percent(interval=0.1)
            self.memory_mb = proc.memory_info().rss / 1024 / 1024
            self.status = proc.status()
            self.cmdline = ' '.join(proc.cmdline()[:3])  # First 3 args only
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            # Process terminated or no access
            self.pid = 0
            self.name = "unknown"
            self.cpu_percent = 0.0
            self.memory_mb = 0.0
            self.status = "unknown"
            self.cmdline = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "pid": self.pid,
            "name": self.name,
            "cpu_percent": round(self.cpu_percent, 2),
            "memory_mb": round(self.memory_mb, 2),
            "status": self.status,
        }


class ComputeSensor(BaseSensor):
    """
    Sensor for CPU and process monitoring.

    Monitors CPU usage, load average, and process lifecycle.
    Only updates .aav file when:
    - CPU changes by 5%+
    - Load average changes significantly
    - Processes start or stop
    - CPU spike detected

    Example:
        >>> sensor = ComputeSensor(
        ...     asset_id="container-api",
        ...     aav_file_path="/assets/container-api.aav"
        ... )
        >>> await sensor.start()

    .aav Output:
        [compute]
        last_updated = "2025-11-16T15:30:45.123Z"
        sensor = "ComputeSensor"
        sensor_status = "healthy"
        update_strategy = "change_driven"

        [compute.real_time]
        cpu_percent = 45.2
        load_average = [1.23, 1.45, 1.67]
        process_count = 47
        last_significant_change = "2025-11-16T15:25:15Z"

        [compute.thresholds]
        cpu_warning = 70.0
        cpu_critical = 85.0
        update_threshold = 5.0

        [[compute.processes.critical]]
        pid = 1234
        name = "payment-service"
        cpu_percent = 12.5
        memory_mb = 256
        status = "running"

        [compute.events]
        recent = [
            {timestamp = "2025-11-16T15:30:40Z", event = "process_started", pid = 1236},
            {timestamp = "2025-11-16T15:25:15Z", event = "cpu_spike", cpu_percent = 89.5}
        ]
    """

    def __init__(
        self,
        asset_id: str,
        aav_file_path: str,
        cpu_warning_threshold: float = 70.0,
        cpu_critical_threshold: float = 85.0,
        critical_process_names: Optional[List[str]] = None,
    ) -> None:
        """
        Initialize Compute Sensor.

        Args:
            asset_id: Unique asset identifier
            aav_file_path: Path to .aav file
            cpu_warning_threshold: CPU warning threshold (default: 70%)
            cpu_critical_threshold: CPU critical threshold (default: 85%)
            critical_process_names: List of process names to monitor closely
        """
        super().__init__(
            asset_id=asset_id,
            aav_file_path=aav_file_path,
            section_name="compute",
            sampling_interval=0.5,  # Sample every 500ms
        )

        self.cpu_warning_threshold = cpu_warning_threshold
        self.cpu_critical_threshold = cpu_critical_threshold
        self.critical_process_names = critical_process_names or []

        # Track process lifecycle
        self.previous_pids: set[int] = set()
        self.events: List[Dict[str, Any]] = []
        self.max_events = 10  # Keep last 10 events

        logger.info(
            f"ComputeSensor initialized for {asset_id} "
            f"(warning: {cpu_warning_threshold}%, critical: {cpu_critical_threshold}%)"
        )

    def collect(self) -> Dict[str, Any]:
        """
        Collect CPU and process metrics.

        Returns:
            Dictionary with CPU metrics and process info

        Raises:
            SensorError: If collection fails
        """
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=0.1)
            cpu_count = psutil.cpu_count()
            load_avg = psutil.getloadavg()  # 1, 5, 15 minute averages

            # Process information
            processes = []
            current_pids = set()

            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info', 'status']):
                try:
                    current_pids.add(proc.info['pid'])

                    # Track critical processes
                    if proc.info['name'] in self.critical_process_names:
                        processes.append(ProcessInfo(proc))

                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            # Detect process lifecycle changes
            new_pids = current_pids - self.previous_pids
            terminated_pids = self.previous_pids - current_pids

            # Record process events
            for pid in new_pids:
                self._add_event("process_started", {"pid": pid})

            for pid in terminated_pids:
                self._add_event("process_stopped", {"pid": pid})

            # Detect CPU spike
            if cpu_percent > self.cpu_critical_threshold:
                self._add_event("cpu_spike", {"cpu_percent": cpu_percent})

            self.previous_pids = current_pids

            return {
                "cpu_percent": cpu_percent,
                "cpu_count": cpu_count,
                "load_average": list(load_avg),
                "process_count": len(current_pids),
                "critical_processes": processes,
                "events": self.events,
            }

        except Exception as e:
            raise SensorError(f"Failed to collect CPU metrics: {e}")

    def process(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process raw CPU data into .aav format.

        Args:
            raw_data: Raw data from collect()

        Returns:
            Processed data for .aav file
        """
        # Determine if this is a significant change
        last_change = None
        if self.change_detector.should_update("cpu_percent", raw_data["cpu_percent"]):
            last_change = datetime.now(timezone.utc).isoformat() + 'Z'

        # Build .aav structure
        processed = {
            "update_strategy": "change_driven",
            "real_time": {
                "cpu_percent": round(raw_data["cpu_percent"], 2),
                "load_average": [round(x, 2) for x in raw_data["load_average"]],
                "process_count": raw_data["process_count"],
            },
            "thresholds": {
                "cpu_warning": self.cpu_warning_threshold,
                "cpu_critical": self.cpu_critical_threshold,
                "update_threshold": 5.0,  # 5% change threshold
            },
            "system": {
                "cpu_count": raw_data["cpu_count"],
            }
        }

        # Add last significant change timestamp
        if last_change:
            processed["real_time"]["last_significant_change"] = last_change

        # Add critical processes
        if raw_data["critical_processes"]:
            processed["processes"] = {
                "critical": [p.to_dict() for p in raw_data["critical_processes"]]
            }

        # Add recent events
        if raw_data["events"]:
            processed["events"] = {
                "recent": raw_data["events"][-10:]  # Last 10 events
            }

        return processed

    def _add_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """
        Add an event to the event log.

        Args:
            event_type: Type of event (process_started, cpu_spike, etc)
            data: Event data
        """
        event = {
            "timestamp": datetime.now(timezone.utc).isoformat() + 'Z',
            "event": event_type,
            **data
        }

        self.events.append(event)

        # Keep only recent events
        if len(self.events) > self.max_events:
            self.events = self.events[-self.max_events:]

    def get_cpu_status(self) -> str:
        """
        Get current CPU status based on thresholds.

        Returns:
            "normal", "warning", or "critical"
        """
        try:
            cpu = psutil.cpu_percent(interval=0.1)

            if cpu >= self.cpu_critical_threshold:
                return "critical"
            elif cpu >= self.cpu_warning_threshold:
                return "warning"
            else:
                return "normal"

        except Exception:
            return "unknown"
