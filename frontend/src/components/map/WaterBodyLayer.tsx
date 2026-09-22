import React, { useEffect } from 'react';
import { GeoJSON, useMap } from 'react-leaflet';
import { useAnalysisStore } from '../../../store/analysisStore';
import { WATER_BODIES_REGISTRY } from '../../../data/waterBodies';
import L from 'leaflet';

export default function WaterBodyLayer() {
  const { selectedWaterBody } = useAnalysisStore();
  const map = useMap();

  const config = WATER_BODIES_REGISTRY[selectedWaterBody];

  useEffect(() => {
    if (config) {
      if (config.aoi) {
        // Create a temporary geojson layer to get bounds
        const tempLayer = L.geoJSON(config.aoi);
        const bounds = tempLayer.getBounds();
        if (bounds.isValid()) {
          map.fitBounds(bounds, { padding: [50, 50], maxZoom: 13 });
        } else {
          map.setView(config.defaultCenter as [number, number], config.defaultZoom);
        }
      } else {
        map.setView(config.defaultCenter as [number, number], config.defaultZoom);
      }
    }
  }, [selectedWaterBody, map, config]);

  if (!config || !config.aoi || config.type === 'custom') {
    return null;
  }

  // Generate a key to force re-render when switching geometries
  const key = `${selectedWaterBody}-${JSON.stringify(config.aoi)}`;

  return (
    <GeoJSON 
      key={key}
      data={config.aoi as any}
      style={() => ({
        color: '#0ea5e9',
        weight: 2,
        opacity: 0.8,
        fillColor: '#38bdf8',
        fillOpacity: 0.2
      })}
    />
  );
}
