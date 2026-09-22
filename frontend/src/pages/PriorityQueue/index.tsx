import React from 'react';
import { Search, Filter, ArrowRight } from 'lucide-react';

const MOCK_QUEUE = [
  { id: '1', rank: 1, body: 'Gosikhurd Reservoir', zone: 'North Basin', date: '2026-09-22', score: 88, severity: 'High', conf: 92, indicator: 'Turbidity', status: 'Pending' },
  { id: '2', rank: 2, body: 'Godavari River', zone: 'Industrial Outflow A', date: '2026-09-21', score: 75, severity: 'Medium', conf: 85, indicator: 'Chlorophyll', status: 'In Progress' },
  { id: '3', rank: 3, body: 'Wainganga River', zone: 'Segment 4', date: '2026-09-20', score: 62, severity: 'Medium', conf: 78, indicator: 'Suspended Sediment', status: 'Pending' },
];

export default function PriorityQueue() {
  return (
    <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden flex flex-col h-full">
      <div className="p-5 border-b border-slate-200 flex items-center justify-between">
        <div>
          <h2 className="text-lg font-bold text-slate-800">Priority Investigation Queue</h2>
          <p className="text-sm text-slate-500 mt-1">Zones requiring ground investigation based on satellite anomalies.</p>
        </div>
        <div className="flex gap-3">
          <div className="relative">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input 
              type="text" 
              placeholder="Search queue..." 
              className="pl-9 pr-4 py-2 border border-slate-300 rounded-md text-sm focus:ring-brand-500 focus:border-brand-500"
            />
          </div>
          <button className="flex items-center gap-2 px-4 py-2 bg-slate-50 border border-slate-300 rounded-md text-sm font-medium text-slate-700 hover:bg-slate-100">
            <Filter className="w-4 h-4" /> Filter
          </button>
        </div>
      </div>

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
            {MOCK_QUEUE.map((row) => (
              <tr key={row.id} className="hover:bg-slate-50/50 transition-colors">
                <td className="px-6 py-4 font-bold text-slate-800">#{row.rank}</td>
                <td className="px-6 py-4">
                  <div className="font-medium text-slate-800">{row.body}</div>
                  <div className="text-xs text-slate-500 mt-0.5">{row.zone}</div>
                </td>
                <td className="px-6 py-4 text-slate-500">{row.date}</td>
                <td className="px-6 py-4">
                  <div className="font-semibold text-slate-800">{row.score}</div>
                </td>
                <td className="px-6 py-4">
                  <span className={`px-2 py-1 rounded text-xs font-semibold ${
                    row.severity === 'High' ? 'bg-red-100 text-red-700' : 'bg-amber-100 text-amber-700'
                  }`}>
                    {row.severity}
                  </span>
                </td>
                <td className="px-6 py-4">{row.conf}%</td>
                <td className="px-6 py-4">{row.indicator}</td>
                <td className="px-6 py-4">
                  <span className={`px-2 py-1 rounded-full text-xs font-medium border ${
                    row.status === 'Pending' ? 'bg-slate-100 border-slate-200 text-slate-600' : 'bg-blue-50 border-blue-200 text-blue-700'
                  }`}>
                    {row.status}
                  </span>
                </td>
                <td className="px-6 py-4 text-right">
                  <button className="text-brand-600 hover:text-brand-700 font-medium inline-flex items-center gap-1">
                    Review <ArrowRight className="w-4 h-4" />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
