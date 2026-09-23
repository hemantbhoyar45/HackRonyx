import React from 'react';
import { ShieldAlert, AlertTriangle, CheckCircle2, Info, ArrowUpRight } from 'lucide-react';
import type { PriorityResult } from '../../types/analysis';

interface Props {
  result: PriorityResult | null;
  loading?: boolean;
}

export const InvestigationPriorityCard: React.FC<Props> = ({ result, loading }) => {
  if (loading) {
    return (
      <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-6 shadow-xl animate-pulse">
        <div className="h-6 w-48 bg-slate-800 rounded mb-4"></div>
        <div className="h-16 w-32 bg-slate-800 rounded mb-4"></div>
        <div className="h-10 w-full bg-slate-800 rounded"></div>
      </div>
    );
  }

  if (!result) return null;

  const score = Math.round(result.investigation_priority_score);

  // Band badge colors
  const getBandBadge = (band: string) => {
    switch (band) {
      case 'VERY HIGH PRIORITY':
      case 'VERY HIGH':
        return 'bg-red-500/20 text-red-400 border-red-500/40 shadow-red-950/40';
      case 'HIGH PRIORITY':
      case 'HIGH':
        return 'bg-amber-500/20 text-amber-400 border-amber-500/40 shadow-amber-950/40';
      case 'MEDIUM PRIORITY':
      case 'MEDIUM':
        return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/40 shadow-yellow-950/40';
      default:
        return 'bg-emerald-500/20 text-emerald-400 border-emerald-500/40 shadow-emerald-950/40';
    }
  };

  const getScoreColor = (scoreVal: number) => {
    if (scoreVal >= 75) return 'text-red-400';
    if (scoreVal >= 50) return 'text-amber-400';
    if (scoreVal >= 25) return 'text-yellow-400';
    return 'text-emerald-400';
  };

  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-6 shadow-xl backdrop-blur-md relative overflow-hidden">
      {/* Background ambient glow */}
      <div className={`absolute -right-16 -top-16 w-48 h-48 rounded-full blur-3xl opacity-20 pointer-events-none ${
        score >= 75 ? 'bg-red-500' : score >= 50 ? 'bg-amber-500' : 'bg-emerald-500'
      }`}></div>

      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-2">
          <ShieldAlert className="w-5 h-5 text-cyan-400" />
          <h3 className="text-sm font-semibold tracking-wider text-slate-300 uppercase">
            Investigation Priority
          </h3>
        </div>
        <span className={`px-3 py-1 text-xs font-bold rounded-full border shadow-sm ${getBandBadge(result.priority_band)}`}>
          {result.priority_band}
        </span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 items-center">
        {/* Priority Score Display */}
        <div className="flex flex-col justify-center border-r border-slate-800/80 pr-4">
          <div className="flex items-baseline space-x-2">
            <span className={`text-5xl font-extrabold tracking-tight ${getScoreColor(score)}`}>
              {score}
            </span>
            <span className="text-xl text-slate-500 font-medium">/ 100</span>
          </div>
          <span className="text-xs text-slate-400 mt-1 font-mono">
            Ground Investigation Priority Score
          </span>
        </div>

        {/* Detailed Metrics */}
        <div className="col-span-2 grid grid-cols-2 sm:grid-cols-3 gap-4">
          <div className="bg-slate-950/60 rounded-lg p-3 border border-slate-800/60">
            <span className="text-xs text-slate-400 block mb-1">Confidence</span>
            <div className="flex items-center space-x-1.5">
              <span className="text-lg font-bold text-slate-100">{Math.round(result.confidence)}%</span>
              <span className="text-xs text-slate-500 font-mono">Analytical</span>
            </div>
          </div>

          <div className="bg-slate-950/60 rounded-lg p-3 border border-slate-800/60">
            <span className="text-xs text-slate-400 block mb-1">Signal Severity</span>
            <div className="flex items-center space-x-1.5">
              <span className={`text-base font-bold ${
                result.severity === 'VERY HIGH' || result.severity === 'HIGH' ? 'text-amber-400' : 'text-slate-200'
              }`}>
                {result.severity}
              </span>
            </div>
          </div>

          <div className="bg-slate-950/60 rounded-lg p-3 border border-slate-800/60 col-span-2 sm:col-span-1">
            <span className="text-xs text-slate-400 block mb-1">Primary Driver</span>
            <div className="flex items-center space-x-1 text-cyan-400 font-semibold text-sm uppercase">
              <span>{result.primary_driver || 'N/A'}</span>
              <ArrowUpRight className="w-4 h-4" />
            </div>
          </div>
        </div>
      </div>

      {/* Scientific Boundary Banner */}
      <div className="mt-5 pt-4 border-t border-slate-800/80 flex items-start space-x-2 text-xs text-slate-400">
        <Info className="w-4 h-4 text-cyan-400 shrink-0 mt-0.5" />
        <p>
          <strong className="text-slate-300">Decision-Support Notice:</strong> This score prioritizes zones showing potential satellite-observable spectral anomalies for ground investigation. It is NOT a laboratory water-quality concentration or pollution confirmation.
        </p>
      </div>
    </div>
  );
};
