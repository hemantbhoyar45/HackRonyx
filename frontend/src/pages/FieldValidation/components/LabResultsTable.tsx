import React from 'react';
import { LabResult } from '../../../../types/validation';

interface LabResultsTableProps {
  results: LabResult[];
}

export function LabResultsTable({ results }: LabResultsTableProps) {
  if (!results || results.length === 0) {
    return (
      <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-200 mt-6">
        <h2 className="text-lg font-bold text-slate-800 mb-4">Lab Results</h2>
        <div className="text-slate-500 italic text-sm text-center py-4">No lab results available yet.</div>
      </div>
    );
  }

  return (
    <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-200 mt-6">
      <h2 className="text-lg font-bold text-slate-800 mb-4">Lab Results</h2>
      <div className="overflow-x-auto">
        <table className="w-full text-left text-sm border-collapse">
          <thead>
            <tr className="border-b border-slate-200 text-slate-500 font-medium">
              <th className="pb-3 px-2">Parameter</th>
              <th className="pb-3 px-2">Value</th>
              <th className="pb-3 px-2">Unit</th>
              <th className="pb-3 px-2">Method</th>
              <th className="pb-3 px-2">Date Added</th>
            </tr>
          </thead>
          <tbody>
            {results.map((r, i) => (
              <tr key={r.lab_result_id} className={`border-b border-slate-100 ${i % 2 === 0 ? 'bg-slate-50' : 'bg-white'} hover:bg-slate-100`}>
                <td className="py-3 px-2 font-medium text-slate-800">{r.parameter_name}</td>
                <td className="py-3 px-2">{r.value !== undefined ? r.value : '-'}</td>
                <td className="py-3 px-2 text-slate-500">{r.unit}</td>
                <td className="py-3 px-2 text-slate-500">{r.method || '-'}</td>
                <td className="py-3 px-2 text-slate-500">{new Date(r.created_at).toLocaleDateString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
