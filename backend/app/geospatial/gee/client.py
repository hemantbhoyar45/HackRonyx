"""
GEE client — initializes and manages the Earth Engine connection.

Uses service-account credentials read from environment variables.
When GEE_ENABLED is false the application runs in demo mode and no
actual Earth Engine calls are made.
"""

import logging
from typing import Optional

import ee

from app.geospatial.gee.config import GEEConfig, load_gee_config

logger = logging.getLogger(__name__)

# Module-level flag so we only initialise once per process
_initialised: bool = False
_config: Optional[GEEConfig] = None


def get_config() -> GEEConfig:
    """Return the cached GEE configuration."""
    global _config
    if _config is None:
        _config = load_gee_config()
    return _config


def initialize_gee() -> bool:
    """
    Initialize Google Earth Engine.

    Returns True if GEE is ready for use, False if running in demo mode.
    Raises RuntimeError on configuration/auth failure when GEE_ENABLED=true.
    """
    global _initialised

    if _initialised:
        return True

    config = get_config()

    if not config.enabled:
        logger.info("GEE_ENABLED=false — running in demo mode.")
        return False

    if not config.project_id:
        raise RuntimeError("GEE_PROJECT_ID is required when GEE_ENABLED=true.")

    try:
        if config.service_account and config.private_key:
            # Authenticate with service-account key
            credentials = ee.ServiceAccountCredentials(
                config.service_account,
                key_data=config.private_key,
            )
            ee.Initialize(credentials, project=config.project_id)
        else:
            # Fall back to default / ADC credentials
            ee.Initialize(project=config.project_id)

        _initialised = True
        logger.info("Google Earth Engine initialized successfully (project=%s).", config.project_id)
        return True
    except Exception as exc:
        logger.error("Failed to initialize Google Earth Engine: %s", exc)
        raise RuntimeError("Google Earth Engine is not configured correctly.") from exc


def is_gee_ready() -> bool:
    """Return True if GEE has been initialised and is usable."""
    return _initialised
