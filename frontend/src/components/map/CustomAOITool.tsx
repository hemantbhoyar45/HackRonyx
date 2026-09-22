import React, { useEffect, useRef } from 'react';
import { FeatureGroup, useMap } from 'react-leaflet';
// @ts-ignore
import { EditControl } from 'react-leaflet-draw';
import L from 'leaflet';
import 'leaflet-draw/dist/leaflet.draw.css';
import { useAnalysisStore } from '../../store/analysisStore';

export default function CustomAOITool() {
  const map = useMap();
  const { selectedWaterBody, setCustomAOI, customAOI } = useAnalysisStore();
  const featureGroupRef = useRef<L.FeatureGroup>(null);

  useEffect(() => {
    // If the tool mounts or unmounts, or customAOI changes externally (e.g. cleared),
    // we should sync it.
    if (!customAOI && featureGroupRef.current) {
      featureGroupRef.current.clearLayers();
    }
  }, [customAOI]);

  const onCreated = (e: any) => {
    const layer = e.layer;
    
    // Convert to GeoJSON
    const geojson = layer.toGeoJSON();
    
    setCustomAOI(geojson);
  };

  const onEdited = (e: any) => {
    const layers = e.layers;
    layers.eachLayer((layer: any) => {
      setCustomAOI(layer.toGeoJSON());
    });
  };

  const onDeleted = () => {
    setCustomAOI(null);
  };

  if (selectedWaterBody !== "custom-aoi") {
    return null;
  }

  return (
    <>
      <div className="absolute top-4 left-1/2 -translate-x-1/2 z-[1000] bg-white/90 backdrop-blur-sm px-4 py-2 rounded shadow text-sm font-semibold text-slate-700 border border-slate-200">
        Draw a polygon on the map to define the analysis area.
      </div>
      <FeatureGroup ref={featureGroupRef}>
        <EditControl
          position="topright"
          onCreated={onCreated}
          onEdited={onEdited}
          onDeleted={onDeleted}
          draw={{
            rectangle: true,
            polygon: true,
            circle: false,
            circlemarker: false,
            marker: false,
            polyline: false,
          }}
        />
      </FeatureGroup>
    </>
  );
}
