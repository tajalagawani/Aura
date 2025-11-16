"""
Custom exceptions for Aura.

This module defines all custom exceptions used throughout the Aura system.
All exceptions inherit from AuraError for easy catching.
"""


class AuraError(Exception):
    """Base exception for all Aura errors."""

    pass


class AAVFileError(AuraError):
    """Raised when AAV file operations fail."""

    pass


class AAVValidationError(AuraError):
    """Raised when AAV file validation fails."""

    pass


class SensorError(AuraError):
    """Raised when sensor operations fail."""

    pass


class GuardianError(AuraError):
    """Raised when Guardian operations fail."""

    pass


class CacheError(AuraError):
    """Raised when cache operations fail."""

    pass


class ScannerError(AuraError):
    """Raised when scanner operations fail."""

    pass


class InstrumentationError(AuraError):
    """Raised when instrumentation fails."""

    pass
