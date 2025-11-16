"""
Redis Cache Implementation.

Provides sub-millisecond queries for AI agents by caching .aav file
contents in Redis.

Features:
- Sub-millisecond read latency
- Automatic TTL management
- Batch operations (mget/mset)
- Cache invalidation
- Connection pooling
"""

import json
import logging
from typing import Any, Dict, List, Optional

from aura.core.exceptions import CacheError

logger = logging.getLogger(__name__)


class RedisCache:
    """
    Redis-based cache for AAV files.

    Provides high-performance caching with automatic TTL management
    and batch operations.

    Example:
        >>> cache = RedisCache("redis://localhost:6379")
        >>> await cache.set("my-asset", {"cpu_percent": 45.2})
        >>> data = await cache.get("my-asset")  # <0.5ms
        >>> print(data['cpu_percent'])
        45.2
    """

    def __init__(
        self,
        redis_url: str,
        default_ttl: int = 300,
        key_prefix: str = "aura:aav:",
    ) -> None:
        """
        Initialize Redis cache.

        Args:
            redis_url: Redis connection URL
            default_ttl: Default TTL in seconds (default: 5 minutes)
            key_prefix: Prefix for all cache keys
        """
        self.redis_url = redis_url
        self.default_ttl = default_ttl
        self.key_prefix = key_prefix

        # Import redis here to make it optional dependency
        try:
            import redis.asyncio as aioredis
            self._redis_module = aioredis
        except ImportError:
            raise CacheError(
                "Redis not installed. Install with: pip install redis"
            )

        self.client: Optional[Any] = None

        logger.info(f"RedisCache initialized (url: {redis_url}, ttl: {default_ttl}s)")

    async def connect(self) -> None:
        """Establish Redis connection."""
        if self.client is not None:
            return

        try:
            self.client = await self._redis_module.from_url(
                self.redis_url,
                decode_responses=True,
                encoding="utf-8",
            )

            # Test connection
            await self.client.ping()

            logger.info("Connected to Redis successfully")

        except Exception as e:
            raise CacheError(f"Failed to connect to Redis: {e}")

    async def get(self, asset_id: str) -> Optional[Dict[str, Any]]:
        """
        Get cached AAV data.

        Args:
            asset_id: Asset identifier

        Returns:
            Cached data or None if not found
        """
        if self.client is None:
            await self.connect()

        try:
            key = f"{self.key_prefix}{asset_id}"
            cached = await self.client.get(key)

            if cached is None:
                return None

            # Deserialize JSON
            return json.loads(cached)

        except Exception as e:
            logger.error(f"Cache get failed for {asset_id}: {e}")
            return None

    async def set(
        self,
        asset_id: str,
        data: Dict[str, Any],
        ttl: Optional[int] = None
    ) -> bool:
        """
        Set cached AAV data.

        Args:
            asset_id: Asset identifier
            data: AAV data to cache
            ttl: TTL in seconds (uses default if not specified)

        Returns:
            True if successful
        """
        if self.client is None:
            await self.connect()

        try:
            key = f"{self.key_prefix}{asset_id}"

            # Serialize to JSON
            serialized = json.dumps(data)

            # Set with TTL
            await self.client.set(
                key,
                serialized,
                ex=ttl or self.default_ttl
            )

            return True

        except Exception as e:
            logger.error(f"Cache set failed for {asset_id}: {e}")
            return False

    async def mget(self, asset_ids: List[str]) -> List[Optional[Dict[str, Any]]]:
        """
        Get multiple cached AAV files.

        Args:
            asset_ids: List of asset identifiers

        Returns:
            List of cached data (None for cache misses)
        """
        if self.client is None:
            await self.connect()

        try:
            keys = [f"{self.key_prefix}{asset_id}" for asset_id in asset_ids]
            cached_list = await self.client.mget(keys)

            results = []
            for cached in cached_list:
                if cached is None:
                    results.append(None)
                else:
                    results.append(json.loads(cached))

            return results

        except Exception as e:
            logger.error(f"Cache mget failed: {e}")
            return [None] * len(asset_ids)

    async def invalidate(self, asset_id: str) -> bool:
        """
        Invalidate cached data.

        Args:
            asset_id: Asset identifier

        Returns:
            True if successful
        """
        if self.client is None:
            await self.connect()

        try:
            key = f"{self.key_prefix}{asset_id}"
            await self.client.delete(key)
            return True

        except Exception as e:
            logger.error(f"Cache invalidate failed for {asset_id}: {e}")
            return False

    async def invalidate_pattern(self, pattern: str) -> int:
        """
        Invalidate all keys matching pattern.

        Args:
            pattern: Pattern to match (e.g., "container-*")

        Returns:
            Number of keys invalidated
        """
        if self.client is None:
            await self.connect()

        try:
            search_pattern = f"{self.key_prefix}{pattern}"

            # Scan for matching keys
            keys = []
            async for key in self.client.scan_iter(match=search_pattern):
                keys.append(key)

            if keys:
                await self.client.delete(*keys)

            return len(keys)

        except Exception as e:
            logger.error(f"Cache pattern invalidate failed: {e}")
            return 0

    async def flush_all(self) -> bool:
        """
        Flush all Aura cache data.

        Returns:
            True if successful
        """
        return await self.invalidate_pattern("*") > 0

    async def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Statistics dictionary
        """
        if self.client is None:
            await self.connect()

        try:
            info = await self.client.info("stats")

            return {
                "total_connections": info.get("total_connections_received", 0),
                "total_commands": info.get("total_commands_processed", 0),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
                "hit_rate": self._calculate_hit_rate(info),
            }

        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            return {}

    def _calculate_hit_rate(self, info: Dict[str, Any]) -> float:
        """Calculate cache hit rate."""
        hits = info.get("keyspace_hits", 0)
        misses = info.get("keyspace_misses", 0)
        total = hits + misses

        if total == 0:
            return 0.0

        return (hits / total) * 100

    async def close(self) -> None:
        """Close Redis connection."""
        if self.client:
            await self.client.close()
            self.client = None
            logger.info("Redis connection closed")
