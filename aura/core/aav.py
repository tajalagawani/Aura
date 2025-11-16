"""
AAV (AI Authority Vector) File System.

This module handles reading, writing, and validating .aav files - the core
data structure that represents computational asset state.

.aav files are TOML-formatted, human-readable files that contain:
- Metadata (format version, timestamps)
- Asset information (id, type, status)
- Real-time metrics from 5 sensors (compute, memory, storage, network, services)

Example .aav file structure:
    [metadata]
    format_version = "2.0.0"
    asset_id = "container-payment-api"
    last_updated = "2025-11-16T15:30:45.123Z"

    [asset]
    id = "container-payment-api"
    type = "container"
    status = "running"

    [compute]
    cpu_percent = 45.2
    load_average = 1.23
    ...
"""

import fcntl
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

import toml
from pydantic import BaseModel, Field, validator

from aura.core.exceptions import AAVFileError, AAVValidationError


class AAVMetadata(BaseModel):
    """Metadata for AAV files."""

    format_version: str = Field(default="2.0.0", description="AAV format version")
    asset_id: str = Field(..., description="Unique asset identifier")
    last_updated: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Last update timestamp"
    )
    schema_version: str = Field(default="2.0", description="Schema version")

    @validator("last_updated", pre=True)
    def parse_datetime(cls, v: Any) -> datetime:
        """Parse datetime from string or datetime object."""
        if isinstance(v, datetime):
            return v
        if isinstance(v, str):
            # Handle ISO format with 'Z' suffix
            if v.endswith('Z'):
                v = v[:-1] + '+00:00'
            return datetime.fromisoformat(v)
        return v

    class Config:
        """Pydantic config."""
        json_encoders = {
            datetime: lambda v: v.isoformat().replace('+00:00', 'Z')
        }


class AssetInfo(BaseModel):
    """Asset information section."""

    id: str = Field(..., description="Asset ID")
    type: str = Field(..., description="Asset type (container, vm, pod, etc)")
    name: Optional[str] = Field(None, description="Human-readable name")
    status: str = Field(default="unknown", description="Asset status")
    tags: list[str] = Field(default_factory=list, description="Asset tags")
    environment: Optional[str] = Field(None, description="Environment (prod, dev, etc)")


