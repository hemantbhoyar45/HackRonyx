import React from 'react';
import type { QueueSummary } from '../../../types/queue';
import { AlertCircle, CheckCircle2, Search, Clock, ArrowUpCircle } from 'lucide-react';

interface Props {
  summary: QueueSummary | null;
  loading: boolean;
}

export function QueueSummaryCards({ summary, loading }: Props) {
  if (loading || !summary) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        {[1, 2, 3, 4].map(i => (
          <div key={i} className="bg-white rounded-xl border border-slate-200 p-4 h-24 animate-pulse" />
        ))}
      </div>
    );
  }

  const cards = [
    { label: 'ACTIVE', value: summary.active, icon: AlertCircle, color: 'text-red-600', bg: 'bg-red-50' },
    { label: 'ACKNOWLEDGED', value: summary.acknowledged, icon: Clock, color: 'text-orange-600', bg: 'bg-orange-50' },
    { label: 'UNDER INVESTIGATION', value: summary.under_investigation, icon: Search, color: 'text-brand-600', bg: 'bg-brand-50' },
    { label: 'RESOLVED', value: summary.resolved, icon: CheckCircle2, color: 'text-emerald-600', bg: 'bg-emerald-50' },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
      {cards.map((card, i) => (
        <div key={i} className="bg-white rounded-xl border border-slate-200 p-4 flex items-center shadow-sm">
          <div className={`${card.bg} ${card.color} w-12 h-12 rounded-lg flex items-center justify-center mr-4`}>
            <card.icon className="w-6 h-6" />
          </div>
          <div>
            <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">{card.label}</p>
            <p className="text-2xl font-bold text-slate-800">{card.value}</p>
          </div>
        </div>
      ))}
    </div>
  );
}
