"""
Base Sensor Framework.

This module provides the abstract base class for all sensors.
Each sensor monitors a specific aspect of a computational asset
and updates its corresponding section in the .aav file.

All sensors inherit from BaseSensor and implement:
- collect(): Gather metrics from the asset
- process(): Process raw metrics into .aav format
- should_update(): Determine if file should be updated
"""

import asyncio
import logging
import time
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Optional

from aura.core.aav import AAVFile
from aura.core.change_detector import ChangeDetector
from aura.core.exceptions import SensorError

logger = logging.getLogger(__name__)


class SensorStatus(str, Enum):
    """Sensor operational status."""

    INITIALIZING = "initializing"
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    STOPPED = "stopped"


class BaseSensor(ABC):
    """
    Abstract base class for all Aura sensors.

    A sensor monitors one aspect of a computational asset (CPU, memory, etc)
    and intelligently updates the corresponding section of the .aav file.

    Sensors implement:
    - Change-driven updates (not time-driven polling)
    - Adaptive sampling based on system load
    - Automatic error handling and recovery
    - Health monitoring and reporting

    Example:
        >>> class MySensor(BaseSensor):
        ...     def collect(self):
        ...         return {"my_metric": 42}
        ...
        ...     def process(self, raw_data):
        ...         return {"real_time": {"my_metric": raw_data["my_metric"]}}
        ...
        >>> sensor = MySensor("my-asset", "/assets/my-asset.aav", "my_section")
        >>> await sensor.start()
    """

    def __init__(
        self,
        asset_id: str,
        aav_file_path: str | Path,
        section_name: str,
        sampling_interval: float = 0.5,
    ) -> None:
        """
        Initialize sensor.

        Args:
            asset_id: Unique asset identifier
            aav_file_path: Path to the .aav file
            section_name: Section name in .aav file (e.g., 'compute')
            sampling_interval: Initial sampling interval in seconds
        """
        self.asset_id = asset_id
        self.aav_file = AAVFile(aav_file_path)
        self.section_name = section_name

        # Sampling configuration
        self.sampling_interval = sampling_interval
        self.min_interval = 0.1  # 100ms
        self.max_interval = 5.0  # 5 seconds

        # State management
        self.status = SensorStatus.INITIALIZING
        self.running = False
        self.consecutive_failures = 0
        self.max_failures = 5

        # Change detection
        self.change_detector = ChangeDetector()

        # Statistics
        self.stats = {
            "samples_collected": 0,
            "updates_written": 0,
            "errors": 0,
            "last_sample_time": 0.0,
            "last_update_time": 0.0,
        }

        logger.info(f"{self.__class__.__name__} initialized for {asset_id}")

    @abstractmethod
    def collect(self) -> Dict[str, Any]:
        """
        Collect raw metrics from the asset.

        This method should gather all necessary data from the system
        (via psutil, API calls, etc.) and return it as a dictionary.

        Returns:
            Dictionary of raw metric data

        Raises:
            SensorError: If collection fails
        """
        pass

    @abstractmethod
    def process(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process raw data into .aav format.

        Transform raw metrics into the standardized structure for
        the .aav file section.

        Args:
            raw_data: Raw data from collect()

        Returns:
            Processed data ready for .aav file
        """
        pass

    async def start(self) -> None:
        """
        Start the sensor monitoring loop.

        This runs continuously, sampling metrics and updating the .aav file
        when significant changes are detected.
        """
        logger.info(f"Starting {self.__class__.__name__} for {self.asset_id}")
        self.running = True
        self.status = SensorStatus.HEALTHY

        try:
            await self._monitoring_loop()
        except asyncio.CancelledError:
            logger.info(f"{self.__class__.__name__} cancelled")
        except Exception as e:
            logger.error(f"{self.__class__.__name__} failed: {e}", exc_info=True)
            self.status = SensorStatus.UNHEALTHY
        finally:
            self.running = False
            self.status = SensorStatus.STOPPED

    async def stop(self) -> None:
        """Stop the sensor gracefully."""
        logger.info(f"Stopping {self.__class__.__name__}")
        self.running = False
        self.status = SensorStatus.STOPPED

    async def _monitoring_loop(self) -> None:
        """Main monitoring loop with adaptive sampling."""
        while self.running:
            loop_start = time.time()

            try:
                # Collect metrics
                raw_data = self.collect()
                self.stats["samples_collected"] += 1
                self.stats["last_sample_time"] = time.time()

                # Process into .aav format
                processed_data = self.process(raw_data)

                # Check if update is needed
                if self._should_update(processed_data):
                    await self._update_aav_file(processed_data)
                    self.stats["updates_written"] += 1
                    self.stats["last_update_time"] = time.time()

                # Success - reduce sampling interval (sample faster)
                self._on_success()

            except Exception as e:
                logger.warning(f"{self.__class__.__name__} error: {e}")
                self.stats["errors"] += 1
                self._on_failure()

            # Adaptive sleep
            elapsed = time.time() - loop_start
            sleep_time = max(0, self.sampling_interval - elapsed)
            await asyncio.sleep(sleep_time)

    def _should_update(self, processed_data: Dict[str, Any]) -> bool:
        """
        Determine if .aav file should be updated.

        Uses change detection to minimize unnecessary writes.

        Args:
            processed_data: Processed sensor data

        Returns:
            True if file should be updated
        """
        # Always update on first run
        if self.stats["updates_written"] == 0:
            return True

        # Check each metric for significant change
        for key, value in processed_data.get("real_time", {}).items():
            if self.change_detector.should_update(key, value):
                return True

        # Time-based fallback (update at least every 5 minutes)
        time_since_update = time.time() - self.stats["last_update_time"]
        if time_since_update > 300:  # 5 minutes
            return True

        return False

    async def _update_aav_file(self, processed_data: Dict[str, Any]) -> None:
        """
        Update the .aav file with new data.

        Args:
            processed_data: Processed data to write
        """
        try:
            # Add metadata
            processed_data["last_updated"] = datetime.now(timezone.utc).isoformat() + 'Z'
            processed_data["sensor"] = self.__class__.__name__
            processed_data["sensor_status"] = self.status.value

            # Update section
            self.aav_file.update_section(self.section_name, processed_data)

        except Exception as e:
            raise SensorError(f"Failed to update .aav file: {e}")

    def _on_success(self) -> None:
        """Handle successful sample collection."""
        self.consecutive_failures = 0

        # Gradually decrease sampling interval (sample faster)
        self.sampling_interval = max(
            self.min_interval,
            self.sampling_interval * 0.95
        )

        # Update status
        if self.status == SensorStatus.DEGRADED:
            self.status = SensorStatus.HEALTHY

    def _on_failure(self) -> None:
        """Handle failed sample collection."""
        self.consecutive_failures += 1

        # Increase sampling interval (slow down)
        backoff_factor = 1.5 ** min(self.consecutive_failures, 5)
        self.sampling_interval = min(
            self.max_interval,
            self.sampling_interval * backoff_factor
        )

        # Update status
        if self.consecutive_failures >= self.max_failures:
            self.status = SensorStatus.UNHEALTHY
        elif self.consecutive_failures >= 3:
            self.status = SensorStatus.DEGRADED

    def get_stats(self) -> Dict[str, Any]:
        """
        Get sensor statistics.

        Returns:
            Dictionary of sensor stats
        """
        return {
            **self.stats,
            "status": self.status.value,
            "sampling_interval": self.sampling_interval,
            "consecutive_failures": self.consecutive_failures,
        }

    def reset_stats(self) -> None:
        """Reset sensor statistics."""
        self.stats = {
            "samples_collected": 0,
            "updates_written": 0,
            "errors": 0,
            "last_sample_time": 0.0,
            "last_update_time": 0.0,
        }
