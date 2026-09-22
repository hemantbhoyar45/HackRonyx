import React from 'react';
import WaterBodySelector from '../../components/dashboard/WaterBodySelector';
import DateRangeSelector from '../../components/dashboard/DateRangeSelector';
import MapView from '../../components/map/MapView';
import { AlertTriangle, Activity, CheckCircle2, Info } from 'lucide-react';

export default function Dashboard() {
  return (
    <div className="flex flex-col h-full gap-4">
      {/* Top Controls */}
      <div className="bg-white p-4 rounded-xl shadow-sm border border-slate-200 flex items-end gap-6 shrink-0">
        <div className="w-80">
          <WaterBodySelector />
        </div>
        <div className="w-[400px]">
          <DateRangeSelector />
        </div>
        <button className="h-[38px] px-6 bg-brand-600 hover:bg-brand-700 text-white text-sm font-semibold rounded-md shadow-sm transition-colors ml-auto">
          Analyze Area
        </button>
      </div>

      <div className="flex flex-1 gap-4 min-h-0">
        {/* Main Map Area */}
        <div className="flex-[2] bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden flex flex-col relative">
          <MapView />
        </div>

        {/* Right Info Panels */}
        <div className="flex-1 flex flex-col gap-4 overflow-y-auto pr-1">
          {/* Status Card */}
          <div className="bg-white p-5 rounded-xl shadow-sm border border-slate-200">
            <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-3">Current Status</h3>
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-amber-100 flex items-center justify-center text-amber-600">
                <AlertTriangle className="w-5 h-5" />
              </div>
              <div>
                <div className="text-lg font-bold text-slate-800">Potential Anomaly</div>
                <div className="text-sm text-slate-500">Based on satellite observation</div>
              </div>
            </div>
          </div>

          {/* Metrics Grid */}
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-white p-4 rounded-xl shadow-sm border border-slate-200">
              <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-1">Priority Score</h3>
              <div className="text-2xl font-bold text-red-600">75<span className="text-sm text-slate-400 font-normal">/100</span></div>
            </div>
            <div className="bg-white p-4 rounded-xl shadow-sm border border-slate-200">
              <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-1">Confidence</h3>
              <div className="text-2xl font-bold text-slate-700">82%</div>
            </div>
          </div>

          <div className="bg-white p-4 rounded-xl shadow-sm border border-slate-200">
            <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-1">Affected Area</h3>
            <div className="text-xl font-bold text-slate-700">12.4 <span className="text-sm text-slate-500 font-medium">km²</span></div>
          </div>

          {/* Indicators */}
          <div className="bg-white p-5 rounded-xl shadow-sm border border-slate-200">
            <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-4 flex items-center justify-between">
              Indicator Summary
              <Info className="w-4 h-4 text-slate-300" />
            </h3>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium text-slate-600">Turbidity Estimate</span>
                <span className="px-2 py-0.5 rounded text-xs font-semibold bg-red-100 text-red-700">High</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium text-slate-600">Suspended Sediment</span>
                <span className="px-2 py-0.5 rounded text-xs font-semibold bg-amber-100 text-amber-700">Elevated</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium text-slate-600">Chlorophyll-a Index</span>
                <span className="px-2 py-0.5 rounded text-xs font-semibold bg-green-100 text-green-700">Normal</span>
              </div>
            </div>
          </div>

          {/* Historical Baseline */}
          <div className="bg-white p-5 rounded-xl shadow-sm border border-slate-200 flex-1">
             <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-4 flex items-center justify-between">
              Historical Comparison
              <Activity className="w-4 h-4 text-slate-300" />
            </h3>
            <div className="h-32 bg-slate-50 rounded-lg border border-slate-100 flex items-center justify-center text-sm text-slate-400 font-medium">
              [ Mock Chart Placeholder ]
            </div>
            <p className="text-xs text-slate-500 mt-3 leading-relaxed">
              Current observation deviates significantly from the 3-year historical baseline for this date range.
            </p>
          </div>

        </div>
      </div>
    </div>
  );
}
