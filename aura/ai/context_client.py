"""
Aura Client SDK for AI Agents.

This module provides a simple, high-performance client for AI agents
to query infrastructure context from Aura.

Features:
- Sub-millisecond queries via Redis cache
- Simple async API
- Filtering and aggregation
- Real-time subscriptions (future)
- Batch operations

Example:
    >>> client = AuraClient(cache_enabled=True)
    >>> context = await client.read_aav("container-payment-api")
    >>> if context['compute']['cpu_percent'] < 70:
    ...     print("Safe to deploy!")
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from aura.core.aav import AAVFile
from aura.core.exceptions import AuraError

logger = logging.getLogger(__name__)


class AuraClient:
    """
    High-performance client for AI agents to query Aura context.

    This client provides optimized access to .aav files with optional
    Redis caching for sub-millisecond queries.

    Example:
        >>> # Simple file-based access
        >>> client = AuraClient(assets_dir="/assets")
        >>> context = await client.read_aav("my-service")
        >>> print(context['compute']['cpu_percent'])
        45.2

        >>> # With caching (recommended for AI agents)
        >>> client = AuraClient(
        ...     assets_dir="/assets",
        ...     cache_enabled=True,
        ...     redis_url="redis://localhost:6379"
        ... )
        >>> context = await client.read_aav("my-service")  # <1ms from cache
    """

    def __init__(
        self,
        assets_dir: str | Path = "/assets",
        cache_enabled: bool = False,
        redis_url: Optional[str] = None,
    ) -> None:
        """
        Initialize Aura client.

        Args:
            assets_dir: Directory containing .aav files
            cache_enabled: Enable Redis caching
            redis_url: Redis connection URL (required if cache_enabled)
        """
        self.assets_dir = Path(assets_dir)
        self.cache_enabled = cache_enabled

        # Initialize cache if enabled
        self.cache = None
        if cache_enabled:
            if not redis_url:
                raise AuraError("redis_url required when cache_enabled=True")

            from aura.cache.redis_cache import RedisCache
            self.cache = RedisCache(redis_url)

        logger.info(f"AuraClient initialized (cache: {cache_enabled})")

    async def read_aav(self, asset_id: str) -> Dict[str, Any]:
        """
        Read AAV file for an asset.

        Args:
            asset_id: Asset identifier

        Returns:
            Dictionary of AAV file contents

        Raises:
            AuraError: If file not found or read fails
        """
        # Try cache first
        if self.cache:
            cached = await self.cache.get(asset_id)
            if cached:
                logger.debug(f"Cache hit for {asset_id}")
                return cached

        # Cache miss or cache disabled - read from file
        aav_file = AAVFile(self.assets_dir / f"{asset_id}.aav")

        try:
            data = aav_file.read()

            # Populate cache
            if self.cache:
                await self.cache.set(asset_id, data)

            return data

        except Exception as e:
            raise AuraError(f"Failed to read AAV for {asset_id}: {e}")

    async def read_multiple(self, asset_ids: List[str]) -> List[Dict[str, Any]]:
        """
        Read multiple AAV files efficiently.

        Args:
            asset_ids: List of asset identifiers

        Returns:
            List of AAV file contents
        """
        # Use batch operation if cache enabled
        if self.cache:
            results = await self.cache.mget(asset_ids)

            # Fill in cache misses from files
            for i, (asset_id, data) in enumerate(zip(asset_ids, results)):
                if data is None:
                    results[i] = await self.read_aav(asset_id)

            return results

        # No cache - read all from files
        results = []
        for asset_id in asset_ids:
            try:
                data = await self.read_aav(asset_id)
                results.append(data)
            except Exception as e:
                logger.warning(f"Failed to read {asset_id}: {e}")
                results.append(None)

        return results

    async def query_assets(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Query assets with filters.

        Args:
            filters: Filter criteria (e.g., {"compute.cpu_percent": {">": 80}})

        Returns:
            List of matching assets

        Example:
            >>> # Find high CPU assets
            >>> results = await client.query_assets({
            ...     "compute.real_time.cpu_percent": {">": 80}
            ... })

            >>> # Find unhealthy services
            >>> results = await client.query_assets({
            ...     "services.application.health_status": "unhealthy"
            ... })
        """
        # Get all asset files
        all_assets = list(self.assets_dir.glob("*.aav"))

        matching = []

        for asset_file in all_assets:
            try:
                asset_id = asset_file.stem
                data = await self.read_aav(asset_id)

                if self._matches_filters(data, filters):
                    matching.append(data)

            except Exception as e:
                logger.warning(f"Error querying {asset_file}: {e}")
                continue

        return matching

    def _matches_filters(self, data: Dict[str, Any], filters: Dict[str, Any]) -> bool:
        """Check if data matches filter criteria."""
        for key, criteria in filters.items():
            # Navigate nested keys (e.g., "compute.real_time.cpu_percent")
            value = self._get_nested_value(data, key)

            if value is None:
                return False

            # Handle different filter types
            if isinstance(criteria, dict):
                # Comparison operators
                for op, target in criteria.items():
                    if op == ">":
                        if not (value > target):
                            return False
                    elif op == ">=":
                        if not (value >= target):
                            return False
                    elif op == "<":
                        if not (value < target):
                            return False
                    elif op == "<=":
                        if not (value <= target):
                            return False
                    elif op == "==":
                        if not (value == target):
                            return False
                    elif op == "!=":
                        if not (value != target):
                            return False
            else:
                # Direct equality check
                if value != criteria:
                    return False

        return True

    def _get_nested_value(self, data: Dict[str, Any], key: str) -> Any:
        """Get value from nested dictionary using dot notation."""
        keys = key.split('.')
        value = data

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return None

        return value

    async def find_unhealthy(self) -> List[Dict[str, Any]]:
        """
        Find all unhealthy assets.

        Returns:
            List of unhealthy assets
        """
        return await self.query_assets({
            "services.application.health_status": "unhealthy"
        })

    async def find_high_cpu(self, threshold: float = 80.0) -> List[Dict[str, Any]]:
        """
        Find assets with high CPU usage.

        Args:
            threshold: CPU percentage threshold

        Returns:
            List of high-CPU assets
        """
        return await self.query_assets({
            "compute.real_time.cpu_percent": {">": threshold}
        })

    async def find_high_memory(self, threshold: float = 80.0) -> List[Dict[str, Any]]:
        """
        Find assets with high memory usage.

        Args:
            threshold: Memory percentage threshold

        Returns:
            List of high-memory assets
        """
        return await self.query_assets({
            "memory.real_time.usage_percent": {">": threshold}
        })

    async def find_low_disk(self, threshold: float = 90.0) -> List[Dict[str, Any]]:
        """
        Find assets with low disk space.

        Args:
            threshold: Disk usage percentage threshold

        Returns:
            List of low-disk assets
        """
        return await self.query_assets({
            "storage.real_time.disk_usage_percent": {">": threshold}
        })

    async def get_health_summary(self) -> Dict[str, Any]:
        """
        Get infrastructure-wide health summary.

        Returns:
            Health summary dictionary
        """
        all_assets = list(self.assets_dir.glob("*.aav"))

        summary = {
            "total_assets": len(all_assets),
            "healthy": 0,
            "unhealthy": 0,
            "degraded": 0,
            "unknown": 0,
            "high_cpu": 0,
            "high_memory": 0,
            "low_disk": 0,
        }

        for asset_file in all_assets:
            try:
                asset_id = asset_file.stem
                data = await self.read_aav(asset_id)

                # Health status
                health = data.get("services", {}).get("application", {}).get("health_status", "unknown")
                summary[health] = summary.get(health, 0) + 1

                # Resource alerts
                cpu = data.get("compute", {}).get("real_time", {}).get("cpu_percent", 0)
                if cpu > 80:
                    summary["high_cpu"] += 1

                memory = data.get("memory", {}).get("real_time", {}).get("usage_percent", 0)
                if memory > 80:
                    summary["high_memory"] += 1

                disk = data.get("storage", {}).get("real_time", {}).get("disk_usage_percent", 0)
                if disk > 90:
                    summary["low_disk"] += 1

            except Exception as e:
                logger.warning(f"Error processing {asset_file}: {e}")
                continue

        return summary

    async def is_safe_to_deploy(self, asset_id: str) -> Dict[str, Any]:
        """
        Check if it's safe to deploy to an asset.

        Args:
            asset_id: Asset identifier

        Returns:
            Safety check result with recommendation
        """
        context = await self.read_aav(asset_id)

        checks = {
            "cpu_healthy": context.get("compute", {}).get("real_time", {}).get("cpu_percent", 100) < 70,
            "memory_healthy": context.get("memory", {}).get("real_time", {}).get("usage_percent", 100) < 80,
            "disk_healthy": context.get("storage", {}).get("real_time", {}).get("disk_usage_percent", 100) < 85,
            "service_healthy": context.get("services", {}).get("application", {}).get("health_status") == "healthy",
        }

        all_healthy = all(checks.values())

        return {
            "safe": all_healthy,
            "asset_id": asset_id,
            "checks": checks,
            "recommendation": "✅ Safe to deploy" if all_healthy else "⚠️  Wait - issues detected",
            "context": context,
        }

    async def close(self) -> None:
        """Close client and cleanup resources."""
        if self.cache:
            await self.cache.close()
