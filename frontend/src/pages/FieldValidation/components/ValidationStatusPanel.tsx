import React from 'react';
import type { ValidationResult } from '../../../types/validation';
import { CheckCircle, AlertTriangle, HelpCircle, XCircle } from 'lucide-react';

interface ValidationStatusPanelProps {
  result: ValidationResult | null;
  onRunComparison: () => Promise<void>;
  isComparing: boolean;
}

export function ValidationStatusPanel({ result, onRunComparison, isComparing }: ValidationStatusPanelProps) {
  
  if (!result) {
    return (
      <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-200 mt-6 text-center">
        <h2 className="text-lg font-bold text-slate-800 mb-4 text-left">Validation Status</h2>
        <p className="text-slate-500 mb-6 text-sm">Run the validation engine to compare field/lab evidence with the satellite-observable anomaly.</p>
        <button
          onClick={onRunComparison}
          disabled={isComparing}
          className="px-6 py-2 bg-brand-600 hover:bg-brand-700 text-white font-medium rounded-md shadow-sm transition-colors disabled:opacity-50"
        >
          {isComparing ? 'Comparing...' : 'Run Validation Comparison'}
        </button>
      </div>
    );
  }

  const getStatusColor = (status: string) => {
    switch(status) {
      case 'SUPPORTED': return 'bg-green-50 text-green-700 border-green-200';
      case 'NOT_SUPPORTED': return 'bg-red-50 text-red-700 border-red-200';
      default: return 'bg-slate-50 text-slate-700 border-slate-200';
    }
  };

  const getStatusIcon = (status: string) => {
    switch(status) {
      case 'SUPPORTED': return <CheckCircle className="w-8 h-8 text-green-600" />;
      case 'NOT_SUPPORTED': return <XCircle className="w-8 h-8 text-red-600" />;
      case 'INCONCLUSIVE': return <HelpCircle className="w-8 h-8 text-slate-500" />;
      default: return <AlertTriangle className="w-8 h-8 text-slate-500" />;
    }
  };

  return (
    <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-200 mt-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-lg font-bold text-slate-800">Validation Status</h2>
        <button
          onClick={onRunComparison}
          disabled={isComparing}
          className="text-sm px-4 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 font-medium rounded shadow-sm transition-colors disabled:opacity-50"
        >
          {isComparing ? 'Updating...' : 'Re-run Comparison'}
        </button>
      </div>

      <div className={`p-4 rounded-lg border flex items-center gap-4 mb-6 ${getStatusColor(result.validation_status)}`}>
        {getStatusIcon(result.validation_status)}
        <div>
          <h3 className="font-bold text-lg uppercase tracking-wider">{result.validation_status.replace('_', ' ')}</h3>
          <p className="text-sm opacity-90">Evidence Score: {result.validation_evidence_score || 0} / 100</p>
        </div>
      </div>

      <div className="mb-6">
        <h4 className="text-sm font-bold text-slate-800 uppercase tracking-wider mb-2">Why?</h4>
        <p className="text-slate-600 text-sm leading-relaxed bg-slate-50 p-4 rounded-lg border border-slate-100">
          {result.explanation}
        </p>
      </div>

      <div className="grid grid-cols-2 gap-6 mb-6">
        <div>
          <h4 className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-3">Evidence Match</h4>
          <ul className="space-y-2 text-sm">
            <li className="flex justify-between border-b border-slate-100 pb-1">
              <span className="text-slate-500">Temporal Relation</span>
              <span className="font-medium text-slate-800">{result.temporal_relation?.replace(/_/g, ' ') || 'Unknown'}</span>
            </li>
            <li className="flex justify-between border-b border-slate-100 pb-1">
              <span className="text-slate-500">Spatial Relation</span>
              <span className="font-medium text-slate-800">{result.spatial_relation?.replace(/_/g, ' ') || 'Unknown'}</span>
            </li>
            <li className="flex justify-between border-b border-slate-100 pb-1">
              <span className="text-slate-500">Related Parameter</span>
              <span className="font-medium text-slate-800">{result.related_lab_parameter || 'None'}</span>
            </li>
          </ul>
        </div>
        <div>
          <h4 className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-3">Satellite Context</h4>
          <ul className="space-y-2 text-sm">
            <li className="flex justify-between border-b border-slate-100 pb-1">
              <span className="text-slate-500">Indicator</span>
              <span className="font-medium text-slate-800">{result.satellite_indicator?.toUpperCase() || 'N/A'}</span>
            </li>
            <li className="flex justify-between border-b border-slate-100 pb-1">
              <span className="text-slate-500">Deviation</span>
              <span className="font-medium text-slate-800">{result.satellite_deviation ? `+${(result.satellite_deviation * 100).toFixed(1)}%` : 'N/A'}</span>
            </li>
          </ul>
        </div>
      </div>

      <div className="bg-blue-50 border border-blue-200 p-4 rounded-lg flex gap-3">
        <InfoIcon className="w-5 h-5 text-blue-600 shrink-0 mt-0.5" />
        <p className="text-sm text-blue-800 leading-relaxed">
          <strong>Scientific Note:</strong> {result.scientific_note}
        </p>
      </div>

    </div>
  );
}

function InfoIcon(props: any) {
  return (
    <svg {...props} fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
    </svg>
  );
}
