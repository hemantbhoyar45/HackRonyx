import React from 'react';
import type { PriorityQueueItem } from '../../../types/queue';
import { ArrowRight } from 'lucide-react';

interface Props {
  items: PriorityQueueItem[];
  loading: boolean;
  onViewItem: (item: PriorityQueueItem) => void;
}

export function QueueTable({ items, loading, onViewItem }: Props) {
  if (loading) {
    return (
      <div className="p-8 text-center text-slate-500">
        Loading priority queue...
      </div>
    );
  }

  if (items.length === 0) {
    return (
      <div className="p-12 text-center text-slate-500">
        <p>No investigation candidates match the selected filters.</p>
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-left text-sm text-slate-600">
        <thead className="text-xs uppercase bg-slate-50 text-slate-500 border-b border-slate-200">
          <tr>
            <th className="px-6 py-4 font-semibold">Rank</th>
            <th className="px-6 py-4 font-semibold">Water Body & Zone</th>
            <th className="px-6 py-4 font-semibold">Date</th>
            <th className="px-6 py-4 font-semibold">Priority Score</th>
            <th className="px-6 py-4 font-semibold">Severity</th>
            <th className="px-6 py-4 font-semibold">Confidence</th>
            <th className="px-6 py-4 font-semibold">Primary Indicator</th>
            <th className="px-6 py-4 font-semibold">Status</th>
            <th className="px-6 py-4 font-semibold text-right">Action</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100">
          {items.map((row) => (
            <tr key={row.alert_id} className="hover:bg-slate-50/50 transition-colors">
              <td className="px-6 py-4 font-bold text-slate-800">#{row.rank}</td>
              <td className="px-6 py-4">
                <div className="font-medium text-slate-800">{row.water_body_id}</div>
                <div className="text-xs text-slate-500 mt-0.5">{row.zone_id}</div>
              </td>
              <td className="px-6 py-4 text-slate-500">{new Date(row.analysis_date).toLocaleDateString()}</td>
              <td className="px-6 py-4">
                <div className="font-semibold text-slate-800">{row.investigation_priority_score.toFixed(0)}</div>
                <div className="text-[10px] text-slate-500 mt-0.5">{row.priority_band}</div>
              </td>
              <td className="px-6 py-4">
                <span className={`px-2 py-1 rounded text-xs font-semibold ${
                  row.severity === 'CRITICAL' ? 'bg-red-100 text-red-700' : 
                  row.severity === 'HIGH' ? 'bg-orange-100 text-orange-700' :
                  'bg-amber-100 text-amber-700'
                }`}>
                  {row.severity}
                </span>
              </td>
              <td className="px-6 py-4">{row.confidence > 0 ? `${row.confidence.toFixed(0)}%` : 'N/A'}</td>
              <td className="px-6 py-4">{row.primary_driver || 'Multiple'}</td>
              <td className="px-6 py-4">
                <span className={`px-2 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider border ${
                  row.investigation_status === 'ACTIVE' ? 'bg-red-50 border-red-200 text-red-700' :
                  row.investigation_status === 'ACKNOWLEDGED' ? 'bg-orange-50 border-orange-200 text-orange-700' :
                  row.investigation_status === 'UNDER_INVESTIGATION' ? 'bg-brand-50 border-brand-200 text-brand-700' :
                  row.investigation_status === 'RESOLVED' ? 'bg-emerald-50 border-emerald-200 text-emerald-700' :
                  'bg-slate-100 border-slate-200 text-slate-600'
                }`}>
                  {row.investigation_status.replace('_', ' ')}
                </span>
              </td>
              <td className="px-6 py-4 text-right">
                <button 
                  onClick={() => onViewItem(row)}
                  className="text-brand-600 hover:text-brand-700 font-medium inline-flex items-center gap-1"
                >
                  View <ArrowRight className="w-4 h-4" />
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
