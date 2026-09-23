import React from 'react';
import { Database, Activity, CheckCircle, Map, Layers, FileWarning, ShieldAlert, Cpu } from 'lucide-react';

export default function Methodology() {
  const steps = [
    { icon: Database, title: "1. Satellite Data Retrieval", desc: "Acquisition of Sentinel-2 (primary) and Landsat 8/9 data via Google Earth Engine." },
    { icon: Layers, title: "2. Preprocessing & Water Mask", desc: "Cloud/shadow masking and generation of precise water boundaries using NDWI/MNDWI." },
    { icon: Activity, title: "3. Spectral Indicators", desc: "Calculation of satellite-observable indicators (NDTI, Suspended Sediment, NDCI, FAI)." },
    { icon: Map, title: "4. Historical Baseline & Time-Series", desc: "Comparison of current spectral values against multi-year historical seasonal baselines (median & MAD)." },
    { icon: Cpu, title: "5. AI & Statistical Anomaly Detection", desc: "Two-stage detection using MAD Z-score thresholding and unsupervised Isolation Forest." },
    { icon: ShieldAlert, title: "6. Multi-Indicator Evidence Fusion & Priority", desc: "Combines NDTI, Suspended Sediment, NDCI, and FAI into a deterministic 0–100 Investigation Priority Score." },
    { icon: Activity, title: "7. Priority Queue & Investigation Workflow", desc: "Operational queue that prioritizes flagged zones for investigation. Maintains status and audit history for analysts." },
    { icon: CheckCircle, title: "8. Ground Validation", desc: "Decision-support layer prioritizing ground investigation. The platform highlights potential anomalies, not confirmed contamination." },
  ];

  return (
    <div className="max-w-4xl mx-auto w-full">
      <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
        <div className="p-8 border-b border-slate-200">
          <h2 className="text-2xl font-bold text-slate-800">System Methodology</h2>
          <p className="text-slate-500 mt-2 text-lg">
            Multi-Indicator Evidence Fusion &amp; Investigation Priority Scoring
          </p>
          
          <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg flex items-start gap-4">
            <div className="mt-0.5 text-blue-600">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
            </div>
            <div>
              <h4 className="font-semibold text-blue-900">Important Product &amp; Scientific Boundary</h4>
              <p className="text-sm text-blue-800 mt-1 leading-relaxed">
                The investigation priority score is a decision-support metric used to prioritize ground investigation of satellite-observable anomalies. 
                The Priority Queue prioritizes regions for investigation based on satellite-observable evidence. It does not independently confirm contamination, illegal discharge, or pollutant concentration.
              </p>
            </div>
          </div>
        </div>

        <div className="p-8">
          <h3 className="text-lg font-bold text-slate-800 mb-4">Multi-Indicator Evidence Fusion Architecture</h3>
          <div className="bg-slate-900 text-slate-200 p-6 rounded-xl font-mono text-xs mb-8 overflow-x-auto space-y-2">
            <div className="text-cyan-400 font-bold">INDICATORS: NDTI (0.30) | Suspended Sediment (0.25) | NDCI (0.20) | FAI (0.25)</div>
            <div className="text-slate-400">  ↓ Weighted Evidence Fusion (Robust Deviation Normalization 0–1)</div>
            <div className="text-slate-400">  ↓ Multi-Indicator Agreement + Data Quality + Historical Support</div>
            <div className="text-amber-400">  ↓ Signal Severity (0–1) &amp; Analytical Confidence (0–100%)</div>
            <div className="text-emerald-400 font-bold">  ↓ INVESTIGATION PRIORITY SCORE: 0–100</div>
          </div>

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
                    <p className="text-slate-600 mt-1 text-sm">{step.desc}</p>
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
