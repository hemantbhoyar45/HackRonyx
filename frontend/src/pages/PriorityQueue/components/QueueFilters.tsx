import React from 'react';
import { Search, Filter, X } from 'lucide-react';

export interface FiltersState {
  search: string;
  water_body_id: string;
  priority_band: string;
  severity: string;
  status: string;
  primary_indicator: string;
}

interface Props {
  filters: FiltersState;
  onFilterChange: (filters: FiltersState) => void;
  onReset: () => void;
}

export function QueueFilters({ filters, onFilterChange, onReset }: Props) {
  const handleChange = (e: React.ChangeEvent<HTMLSelectElement | HTMLInputElement>) => {
    onFilterChange({
      ...filters,
      [e.target.name]: e.target.value
    });
  };

  const activeFilterCount = Object.entries(filters).filter(([k, v]) => k !== 'search' && v !== '').length;

  return (
    <div className="p-4 border-b border-slate-200 bg-slate-50 flex flex-col md:flex-row gap-4 justify-between items-center">
      <div className="relative w-full md:w-96">
        <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
        <input 
          type="text" 
          name="search"
          value={filters.search}
          onChange={handleChange}
          placeholder="Search water body, zone, alert ID..." 
          className="w-full pl-9 pr-4 py-2 bg-white border border-slate-300 rounded-md text-sm focus:ring-brand-500 focus:border-brand-500"
        />
      </div>
      
      <div className="flex flex-wrap items-center gap-2 w-full md:w-auto">
        <select name="water_body_id" value={filters.water_body_id} onChange={handleChange} className="border border-slate-300 bg-white rounded-md text-sm px-3 py-2">
          <option value="">All Water Bodies</option>
          <option value="gosikhurd-reservoir">Gosikhurd Reservoir</option>
          <option value="godavari-river-segment">Godavari River Segment</option>
          <option value="wainganga-river-segment">Wainganga River Segment</option>
          <option value="jaikwadi-reservoir">Jaikwadi Reservoir</option>
        </select>
        
        <select name="priority_band" value={filters.priority_band} onChange={handleChange} className="border border-slate-300 bg-white rounded-md text-sm px-3 py-2">
          <option value="">All Priorities</option>
          <option value="CRITICAL">Critical</option>
          <option value="VERY HIGH">Very High</option>
          <option value="HIGH">High</option>
          <option value="MODERATE">Moderate</option>
        </select>
        
        <select name="severity" value={filters.severity} onChange={handleChange} className="border border-slate-300 bg-white rounded-md text-sm px-3 py-2">
          <option value="">All Severities</option>
          <option value="CRITICAL">Critical</option>
          <option value="HIGH">High</option>
          <option value="MODERATE">Moderate</option>
          <option value="LOW">Low</option>
        </select>

        <select name="status" value={filters.status} onChange={handleChange} className="border border-slate-300 bg-white rounded-md text-sm px-3 py-2">
          <option value="">All Statuses</option>
          <option value="ACTIVE">Active</option>
          <option value="ACKNOWLEDGED">Acknowledged</option>
          <option value="UNDER_INVESTIGATION">Under Investigation</option>
          <option value="RESOLVED">Resolved</option>
          <option value="DISMISSED">Dismissed</option>
        </select>

        {activeFilterCount > 0 && (
          <button onClick={onReset} className="ml-2 text-slate-500 hover:text-slate-700 p-1 flex items-center gap-1 text-sm font-medium">
            <X className="w-4 h-4" /> Reset
          </button>
        )}
      </div>
    </div>
  );
}
