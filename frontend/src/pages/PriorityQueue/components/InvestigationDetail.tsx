import React, { useState, useEffect } from 'react';
import { X, ShieldAlert, CheckCircle2, Clock, MapPin, Search } from 'lucide-react';
import type { PriorityQueueItem, AlertStatusHistory } from '../../../types/queue';
import { queueService } from '../../../services/api/queueService';

interface Props {
  item: PriorityQueueItem | null;
  onClose: () => void;
  onStatusChange: (alertId: string, status: string, reason?: string) => void;
}

export function InvestigationDetail({ item, onClose, onStatusChange }: Props) {
  const [history, setHistory] = useState<AlertStatusHistory[]>([]);
  const [reason, setReason] = useState('');
  const [updating, setUpdating] = useState(false);

  useEffect(() => {
    if (item) {
      queueService.getHistory(item.alert_id).then(setHistory).catch(console.error);
    }
  }, [item]);

  if (!item) return null;

  const alert = item.alert_details;

  const handleStatusUpdate = async (newStatus: string) => {
    if (newStatus === 'DISMISSED' && !reason.trim()) {
      window.alert('Please provide a reason for dismissal.');
      return;
    }
    setUpdating(true);
    try {
      await onStatusChange(item.alert_id, newStatus, reason);
      setReason('');
    } finally {
      setUpdating(false);
    }
  };

  return (
    <>
      <div className="fixed inset-0 bg-slate-900/20 backdrop-blur-sm z-40 transition-opacity" onClick={onClose} />
      <div className="fixed inset-y-0 right-0 w-full md:w-[600px] bg-white shadow-2xl border-l border-slate-200 z-50 flex flex-col overflow-hidden animate-in slide-in-from-right duration-300">
        <div className="p-6 border-b border-slate-200 flex items-center justify-between bg-slate-50">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <ShieldAlert className="w-5 h-5 text-brand-600" />
              <h2 className="text-lg font-bold text-slate-800">POTENTIAL WATER QUALITY ANOMALY</h2>
            </div>
            <p className="text-sm text-slate-500 font-mono">{item.alert_id}</p>
          </div>
          <button onClick={onClose} className="p-2 hover:bg-slate-200 rounded-full transition-colors text-slate-500">
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-6 space-y-8">
          
          {/* Core Info */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-xs text-slate-500 font-medium uppercase">Water Body</p>
              <p className="font-semibold text-slate-800">{item.water_body_id}</p>
            </div>
            <div>
              <p className="text-xs text-slate-500 font-medium uppercase">Zone</p>
              <p className="font-semibold text-slate-800">{item.zone_id}</p>
            </div>
            <div>
              <p className="text-xs text-slate-500 font-medium uppercase">Analysis Date</p>
              <p className="font-semibold text-slate-800">{new Date(item.analysis_date).toLocaleDateString()}</p>
            </div>
            <div>
              <p className="text-xs text-slate-500 font-medium uppercase">Priority Score</p>
              <p className="font-semibold text-slate-800">{item.investigation_priority_score.toFixed(0)} / 100 ({item.priority_band})</p>
            </div>
            <div>
              <p className="text-xs text-slate-500 font-medium uppercase">Confidence</p>
              <p className="font-semibold text-slate-800">{item.confidence > 0 ? `${item.confidence.toFixed(0)}%` : 'N/A'}</p>
            </div>
            <div>
              <p className="text-xs text-slate-500 font-medium uppercase">Severity</p>
              <p className="font-semibold text-slate-800">{item.severity}</p>
            </div>
          </div>

          {/* Why Flagged */}
          <div>
            <h3 className="text-sm font-bold text-slate-800 uppercase tracking-wider mb-3">WHY WAS THIS ZONE FLAGGED?</h3>
            <div className="bg-brand-50 rounded-lg p-4 text-sm text-brand-900 border border-brand-100 mb-4">
              {alert.summary}
            </div>
            
            <ul className="space-y-3">
              {alert.evidence_statements.map((ev: any, idx: number) => (
                <li key={idx} className="flex gap-3 text-sm">
                  <div className={`mt-0.5 w-2 h-2 rounded-full flex-shrink-0 ${ev.significance === 'HIGH' ? 'bg-red-500' : ev.significance === 'MODERATE' ? 'bg-orange-500' : 'bg-amber-500'}`} />
                  <span className="text-slate-700">{ev.description}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Recommended Actions */}
          <div>
            <h3 className="text-sm font-bold text-slate-800 uppercase tracking-wider mb-3">RECOMMENDED ACTION</h3>
            <ul className="space-y-3">
              {alert.recommended_actions.map((act: any, idx: number) => (
                <li key={idx} className="flex items-start gap-3 bg-slate-50 p-3 rounded-md border border-slate-200">
                  <CheckCircle2 className="w-5 h-5 text-emerald-600 flex-shrink-0 mt-0.5" />
                  <span className="text-sm text-slate-700">{act.action}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Operational Actions */}
          <div className="pt-6 border-t border-slate-200">
            <h3 className="text-sm font-bold text-slate-800 uppercase tracking-wider mb-4">INVESTIGATION STATUS</h3>
            
            <div className="mb-4">
              <span className={`px-3 py-1.5 rounded-full text-xs font-bold uppercase tracking-wider border ${
                item.investigation_status === 'ACTIVE' ? 'bg-red-50 border-red-200 text-red-700' :
                item.investigation_status === 'ACKNOWLEDGED' ? 'bg-orange-50 border-orange-200 text-orange-700' :
                item.investigation_status === 'UNDER_INVESTIGATION' ? 'bg-brand-50 border-brand-200 text-brand-700' :
                item.investigation_status === 'RESOLVED' ? 'bg-emerald-50 border-emerald-200 text-emerald-700' :
                'bg-slate-100 border-slate-200 text-slate-600'
              }`}>
                CURRENT: {item.investigation_status.replace('_', ' ')}
              </span>
            </div>

            <textarea
              className="w-full text-sm border border-slate-300 rounded-md p-3 mb-4 focus:ring-brand-500 focus:border-brand-500"
              rows={2}
              placeholder="Optional reason or comment for status change (Required for Dismiss)"
              value={reason}
              onChange={(e) => setReason(e.target.value)}
            />

            <div className="flex flex-wrap gap-3">
              {item.investigation_status === 'ACTIVE' && (
                <>
                  <button disabled={updating} onClick={() => handleStatusUpdate('ACKNOWLEDGED')} className="px-4 py-2 bg-orange-600 hover:bg-orange-700 text-white text-sm font-medium rounded-md transition-colors">Acknowledge</button>
                  <button disabled={updating} onClick={() => handleStatusUpdate('DISMISSED')} className="px-4 py-2 bg-slate-200 hover:bg-slate-300 text-slate-800 text-sm font-medium rounded-md transition-colors">Dismiss</button>
                </>
              )}
              
              {item.investigation_status === 'ACKNOWLEDGED' && (
                <>
                  <button disabled={updating} onClick={() => handleStatusUpdate('UNDER_INVESTIGATION')} className="px-4 py-2 bg-brand-600 hover:bg-brand-700 text-white text-sm font-medium rounded-md transition-colors">Start Investigation</button>
                  <button disabled={updating} onClick={() => handleStatusUpdate('DISMISSED')} className="px-4 py-2 bg-slate-200 hover:bg-slate-300 text-slate-800 text-sm font-medium rounded-md transition-colors">Dismiss</button>
                </>
              )}

              {item.investigation_status === 'UNDER_INVESTIGATION' && (
                <button disabled={updating} onClick={() => handleStatusUpdate('RESOLVED')} className="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white text-sm font-medium rounded-md transition-colors">Mark Resolved</button>
              )}

              {(item.investigation_status === 'RESOLVED' || item.investigation_status === 'DISMISSED') && (
                <button disabled={updating} onClick={() => handleStatusUpdate('ACTIVE')} className="px-4 py-2 bg-white border border-slate-300 hover:bg-slate-50 text-slate-700 text-sm font-medium rounded-md transition-colors">Reopen to Active</button>
              )}
            </div>
          </div>

          {/* Audit History */}
          {history.length > 0 && (
            <div className="pt-6 border-t border-slate-200">
              <h3 className="text-sm font-bold text-slate-800 uppercase tracking-wider mb-4">STATUS HISTORY</h3>
              <div className="space-y-4">
                {history.map((h) => (
                  <div key={h.id} className="text-sm flex gap-3">
                    <Clock className="w-4 h-4 text-slate-400 mt-0.5 flex-shrink-0" />
                    <div>
                      <p className="text-slate-800 font-medium">Changed to {h.new_status.replace('_', ' ')}</p>
                      <p className="text-xs text-slate-500 mt-0.5">{new Date(h.changed_at).toLocaleString()} by {h.changed_by}</p>
                      {h.reason && <p className="text-slate-600 mt-1 italic">"{h.reason}"</p>}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Disclaimer */}
          <div className="mt-8 bg-slate-50 p-4 rounded-md border border-slate-200 text-xs text-slate-500">
            <strong>SCIENTIFIC NOTE:</strong> Satellite-derived indicators identify observable spectral anomalies. They do not independently confirm contamination or identify its source.
          </div>

        </div>
      </div>
    </>
  );
}
