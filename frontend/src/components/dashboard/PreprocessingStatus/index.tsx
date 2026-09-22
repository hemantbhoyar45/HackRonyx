import React from 'react';
import { ShieldCheck, CheckCircle2, AlertTriangle } from 'lucide-react';
import type { PreprocessingResult } from '../../../types/analysis';

interface Props {
  data: PreprocessingResult | null;
  status: 'idle' | 'processing' | 'done' | 'error';
  errorMessage?: string;
}

export default function PreprocessingStatus({ data, status, errorMessage }: Props) {
  if (status === 'idle') {
    return null;
  }

  if (status === 'processing') {
    return (
      <div className="bg-white p-5 rounded-xl shadow-sm border border-slate-200 mt-4">
        <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-3">
          Preprocessing Pipeline
        </h3>
        <div className="flex items-center gap-3 text-slate-500">
          <div className="w-5 h-5 border-2 border-brand-500 border-t-transparent rounded-full animate-spin" />
          <span className="text-sm font-medium">Applying quality masks and preparing bands…</span>
        </div>
      </div>
    );
  }

  if (status === 'error') {
    return (
      <div className="bg-white p-5 rounded-xl shadow-sm border border-red-200 mt-4">
        <h3 className="text-xs font-bold text-red-400 uppercase tracking-wider mb-3">
          Preprocessing Pipeline
        </h3>
        <div className="flex items-center gap-2 text-red-600 text-sm font-medium">
          <AlertTriangle className="w-4 h-4 shrink-0" />
          {errorMessage || 'Preprocessing failed.'}
        </div>
      </div>
    );
  }

  if (!data) return null;

  const isDemo = data.data_source_mode === 'demo';
  const q = data.quality;

  return (
    <div className="bg-white p-5 rounded-xl shadow-sm border border-slate-200 mt-4">
      <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-4 flex items-center justify-between">
        Preprocessing Pipeline
        {isDemo && (
          <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-100 text-amber-700 uppercase">
            Demo
          </span>
        )}
      </h3>

      <div className="space-y-4">
        {/* Steps */}
        <div className="space-y-2">
          <div className="flex items-center gap-2 text-sm text-slate-700">
            <CheckCircle2 className="w-4 h-4 text-green-500" />
            <span className="font-medium">Cloud mask applied</span>
          </div>
          <div className="flex items-center gap-2 text-sm text-slate-700">
            <CheckCircle2 className="w-4 h-4 text-green-500" />
            <span className="font-medium">Shadow mask applied</span>
          </div>
          <div className="flex items-center gap-2 text-sm text-slate-700">
            <CheckCircle2 className="w-4 h-4 text-green-500" />
            <span className="font-medium">AOI clipped</span>
          </div>
          <div className="flex items-center gap-2 text-sm text-slate-700">
            <CheckCircle2 className="w-4 h-4 text-green-500" />
            <span className="font-medium">Required bands prepared ({data.bands.length})</span>
          </div>
        </div>

        <div className="border-t border-slate-100 pt-3">
          <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-3">
            Quality Metrics
          </h4>
          <div className="grid grid-cols-2 gap-3">
            <div className="bg-slate-50 p-2.5 rounded-lg border border-slate-100">
              <div className="text-[10px] font-bold text-slate-500 uppercase">Valid Pixels</div>
              <div className="text-lg font-bold text-slate-800">{q.valid_pixel_percentage.toFixed(1)}%</div>
            </div>
            <div className="bg-slate-50 p-2.5 rounded-lg border border-slate-100">
              <div className="text-[10px] font-bold text-slate-500 uppercase">Masked</div>
              <div className="text-lg font-bold text-slate-600">{q.masked_pixel_percentage.toFixed(1)}%</div>
            </div>
          </div>
          
          {q.scene_cloud_percentage !== null && (
            <div className="mt-2 text-xs text-slate-500 flex items-center justify-between">
              <span>Scene cloud coverage:</span>
              <span className="font-medium">{q.scene_cloud_percentage.toFixed(1)}%</span>
            </div>
          )}
        </div>

        <div className="border-t border-slate-100 pt-3 flex items-center gap-2 text-sm">
          {data.status === 'success' ? (
            <>
              <ShieldCheck className="w-5 h-5 text-green-600" />
              <span className="font-bold text-green-700">Ready for water detection</span>
            </>
          ) : (
            <>
              <AlertTriangle className="w-5 h-5 text-amber-600" />
              <span className="font-bold text-amber-700">Low quality — consider another date</span>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
