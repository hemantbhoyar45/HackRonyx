import React from 'react';
import { AlertTriangle, ShieldAlert, FileText, CheckCircle2, ChevronRight, Activity, Clock, MapPin } from 'lucide-react';
import type { AlertResponse } from '../../types/analysis';

interface ExplainableAlertPanelProps {
  status: 'idle' | 'loading' | 'done' | 'error';
  data: AlertResponse | null;
}

export const ExplainableAlertPanel: React.FC<ExplainableAlertPanelProps> = ({ status, data }) => {
  if (status === 'idle') return null;

  if (status === 'loading') {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-brand-200 p-5 relative overflow-hidden">
        <div className="absolute top-0 left-0 w-1 h-full bg-brand-400 animate-pulse"></div>
        <div className="flex items-center gap-3 mb-4">
          <div className="p-2 bg-brand-50 text-brand-600 rounded-lg">
            <Activity className="w-5 h-5 animate-pulse" />
          </div>
          <div>
            <h3 className="font-semibold text-slate-900">Generating Explainable Alert</h3>
            <p className="text-xs text-slate-500">Synthesizing evidence and recommendations...</p>
          </div>
        </div>
        <div className="space-y-2">
          <div className="h-4 bg-slate-100 rounded w-3/4 animate-pulse"></div>
          <div className="h-4 bg-slate-100 rounded w-1/2 animate-pulse"></div>
        </div>
      </div>
    );
  }

  if (status === 'error') {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-red-200 p-5">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-red-50 text-red-600 rounded-lg">
            <AlertTriangle className="w-5 h-5" />
          </div>
          <div>
            <h3 className="font-semibold text-slate-900">Alert Generation Failed</h3>
            <p className="text-xs text-red-600">Failed to generate explainability report.</p>
          </div>
        </div>
      </div>
    );
  }

  if (!data || !data.alerts || data.alerts.length === 0) {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-green-200 p-5 relative overflow-hidden">
         <div className="absolute top-0 left-0 w-1 h-full bg-green-500"></div>
         <div className="flex items-center gap-3">
          <div className="p-2 bg-green-50 text-green-600 rounded-lg">
            <CheckCircle2 className="w-5 h-5" />
          </div>
          <div>
            <h3 className="font-semibold text-slate-900">No Actionable Alerts</h3>
            <p className="text-xs text-slate-500">Water quality indicators are within expected historical baselines.</p>
          </div>
        </div>
      </div>
    );
  }

  // Render the most critical alert (assumes they are sorted by priority)
  const alert = data.alerts[0];

  const getUrgencyColor = (urgency: string) => {
    switch (urgency) {
      case 'IMMEDIATE': return 'bg-red-100 text-red-700 border-red-200';
      case 'HIGH': return 'bg-orange-100 text-orange-700 border-orange-200';
      case 'MODERATE': return 'bg-amber-100 text-amber-700 border-amber-200';
      default: return 'bg-slate-100 text-slate-700 border-slate-200';
    }
  };

  const getAlertBorder = (band: string) => {
    switch (band) {
      case 'CRITICAL': return 'border-red-500';
      case 'HIGH': return 'border-orange-500';
      case 'MODERATE': return 'border-amber-400';
      default: return 'border-blue-400';
    }
  };

  const getAlertIconBg = (band: string) => {
    switch (band) {
      case 'CRITICAL': return 'bg-red-50 text-red-600';
      case 'HIGH': return 'bg-orange-50 text-orange-600';
      case 'MODERATE': return 'bg-amber-50 text-amber-600';
      default: return 'bg-blue-50 text-blue-600';
    }
  };

  return (
    <div className={`bg-white rounded-xl shadow-md border-l-4 p-5 ${getAlertBorder(alert.priority_band)}`}>
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className={`p-2 rounded-lg ${getAlertIconBg(alert.priority_band)}`}>
            <ShieldAlert className="w-6 h-6" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="font-bold text-slate-900">{alert.title}</h3>
              <span className="px-2 py-0.5 rounded text-[10px] font-bold tracking-wider uppercase bg-slate-100 text-slate-600">
                {alert.alert_id}
              </span>
            </div>
            <p className="text-sm font-medium text-slate-600 mt-1">{alert.primary_reason}</p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-3 mb-5 text-sm">
        <div className="flex items-center gap-2 text-slate-600 bg-slate-50 p-2 rounded">
          <MapPin className="w-4 h-4 text-slate-400" />
          <span className="font-medium text-slate-700">{alert.water_body_id} ({alert.zone_id})</span>
        </div>
        <div className="flex items-center gap-2 text-slate-600 bg-slate-50 p-2 rounded">
          <Clock className="w-4 h-4 text-slate-400" />
          <span className="font-medium text-slate-700">{new Date(alert.analysis_date).toLocaleDateString()}</span>
        </div>
      </div>

      <div className="mb-5 bg-blue-50/50 border border-blue-100 p-4 rounded-lg">
        <h4 className="text-xs font-bold text-blue-800 uppercase tracking-wider mb-2 flex items-center gap-1">
          <FileText className="w-3 h-3" />
          Why was this flagged?
        </h4>
        <p className="text-sm text-slate-700 leading-relaxed">
          {alert.summary}
        </p>
      </div>

      <div className="space-y-4 mb-5">
        <div>
          <h4 className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-3">Evidence Statements</h4>
          <ul className="space-y-2">
            {alert.evidence_statements.map((ev, idx) => (
              <li key={idx} className="flex items-start gap-2 text-sm">
                <ChevronRight className="w-4 h-4 text-brand-500 shrink-0 mt-0.5" />
                <span className="text-slate-700">
                  <strong className="text-slate-900">{ev.indicator}:</strong> {ev.description}
                </span>
              </li>
            ))}
          </ul>
        </div>
      </div>

      <div className="border-t border-slate-100 pt-4">
        <h4 className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-3">Recommended Actions</h4>
        <div className="flex flex-col gap-2">
          {alert.recommended_actions.map((rec, idx) => (
            <div key={idx} className="flex items-center justify-between text-sm p-3 bg-slate-50 rounded-lg border border-slate-100">
              <span className="text-slate-700 font-medium">{rec.action}</span>
              <span className={`px-2 py-1 rounded text-xs font-bold border ${getUrgencyColor(rec.urgency)}`}>
                {rec.urgency}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
