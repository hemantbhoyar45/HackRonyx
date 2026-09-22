import React from 'react';
import { MapPin } from 'lucide-react';

const WATER_BODIES = [
  "Gosikhurd Reservoir",
  "Godavari River \u2013 Selected Segment",
  "Wainganga River \u2013 Selected Segment",
  "Jaikwadi Reservoir",
  "Custom AOI"
];

export default function WaterBodySelector() {
  return (
    <div className="flex flex-col gap-1.5">
      <label className="text-sm font-semibold text-slate-700">Water Body</label>
      <div className="relative">
        <MapPin className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
        <select className="w-full pl-9 pr-4 py-2 bg-white border border-slate-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-brand-500 text-sm font-medium text-slate-700 appearance-none cursor-pointer">
          {WATER_BODIES.map(wb => (
            <option key={wb} value={wb}>{wb}</option>
          ))}
        </select>
        <div className="absolute inset-y-0 right-0 flex items-center px-2 pointer-events-none">
          <svg className="w-4 h-4 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7"></path></svg>
        </div>
      </div>
    </div>
  );
}
