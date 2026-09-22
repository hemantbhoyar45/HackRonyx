import React from 'react';
import { Calendar } from 'lucide-react';
import { useAnalysisStore } from '../../store/analysisStore';

export default function DateRangeSelector() {
  const { startDate, endDate, setStartDate, setEndDate } = useAnalysisStore();

  return (
    <div className="flex flex-col gap-1.5">
      <label className="text-sm font-semibold text-slate-700">Date Range</label>
      <div className="flex items-center gap-2">
        <div className="relative flex-1">
          <Calendar className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
          <input 
            type="date" 
            className="w-full pl-9 pr-3 py-2 bg-white border border-slate-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-brand-500 text-sm font-medium text-slate-700"
            value={startDate}
            onChange={(e) => setStartDate(e.target.value)}
          />
        </div>
        <span className="text-slate-400 text-sm font-medium">to</span>
        <div className="relative flex-1">
          <Calendar className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
          <input 
            type="date" 
            className="w-full pl-9 pr-3 py-2 bg-white border border-slate-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-brand-500 text-sm font-medium text-slate-700"
            value={endDate}
            min={startDate}
            onChange={(e) => setEndDate(e.target.value)}
          />
        </div>
      </div>
    </div>
  );
}
