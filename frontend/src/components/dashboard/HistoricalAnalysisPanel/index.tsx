import React, { useState } from 'react';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, ReferenceLine, Area, AreaChart, Legend
} from 'recharts';
import { HistoricalResponse, TimeSeriesPoint } from '../../../types/analysis';
import { Activity, Clock, Database, TrendingUp, TrendingDown, Minus, AlertCircle } from 'lucide-react';

// ─────────────────────────────────────────────────────────────
// Types
// ─────────────────────────────────────────────────────────────

interface Props {
  data: HistoricalResponse | null;
  status: 'idle' | 'loading' | 'done' | 'error';
  lookback: '1yr' | '2yr';
  onLookbackChange: (v: '1yr' | '2yr') => void;
}

interface IndicatorConfig {
  key: string;
  label: string;
  color: string;
  unit: string;
  description: string;
  higherMeaning: string;
}

const INDICATOR_CONFIGS: IndicatorConfig[] = [
  {
    key: 'ndti',
    label: 'NDTI',
    color: '#f97316',
    unit: 'index',
    description: 'Normalised Difference Turbidity Index',
    higherMeaning: 'Higher = more turbid water',
  },
  {
    key: 'ndci',
    label: 'NDCI',
    color: '#10b981',
    unit: 'index',
    description: 'Normalised Difference Chlorophyll Index',
    higherMeaning: 'Higher = more chlorophyll / algal activity',
  },
  {
    key: 'fai',
    label: 'FAI',
    color: '#8b5cf6',
    unit: 'index',
    description: 'Floating Algae Index',
    higherMeaning: 'Higher = more surface algae',
  },
  {
    key: 'suspended_sediment',
    label: 'Sediment',
    color: '#eab308',
    unit: 'index',
    description: 'Suspended Sediment Proxy',
    higherMeaning: 'Higher = more suspended sediment load',
  },
];

// ─────────────────────────────────────────────────────────────
// Helpers
// ─────────────────────────────────────────────────────────────

function calcBaseline(points: TimeSeriesPoint[]): { median: number; p25: number; p75: number } | null {
  if (!points || points.length < 3) return null;
  const vals = points.map(p => p.median).sort((a, b) => a - b);
  const n = vals.length;
  const median = n % 2 === 1 ? vals[Math.floor(n / 2)] : (vals[n / 2 - 1] + vals[n / 2]) / 2;
  const p25 = vals[Math.floor(n * 0.25)];
  const p75 = vals[Math.floor(n * 0.75)];
  return { median, p25, p75 };
}

function formatDate(dateStr: string): string {
  const d = new Date(dateStr);
  return d.toLocaleDateString('en-IN', { month: 'short', year: '2-digit' });
}

function formatValue(v: number, unit: string): string {
  return `${v.toFixed(4)} ${unit}`;
}

// ─────────────────────────────────────────────────────────────
// Sub-components
// ─────────────────────────────────────────────────────────────

const StatusBadge = ({ count, baseline }: { count: number; baseline: boolean }) => (
  <div className="flex items-center gap-2 text-xs">
    <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full font-medium
      ${baseline ? 'bg-emerald-100 text-emerald-700' : 'bg-amber-100 text-amber-700'}`}>
      <Database className="w-3 h-3" />
      {count} obs
    </span>
    <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full font-medium
      ${baseline ? 'bg-blue-100 text-blue-700' : 'bg-slate-100 text-slate-500'}`}>
      {baseline ? '✓ Baseline available' : 'Insufficient history'}
    </span>
  </div>
);

const DemoBadge = () => (
  <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-semibold bg-violet-100 text-violet-700 border border-violet-200">
    DEMO DATA
  </span>
);

interface MiniChartProps {
  points: TimeSeriesPoint[];
  config: IndicatorConfig;
  currentValue?: number;
}

