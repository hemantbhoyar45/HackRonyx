import React from 'react';
import { Layers, Activity, TrendingUp, TrendingDown, Minus, Info } from 'lucide-react';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, Cell } from 'recharts';
import type { PriorityResult } from '../../types/analysis';

interface Props {
  result: PriorityResult | null;
  loading?: boolean;
}

const INDICATOR_LABELS: Record<string, { label: string; name: string; description: string }> = {
  ndti: {
    label: 'NDTI',
    name: 'Normalized Difference Turbidity Index',
    description: 'Satellite spectral signal sensitive to water turbidity and particulates',
  },
  suspended_sediment: {
    label: 'Suspended Sediment',
    name: 'Suspended Sediment Proxy',
    description: 'Satellite-derived proxy for suspended particulate matter',
  },
  ndci: {
    label: 'NDCI',
    name: 'Normalized Difference Chlorophyll Index',
    description: 'Satellite spectral signal responsive to chlorophyll-a absorption',
  },
  fai: {
    label: 'FAI',
    name: 'Floating Algae Index',
    description: 'Satellite spectral index measuring floating vegetation and algae signal',
  },
};

const CHART_COLORS = ['#38bdf8', '#818cf8', '#34d399', '#f43f5e'];

export const MultiIndicatorEvidencePanel: React.FC<Props> = ({ result, loading }) => {
  if (loading) {
    return (
      <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-6 shadow-xl animate-pulse">
        <div className="h-6 w-48 bg-slate-800 rounded mb-4"></div>
        <div className="h-48 w-full bg-slate-800 rounded"></div>
      </div>
    );
  }

  if (!result || !result.indicators) return null;

  const indicators = result.indicators;

  // Prepare data for Recharts evidence bar chart
  const chartData = indicators.map((ind, idx) => ({
    name: INDICATOR_LABELS[ind.indicator_name]?.label || ind.indicator_name.toUpperCase(),
    contribution: Math.round(ind.weighted_contribution * 1000) / 10, // percentage 0-100%
    rawContribution: ind.weighted_contribution,
    evidenceScore: Math.round(ind.evidence_score * 100),
    fill: CHART_COLORS[idx % CHART_COLORS.length],
  }));

  const getDirectionIcon = (direction: string) => {
    switch (direction) {
      case 'INCREASE':
        return <TrendingUp className="w-3.5 h-3.5 text-amber-400 inline ml-1" />;
      case 'DECREASE':
        return <TrendingDown className="w-3.5 h-3.5 text-cyan-400 inline ml-1" />;
      default:
        return <Minus className="w-3.5 h-3.5 text-slate-500 inline ml-1" />;
    }
  };

  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-6 shadow-xl backdrop-blur-md">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-2">
          <Layers className="w-5 h-5 text-cyan-400" />
          <h3 className="text-sm font-semibold tracking-wider text-slate-300 uppercase">
            Multi-Indicator Evidence Fusion
          </h3>
        </div>
        <span className="text-xs text-slate-400 bg-slate-800/80 px-2.5 py-1 rounded-md border border-slate-700/60 font-mono">
          Agreement: {Math.round(result.indicator_agreement_score * 100)}%
        </span>
      </div>

      {/* Grid of 4 Indicator Evidence Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        {indicators.map((ind, idx) => {
          const info = INDICATOR_LABELS[ind.indicator_name] || {
            label: ind.indicator_name.toUpperCase(),
            name: ind.indicator_name,
            description: '',
          };

          const isPrimary = result.primary_driver === ind.indicator_name;

          return (
            <div
              key={ind.indicator_name}
              className={`rounded-xl p-4 border transition-all ${
                isPrimary
                  ? 'bg-slate-950/90 border-cyan-500/50 shadow-lg shadow-cyan-950/30'
                  : 'bg-slate-950/50 border-slate-800/80 hover:border-slate-700'
              }`}
            >
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-bold text-slate-200 tracking-wide">
                  {info.label}
                </span>
                {isPrimary && (
                  <span className="text-[10px] uppercase tracking-wider font-bold text-cyan-400 bg-cyan-950/80 px-1.5 py-0.5 rounded border border-cyan-800/60">
                    Primary
                  </span>
                )}
              </div>

              <div className="text-[11px] text-slate-400 truncate mb-3" title={info.name}>
                {info.name}
              </div>

              <div className="space-y-2 text-xs">
                <div className="flex justify-between items-center text-slate-300">
                  <span className="text-slate-400">Current:</span>
                  <span className="font-mono font-medium text-slate-100">
                    {ind.current_value !== null ? ind.current_value.toFixed(3) : 'N/A'}
                  </span>
                </div>

                <div className="flex justify-between items-center text-slate-300">
                  <span className="text-slate-400">Baseline:</span>
                  <span className="font-mono text-slate-400">
                    {ind.baseline_value !== null ? ind.baseline_value.toFixed(3) : 'N/A'}
                  </span>
                </div>

                <div className="flex justify-between items-center text-slate-300">
                  <span className="text-slate-400">Direction:</span>
                  <span className="font-mono text-xs flex items-center">
                    {ind.direction}
                    {getDirectionIcon(ind.direction)}
                  </span>
                </div>

                <div className="pt-2 border-t border-slate-800/80 flex justify-between items-center">
                  <span className="text-slate-400">Evidence:</span>
                  <span className="font-semibold text-slate-200">
                    {Math.round(ind.evidence_score * 100)}%
                  </span>
                </div>

                <div className="flex justify-between items-center text-slate-300">
                  <span className="text-slate-400">Contribution:</span>
                  <span className="font-bold font-mono text-cyan-400">
                    {ind.weighted_contribution.toFixed(3)}
                  </span>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Visual Chart Section */}
      <div className="bg-slate-950/60 border border-slate-800/80 rounded-xl p-4">
        <div className="flex items-center justify-between mb-3">
          <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-300">
            Satellite-Observable Evidence Contribution
          </h4>
          <span className="text-[11px] text-slate-400">Combined Evidence: {Math.round(result.combined_evidence * 100)}%</span>
        </div>

        <div className="h-44 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData} layout="vertical" margin={{ top: 5, right: 20, left: 40, bottom: 5 }}>
              <XAxis type="number" domain={[0, 30]} tickFormatter={(v) => `${v}%`} stroke="#64748b" fontSize={11} />
              <YAxis type="category" dataKey="name" stroke="#94a3b8" fontSize={11} tickLine={false} />
              <Tooltip
                contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', color: '#f8fafc' }}
                formatter={(value: any) => [`${value}%`, 'Weighted Contribution']}
              />
              <Bar dataKey="contribution" radius={[0, 4, 4, 0]}>
                {chartData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.fill} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};
