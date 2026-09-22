import React from 'react';
import { Download, FileText, Calendar, MapPin } from 'lucide-react';
import WaterBodySelector from '../../components/dashboard/WaterBodySelector';
import DateRangeSelector from '../../components/dashboard/DateRangeSelector';

export default function DownloadReport() {
  return (
    <div className="max-w-3xl mx-auto w-full">
      <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
        <div className="p-6 border-b border-slate-200">
          <h2 className="text-lg font-bold text-slate-800 flex items-center gap-2">
            <FileText className="w-5 h-5 text-brand-600" />
            Generate Water Quality Report
          </h2>
          <p className="text-sm text-slate-500 mt-1">
            Export a detailed PDF report containing satellite evidence, historical baseline comparisons, and investigation recommendations for official use.
          </p>
        </div>
        
        <div className="p-6 space-y-8">
          <div className="grid grid-cols-2 gap-8">
            <div className="space-y-6">
              <div>
                <h3 className="text-sm font-bold text-slate-800 mb-3 flex items-center gap-2">
                  <MapPin className="w-4 h-4 text-slate-400" /> Location Details
                </h3>
                <WaterBodySelector />
              </div>
              
              <div>
                <h3 className="text-sm font-bold text-slate-800 mb-3 flex items-center gap-2">
                  <Calendar className="w-4 h-4 text-slate-400" /> Time Period
                </h3>
                <DateRangeSelector />
              </div>
            </div>
            
            <div className="bg-slate-50 p-5 rounded-lg border border-slate-200">
              <h3 className="text-sm font-bold text-slate-800 mb-4">Report Contents</h3>
              <ul className="space-y-3 text-sm text-slate-600">
                <li className="flex items-start gap-2">
                  <CheckIcon /> Executive Summary & Status
                </li>
                <li className="flex items-start gap-2">
                  <CheckIcon /> Satellite Imagery (Sentinel-2)
                </li>
                <li className="flex items-start gap-2">
                  <CheckIcon /> Spectral Indicator Maps
                </li>
                <li className="flex items-start gap-2">
                  <CheckIcon /> Historical Baseline Charts
                </li>
                <li className="flex items-start gap-2">
                  <CheckIcon /> Anomaly & Confidence Scores
                </li>
                <li className="flex items-start gap-2">
                  <CheckIcon /> Recommended Ground Actions
                </li>
              </ul>
            </div>
          </div>
          
          <div className="pt-6 border-t border-slate-200 flex justify-end gap-4">
            <button className="px-6 py-2.5 bg-white border border-slate-300 rounded-md text-sm font-semibold text-slate-700 hover:bg-slate-50 transition-colors">
              Preview
            </button>
            <button className="flex items-center gap-2 px-6 py-2.5 bg-brand-600 hover:bg-brand-700 text-white rounded-md text-sm font-semibold shadow-sm transition-colors">
              <Download className="w-4 h-4" />
              Generate & Download PDF
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

function CheckIcon() {
  return (
    <svg className="w-4 h-4 text-brand-500 mt-0.5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7"></path>
    </svg>
  );
}
