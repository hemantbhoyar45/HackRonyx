"""
GEE configuration — reads environment variables for Earth Engine setup.

Required environment variables:
  GEE_ENABLED       - "true" to connect to real GEE, "false" for demo mode
  GEE_PROJECT_ID    - Google Cloud project with EE enabled
  GEE_SERVICE_ACCOUNT - service-account email
  GEE_PRIVATE_KEY   - JSON private key (newlines escaped as \\n)
"""

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class GEEConfig:
    enabled: bool
    project_id: str
    service_account: str
    private_key: str


def load_gee_config() -> GEEConfig:
    """Load GEE configuration from environment variables."""
    enabled = os.getenv("GEE_ENABLED", "false").lower() == "true"
    return GEEConfig(
        enabled=enabled,
        project_id=os.getenv("GEE_PROJECT_ID", ""),
        service_account=os.getenv("GEE_SERVICE_ACCOUNT", ""),
        private_key=os.getenv("GEE_PRIVATE_KEY", ""),
    )
