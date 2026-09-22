"""
Sentinel-2 scene search and metadata retrieval via Google Earth Engine.

This module only performs scene *discovery* — no raster download,
no preprocessing, no water detection.  Those belong to later prompts.
"""

import logging
import uuid
from datetime import date, timedelta
from typing import Any, Dict, List, Optional

import ee

from app.geospatial.gee.client import initialize_gee, is_gee_ready
from app.geospatial.gee.collections import MAX_SCENE_CLOUD_PERCENT, SENTINEL2_COLLECTION
from app.geospatial.gee.geometry import geojson_to_ee_geometry

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Live GEE implementation
# ---------------------------------------------------------------------------

def search_scenes(
    aoi_geojson: Dict[str, Any],
    start_date: date,
    end_date: date,
    max_cloud_pct: float = MAX_SCENE_CLOUD_PERCENT,
) -> Dict[str, Any]:
    """
    Search Sentinel-2 scenes that intersect *aoi_geojson* within the
    given date range, applying scene-level cloud filtering.

    Returns a dict ready for JSON serialisation.
    """
    analysis_id = str(uuid.uuid4())

    if not is_gee_ready():
        # Attempt initialisation on first call
        try:
            ready = initialize_gee()
        except RuntimeError:
            ready = False

        if not ready:
            return _demo_scene_response(aoi_geojson, start_date, end_date, analysis_id)

    try:
        ee_aoi = geojson_to_ee_geometry(aoi_geojson)

        # Earth Engine filterDate end is *exclusive*, so add one day
        # to make the user-facing range inclusive on both ends.
        ee_end = (end_date + timedelta(days=1)).isoformat()

        collection = (
            ee.ImageCollection(SENTINEL2_COLLECTION)
            .filterBounds(ee_aoi)
            .filterDate(start_date.isoformat(), ee_end)
            .filter(ee.Filter.lte("CLOUDY_PIXEL_PERCENTAGE", max_cloud_pct))
        )

        count = collection.size().getInfo()

        scenes: List[Dict[str, Any]] = []
        if count > 0:
            # Pull metadata for up to 100 scenes to avoid large payloads
            image_list = collection.sort("system:time_start").toList(min(count, 100))
            for i in range(min(count, 100)):
                img = ee.Image(image_list.get(i))
                props = img.getInfo().get("properties", {})
                scenes.append(_extract_scene_meta(props))

        logger.info(
            "Scene search complete — analysis_id=%s, scenes=%d, collection=%s",
            analysis_id, count, SENTINEL2_COLLECTION,
        )

        return {
            "analysis_id": analysis_id,
            "status": "scenes_found" if count > 0 else "no_data",
            "data_source_mode": "live",
            "provider": "Google Earth Engine",
            "source": "Sentinel-2",
            "collection": SENTINEL2_COLLECTION,
            "water_body_id": aoi_geojson.get("properties", {}).get("waterBodyId", ""),
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "max_cloud_percent": max_cloud_pct,
            "scene_count": count,
            "scenes": scenes,
            "message": (
                f"Found {count} Sentinel-2 scene(s) matching the criteria."
                if count > 0
                else "No suitable Sentinel-2 scenes were found for the selected AOI and date range."
            ),
        }

    except ValueError as exc:
        # Geometry / validation errors
        raise
    except Exception as exc:
        logger.error("GEE scene search failed: %s", exc)
        raise RuntimeError("Google Earth Engine request failed.") from exc


# ---------------------------------------------------------------------------
# Metadata helpers
# ---------------------------------------------------------------------------

def _extract_scene_meta(props: Dict[str, Any]) -> Dict[str, Any]:
    """Extract serialisable metadata from an EE image property dict."""
    # Sentinel-2 timestamp is in milliseconds since epoch
    timestamp_ms = props.get("system:time_start")
    acq_date = None
    if timestamp_ms is not None:
        from datetime import datetime, timezone
        dt = datetime.fromtimestamp(timestamp_ms / 1000, tz=timezone.utc)
        acq_date = dt.strftime("%Y-%m-%d")

    return {
        "scene_id": props.get("system:index", "unknown"),
        "acquisition_date": acq_date,
        "cloud_percentage": props.get("CLOUDY_PIXEL_PERCENTAGE"),
        "platform": props.get("SPACECRAFT_NAME", props.get("SENSING_ORBIT_DIRECTION", "unknown")),
        "product_id": props.get("PRODUCT_ID"),
        "processing_baseline": props.get("PROCESSING_BASELINE"),
    }


# ---------------------------------------------------------------------------
# Demo / mock fallback
# ---------------------------------------------------------------------------

def _demo_scene_response(
    aoi_geojson: Dict[str, Any],
    start_date: date,
    end_date: date,
    analysis_id: str,
) -> Dict[str, Any]:
    """Return clearly labelled demo data when GEE is not connected."""
    logger.info("Returning demo scene data (GEE not connected).")

    demo_scenes = [
        {
            "scene_id": "DEMO_S2A_20260115T053131_N0400_R005_T44QNF",
            "acquisition_date": "2026-01-15",
            "cloud_percentage": 8.4,
            "platform": "Sentinel-2A",
            "product_id": "DEMO_PRODUCT",
            "processing_baseline": "N/A",
        },
        {
            "scene_id": "DEMO_S2B_20260127T052939_N0400_R005_T44QNF",
            "acquisition_date": "2026-01-27",
            "cloud_percentage": 14.2,
            "platform": "Sentinel-2B",
            "product_id": "DEMO_PRODUCT",
            "processing_baseline": "N/A",
        },
        {
            "scene_id": "DEMO_S2A_20260210T053131_N0400_R005_T44QNF",
            "acquisition_date": "2026-02-10",
            "cloud_percentage": 5.1,
            "platform": "Sentinel-2A",
            "product_id": "DEMO_PRODUCT",
            "processing_baseline": "N/A",
        },
    ]

    water_body_id = ""
    if isinstance(aoi_geojson, dict):
        water_body_id = aoi_geojson.get("properties", {}).get("waterBodyId", "")

    return {
        "analysis_id": analysis_id,
        "status": "scenes_found",
        "data_source_mode": "demo",
        "provider": "Google Earth Engine",
        "source": "Sentinel-2",
        "collection": SENTINEL2_COLLECTION,
        "water_body_id": water_body_id,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "max_cloud_percent": MAX_SCENE_CLOUD_PERCENT,
        "scene_count": len(demo_scenes),
        "scenes": demo_scenes,
        "message": "Demo satellite data — Google Earth Engine is not connected.",
    }
