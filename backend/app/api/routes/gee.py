"""
GEE health / status route.
"""

from fastapi import APIRouter

from app.geospatial.gee.client import get_config, is_gee_ready, initialize_gee

router = APIRouter()


@router.get("/health")
def gee_health():
    """
    Check whether Google Earth Engine is configured and reachable.

    Never exposes credentials or internal stack traces.
    """
    config = get_config()

    if not config.enabled:
        return {
            "status": "unavailable",
            "provider": "Google Earth Engine",
            "data_source_mode": "demo",
            "message": "GEE is disabled (GEE_ENABLED=false). Running in demo mode.",
        }

    if is_gee_ready():
        return {
            "status": "connected",
            "provider": "Google Earth Engine",
            "data_source_mode": "live",
        }

    # Not yet initialised — try now
    try:
        initialize_gee()
        return {
            "status": "connected",
            "provider": "Google Earth Engine",
            "data_source_mode": "live",
        }
    except RuntimeError:
        return {
            "status": "unavailable",
            "provider": "Google Earth Engine",
            "data_source_mode": "demo",
            "message": "GEE configuration is missing or unavailable.",
        }