const MiniChart: React.FC<MiniChartProps> = ({ points, config, currentValue }) => {
  const baseline = calcBaseline(points);

  const chartData = points.map(p => ({
    date: p.date,
    label: formatDate(p.date),
    value: p.median,
    bandLow: baseline?.p25 ?? p.median,
    bandHigh: baseline?.p75 ?? p.median,
    baseline: baseline?.median,
  }));

  // Compute deviation category for current value
  let deviationIcon = <Minus className="w-3.5 h-3.5 text-slate-400" />;
  let deviationLabel = '—';
  if (baseline && currentValue !== undefined) {
    const pct = ((currentValue - baseline.median) / Math.abs(baseline.median || 1)) * 100;
    if (pct > 20) {
      deviationIcon = <TrendingUp className="w-3.5 h-3.5 text-red-500" />;
      deviationLabel = `+${pct.toFixed(1)}% vs baseline`;
    } else if (pct < -20) {
      deviationIcon = <TrendingDown className="w-3.5 h-3.5 text-blue-500" />;
      deviationLabel = `${pct.toFixed(1)}% vs baseline`;
    } else {
      deviationLabel = `${pct > 0 ? '+' : ''}${pct.toFixed(1)}% vs baseline`;
    }
  }

  return (
    <div className="bg-slate-50 rounded-xl border border-slate-200 p-3 flex flex-col gap-2">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <span className="text-xs font-bold text-slate-700">{config.label}</span>
          <p className="text-[10px] text-slate-500 mt-0.5">{config.description}</p>
        </div>
        <div className="flex items-center gap-1 text-[10px] text-slate-500">
          {deviationIcon}
          <span>{deviationLabel}</span>
        </div>
      </div>

      {/* Chart */}
      <ResponsiveContainer width="100%" height={90}>
        <AreaChart data={chartData} margin={{ top: 4, right: 4, bottom: 0, left: 0 }}>
          <defs>
            <linearGradient id={`grad_${config.key}`} x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor={config.color} stopOpacity={0.15} />
              <stop offset="95%" stopColor={config.color} stopOpacity={0.02} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" vertical={false} />
          <XAxis
            dataKey="label"
            tick={{ fontSize: 9, fill: '#94a3b8' }}
            tickLine={false}
            interval="preserveStartEnd"
          />
          <YAxis
            tick={{ fontSize: 9, fill: '#94a3b8' }}
            tickLine={false}
            axisLine={false}
            width={38}
            tickFormatter={v => v.toFixed(3)}
          />
          <Tooltip
            contentStyle={{ fontSize: 11, borderRadius: 6, borderColor: '#e2e8f0' }}
            formatter={(val: number) => [val.toFixed(5), config.label]}
            labelFormatter={l => `Date: ${l}`}
          />
          {/* P25–P75 variability band */}
          <Area
            type="monotone"
            dataKey="bandHigh"
            stroke="transparent"
            fill={`url(#grad_${config.key})`}
            fillOpacity={1}
            legendType="none"
          />
          {/* Baseline median reference line */}
          {baseline && (
            <ReferenceLine
              y={baseline.median}
              stroke={config.color}
              strokeDasharray="4 3"
              strokeOpacity={0.6}
              label={{ value: 'Baseline', position: 'insideTopRight', fontSize: 8, fill: config.color }}
            />
          )}
          {/* Observation dots + line */}
          <Line
            type="monotone"
            dataKey="value"
            stroke={config.color}
            strokeWidth={1.5}
            dot={{ r: 2, fill: config.color, fillOpacity: 0.6 }}
            activeDot={{ r: 4, fill: config.color }}
          />
          {/* Current observation star marker */}
          {currentValue !== undefined && chartData.length > 0 && (
            <ReferenceLine
              y={currentValue}
              stroke="#ef4444"
              strokeWidth={1.5}
              strokeDasharray="2 2"
              label={{ value: 'Current', position: 'insideTopLeft', fontSize: 8, fill: '#ef4444' }}
            />
          )}
        </AreaChart>
      </ResponsiveContainer>

      {/* Footer stat row */}
      {baseline && (
        <div className="flex items-center justify-between text-[10px] text-slate-500 border-t border-slate-200 pt-1.5">
          <span>P25: <b className="text-slate-700">{baseline.p25.toFixed(4)}</b></span>
          <span>Median: <b style={{ color: config.color }}>{baseline.median.toFixed(4)}</b></span>
          <span>P75: <b className="text-slate-700">{baseline.p75.toFixed(4)}</b></span>
        </div>
      )}
    </div>
  );
};

// ─────────────────────────────────────────────────────────────
// Main Component
// ─────────────────────────────────────────────────────────────

