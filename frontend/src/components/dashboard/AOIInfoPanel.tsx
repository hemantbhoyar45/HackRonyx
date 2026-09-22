import React from 'react';
import { useAnalysisStore } from '../../store/analysisStore';
import { WATER_BODIES_REGISTRY } from '../../data/waterBodies';

export default function AOIInfoPanel() {
  const { selectedWaterBody, customAOI } = useAnalysisStore();
  const config = WATER_BODIES_REGISTRY[selectedWaterBody];

  if (!config) return null;

  const getStatusDisplay = () => {
    if (config.type === 'custom') {
      return customAOI ? "Ready" : "Drawing";
    }
    return config.aoiStatus === 'demo' ? 'Demo Geometry' : 'Validated';
  };

  const getStatusColor = () => {
    if (config.type === 'custom') {
      return customAOI ? "bg-green-100 text-green-700" : "bg-amber-100 text-amber-700";
    }
    return config.aoiStatus === 'demo' ? 'bg-blue-100 text-blue-700' : 'bg-green-100 text-green-700';
  };

  return (
    <div className="bg-white p-5 rounded-xl shadow-sm border border-slate-200">
      <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-4">
        AOI Information
      </h3>
      <div className="space-y-4">
        <div>
          <div className="text-xs text-slate-500 font-semibold mb-1">Selected Water Body</div>
          <div className="text-sm font-bold text-slate-800">{config.name}</div>
        </div>
        
        <div className="grid grid-cols-2 gap-4">
          <div>
            <div className="text-xs text-slate-500 font-semibold mb-1">AOI Type</div>
            <div className="text-sm font-medium text-slate-700 capitalize">
              {config.type.replace('_', ' ')}
            </div>
          </div>
          <div>
            <div className="text-xs text-slate-500 font-semibold mb-1">AOI Status</div>
            <span className={`px-2 py-0.5 rounded text-xs font-semibold ${getStatusColor()}`}>
              {getStatusDisplay()}
            </span>
          </div>
        </div>

        <div>
          <div className="text-xs text-slate-500 font-semibold mb-1">Center Coordinates</div>
          <div className="text-sm font-medium text-slate-700">
            {config.defaultCenter[0].toFixed(4)}, {config.defaultCenter[1].toFixed(4)}
          </div>
        </div>
      </div>
    </div>
  );
}
