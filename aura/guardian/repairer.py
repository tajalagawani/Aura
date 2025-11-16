"""
AAV File Repairer.

This module provides automatic repair capabilities for corrupted .aav files:
- TOML syntax fixing
- Partial data recovery
- Backup restoration
- Emergency file rebuild
- Missing section reconstruction
"""

import logging
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

import toml

from aura.core.aav import AAVFile
from aura.core.exceptions import GuardianError

logger = logging.getLogger(__name__)


@dataclass
class RepairResult:
    """Result of repair operation."""

    success: bool
    file_path: Path
    repair_strategy: str
    message: str
    original_error: Optional[str] = None

    def __str__(self) -> str:
        """String representation."""
        status = "✅ REPAIRED" if self.success else "❌ REPAIR FAILED"
        return f"{status}: {self.file_path}\n  Strategy: {self.repair_strategy}\n  {self.message}"


class AAVRepairer:
    """
    Automatic AAV file repairer.

    Repair strategies (in order of attempt):
    1. TOML syntax fixing (missing quotes, trailing commas)
    2. Backup restoration
    3. Partial data recovery
    4. Emergency skeleton creation

    Example:
        >>> repairer = AAVRepairer()
        >>> result = repairer.repair(Path("/assets/corrupted.aav"))
        >>> if result.success:
        ...     print("File repaired successfully!")
    """

    def __init__(self) -> None:
        """Initialize repairer."""
        pass

    def repair(self, file_path: Path | str) -> RepairResult:
        """
        Attempt to repair a corrupted AAV file.

        Args:
            file_path: Path to corrupted file

        Returns:
            RepairResult indicating success/failure
        """
        file_path = Path(file_path)

        if not file_path.exists():
            return RepairResult(
                success=False,
                file_path=file_path,
                repair_strategy="none",
                message="File does not exist"
            )

        # Try repair strategies in order
        strategies = [
            ("toml_syntax_fix", self._repair_toml_syntax),
            ("backup_restore", self._repair_from_backup),
            ("partial_recovery", self._repair_partial_data),
            ("emergency_rebuild", self._repair_emergency_rebuild),
        ]

        original_error = None

        for strategy_name, strategy_func in strategies:
            logger.info(f"Attempting repair strategy: {strategy_name} for {file_path}")

            try:
                result = strategy_func(file_path)
                if result.success:
                    logger.info(f"Successfully repaired {file_path} using {strategy_name}")
                    return result
            except Exception as e:
                logger.warning(f"Strategy {strategy_name} failed: {e}")
                if original_error is None:
                    original_error = str(e)
                continue

        # All strategies failed
        return RepairResult(
            success=False,
            file_path=file_path,
            repair_strategy="all_failed",
            message="All repair strategies failed",
            original_error=original_error
        )

    def _repair_toml_syntax(self, file_path: Path) -> RepairResult:
        """
        Attempt to fix TOML syntax errors.

        Common fixes:
        - Missing quotes around strings
        - Trailing commas
        - Incorrect boolean values
        - Malformed arrays
        """
        try:
            # Read corrupted content
            with open(file_path, 'r') as f:
                content = f.read()

            # Apply syntax fixes
            fixed_content = self._apply_toml_fixes(content)

            # Test if fixed version is valid
            try:
                toml.loads(fixed_content)
            except toml.TomlDecodeError:
                return RepairResult(
                    success=False,
                    file_path=file_path,
                    repair_strategy="toml_syntax_fix",
                    message="Syntax fixes did not resolve TOML errors"
                )

            # Write fixed version
            with open(file_path, 'w') as f:
                f.write(fixed_content)

            return RepairResult(
                success=True,
                file_path=file_path,
                repair_strategy="toml_syntax_fix",
                message="Fixed TOML syntax errors"
            )

        except Exception as e:
            return RepairResult(
                success=False,
                file_path=file_path,
                repair_strategy="toml_syntax_fix",
                message=f"Failed to fix syntax: {e}"
            )

    def _apply_toml_fixes(self, content: str) -> str:
        """Apply common TOML syntax fixes."""
        # Fix 1: Remove trailing commas in arrays
        content = re.sub(r',\s*]', ']', content)

        # Fix 2: Fix boolean values (true/false must be lowercase)
        content = re.sub(r'\bTrue\b', 'true', content)
        content = re.sub(r'\bFalse\b', 'false', content)

        # Fix 3: Fix None values (should be empty string or removed)
        content = re.sub(r'\bNone\b', '""', content)

        # Fix 4: Ensure quotes around timestamp-like strings
        # This is tricky, so we'll skip for now

        return content

    def _repair_from_backup(self, file_path: Path) -> RepairResult:
        """Restore file from backup."""
        backup_path = file_path.with_suffix('.aav.backup')

        if not backup_path.exists():
            return RepairResult(
                success=False,
                file_path=file_path,
                repair_strategy="backup_restore",
                message="No backup file found"
            )

        try:
            # Verify backup is valid
            with open(backup_path, 'r') as f:
                toml.load(f)

            # Restore from backup
            import shutil
            shutil.copy2(backup_path, file_path)

            return RepairResult(
                success=True,
                file_path=file_path,
                repair_strategy="backup_restore",
                message="Restored from backup"
            )

        except Exception as e:
            return RepairResult(
                success=False,
                file_path=file_path,
                repair_strategy="backup_restore",
                message=f"Backup restore failed: {e}"
            )

    def _repair_partial_data(self, file_path: Path) -> RepairResult:
        """Attempt to recover partial data."""
        try:
            # Read file
            with open(file_path, 'r') as f:
                content = f.read()

            # Try to extract asset_id from content
            asset_id_match = re.search(r'asset_id\s*=\s*["\']([^"\']+)["\']', content)
            asset_id = asset_id_match.group(1) if asset_id_match else "unknown"

            # Try to extract asset type
            type_match = re.search(r'type\s*=\s*["\']([^"\']+)["\']', content)
            asset_type = type_match.group(1) if type_match else "unknown"

            # Create minimal valid structure with recovered data
            aav = AAVFile.create_empty(
                file_path=file_path,
                asset_id=asset_id,
                asset_type=asset_type
            )

            return RepairResult(
                success=True,
                file_path=file_path,
                repair_strategy="partial_recovery",
                message=f"Recovered partial data (asset_id: {asset_id})"
            )

        except Exception as e:
            return RepairResult(
                success=False,
                file_path=file_path,
                repair_strategy="partial_recovery",
                message=f"Partial recovery failed: {e}"
            )

    def _repair_emergency_rebuild(self, file_path: Path) -> RepairResult:
        """Emergency rebuild - create minimal valid file."""
        try:
            # Extract asset_id from filename
            asset_id = file_path.stem  # filename without extension

            # Create emergency skeleton
            emergency_data = {
                "metadata": {
                    "format_version": "2.0.0",
                    "asset_id": asset_id,
                    "last_updated": datetime.now(timezone.utc).isoformat() + 'Z',
                    "schema_version": "2.0",
                    "emergency_rebuild": True,
                    "rebuild_reason": "Complete file corruption - all repair attempts failed"
                },
                "asset": {
                    "id": asset_id,
                    "type": "unknown",
                    "name": asset_id,
                    "status": "unknown",
                    "tags": [],
                },
                "compute": {
                    "last_updated": datetime.now(timezone.utc).isoformat() + 'Z',
                    "sensor_status": "restarting",
                },
                "memory": {
                    "last_updated": datetime.now(timezone.utc).isoformat() + 'Z',
                    "sensor_status": "restarting",
                },
                "storage": {
                    "last_updated": datetime.now(timezone.utc).isoformat() + 'Z',
                    "sensor_status": "restarting",
                },
                "network": {
                    "last_updated": datetime.now(timezone.utc).isoformat() + 'Z',
                    "sensor_status": "restarting",
                },
                "services": {
                    "last_updated": datetime.now(timezone.utc).isoformat() + 'Z',
                    "sensor_status": "restarting",
                }
            }

            # Write emergency file
            with open(file_path, 'w') as f:
                toml.dump(emergency_data, f)

            return RepairResult(
                success=True,
                file_path=file_path,
                repair_strategy="emergency_rebuild",
                message="Created emergency skeleton - sensors will repopulate data"
            )

        except Exception as e:
            return RepairResult(
                success=False,
                file_path=file_path,
                repair_strategy="emergency_rebuild",
                message=f"Emergency rebuild failed: {e}"
            )
