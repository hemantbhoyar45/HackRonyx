import React from 'react';
import { ShieldAlert, X, AlertTriangle, CheckCircle2, Info, Activity } from 'lucide-react';
import type { AnomalyZoneResult } from '../../../types/analysis';

interface Props {
  zone: AnomalyZoneResult;
  onClose: () => void;
}

export function ZoneDetailView({ zone, onClose }: Props) {
  
  const renderIndicatorRow = (key: string, label: string) => {
    const data = zone.indicators[key];
    if (!data) return null;
    
    return (
      <div key={key} className="bg-slate-50 border border-slate-100 rounded-lg p-3 mb-2">
        <div className="font-medium text-slate-700 text-sm mb-2">{label}</div>
        <div className="grid grid-cols-3 gap-2 text-xs">
          <div>
            <span className="text-slate-400 block mb-0.5">Current</span>
            <span className="font-semibold text-slate-800">{data.current_value.toFixed(3)}</span>
          </div>
          <div>
            <span className="text-slate-400 block mb-0.5">Baseline</span>
            <span className="font-medium text-slate-600">{data.baseline_median.toFixed(3)}</span>
          </div>
          <div>
            <span className="text-slate-400 block mb-0.5">Deviation (Robust)</span>
            <span className={`font-semibold ${Math.abs(data.robust_deviation) >= zone.statistical_threshold ? 'text-amber-600' : 'text-slate-600'}`}>
              {data.robust_deviation > 0 ? '+' : ''}{data.robust_deviation.toFixed(1)}
            </span>
          </div>
        </div>
      </div>
    );
  };

  const isAnomaly = zone.combined_status === 'POTENTIAL_ANOMALY';

  return (
    <div className="bg-white rounded-xl shadow-lg border border-slate-200 overflow-hidden mt-4 animate-in slide-in-from-right-4 duration-300">
      <div className={`px-4 py-3 border-b flex items-center justify-between ${
        isAnomaly ? 'bg-amber-50 border-amber-200' : 'bg-slate-50 border-slate-200'
      }`}>
        <div className="flex items-center gap-2">
          {isAnomaly ? (
            <AlertTriangle className="w-5 h-5 text-amber-600" />
          ) : (
            <Activity className="w-5 h-5 text-slate-600" />
          )}
          <div>
            <h3 className={`font-bold ${isAnomaly ? 'text-amber-900' : 'text-slate-800'}`}>
              Zone: {zone.zone_id.replace('zone-', '').toUpperCase()}
            </h3>
            <div className={`text-xs ${isAnomaly ? 'text-amber-700' : 'text-slate-500'}`}>
              {zone.combined_status.replace(/_/g, ' ')}
            </div>
          </div>
        </div>
        <button onClick={onClose} className="p-1.5 hover:bg-black/5 rounded-full text-slate-400 transition-colors">
          <X className="w-4 h-4" />
        </button>
      </div>

      <div className="p-4 max-h-[60vh] overflow-y-auto">
        
        {/* ML & Stats Summary */}
        <div className="grid grid-cols-2 gap-3 mb-5">
          <div className="bg-slate-50 rounded-lg p-3 border border-slate-100">
            <div className="text-xs text-slate-500 mb-1">Statistical Signal</div>
            <div className="font-medium text-sm flex items-center gap-1.5">
              {zone.statistical_anomaly ? (
                <><AlertTriangle className="w-4 h-4 text-amber-500"/> Anomalous</>
              ) : (
                <><CheckCircle2 className="w-4 h-4 text-emerald-500"/> Normal</>
              )}
            </div>
          </div>
          <div className="bg-slate-50 rounded-lg p-3 border border-slate-100">
            <div className="text-xs text-slate-500 mb-1">Isolation Forest</div>
            <div className="font-medium text-sm flex items-center gap-1.5">
              {zone.ml.status !== 'available' ? (
                <span className="text-slate-400 capitalize">{zone.ml.status.replace(/_/g, ' ')}</span>
              ) : zone.ml.prediction === -1 ? (
                <><AlertTriangle className="w-4 h-4 text-amber-500"/> Anomalous</>
              ) : (
                <><CheckCircle2 className="w-4 h-4 text-emerald-500"/> Normal</>
              )}
            </div>
          </div>
        </div>

        {/* Anomaly Score */}
        <div className="mb-6">
          <div className="flex justify-between text-xs mb-1">
            <span className="font-medium text-slate-600">Anomaly Score</span>
            <span className="font-bold text-slate-800">{zone.anomaly_score} / 100</span>
          </div>
          <div className="h-2 w-full bg-slate-100 rounded-full overflow-hidden">
            <div 
              className={`h-full ${zone.anomaly_score > 60 ? 'bg-amber-500' : zone.anomaly_score > 30 ? 'bg-yellow-400' : 'bg-emerald-400'}`}
              style={{ width: `${zone.anomaly_score}%` }}
            />
          </div>
        </div>

        {/* Indicators Breakdown */}
        <div>
          <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-3">Indicator Breakdown</h4>
          {renderIndicatorRow('ndti', 'NDTI (Turbidity-Related)')}
          {renderIndicatorRow('suspended_sediment', 'Suspended Sediment Proxy')}
          {renderIndicatorRow('ndci', 'NDCI (Chlorophyll-Related)')}
          {renderIndicatorRow('fai', 'FAI (Algal Activity)')}
        </div>

        {/* Explainability Text */}
        <div className="mt-5 p-3 bg-blue-50/50 rounded-lg text-sm text-slate-700 leading-relaxed border border-blue-100">
          <div className="flex items-start gap-2">
            <Info className="w-4 h-4 text-blue-500 flex-shrink-0 mt-0.5" />
            <div>
              {zone.combined_status === 'POTENTIAL_ANOMALY' && (
                <p>This zone was flagged because one or more indicators show substantial deviation from historical seasonal baselines.</p>
              )}
              {zone.combined_status === 'NO_ANOMALY_SIGNAL' && (
                <p>Indicator values are consistent with the historical seasonal baseline for this area.</p>
              )}
              {zone.combined_status === 'MIXED_EVIDENCE' && (
                <p>There is conflicting evidence between the statistical baseline comparison and the Isolation Forest model.</p>
              )}
              {zone.ml.prediction === -1 && (
                <p className="mt-2">Isolation Forest also identified the current feature pattern as unusual relative to historical observations.</p>
              )}
            </div>
          </div>
        </div>

      </div>
    </div>
  );
}
