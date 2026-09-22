import React from 'react';
import { Database, Activity, CheckCircle, Map, Layers, FileWarning } from 'lucide-react';

export default function Methodology() {
  const steps = [
    { icon: Database, title: "1. Satellite Data Retrieval", desc: "Acquisition of Sentinel-2 (primary) and Landsat 8/9 data via Google Earth Engine." },
    { icon: Layers, title: "2. Preprocessing & Water Mask", desc: "Cloud/shadow masking and generation of precise water boundaries using NDWI/MNDWI." },
    { icon: Activity, title: "3. Spectral Indicators", desc: "Calculation of satellite-observable indicators (Turbidity, Chlorophyll-a index, Suspended Sediment)." },
    { icon: Map, title: "4. Historical Baseline", desc: "Comparison of current spectral values against multi-year historical averages for the specific water body and season." },
    { icon: FileWarning, title: "5. Anomaly Detection & Priority", desc: "Fusion of multi-indicator evidence to generate a priority score and confidence metric." },
    { icon: CheckCircle, title: "6. Ground Validation", desc: "Alerts are sent for physical ground and laboratory testing. The platform highlights potential anomalies, not confirmed contamination." },
  ];

  return (
    <div className="max-w-4xl mx-auto w-full">
      <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
        <div className="p-8 border-b border-slate-200">
          <h2 className="text-2xl font-bold text-slate-800">System Methodology</h2>
          <p className="text-slate-500 mt-2 text-lg">
            This platform identifies satellite-observable anomalies to prioritize ground investigation.
          </p>
          
          <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg flex items-start gap-4">
            <div className="mt-0.5 text-blue-600">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
            </div>
            <div>
              <h4 className="font-semibold text-blue-900">Important Product Boundary</h4>
              <p className="text-sm text-blue-800 mt-1 leading-relaxed">
                The system does <strong>not</strong> independently confirm contamination or pollution. It flags <em>potential water quality anomalies</em> based on deviations from historical optical patterns. Ground and laboratory testing remain the authoritative validation layer.
              </p>
            </div>
          </div>
        </div>

        <div className="p-8">
          <h3 className="text-lg font-bold text-slate-800 mb-6">Processing Pipeline</h3>
          
          <div className="relative">
            <div className="absolute left-6 top-4 bottom-4 w-0.5 bg-slate-200"></div>
            
            <div className="space-y-8 relative">
              {steps.map((step, i) => (
                <div key={i} className="flex gap-6 relative">
                  <div className="w-12 h-12 rounded-full bg-white border-2 border-brand-500 flex items-center justify-center shrink-0 shadow-sm z-10 text-brand-600">
                    <step.icon className="w-5 h-5" />
                  </div>
                  <div className="pt-2">
                    <h4 className="font-bold text-slate-800 text-lg">{step.title}</h4>
                    <p className="text-slate-600 mt-1">{step.desc}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
