import React from 'react';
import { GeoJSON } from 'react-leaflet';
import { useAnalysisStore } from '../../store/analysisStore';

export function WaterMaskLayer() {
  const result = useAnalysisStore(state => state.waterMaskResult);
  
  if (!result || !result.geometry || !result.geometry.features || result.geometry.features.length === 0) {
    return null;
  }
  
  // Style for the water mask - distinct from AOI boundary
  // Solid blue fill, thin blue border
  const maskStyle = {
    color: '#2563eb', // blue-600
    weight: 1,
    opacity: 0.8,
    fillColor: '#3b82f6', // blue-500
    fillOpacity: 0.5,
  };
  
  return (
    <GeoJSON 
      key={`water-mask-${result.scene_id}`} 
      data={result.geometry} 
      style={maskStyle} 
    />
  );
}
