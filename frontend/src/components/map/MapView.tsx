import React from 'react';
import { MapContainer, TileLayer } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';

// Fix leaflet icon issue in React
import L from 'leaflet';
import icon from 'leaflet/dist/images/marker-icon.png';
import iconShadow from 'leaflet/dist/images/marker-shadow.png';
import WaterBodyLayer from './WaterBodyLayer';
import CustomAOITool from './CustomAOITool';
import { WaterMaskLayer } from './WaterMaskLayer';
import { useAnalysisStore } from '../../store/analysisStore';

let DefaultIcon = L.icon({
    iconUrl: icon,
    shadowUrl: iconShadow
});
L.Marker.prototype.options.icon = DefaultIcon;

export default function MapView() {
  const { customAOI, selectedWaterBody } = useAnalysisStore();

  return (
    <div className="w-full h-full rounded-lg overflow-hidden border border-slate-300 shadow-sm relative z-0">
      <MapContainer 
        center={[20.87, 79.62]} // Approx Gosikhurd
        zoom={11} 
        style={{ height: '100%', width: '100%' }}
        zoomControl={true}
      >
        {/* Using a standard reliable basemap. In production, maybe use Esri Satellite or Mapbox */}
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        <WaterBodyLayer />
        <CustomAOITool />
        <WaterMaskLayer />
        {/* Placeholders for future AOILayer, HotspotLayer etc. */}
      </MapContainer>
      
      {/* Overlay Mock Badge */}
      <div className="absolute bottom-4 left-4 z-[1000] bg-white/90 backdrop-blur-sm px-3 py-1.5 rounded shadow text-xs font-semibold text-slate-700 border border-slate-200">
        Demo Map View (Mock Data)
      </div>
    </div>
  );
}
