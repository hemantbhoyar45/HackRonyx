import React from 'react';
import { useAnalysisStore } from '../../store/analysisStore';

// Color palettes for each indicator (as CSS gradients for the legend)
const INDICATOR_CONFIG: Record<string, {
  label: string;
  palette: string[];
  minLabel: string;
  maxLabel: string;
  unit: string;
  note: string;
}> = {
  ndti: {
    label: 'NDTI — Turbidity-Related',
    palette: ['#313695', '#4575b4', '#74add1', '#ffffbf', '#fdae61', '#f46d43', '#d73027'],
    minLabel: 'Low signal',
    maxLabel: 'High signal',
    unit: 'Dimensionless spectral ratio',
    note: 'Not a direct turbidity measurement'
  },
  suspended_sediment: {
    label: 'Suspended Sediment Proxy',
    palette: ['#fff7fb', '#ece7f2', '#d0d1e6', '#a6bddb', '#74a9cf', '#2b8cbe', '#045a8d'],
    minLabel: 'Low signal',
    maxLabel: 'High signal',
    unit: 'Dimensionless spectral proxy',
    note: 'Not calibrated to lab concentration'
  },
  ndci: {
    label: 'NDCI — Chlorophyll-Related',
    palette: ['#ffffe5', '#f7fcb9', '#d9f0a3', '#addd8e', '#78c679', '#31a354', '#006837'],
    minLabel: 'Low signal',
    maxLabel: 'High signal',
    unit: 'Dimensionless spectral ratio',
    note: 'Not a direct chlorophyll measurement'
  },
  fai: {
    label: 'FAI — Algal Activity-Related',
    palette: ['#f7fcfd', '#e0f3db', '#ccebc5', '#a8ddb5', '#7bccc4', '#43a2ca', '#0868ac'],
    minLabel: 'Baseline',
    maxLabel: 'Elevated NIR',
    unit: 'Dimensionless reflectance residual',
    note: 'Not a confirmed algal bloom detection'
  }
};

function GradientLegend({ palette, minLabel, maxLabel }: { palette: string[]; minLabel: string; maxLabel: string }) {
  const gradient = `linear-gradient(to right, ${palette.join(', ')})`;
  return (
    <div className="w-full">
      <div className="h-3 rounded-sm w-full" style={{ background: gradient }} />
      <div className="flex justify-between mt-1">
        <span className="text-xs text-slate-500">{minLabel}</span>
        <span className="text-xs text-slate-500">{maxLabel}</span>
      </div>
    </div>
  );
}

export function IndicatorLayer() {
  const { activeMapLayer, indicatorsResult } = useAnalysisStore();

  // For now this component renders only the legend overlay on the map.
  // In a full production build with a GEE tile server, we'd render an ee.TileLayer here.
  // Demo mode: just show the legend with the active layer's info.

  if (!activeMapLayer || activeMapLayer === 'water_mask' || !indicatorsResult) {
    return null;
  }

  const config = INDICATOR_CONFIG[activeMapLayer];
  if (!config) return null;

  const indicatorData = indicatorsResult.global_indicators[activeMapLayer];
  if (!indicatorData) return null;

  const min = indicatorData.statistics.percentile_10.toFixed(3);
  const max = indicatorData.statistics.percentile_90.toFixed(3);

  return (
    <>
      {/* Legend overlay in map bottom-right */}
      <div
        className="absolute bottom-4 right-4 z-[1000] bg-white/95 backdrop-blur-sm rounded-lg shadow-md border border-slate-200 p-3 w-64"
        style={{ pointerEvents: 'none' }}
      >
        <div className="text-xs font-bold text-slate-700 mb-1">{config.label}</div>
        <div className="text-xs text-slate-400 mb-2 italic">{config.note}</div>
        <GradientLegend
          palette={config.palette}
          minLabel={`${min} (P10)`}
          maxLabel={`${max} (P90)`}
        />
        <div className="mt-2 text-xs text-slate-500 pt-2 border-t border-slate-100">
          <span className="font-medium">Type:</span> {config.unit}
        </div>
        {indicatorsResult.data_source_mode === 'demo' && (
          <div className="mt-1 text-xs text-amber-600 font-medium">⚠ Demo data</div>
        )}
      </div>
    </>
  );
}
