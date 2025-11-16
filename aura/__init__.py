"""
Aura - Universal AI Asset Authority & Real-Time Context System.

Aura provides AI systems with environmental awareness through real-time,
living infrastructure files (.aav) powered by lightweight embedded sensors.

Example:
    >>> from aura import AuraClient
    >>> client = AuraClient()
    >>> context = await client.read_aav("container-payment-api")
    >>> print(context['compute']['cpu_percent'])
    45.2
"""

__version__ = "2.0.0"
__author__ = "Aura Project"
__license__ = "MIT"

from aura.ai.context_client import AuraClient
from aura.core.aav import AAVFile, AAVMetadata
from aura.core.exceptions import (
    AuraError,
    AAVFileError,
    AAVValidationError,
    SensorError,
    GuardianError,
    CacheError,
)

__all__ = [
    "AuraClient",
    "AAVFile",
    "AAVMetadata",
    "AuraError",
    "AAVFileError",
    "AAVValidationError",
    "SensorError",
    "GuardianError",
    "CacheError",
    "__version__",
]
