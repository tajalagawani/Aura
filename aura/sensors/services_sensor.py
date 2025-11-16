"""
Services Sensor - Application Health and API Monitoring.

This sensor monitors:
- Application health status
- API endpoint response times
- Error rates
- Service uptime
- Dependency health
- Version information

Updates .aav file when health status changes or response time doubles.
"""

import logging
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import psutil

from aura.sensors.base import BaseSensor
from aura.core.exceptions import SensorError

logger = logging.getLogger(__name__)


class ServicesSensor(BaseSensor):
    """
    Sensor for application and service monitoring.

    Monitors application health, API performance, and dependencies.

    Example:
        >>> sensor = ServicesSensor(
        ...     asset_id="container-api",
        ...     aav_file_path="/assets/container-api.aav",
        ...     health_check_url="http://localhost:8080/health"
        ... )
        >>> await sensor.start()

    .aav Output:
        [services]
        last_updated = "2025-11-16T15:30:45.300Z"
        sensor = "ServicesSensor"
        sensor_status = "healthy"

        [services.application]
        health_status = "healthy"
        version = "3.2.2"
        uptime_seconds = 86400

        [[services.api_endpoints.monitored]]
        path = "/api/v1/payments"
        method = "POST"
        avg_response_time_ms = 45
        requests_per_minute = 1250
        error_rate_percent = 0.02

        [[services.dependencies]]
        name = "postgres-db"
        status = "healthy"
        response_time_ms = 15
    """

    def __init__(
        self,
        asset_id: str,
        aav_file_path: str,
        health_check_url: Optional[str] = None,
        health_check_port: Optional[int] = None,
        monitored_endpoints: Optional[List[str]] = None,
        dependencies: Optional[List[Dict[str, str]]] = None,
    ) -> None:
        """
        Initialize Services Sensor.

        Args:
            asset_id: Unique asset identifier
            aav_file_path: Path to .aav file
            health_check_url: URL for health check endpoint
            health_check_port: Port to check for service availability
            monitored_endpoints: List of API endpoints to monitor
            dependencies: List of dependencies to check
        """
        super().__init__(
            asset_id=asset_id,
            aav_file_path=aav_file_path,
            section_name="services",
            sampling_interval=5.0,  # Sample every 5 seconds
        )

        self.health_check_url = health_check_url
        self.health_check_port = health_check_port
        self.monitored_endpoints = monitored_endpoints or []
        self.dependencies = dependencies or []

        # Track uptime
        self.start_time = time.time()

        logger.info(f"ServicesSensor initialized for {asset_id}")

    def collect(self) -> Dict[str, Any]:
        """
        Collect service health metrics.

        Returns:
            Dictionary with service metrics

        Raises:
            SensorError: If collection fails
        """
        try:
            # Application health
            health_status = self._check_health()
            version = self._get_version()
            uptime = time.time() - self.start_time

            # Check dependencies
            dependency_status = self._check_dependencies()

            # Get endpoint metrics (if available)
            endpoint_metrics = self._get_endpoint_metrics()

            return {
                "health_status": health_status,
                "version": version,
                "uptime_seconds": uptime,
                "dependencies": dependency_status,
                "endpoint_metrics": endpoint_metrics,
            }

        except Exception as e:
            raise SensorError(f"Failed to collect service metrics: {e}")

    def process(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process raw service data into .aav format.

        Args:
            raw_data: Raw data from collect()

        Returns:
            Processed data for .aav file
        """
        # Build .aav structure
        processed = {
            "update_strategy": "change_driven",
            "application": {
                "health_status": raw_data["health_status"],
                "version": raw_data["version"],
                "uptime_seconds": round(raw_data["uptime_seconds"], 2),
            }
        }

        # Add dependencies if available
        if raw_data["dependencies"]:
            processed["dependencies"] = raw_data["dependencies"]

        # Add endpoint metrics if available
        if raw_data["endpoint_metrics"]:
            processed["api_endpoints"] = {
                "monitored": raw_data["endpoint_metrics"]
            }

        # Add last significant change if health status changed
        if self.change_detector.should_update("health_status", raw_data["health_status"]):
            processed["application"]["last_significant_change"] = \
                datetime.now(timezone.utc).isoformat() + 'Z'

        return processed

    def _check_health(self) -> str:
        """
        Check application health.

        Returns:
            "healthy", "degraded", or "unhealthy"
        """
        # If health check URL provided, use HTTP check
        if self.health_check_url:
            return self._http_health_check()

        # If port provided, check if port is listening
        if self.health_check_port:
            return self._port_health_check()

        # Default: assume healthy
        return "healthy"

    def _http_health_check(self) -> str:
        """
        Perform HTTP health check.

        Returns:
            Health status
        """
        try:
            import urllib.request
            import urllib.error

            req = urllib.request.Request(
                self.health_check_url,
                headers={'User-Agent': 'Aura/2.0'}
            )

            with urllib.request.urlopen(req, timeout=5) as response:
                status_code = response.getcode()

                if status_code == 200:
                    return "healthy"
                elif 200 <= status_code < 300:
                    return "healthy"
                elif 500 <= status_code < 600:
                    return "unhealthy"
                else:
                    return "degraded"

        except urllib.error.URLError:
            return "unhealthy"
        except Exception as e:
            logger.warning(f"Health check failed: {e}")
            return "unknown"

    def _port_health_check(self) -> str:
        """
        Check if port is listening.

        Returns:
            Health status
        """
        try:
            connections = psutil.net_connections(kind='inet')

            # Check if any connection is listening on the port
            listening = any(
                conn.status == 'LISTEN' and conn.laddr.port == self.health_check_port
                for conn in connections
            )

            return "healthy" if listening else "unhealthy"

        except Exception as e:
            logger.warning(f"Port check failed: {e}")
            return "unknown"

    def _get_version(self) -> str:
        """
        Get application version.

        In a real implementation, this would read from environment variables,
        version file, or API endpoint.

        Returns:
            Version string
        """
        import os
        return os.environ.get('APP_VERSION', 'unknown')

    def _check_dependencies(self) -> List[Dict[str, Any]]:
        """
        Check health of dependencies.

        Returns:
            List of dependency statuses
        """
        dependency_status = []

        for dep in self.dependencies:
            status = self._check_dependency(dep)
            dependency_status.append(status)

        return dependency_status

    def _check_dependency(self, dependency: Dict[str, str]) -> Dict[str, Any]:
        """
        Check a single dependency.

        Args:
            dependency: Dependency configuration

        Returns:
            Dependency status
        """
        name = dependency.get('name', 'unknown')
        check_type = dependency.get('type', 'http')
        target = dependency.get('target')

        if check_type == 'http' and target:
            # HTTP check
            try:
                import urllib.request
                import urllib.error

                start = time.time()
                req = urllib.request.Request(target, headers={'User-Agent': 'Aura/2.0'})

                with urllib.request.urlopen(req, timeout=5) as response:
                    response_time = (time.time() - start) * 1000  # ms
                    status_code = response.getcode()

                    return {
                        "name": name,
                        "status": "healthy" if status_code == 200 else "degraded",
                        "response_time_ms": round(response_time, 2),
                    }

            except Exception:
                return {
                    "name": name,
                    "status": "unhealthy",
                    "response_time_ms": 0,
                }

        # Unknown check type
        return {
            "name": name,
            "status": "unknown",
            "response_time_ms": 0,
        }

    def _get_endpoint_metrics(self) -> List[Dict[str, Any]]:
        """
        Get metrics for monitored endpoints.

        In a real implementation, this would aggregate metrics from
        application instrumentation (e.g., Prometheus, StatsD).

        Returns:
            List of endpoint metrics
        """
        # Placeholder - in production, this would read from metrics store
        return []

    def get_service_status(self) -> str:
        """
        Get current service status.

        Returns:
            "healthy", "degraded", or "unhealthy"
        """
        return self._check_health()
