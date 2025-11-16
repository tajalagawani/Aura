"""
AAV File Validator.

This module validates .aav files for:
- File existence and readability
- TOML syntax correctness
- Required section presence
- Data structure validity
- Freshness (recent updates)
- Sensor health status
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

import toml

from aura.core.aav import AAVFile
from aura.core.exceptions import AAVValidationError

logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Result of AAV file validation."""

    valid: bool
    file_path: Path
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    validation_time: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __str__(self) -> str:
        """String representation."""
        status = "✅ VALID" if self.valid else "❌ INVALID"
        result = [f"{status}: {self.file_path}"]

        if self.errors:
            result.append(f"  Errors ({len(self.errors)}):")
            for error in self.errors:
                result.append(f"    - {error}")

        if self.warnings:
            result.append(f"  Warnings ({len(self.warnings)}):")
            for warning in self.warnings:
                result.append(f"    - {warning}")

        return "\n".join(result)


class AAVValidator:
    """
    Comprehensive AAV file validator.

    Performs multiple validation checks:
    1. File exists and is readable
    2. Valid TOML syntax
    3. Required sections present
    4. Data structure validity
    5. Freshness check (not stale)
    6. Sensor health validation

    Example:
        >>> validator = AAVValidator()
        >>> result = validator.validate(Path("/assets/my-asset.aav"))
        >>> if not result.valid:
        ...     print(result.errors)
    """

    REQUIRED_SECTIONS = ["metadata", "asset", "compute", "memory", "storage", "network", "services"]
    MAX_AGE_SECONDS = 300  # 5 minutes

    def __init__(self, max_age_seconds: int = MAX_AGE_SECONDS) -> None:
        """
        Initialize validator.

        Args:
            max_age_seconds: Maximum age before file is considered stale
        """
        self.max_age_seconds = max_age_seconds

    def validate(self, file_path: Path | str) -> ValidationResult:
        """
        Validate an AAV file.

        Args:
            file_path: Path to AAV file

        Returns:
            ValidationResult with errors and warnings
        """
        file_path = Path(file_path)
        result = ValidationResult(valid=True, file_path=file_path)

        # Check 1: File exists and readable
        if not self._validate_file_exists(file_path, result):
            return result  # Can't continue if file doesn't exist

        # Check 2: Valid TOML syntax
        data = self._validate_toml_syntax(file_path, result)
        if data is None:
            return result  # Can't continue if TOML is invalid

        # Check 3: Required sections
        self._validate_required_sections(data, result)

        # Check 4: Metadata structure
        self._validate_metadata(data, result)

        # Check 5: Asset information
        self._validate_asset_info(data, result)

        # Check 6: Freshness
        self._validate_freshness(data, result)

        # Check 7: Sensor sections
        self._validate_sensor_sections(data, result)

        # Check 8: Sensor health
        self._validate_sensor_health(data, result)

        return result

    def _validate_file_exists(self, file_path: Path, result: ValidationResult) -> bool:
        """Check if file exists and is readable."""
        if not file_path.exists():
            result.valid = False
            result.errors.append(f"File does not exist: {file_path}")
            return False

        if not file_path.is_file():
            result.valid = False
            result.errors.append(f"Path is not a file: {file_path}")
            return False

        try:
            with open(file_path, 'r') as f:
                f.read(1)  # Try to read one byte
        except PermissionError:
            result.valid = False
            result.errors.append("Permission denied reading file")
            return False
        except Exception as e:
            result.valid = False
            result.errors.append(f"Cannot read file: {e}")
            return False

        return True

    def _validate_toml_syntax(
        self,
        file_path: Path,
        result: ValidationResult
    ) -> Dict[str, Any] | None:
        """Validate TOML syntax."""
        try:
            with open(file_path, 'r') as f:
                data = toml.load(f)
            return data

        except toml.TomlDecodeError as e:
            result.valid = False
            result.errors.append(f"Invalid TOML syntax: {e}")
            return None
        except Exception as e:
            result.valid = False
            result.errors.append(f"Failed to parse file: {e}")
            return None

    def _validate_required_sections(self, data: Dict[str, Any], result: ValidationResult) -> None:
        """Check all required sections are present."""
        missing = [section for section in self.REQUIRED_SECTIONS if section not in data]

        if missing:
            result.valid = False
            result.errors.append(f"Missing required sections: {', '.join(missing)}")

    def _validate_metadata(self, data: Dict[str, Any], result: ValidationResult) -> None:
        """Validate metadata section."""
        if 'metadata' not in data:
            return

        metadata = data['metadata']

        # Check required metadata fields
        required_fields = ['format_version', 'asset_id', 'last_updated']
        missing = [field for field in required_fields if field not in metadata]

        if missing:
            result.valid = False
            result.errors.append(f"Missing metadata fields: {', '.join(missing)}")

        # Validate format version
        if 'format_version' in metadata:
            version = metadata['format_version']
            if not version.startswith('2.'):
                result.warnings.append(f"Unexpected format version: {version}")

    def _validate_asset_info(self, data: Dict[str, Any], result: ValidationResult) -> None:
        """Validate asset section."""
        if 'asset' not in data:
            return

        asset = data['asset']

        # Check required asset fields
        required_fields = ['id', 'type', 'status']
        missing = [field for field in required_fields if field not in asset]

        if missing:
            result.valid = False
            result.errors.append(f"Missing asset fields: {', '.join(missing)}")

        # Validate asset type
        if 'type' in asset:
            valid_types = ['container', 'vm', 'pod', 'machine', 'database', 'service']
            if asset['type'] not in valid_types:
                result.warnings.append(f"Unknown asset type: {asset['type']}")

    def _validate_freshness(self, data: Dict[str, Any], result: ValidationResult) -> None:
        """Check if file is fresh (recently updated)."""
        if 'metadata' not in data or 'last_updated' not in data['metadata']:
            return

        try:
            last_updated_str = data['metadata']['last_updated']

            # Parse timestamp
            if last_updated_str.endswith('Z'):
                last_updated_str = last_updated_str[:-1] + '+00:00'
            last_updated = datetime.fromisoformat(last_updated_str)

            # Calculate age
            now = datetime.now(timezone.utc)
            age_seconds = (now - last_updated).total_seconds()

            if age_seconds > self.max_age_seconds:
                result.warnings.append(
                    f"File is stale (age: {age_seconds:.0f}s, max: {self.max_age_seconds}s)"
                )

        except Exception as e:
            result.warnings.append(f"Could not validate freshness: {e}")

    def _validate_sensor_sections(self, data: Dict[str, Any], result: ValidationResult) -> None:
        """Validate sensor sections."""
        sensor_sections = ['compute', 'memory', 'storage', 'network', 'services']

        for section in sensor_sections:
            if section not in data:
                continue

            section_data = data[section]

            # Check required sensor fields
            if 'last_updated' not in section_data:
                result.warnings.append(f"Section '{section}' missing last_updated")

            if 'sensor_status' not in section_data:
                result.warnings.append(f"Section '{section}' missing sensor_status")

    def _validate_sensor_health(self, data: Dict[str, Any], result: ValidationResult) -> None:
        """Check sensor health status."""
        sensor_sections = ['compute', 'memory', 'storage', 'network', 'services']

        for section in sensor_sections:
            if section not in data:
                continue

            section_data = data[section]

            if 'sensor_status' in section_data:
                status = section_data['sensor_status']

                if status == 'unhealthy':
                    result.warnings.append(f"Sensor '{section}' is unhealthy")
                elif status == 'degraded':
                    result.warnings.append(f"Sensor '{section}' is degraded")
                elif status not in ['healthy', 'initializing', 'stopped']:
                    result.warnings.append(f"Unknown sensor status for '{section}': {status}")

    def validate_batch(self, file_paths: List[Path | str]) -> List[ValidationResult]:
        """
        Validate multiple AAV files.

        Args:
            file_paths: List of paths to validate

        Returns:
            List of ValidationResults
        """
        results = []

        for file_path in file_paths:
            result = self.validate(file_path)
            results.append(result)

        return results

    def get_summary(self, results: List[ValidationResult]) -> Dict[str, Any]:
        """
        Get summary of validation results.

        Args:
            results: List of ValidationResults

        Returns:
            Summary dictionary
        """
        total = len(results)
        valid = sum(1 for r in results if r.valid)
        invalid = total - valid

        total_errors = sum(len(r.errors) for r in results)
        total_warnings = sum(len(r.warnings) for r in results)

        return {
            "total_files": total,
            "valid": valid,
            "invalid": invalid,
            "total_errors": total_errors,
            "total_warnings": total_warnings,
            "validation_rate": (valid / total * 100) if total > 0 else 0,
        }
