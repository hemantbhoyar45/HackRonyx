import React, { useState } from 'react';
import { Activity, CheckCircle2, AlertTriangle, Map, ChevronDown, ChevronUp, Info } from 'lucide-react';
import type { IndicatorsResponse, IndicatorResult } from '../../../types/analysis';

interface Props {
  data: IndicatorsResponse | null;
  status: 'idle' | 'processing' | 'done' | 'error';
  onLayerToggle?: (layerId: string | null) => void;
  activeLayer?: string | null;
}

const INDICATOR_META: Record<string, { label: string; description: string; color: string; interpretation: string }> = {
  ndti: {
    label: 'Turbidity-Related Indicator',
    description: 'NDTI — (B4 − B3) / (B4 + B3)',
    color: 'amber',
    interpretation: 'Reflects differences in the Red/Green spectral ratio. Higher values may indicate increased particulate matter in the water column. Not a direct turbidity measurement.'
  },
  suspended_sediment: {
    label: 'Suspended Sediment Proxy',
    description: 'NDSS — (B4 − B2) / (B4 + B2)',
    color: 'orange',
    interpretation: 'A normalized Red/Blue proxy. Higher values may indicate elevated suspended particles. Not calibrated to laboratory concentration.'
  },
  ndci: {
    label: 'Chlorophyll-Related Indicator',
    description: 'NDCI — (B5 − B4) / (B5 + B4)',
    color: 'green',
    interpretation: 'Exploits the red-edge spectral region. Higher values may correlate with increased phytoplankton activity. Not a direct chlorophyll measurement.'
  },
  fai: {
    label: 'Algal Activity-Related Indicator',
    description: 'FAI — NIR Baseline Residual',
    color: 'emerald',
    interpretation: 'Computes NIR departure from the expected baseline between Red and SWIR. Positive anomalies may indicate floating algal matter. Not a confirmed algal bloom detection.'
  }
};

function StatBadge({ label, value, colorClass }: { label: string; value: string; colorClass: string }) {
  return (
    <div className={`flex flex-col items-center bg-${colorClass}-50 border border-${colorClass}-100 rounded-lg px-3 py-2 min-w-[80px]`}>
      <span className={`text-xs font-medium text-${colorClass}-600 mb-0.5`}>{label}</span>
      <span className={`text-sm font-bold text-${colorClass}-900`}>{value}</span>
    </div>
  );
}

function IndicatorCard({ id, result, isExpanded, onToggle, onMapLayer, isActiveLayer }: {
  id: string;
  result: IndicatorResult;
  isExpanded: boolean;
  onToggle: () => void;
  onMapLayer: () => void;
  isActiveLayer: boolean;
}) {
  const meta = INDICATOR_META[id] || {
    label: result.indicator_type,
    description: result.formula,
    color: 'blue',
    interpretation: 'Satellite-derived spectral proxy.'
  };

  const colorMap: Record<string, string> = {
    amber: 'bg-amber-500',
    orange: 'bg-orange-500',
    green: 'bg-green-600',
    emerald: 'bg-emerald-600',
    blue: 'bg-blue-600'
  };

  const bgDot = colorMap[meta.color] || 'bg-blue-600';
  const st = result.statistics;

  return (
    <div className={`border rounded-xl overflow-hidden transition-all duration-200 ${isActiveLayer ? 'border-blue-400 shadow-md shadow-blue-100' : 'border-slate-200'}`}>
      {/* Card Header */}
      <div
        className="flex items-center justify-between px-4 py-3 bg-white cursor-pointer hover:bg-slate-50 transition-colors"
        onClick={onToggle}
      >
        <div className="flex items-center gap-3">
          <span className={`w-3 h-3 rounded-full flex-shrink-0 ${bgDot}`} />
          <div>
            <div className="text-sm font-semibold text-slate-800">{meta.label}</div>
            <div className="text-xs text-slate-400 font-mono mt-0.5">{meta.description}</div>
          </div>
        </div>
        <div className="flex items-center gap-3">
          {/* Median pill */}
          <div className="text-right mr-2">
            <div className="text-xs text-slate-400">Median</div>
            <div className="text-sm font-bold text-slate-700">{st.median.toFixed(4)}</div>
          </div>
          {/* Map toggle */}
          <button
            onClick={e => { e.stopPropagation(); onMapLayer(); }}
            title={isActiveLayer ? 'Showing on map' : 'Show on map'}
            className={`p-1.5 rounded-md transition-colors ${isActiveLayer ? 'bg-blue-100 text-blue-600' : 'text-slate-400 hover:text-blue-500 hover:bg-blue-50'}`}
          >
            <Map className="w-4 h-4" />
          </button>
          {isExpanded ? <ChevronUp className="w-4 h-4 text-slate-400" /> : <ChevronDown className="w-4 h-4 text-slate-400" />}
        </div>
      </div>

      {/* Expanded Body */}
      {isExpanded && (
        <div className="px-4 pb-4 pt-2 bg-slate-50 border-t border-slate-100 space-y-4">
          {/* Stats row */}
          <div className="flex flex-wrap gap-2">
            <StatBadge label="Mean" value={st.mean.toFixed(4)} colorClass={meta.color} />
            <StatBadge label="Median" value={st.median.toFixed(4)} colorClass={meta.color} />
            <StatBadge label="Std Dev" value={st.std.toFixed(4)} colorClass={meta.color} />
            <StatBadge label="Min" value={st.min.toFixed(4)} colorClass={meta.color} />
            <StatBadge label="Max" value={st.max.toFixed(4)} colorClass={meta.color} />
          </div>
          {/* Percentiles */}
          <div>
            <div className="text-xs font-medium text-slate-500 mb-1.5">Percentile Distribution</div>
            <div className="flex gap-2 text-xs text-slate-600">
              <span className="bg-white border border-slate-200 rounded px-2 py-1">P10: {st.percentile_10.toFixed(3)}</span>
              <span className="bg-white border border-slate-200 rounded px-2 py-1">P25: {st.percentile_25.toFixed(3)}</span>
              <span className="bg-white border border-slate-200 rounded px-2 py-1">P75: {st.percentile_75.toFixed(3)}</span>
              <span className="bg-white border border-slate-200 rounded px-2 py-1">P90: {st.percentile_90.toFixed(3)}</span>
            </div>
          </div>
          {/* Metadata & interpretation */}
          <div className="flex items-start gap-2 bg-white border border-slate-200 rounded-lg p-3">
            <Info className="w-4 h-4 text-slate-400 flex-shrink-0 mt-0.5" />
            <p className="text-xs text-slate-500 leading-relaxed">{meta.interpretation}</p>
          </div>
          <div className="flex gap-2 text-xs">
            <span className="bg-slate-100 text-slate-600 rounded-full px-2 py-0.5">Bands: {result.bands_used.join(', ')}</span>
            <span className="bg-slate-100 text-slate-600 rounded-full px-2 py-0.5">Valid: {st.valid_pixel_count.toLocaleString()} px</span>
            <span className="bg-yellow-100 text-yellow-700 rounded-full px-2 py-0.5 capitalize">{result.calibration_status.replace('_', ' ')}</span>
          </div>
        </div>
      )}
    </div>
  );
}

