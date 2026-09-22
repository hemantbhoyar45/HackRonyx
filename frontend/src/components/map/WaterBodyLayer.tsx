import React, { useEffect } from 'react';
import { GeoJSON, useMap } from 'react-leaflet';
import { useAnalysisStore } from '../../store/analysisStore';
import { WATER_BODIES_REGISTRY } from '../../data/waterBodies';
import L from 'leaflet';

export default function WaterBodyLayer() {
  const { selectedWaterBody, anomalyResult, anomalyStatus, setSelectedZoneResult } = useAnalysisStore();
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

  // Generate a key to force re-render when switching geometries or when anomaly status changes
  const key = `${selectedWaterBody}-${anomalyStatus}-${JSON.stringify(config.aoi)}`;

  const getStyle = (feature: any) => {
    const defaultStyle = {
      color: '#0ea5e9',
      weight: 2,
      opacity: 0.8,
      fillColor: '#38bdf8',
      fillOpacity: 0.2
    };

    if (anomalyStatus !== 'done' || !anomalyResult) {
      return defaultStyle;
    }

    // In a real app we'd map feature.properties.id to zone_id.
    // For this prompt MVP, we assume the whole AOI is 'zone-main'.
    const zoneId = feature.properties?.id || 'zone-main';
    const zoneRes = anomalyResult.results.find(r => r.zone_id === zoneId);
    
    if (zoneRes) {
      if (zoneRes.combined_status === 'POTENTIAL_ANOMALY') {
        return { ...defaultStyle, color: '#f59e0b', fillColor: '#fbbf24', fillOpacity: 0.4 }; // Amber
      } else if (zoneRes.combined_status === 'MIXED_EVIDENCE') {
        return { ...defaultStyle, color: '#8b5cf6', fillColor: '#a78bfa', fillOpacity: 0.4 }; // Purple
      } else if (zoneRes.combined_status === 'NO_ANOMALY_SIGNAL') {
        return { ...defaultStyle, color: '#10b981', fillColor: '#34d399', fillOpacity: 0.3 }; // Emerald
      }
    }

    return defaultStyle;
  };

  const onEachFeature = (feature: any, layer: L.Layer) => {
    layer.on({
      click: () => {
        if (anomalyStatus === 'done' && anomalyResult) {
          const zoneId = feature.properties?.id || 'zone-main';
          const zoneRes = anomalyResult.results.find(r => r.zone_id === zoneId);
          if (zoneRes) {
            setSelectedZoneResult(zoneRes);
          }
        }
      }
    });
  };

  return (
    <GeoJSON 
      key={key}
      data={config.aoi as any}
      style={getStyle}
      onEachFeature={onEachFeature}
    />
  );
}
