import React from 'react';
import { Droplets, CheckCircle2, AlertTriangle } from 'lucide-react';
import type { WaterMaskResult } from '../../../types/analysis';

interface Props {
  data: WaterMaskResult | null;
  status: 'idle' | 'processing' | 'done' | 'error';
}

export function WaterDetectionStatus({ data, status }: Props) {
  if (status === 'idle') return null;

  return (
    <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-5 mt-6">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-2">
          <Droplets className="w-5 h-5 text-blue-600" />
          <h3 className="font-semibold text-slate-900">Water Body Detection</h3>
        </div>
        {status === 'processing' && (
          <span className="flex items-center text-sm text-blue-600 font-medium">
            <div className="w-4 h-4 border-2 border-blue-600 border-t-transparent rounded-full animate-spin mr-2"></div>
            Detecting water...
          </span>
        )}
        {status === 'done' && data?.status === 'success' && (
          <span className="flex items-center text-sm text-emerald-600 font-medium">
            <CheckCircle2 className="w-4 h-4 mr-1" />
            Complete
          </span>
        )}
        {(status === 'error' || data?.status === 'error') && (
          <span className="flex items-center text-sm text-red-600 font-medium">
            <AlertTriangle className="w-4 h-4 mr-1" />
            Error
          </span>
        )}
      </div>

      {status === 'done' && data && data.status === 'success' && (
        <div className="space-y-4">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-slate-50 p-3 rounded-lg border border-slate-100">
              <div className="text-sm text-slate-500 mb-1">Water Area</div>
              <div className="font-semibold text-slate-900">{data.water_area_km2.toFixed(2)} km²</div>
            </div>
            
            <div className="bg-slate-50 p-3 rounded-lg border border-slate-100">
              <div className="text-sm text-slate-500 mb-1">AOI Area</div>
              <div className="font-semibold text-slate-900">{data.aoi_area_km2.toFixed(2)} km²</div>
            </div>
            
            <div className="bg-slate-50 p-3 rounded-lg border border-slate-100">
              <div className="text-sm text-slate-500 mb-1">Water Coverage</div>
              <div className="font-semibold text-slate-900">{data.water_coverage_percentage.toFixed(1)}%</div>
            </div>

            <div className="bg-slate-50 p-3 rounded-lg border border-slate-100">
              <div className="text-sm text-slate-500 mb-1">Method</div>
              <div className="font-semibold text-slate-900 capitalize">
                {data.method.replace('_', ' ')}
              </div>
            </div>
          </div>
          
          <div className="flex flex-wrap gap-2 pt-2 border-t border-slate-100">
            {data.ndwi.available && (
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                NDWI (Threshold: {data.ndwi.threshold?.toFixed(3) || 'Auto'})
              </span>
            )}
            {data.mndwi.available && (
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-indigo-100 text-indigo-800">
                MNDWI (Threshold: {data.mndwi.threshold?.toFixed(3) || 'Auto'})
              </span>
            )}
            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-slate-100 text-slate-800">
              Thresholding: {data.threshold_method}
            </span>
          </div>

          {data.data_source_mode === 'demo' && (
            <div className="mt-3 p-3 bg-amber-50 rounded-lg border border-amber-200">
              <div className="flex">
                <AlertTriangle className="h-5 w-5 text-amber-600 mr-2 flex-shrink-0" />
                <p className="text-sm text-amber-700">
                  <strong>Demo Mode:</strong> Google Earth Engine is not connected. Showing simulated water boundaries for demonstration purposes.
                </p>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