export const HistoricalAnalysisPanel: React.FC<Props> = ({ data, status, lookback, onLookbackChange }) => {
  const [expanded, setExpanded] = useState(true);

  const isLoading = status === 'loading';
  const hasData = status === 'done' && data !== null;

  if (status === 'idle') {
    return (
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-4">
        <div className="flex items-center gap-2 mb-1">
          <Activity className="w-4 h-4 text-slate-400" />
          <h3 className="text-sm font-semibold text-slate-700">Historical Baseline</h3>
        </div>
        <p className="text-xs text-slate-400 ml-6">Runs automatically after spectral indicators complete.</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
      {/* Panel Header */}
      <button
        onClick={() => setExpanded(e => !e)}
        className="w-full flex items-center justify-between px-4 py-3 hover:bg-slate-50 transition-colors"
      >
        <div className="flex items-center gap-2">
          <div className={`w-2 h-2 rounded-full flex-shrink-0 ${
            isLoading ? 'bg-blue-400 animate-pulse' :
            status === 'done' ? 'bg-emerald-500' :
            status === 'error' ? 'bg-red-500' : 'bg-slate-300'
          }`} />
          <Activity className="w-4 h-4 text-violet-600" />
          <span className="text-sm font-semibold text-slate-800">Historical Baseline & Time-Series</span>
          {hasData && data.data_source_mode === 'demo' && <DemoBadge />}
        </div>
        <span className="text-slate-400 text-xs">{expanded ? '▲' : '▼'}</span>
      </button>

      {expanded && (
        <div className="px-4 pb-4 space-y-3">
          {/* Loading State */}
          {isLoading && (
            <div className="flex flex-col items-center justify-center py-8 gap-2 text-sm text-slate-500">
              <div className="w-6 h-6 border-2 border-violet-400 border-t-transparent rounded-full animate-spin" />
              <span>Retrieving historical observations…</span>
            </div>
          )}

          {/* Error State */}
          {status === 'error' && (
            <div className="flex items-center gap-2 text-sm text-red-600 bg-red-50 rounded-lg p-3 border border-red-100">
              <AlertCircle className="w-4 h-4 flex-shrink-0" />
              <span>Historical analysis failed. Check the API server.</span>
            </div>
          )}

          {/* Data State */}
          {hasData && (
            <>
              {/* Summary row */}
              <div className="flex items-center justify-between flex-wrap gap-2 pb-2 border-b border-slate-100">
                <StatusBadge
                  count={data.valid_observations}
                  baseline={data.valid_observations >= 6}
                />
                {/* Lookback selector */}
                <div className="flex items-center gap-1">
                  <Clock className="w-3 h-3 text-slate-400" />
                  {(['1yr', '2yr'] as const).map(v => (
                    <button
                      key={v}
                      onClick={() => onLookbackChange(v)}
                      className={`text-[10px] px-2 py-0.5 rounded font-semibold border transition-colors ${
                        lookback === v
                          ? 'bg-violet-600 text-white border-violet-600'
                          : 'bg-white text-slate-500 border-slate-200 hover:border-violet-400'
                      }`}
                    >
                      {v}
                    </button>
                  ))}
                </div>
              </div>

              {/* Date range info */}
              <p className="text-[10px] text-slate-400">
                {data.start_date} → {data.end_date} &nbsp;|&nbsp;
                {data.total_scenes_found} scenes &nbsp;|&nbsp;
                {data.rejected_observations} rejected
              </p>

              {/* Charts — one per indicator */}
              <div className="space-y-3">
                {INDICATOR_CONFIGS.map(cfg => {
                  const points = data.time_series[cfg.key] ?? [];
                  return (
                    <MiniChart
                      key={cfg.key}
                      points={points}
                      config={cfg}
                    />
                  );
                })}
              </div>

              {/* Demo disclaimer */}
              {data.data_source_mode === 'demo' && (
                <p className="text-[10px] text-violet-600 bg-violet-50 rounded p-2 border border-violet-100 leading-snug">
                  ⚠ Demo data — synthetic seasonal observations generated from realistic baselines.
                  Enable GEE integration to ingest real Sentinel-2 historical scenes.
                </p>
              )}
            </>
          )}
        </div>
      )}
    </div>
  );
};
