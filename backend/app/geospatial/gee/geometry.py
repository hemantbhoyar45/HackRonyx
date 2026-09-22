"""
GeoJSON → Earth Engine geometry conversion.

GeoJSON coordinate order: [longitude, latitude]
Earth Engine expects the same order, so NO reversal is needed.

Supports Polygon and MultiPolygon geometry types.
"""

import logging
from typing import Any, Dict

import ee
from shapely.geometry import shape as shapely_shape
from shapely.validation import explain_validity

logger = logging.getLogger(__name__)


def validate_geojson(geojson: Dict[str, Any]) -> None:
    """
    Validate a GeoJSON Feature or plain geometry dict.

    Raises ValueError with a human-readable message on failure.
    """
    if geojson is None:
        raise ValueError("AOI geometry is missing.")

    # Accept both a Feature and a raw geometry
    geom = geojson.get("geometry", geojson)

    geom_type = geom.get("type")
    if geom_type not in ("Polygon", "MultiPolygon"):
        raise ValueError(
            f"Unsupported geometry type '{geom_type}'. Only Polygon and MultiPolygon are supported."
        )

    coordinates = geom.get("coordinates")
    if not coordinates:
        raise ValueError("AOI geometry has no coordinates.")

    # Use Shapely for structural validation
    try:
        shp = shapely_shape(geom)
    except Exception as exc:
        raise ValueError(f"Invalid AOI geometry: {exc}") from exc

    if shp.is_empty:
        raise ValueError("AOI geometry is empty.")

    if not shp.is_valid:
        reason = explain_validity(shp)
        raise ValueError(f"AOI geometry is invalid: {reason}")

    # Basic coordinate-range sanity check (WGS-84)
    minx, miny, maxx, maxy = shp.bounds
    if minx < -180 or maxx > 180 or miny < -90 or maxy > 90:
        raise ValueError("AOI coordinates are outside valid WGS-84 range.")


def geojson_to_ee_geometry(geojson: Dict[str, Any]) -> ee.Geometry:
    """
    Convert a GeoJSON Feature or Geometry dict to an ee.Geometry.

    Validates the geometry first, then builds the Earth Engine object.
    """
    validate_geojson(geojson)

    # Extract the raw geometry dict (handles both Feature and plain Geometry)
    geom = geojson.get("geometry", geojson)
    geom_type = geom["type"]
    coordinates = geom["coordinates"]

    if geom_type == "Polygon":
        return ee.Geometry.Polygon(coordinates)
    elif geom_type == "MultiPolygon":
        return ee.Geometry.MultiPolygon(coordinates)
    else:
        # Should never reach here because validate_geojson checks type
        raise ValueError(f"Unsupported geometry type: {geom_type}")
