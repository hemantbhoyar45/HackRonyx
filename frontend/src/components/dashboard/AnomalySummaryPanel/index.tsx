import React from 'react';
import { ShieldAlert, Info, AlertTriangle, AlertCircle, CheckCircle2 } from 'lucide-react';
import { AnomalyResponse } from '../../../types/analysis';

interface Props {
  data: AnomalyResponse | null;
  status: 'idle' | 'loading' | 'done' | 'error';
}

export function AnomalySummaryPanel({ data, status }: Props) {
  if (status === 'idle') return null;

  if (status === 'loading') {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-5 mt-4 animate-pulse">
        <div className="h-5 w-48 bg-slate-200 rounded mb-4"></div>
        <div className="space-y-3">
          <div className="h-4 w-full bg-slate-100 rounded"></div>
          <div className="h-4 w-3/4 bg-slate-100 rounded"></div>
        </div>
      </div>
    );
  }

  if (status === 'error' || !data) {
    return (
      <div className="bg-red-50 text-red-700 rounded-xl p-4 mt-4 text-sm flex items-start">
        <AlertTriangle className="w-4 h-4 mr-2 mt-0.5 flex-shrink-0" />
        Failed to load anomaly detection data.
      </div>
    );
  }

  const results = data.results;
  const total = results.length;
  const potential = results.filter(r => r.combined_status === 'POTENTIAL_ANOMALY').length;
  const mixed = results.filter(r => r.combined_status === 'MIXED_EVIDENCE').length;
  const normal = results.filter(r => r.combined_status === 'NO_ANOMALY_SIGNAL').length;
  const insufficient = results.filter(r => r.combined_status === 'INSUFFICIENT_HISTORY' || r.combined_status === 'INSUFFICIENT_DATA').length;
  const lowQuality = results.filter(r => r.combined_status === 'LOW_QUALITY_OBSERVATION').length;

  return (
    <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden mt-4">
      <div className="bg-slate-50 border-b border-slate-200 px-5 py-3 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <ShieldAlert className="w-5 h-5 text-slate-700" />
          <h3 className="font-semibold text-slate-800">Anomaly Detection</h3>
        </div>
        <div className="text-xs px-2 py-1 bg-amber-100 text-amber-800 font-medium rounded-full">
          Demo
        </div>
      </div>

      <div className="p-5">
        <p className="text-sm text-slate-600 mb-4">
          Comparing current satellite-derived indicator features with historical seasonal baselines to identify unusual observations.
        </p>

        <div className="grid grid-cols-2 gap-3 mb-4">
          <div className="bg-slate-50 rounded-lg p-3 text-center border border-slate-100">
            <div className="text-2xl font-bold text-slate-700">{total}</div>
            <div className="text-xs text-slate-500 uppercase font-semibold">Zones Analyzed</div>
          </div>
          <div className={`rounded-lg p-3 text-center border ${potential > 0 ? 'bg-amber-50 border-amber-200' : 'bg-green-50 border-green-200'}`}>
            <div className={`text-2xl font-bold ${potential > 0 ? 'text-amber-700' : 'text-green-700'}`}>{potential}</div>
            <div className="text-xs uppercase font-semibold opacity-70">Potential Anomalies</div>
          </div>
        </div>

        <div className="space-y-2 text-sm">
          {normal > 0 && (
            <div className="flex justify-between items-center text-slate-600">
              <span className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-emerald-500"/> No Anomaly Signal</span>
              <span className="font-medium bg-slate-100 px-2 py-0.5 rounded">{normal}</span>
            </div>
          )}
          {mixed > 0 && (
            <div className="flex justify-between items-center text-slate-600">
              <span className="flex items-center gap-2"><Info className="w-4 h-4 text-blue-500"/> Mixed Evidence</span>
              <span className="font-medium bg-slate-100 px-2 py-0.5 rounded">{mixed}</span>
            </div>
          )}
          {insufficient > 0 && (
            <div className="flex justify-between items-center text-slate-600">
              <span className="flex items-center gap-2"><AlertCircle className="w-4 h-4 text-slate-400"/> Insufficient History</span>
              <span className="font-medium bg-slate-100 px-2 py-0.5 rounded">{insufficient}</span>
            </div>
          )}
          {lowQuality > 0 && (
            <div className="flex justify-between items-center text-slate-600">
              <span className="flex items-center gap-2"><AlertTriangle className="w-4 h-4 text-red-400"/> Low Quality Obs</span>
              <span className="font-medium bg-slate-100 px-2 py-0.5 rounded">{lowQuality}</span>
            </div>
          )}
        </div>

        <div className="mt-5 text-xs text-slate-500 flex gap-2 items-start bg-slate-50 p-3 rounded-lg">
          <Info className="w-4 h-4 flex-shrink-0 mt-0.5" />
          <p>
            <strong>Note:</strong> The anomaly result indicates unusual satellite-observable behavior. It does not confirm contamination. Use this to prioritize investigation.
          </p>
        </div>
      </div>
    </div>
  );
}