class AAVFile:
    """
    AAV File handler for reading, writing, and validating .aav files.

    This class provides atomic file operations with built-in validation,
    locking, and backup mechanisms to ensure data integrity.

    Example:
        >>> aav = AAVFile("/assets/container-api.aav")
        >>> data = aav.read()
        >>> print(data['compute']['cpu_percent'])
        45.2

        >>> aav.update_section('compute', {'cpu_percent': 50.5})
        >>> aav.write(data)
    """

    REQUIRED_SECTIONS = ["metadata", "asset", "compute", "memory", "storage", "network", "services"]

    def __init__(self, file_path: str | Path) -> None:
        """
        Initialize AAV file handler.

        Args:
            file_path: Path to the .aav file
        """
        self.file_path = Path(file_path)
        self.backup_path = self.file_path.with_suffix(".aav.backup")

    def read(self) -> Dict[str, Any]:
        """
        Read and parse AAV file.

        Returns:
            Dictionary containing AAV file data

        Raises:
            AAVFileError: If file cannot be read or parsed
        """
        if not self.file_path.exists():
            raise AAVFileError(f"AAV file not found: {self.file_path}")

        try:
            with open(self.file_path, 'r') as f:
                # Acquire shared lock for reading
                fcntl.flock(f.fileno(), fcntl.LOCK_SH)
                try:
                    data = toml.load(f)
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)

            return data

        except toml.TomlDecodeError as e:
            raise AAVFileError(f"Invalid TOML in {self.file_path}: {e}")
        except Exception as e:
            raise AAVFileError(f"Failed to read {self.file_path}: {e}")

    def write(self, data: Dict[str, Any], create_backup: bool = True) -> None:
        """
        Write data to AAV file atomically.

        Uses atomic write pattern: write to temp file, then rename.
        This ensures the file is never in a corrupted state.

        Args:
            data: Dictionary to write
            create_backup: Whether to create backup before writing

        Raises:
            AAVFileError: If write fails
        """
        try:
            # Validate before writing
            self.validate(data)

            # Create backup if file exists
            if create_backup and self.file_path.exists():
                self._create_backup()

            # Update last_updated timestamp
            if 'metadata' not in data:
                data['metadata'] = {}
            # Use ISO format with Z suffix (remove +00:00 and add Z)
            timestamp = datetime.now(timezone.utc).isoformat()
            if timestamp.endswith('+00:00'):
                timestamp = timestamp[:-6] + 'Z'
            data['metadata']['last_updated'] = timestamp

            # Atomic write: write to temp, then rename
            temp_path = self.file_path.with_suffix('.tmp')

            with open(temp_path, 'w') as f:
                # Acquire exclusive lock
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    toml.dump(data, f)
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)

            # Atomic rename (POSIX guarantees atomicity)
            temp_path.replace(self.file_path)

        except Exception as e:
            # Clean up temp file if it exists
            temp_path = self.file_path.with_suffix('.tmp')
            if temp_path.exists():
                temp_path.unlink()
            raise AAVFileError(f"Failed to write {self.file_path}: {e}")

    def update_section(self, section: str, data: Dict[str, Any]) -> None:
        """
        Update a specific section of the AAV file.

        This performs a read-modify-write operation atomically.

        Args:
            section: Section name (e.g., 'compute', 'memory')
            data: Data to merge into the section

        Raises:
            AAVFileError: If update fails
        """
        try:
            # Read current data
            current = self.read() if self.file_path.exists() else {}

            # Merge section data
            if section not in current:
                current[section] = {}
            current[section].update(data)

            # Write back atomically
            self.write(current)

        except Exception as e:
            raise AAVFileError(f"Failed to update section {section}: {e}")

    def validate(self, data: Dict[str, Any]) -> bool:
        """
        Validate AAV file structure and content.

        Args:
            data: Data to validate

        Returns:
            True if valid

        Raises:
            AAVValidationError: If validation fails
        """
        # Check required sections exist
        missing_sections = [s for s in self.REQUIRED_SECTIONS if s not in data]
        if missing_sections:
            raise AAVValidationError(f"Missing required sections: {missing_sections}")

        # Validate metadata
        try:
            AAVMetadata(**data['metadata'])
        except Exception as e:
            raise AAVValidationError(f"Invalid metadata: {e}")

        # Validate asset info
        try:
            AssetInfo(**data['asset'])
        except Exception as e:
            raise AAVValidationError(f"Invalid asset info: {e}")

        # Validate each sensor section has required fields
        sensor_sections = ['compute', 'memory', 'storage', 'network', 'services']
        for section in sensor_sections:
            if section in data:
                if 'last_updated' not in data[section]:
                    raise AAVValidationError(f"Section {section} missing last_updated")
                if 'sensor_status' not in data[section]:
                    raise AAVValidationError(f"Section {section} missing sensor_status")

        return True

    def _create_backup(self) -> None:
        """Create backup of current file."""
        try:
            if self.file_path.exists():
                import shutil
                shutil.copy2(self.file_path, self.backup_path)
        except Exception as e:
            # Backup failure shouldn't prevent writes
            import logging
            logging.warning(f"Failed to create backup: {e}")

    def restore_from_backup(self) -> bool:
        """
        Restore AAV file from backup.

        Returns:
            True if restored successfully, False if no backup exists
        """
        if not self.backup_path.exists():
            return False

        try:
            import shutil
            shutil.copy2(self.backup_path, self.file_path)
            return True
        except Exception as e:
            raise AAVFileError(f"Failed to restore from backup: {e}")

    @staticmethod
    def create_empty(
        file_path: str | Path,
        asset_id: str,
        asset_type: str,
        asset_name: Optional[str] = None
    ) -> "AAVFile":
        """
        Create a new empty AAV file with minimal structure.

        Args:
            file_path: Path for the new file
            asset_id: Unique asset identifier
            asset_type: Type of asset (container, vm, pod, etc)
            asset_name: Optional human-readable name

        Returns:
            AAVFile instance
        """
        aav = AAVFile(file_path)

        # Generate consistent timestamp format
        now = datetime.now(timezone.utc)
        timestamp = now.isoformat()
        if timestamp.endswith('+00:00'):
            timestamp = timestamp[:-6] + 'Z'

        # Create minimal valid structure
        data = {
            "metadata": {
                "format_version": "2.0.0",
                "asset_id": asset_id,
                "last_updated": timestamp,
                "schema_version": "2.0",
            },
            "asset": {
                "id": asset_id,
                "type": asset_type,
                "name": asset_name or asset_id,
                "status": "unknown",
                "tags": [],
            },
            "compute": {
                "last_updated": timestamp,
                "sensor_status": "initializing",
            },
            "memory": {
                "last_updated": timestamp,
                "sensor_status": "initializing",
            },
            "storage": {
                "last_updated": timestamp,
                "sensor_status": "initializing",
            },
            "network": {
                "last_updated": timestamp,
                "sensor_status": "initializing",
            },
            "services": {
                "last_updated": timestamp,
                "sensor_status": "initializing",
            },
        }

        aav.write(data, create_backup=False)
        return aav

    def to_dict(self) -> Dict[str, Any]:
        """
        Read and return file contents as dictionary.

        Returns:
            Dictionary of file contents
        """
        return self.read()

    def to_json(self) -> str:
        """
        Export AAV file as JSON string.

        Returns:
            JSON string representation
        """
        data = self.read()
        return json.dumps(data, indent=2, default=str)

    def get_age_seconds(self) -> float:
        """
        Get age of the AAV file in seconds.

        Returns time since last_updated timestamp.

        Returns:
            Age in seconds
        """
        data = self.read()
        last_updated_str = data['metadata']['last_updated']

        # Parse timestamp
        if last_updated_str.endswith('Z'):
            last_updated_str = last_updated_str[:-1] + '+00:00'
        last_updated = datetime.fromisoformat(last_updated_str)

        now = datetime.now(timezone.utc)
        age = (now - last_updated).total_seconds()

        return age

    def is_fresh(self, max_age_seconds: int = 300) -> bool:
        """
        Check if AAV file is fresh (recently updated).

        Args:
            max_age_seconds: Maximum age in seconds (default: 5 minutes)

        Returns:
            True if file is fresh
        """
        try:
            age = self.get_age_seconds()
            return age <= max_age_seconds
        except Exception:
            return False