export function SpectralIndicatorsPanel({ data, status, onLayerToggle, activeLayer }: Props) {
  const [expanded, setExpanded] = useState<string | null>(null);

  if (status === 'idle') return null;

  const toggle = (id: string) => setExpanded(prev => prev === id ? null : id);

  const INDICATOR_ORDER = ['ndti', 'suspended_sediment', 'ndci', 'fai'];

  return (
    <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-5 mt-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-2">
          <Activity className="w-5 h-5 text-purple-600" />
          <h3 className="font-semibold text-slate-900">Spectral Indicators</h3>
        </div>
        {status === 'processing' && (
          <span className="flex items-center text-sm text-purple-600 font-medium">
            <div className="w-4 h-4 border-2 border-purple-600 border-t-transparent rounded-full animate-spin mr-2" />
            Calculating...
          </span>
        )}
        {status === 'done' && data?.status === 'success' && (
          <span className="flex items-center text-sm text-emerald-600 font-medium">
            <CheckCircle2 className="w-4 h-4 mr-1" />Complete
          </span>
        )}
        {status === 'error' && (
          <span className="flex items-center text-sm text-red-600 font-medium">
            <AlertTriangle className="w-4 h-4 mr-1" />Error
          </span>
        )}
      </div>

      {/* Scientific disclaimer */}
      <div className="mb-4 p-3 bg-purple-50 border border-purple-200 rounded-lg">
        <p className="text-xs text-purple-700 leading-relaxed">
          <strong>Scientific note:</strong> These are satellite-derived spectral proxies/signals — not direct laboratory measurements. Values indicate observable changes in water surface characteristics and must be interpreted in context.
        </p>
      </div>

      {/* Indicator cards */}
      {status === 'done' && data?.status === 'success' && (
        <div className="space-y-3">
          {INDICATOR_ORDER.map(id => {
            const result = data.global_indicators[id];
            if (!result) return null;
            return (
              <IndicatorCard
                key={id}
                id={id}
                result={result}
                isExpanded={expanded === id}
                onToggle={() => toggle(id)}
                onMapLayer={() => onLayerToggle?.(activeLayer === id ? null : id)}
                isActiveLayer={activeLayer === id}
              />
            );
          })}
        </div>
      )}

      {/* Demo badge */}
      {status === 'done' && data?.data_source_mode === 'demo' && (
        <div className="mt-4 p-3 bg-amber-50 rounded-lg border border-amber-200">
          <div className="flex items-center">
            <AlertTriangle className="h-4 w-4 text-amber-600 mr-2 flex-shrink-0" />
            <p className="text-xs text-amber-700">
              <strong>Demo Mode:</strong> Values shown are synthetic data for demonstration. Connect Google Earth Engine to enable live analysis.
            </p>
          </div>
        </div>
      )}

      {/* Quality metadata */}
      {status === 'done' && data && (
        <div className="mt-4 pt-3 border-t border-slate-100 flex flex-wrap gap-3 text-xs text-slate-500">
          <span>Scene: <span className="font-mono text-slate-600">{data.quality_metadata.scene_id}</span></span>
          <span>Sensor: {data.quality_metadata.sensor}</span>
          <span>Valid water pixels: {data.quality_metadata.total_water_pixels.toLocaleString()}</span>
        </div>
      )}
    </div>
  );
}
