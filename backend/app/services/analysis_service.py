"""
Analysis service — orchestrates the analysis pipeline.

Currently limited to scene discovery (PROMPT 03).
Future prompts will add preprocessing, water detection, spectral
indicators, historical baseline, and anomaly detection.
"""

import logging
from datetime import date
from typing import Any, Dict

from app.geospatial.gee.scenes import search_scenes

logger = logging.getLogger(__name__)


def run_scene_search(
    water_body_id: str,
    water_body_name: str,
    aoi: Dict[str, Any],
    start_date: date,
    end_date: date,
    max_cloud_pct: float | None = None,
) -> Dict[str, Any]:
    """
    Execute a satellite scene search for the given AOI and date range.

    Delegates to the GEE scenes module and enriches the response with
    request-level metadata.
    """
    logger.info(
        "Scene search requested — water_body=%s, dates=%s→%s",
        water_body_id, start_date, end_date,
    )

    kwargs: Dict[str, Any] = {
        "aoi_geojson": aoi,
        "start_date": start_date,
        "end_date": end_date,
    }
    if max_cloud_pct is not None:
        kwargs["max_cloud_pct"] = max_cloud_pct

    result = search_scenes(**kwargs)

    # Ensure water-body info is present even when the GeoJSON properties
    # did not carry it (e.g. custom AOI).
    result["water_body_id"] = water_body_id
    result["water_body_name"] = water_body_name

    return result
