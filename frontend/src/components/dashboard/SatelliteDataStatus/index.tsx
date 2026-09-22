import React from 'react';
import { Satellite, Cloud, Calendar, Database, AlertTriangle } from 'lucide-react';
import type { SceneSearchResponse } from '../../../types/analysis';

interface Props {
  data: SceneSearchResponse | null;
  status: 'idle' | 'searching' | 'done' | 'error';
  errorMessage?: string;
}

export default function SatelliteDataStatus({ data, status, errorMessage }: Props) {
  if (status === 'idle') {
    return null;
  }

  if (status === 'searching') {
    return (
      <div className="bg-white p-5 rounded-xl shadow-sm border border-slate-200">
        <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-3">
          Satellite Data
        </h3>
        <div className="flex items-center gap-3 text-slate-500">
          <div className="w-5 h-5 border-2 border-brand-500 border-t-transparent rounded-full animate-spin" />
          <span className="text-sm font-medium">Searching satellite imagery…</span>
        </div>
      </div>
    );
  }

  if (status === 'error') {
    return (
      <div className="bg-white p-5 rounded-xl shadow-sm border border-red-200">
        <h3 className="text-xs font-bold text-red-400 uppercase tracking-wider mb-3">
          Satellite Data
        </h3>
        <div className="flex items-center gap-2 text-red-600 text-sm font-medium">
          <AlertTriangle className="w-4 h-4 shrink-0" />
          {errorMessage || 'Unable to retrieve satellite data.'}
        </div>
      </div>
    );
  }

  if (!data) return null;

  const isDemo = data.data_source_mode === 'demo';

  return (
    <div className="bg-white p-5 rounded-xl shadow-sm border border-slate-200">
      <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-4 flex items-center justify-between">
        Satellite Data
        {isDemo && (
          <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-100 text-amber-700 uppercase">
            Demo
          </span>
        )}
      </h3>

      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2 text-sm text-slate-600">
            <Satellite className="w-4 h-4 text-slate-400" />
            <span className="font-medium">Source</span>
          </div>
          <span className="text-sm font-semibold text-slate-800">{data.source}</span>
        </div>

        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2 text-sm text-slate-600">
            <Database className="w-4 h-4 text-slate-400" />
            <span className="font-medium">Scenes Found</span>
          </div>
          <span className="text-sm font-bold text-brand-700">{data.scene_count}</span>
        </div>

        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2 text-sm text-slate-600">
            <Calendar className="w-4 h-4 text-slate-400" />
            <span className="font-medium">Date Range</span>
          </div>
          <span className="text-sm font-medium text-slate-700">
            {data.start_date} → {data.end_date}
          </span>
        </div>

        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2 text-sm text-slate-600">
            <Cloud className="w-4 h-4 text-slate-400" />
            <span className="font-medium">Max Cloud</span>
          </div>
          <span className="text-sm font-medium text-slate-700">
            ≤ {data.max_cloud_percent}%
          </span>
        </div>
      </div>

      {data.scene_count > 0 && (
        <div className="mt-4 border-t border-slate-100 pt-3">
          <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">
            Scene List
          </h4>
          <div className="max-h-40 overflow-y-auto">
            <table className="w-full text-xs">
              <thead>
                <tr className="text-slate-400 font-semibold border-b border-slate-100">
                  <th className="text-left py-1 pr-2">Date</th>
                  <th className="text-left py-1 pr-2">Platform</th>
                  <th className="text-right py-1">Cloud %</th>
                </tr>
              </thead>
              <tbody>
                {data.scenes.map((scene) => (
                  <tr key={scene.scene_id} className="border-b border-slate-50 text-slate-600">
                    <td className="py-1 pr-2 font-medium">{scene.acquisition_date ?? '—'}</td>
                    <td className="py-1 pr-2">{scene.platform ?? '—'}</td>
                    <td className="py-1 text-right">
                      {scene.cloud_percentage != null ? scene.cloud_percentage.toFixed(1) : '—'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {data.status === 'no_data' && (
        <p className="mt-3 text-xs text-amber-600 font-medium">{data.message}</p>
      )}

      {isDemo && (
        <p className="mt-3 text-xs text-amber-600 font-medium">
          Demo satellite data — Google Earth Engine is not connected.
        </p>
      )}
    </div>
  );
}
