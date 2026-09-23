import React, { useEffect } from 'react';
import { GeoJSON, useMap } from 'react-leaflet';
import { useAnalysisStore } from '../../store/analysisStore';
import { WATER_BODIES_REGISTRY } from '../../data/waterBodies';
import L from 'leaflet';

export default function WaterBodyLayer() {
  const {
    selectedWaterBody,
    anomalyResult,
    anomalyStatus,
    priorityResult,
    priorityStatus,
    setSelectedZoneResult,
    setSelectedZonePriority,
  } = useAnalysisStore();
  const map = useMap();

  const config = WATER_BODIES_REGISTRY[selectedWaterBody];

  useEffect(() => {
    if (config) {
      if (config.aoi) {
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

  const key = `${selectedWaterBody}-${anomalyStatus}-${priorityStatus}-${JSON.stringify(config.aoi)}`;

  const getStyle = (feature: any) => {
    const defaultStyle = {
      color: '#0ea5e9',
      weight: 2,
      opacity: 0.8,
      fillColor: '#38bdf8',
      fillOpacity: 0.2
    };

    if (priorityStatus === 'done' && priorityResult && priorityResult.results.length > 0) {
      const zoneId = feature.properties?.id || 'zone-main';
      const prioRes = priorityResult.results.find(r => r.zone_id === zoneId) || priorityResult.results[0];

      if (prioRes) {
        switch (prioRes.priority_band) {
          case 'VERY HIGH PRIORITY':
            return { ...defaultStyle, color: '#dc2626', fillColor: '#ef4444', fillOpacity: 0.5 };
          case 'HIGH PRIORITY':
            return { ...defaultStyle, color: '#ea580c', fillColor: '#f97316', fillOpacity: 0.45 };
          case 'MEDIUM PRIORITY':
            return { ...defaultStyle, color: '#d97706', fillColor: '#f59e0b', fillOpacity: 0.35 };
          case 'LOW PRIORITY':
          default:
            return { ...defaultStyle, color: '#0284c7', fillColor: '#38bdf8', fillOpacity: 0.25 };
        }
      }
    }

    if (anomalyStatus === 'done' && anomalyResult) {
      const zoneId = feature.properties?.id || 'zone-main';
      const zoneRes = anomalyResult.results.find(r => r.zone_id === zoneId);
      
      if (zoneRes) {
        if (zoneRes.combined_status === 'POTENTIAL_ANOMALY') {
          return { ...defaultStyle, color: '#f59e0b', fillColor: '#fbbf24', fillOpacity: 0.4 };
        } else if (zoneRes.combined_status === 'MIXED_EVIDENCE') {
          return { ...defaultStyle, color: '#8b5cf6', fillColor: '#a78bfa', fillOpacity: 0.4 };
        } else if (zoneRes.combined_status === 'NO_ANOMALY_SIGNAL') {
          return { ...defaultStyle, color: '#10b981', fillColor: '#34d399', fillOpacity: 0.3 };
        }
      }
    }

    return defaultStyle;
  };

  const onEachFeature = (feature: any, layer: L.Layer) => {
    const zoneId = feature.properties?.id || 'zone-main';

    if (priorityStatus === 'done' && priorityResult && priorityResult.results.length > 0) {
      const prioRes = priorityResult.results.find(r => r.zone_id === zoneId) || priorityResult.results[0];
      if (prioRes) {
        const tooltipContent = `
          <div class="p-1 font-sans text-xs text-slate-100">
            <div class="font-bold border-b border-slate-700 pb-1 mb-1 text-cyan-400 uppercase tracking-wide">
              Zone: ${prioRes.zone_id}
            </div>
            <div><strong>Investigation Priority:</strong> ${Math.round(prioRes.investigation_priority_score)} / 100 (${prioRes.priority_band})</div>
            <div><strong>Confidence:</strong> ${Math.round(prioRes.confidence)}%</div>
            <div><strong>Signal Severity:</strong> ${prioRes.severity}</div>
            <div><strong>Primary Driver:</strong> ${prioRes.primary_driver?.toUpperCase() || 'N/A'}</div>
            <div class="mt-1 text-[10px] text-slate-400 italic">Area showing anomalous satellite-observable signals</div>
          </div>
        `;
        layer.bindTooltip(tooltipContent, { sticky: true, className: 'custom-leaflet-tooltip' });
      }
    }

    layer.on({
      click: () => {
        if (anomalyStatus === 'done' && anomalyResult) {
          const zoneRes = anomalyResult.results.find(r => r.zone_id === zoneId);
          if (zoneRes) setSelectedZoneResult(zoneRes);
        }
        if (priorityStatus === 'done' && priorityResult) {
          const prioRes = priorityResult.results.find(r => r.zone_id === zoneId);
          if (prioRes) setSelectedZonePriority(prioRes);
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
