import React, { useState } from 'react';
import WaterBodySelector from '../../components/dashboard/WaterBodySelector';
import DateRangeSelector from '../../components/dashboard/DateRangeSelector';
import MapView from '../../components/map/MapView';
import AOIInfoPanel from '../../components/dashboard/AOIInfoPanel';
import { AlertTriangle, Activity, Info, CheckCircle2 } from 'lucide-react';
import { useAnalysisStore } from '../../store/analysisStore';
import { analysisService } from '../../services/api/analysisService';

export default function Dashboard() {
  const { getAnalysisRequest, isAnalyzing, setIsAnalyzing } = useAnalysisStore();
  const [statusMessage, setStatusMessage] = useState<{type: 'error' | 'success', text: string} | null>(null);

  const handleAnalyze = async () => {
    setStatusMessage(null);
    const request = getAnalysisRequest();
    
    if (!request) {
      setStatusMessage({ type: 'error', text: 'Please complete your selection and ensure a valid AOI is selected.' });
      return;
    }

    if (new Date(request.startDate) > new Date(request.endDate)) {
      setStatusMessage({ type: 'error', text: 'Start date must be earlier than or equal to the end date.' });
      return;
    }

    setIsAnalyzing(true);
    try {
      await analysisService.prepareAnalysis(request);
      setStatusMessage({ type: 'success', text: 'AOI and date range are ready for satellite analysis.' });
    } catch (err) {
      setStatusMessage({ type: 'error', text: 'Unable to prepare the analysis request. Please try again.' });
    } finally {
      setIsAnalyzing(false);
    }
  };

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
        <button 
          onClick={handleAnalyze}
          disabled={isAnalyzing}
          className="h-[38px] px-6 bg-brand-600 hover:bg-brand-700 disabled:bg-brand-400 text-white text-sm font-semibold rounded-md shadow-sm transition-colors ml-auto flex items-center justify-center min-w-[120px]"
        >
          {isAnalyzing ? "Preparing..." : "Analyze Area"}
        </button>
      </div>
      
      {statusMessage && (
        <div className={`p-4 rounded-lg shadow-sm text-sm font-semibold flex items-center gap-2 ${statusMessage.type === 'error' ? 'bg-red-50 text-red-700 border border-red-200' : 'bg-green-50 text-green-700 border border-green-200'}`}>
          {statusMessage.type === 'error' ? <AlertTriangle className="w-5 h-5" /> : <CheckCircle2 className="w-5 h-5" />}
          {statusMessage.text}
        </div>
      )}

      <div className="flex flex-1 gap-4 min-h-0">
        {/* Main Map Area */}
        <div className="flex-[2] bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden flex flex-col relative">
          <MapView />
        </div>

        {/* Right Info Panels */}
        <div className="flex-1 flex flex-col gap-4 overflow-y-auto pr-1">
          <AOIInfoPanel />

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

        </div>
      </div>
    </div>
  );
}
