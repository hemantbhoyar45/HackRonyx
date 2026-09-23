import React, { useState } from 'react';
import type { FieldSampleCreate } from '../../../types/validation';

interface FieldSampleFormProps {
  initialAlertId?: string;
  initialWaterBodyId?: string;
  initialZoneId?: string;
  initialAnalysisId?: string;
  onSubmit: (data: FieldSampleCreate) => Promise<void>;
  isSubmitting?: boolean;
}

export function FieldSampleForm({
  initialAlertId,
  initialWaterBodyId,
  initialZoneId,
  initialAnalysisId,
  onSubmit,
  isSubmitting
}: FieldSampleFormProps) {
  const [formData, setFormData] = useState<Partial<FieldSampleCreate>>({
    alert_id: initialAlertId || '',
    water_body_id: initialWaterBodyId || '',
    zone_id: initialZoneId || 'zone-main',
    analysis_id: initialAnalysisId || '',
    sample_date: new Date().toISOString().split('T')[0],
    sample_time: '',
    latitude: 0,
    longitude: 0,
    sample_type: 'SURFACE_WATER',
    collected_by: '',
    notes: ''
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // basic validation
    if (!formData.water_body_id || !formData.sample_date || formData.latitude === undefined || formData.longitude === undefined) {
      alert("Please fill in all required fields.");
      return;
    }
    onSubmit(formData as FieldSampleCreate);
  };

  return (
    <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-200">
      <h2 className="text-lg font-bold text-slate-800 mb-4">Field Sample</h2>
      <form onSubmit={handleSubmit} className="space-y-4">
        
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Water Body ID *</label>
            <input 
              type="text" 
              className="w-full px-3 py-2 border border-slate-300 rounded-md focus:outline-none focus:ring-1 focus:ring-brand-500"
              value={formData.water_body_id}
              onChange={(e) => setFormData({...formData, water_body_id: e.target.value})}
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Zone ID</label>
            <input 
              type="text" 
              className="w-full px-3 py-2 border border-slate-300 rounded-md focus:outline-none focus:ring-1 focus:ring-brand-500"
              value={formData.zone_id}
              onChange={(e) => setFormData({...formData, zone_id: e.target.value})}
            />
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Alert ID</label>
            <input 
              type="text" 
              className="w-full px-3 py-2 border border-slate-300 rounded-md focus:outline-none focus:ring-1 focus:ring-brand-500"
              value={formData.alert_id}
              onChange={(e) => setFormData({...formData, alert_id: e.target.value})}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Analysis ID</label>
            <input 
              type="text" 
              className="w-full px-3 py-2 border border-slate-300 rounded-md focus:outline-none focus:ring-1 focus:ring-brand-500"
              value={formData.analysis_id}
              onChange={(e) => setFormData({...formData, analysis_id: e.target.value})}
            />
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Sample Date *</label>
            <input 
              type="date" 
              className="w-full px-3 py-2 border border-slate-300 rounded-md focus:outline-none focus:ring-1 focus:ring-brand-500"
              value={formData.sample_date}
              onChange={(e) => setFormData({...formData, sample_date: e.target.value})}
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Sample Time</label>
            <input 
              type="time" 
              className="w-full px-3 py-2 border border-slate-300 rounded-md focus:outline-none focus:ring-1 focus:ring-brand-500"
              value={formData.sample_time}
              onChange={(e) => setFormData({...formData, sample_time: e.target.value})}
            />
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Latitude *</label>
            <input 
              type="number" 
              step="any"
              className="w-full px-3 py-2 border border-slate-300 rounded-md focus:outline-none focus:ring-1 focus:ring-brand-500"
              value={formData.latitude}
              onChange={(e) => setFormData({...formData, latitude: parseFloat(e.target.value)})}
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Longitude *</label>
            <input 
              type="number" 
              step="any"
              className="w-full px-3 py-2 border border-slate-300 rounded-md focus:outline-none focus:ring-1 focus:ring-brand-500"
              value={formData.longitude}
              onChange={(e) => setFormData({...formData, longitude: parseFloat(e.target.value)})}
              required
            />
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Sample Type</label>
            <select 
              className="w-full px-3 py-2 border border-slate-300 rounded-md focus:outline-none focus:ring-1 focus:ring-brand-500 bg-white"
              value={formData.sample_type}
              onChange={(e) => setFormData({...formData, sample_type: e.target.value})}
            >
              <option value="SURFACE_WATER">Surface Water</option>
              <option value="RESERVOIR_WATER">Reservoir Water</option>
              <option value="RIVER_WATER">River Water</option>
              <option value="LAKE_WATER">Lake Water</option>
              <option value="OTHER">Other</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Collected By</label>
            <input 
              type="text" 
              className="w-full px-3 py-2 border border-slate-300 rounded-md focus:outline-none focus:ring-1 focus:ring-brand-500"
              value={formData.collected_by}
              onChange={(e) => setFormData({...formData, collected_by: e.target.value})}
            />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">Notes</label>
          <textarea 
            className="w-full px-3 py-2 border border-slate-300 rounded-md focus:outline-none focus:ring-1 focus:ring-brand-500"
            rows={3}
            value={formData.notes}
            onChange={(e) => setFormData({...formData, notes: e.target.value})}
          />
        </div>

        <div className="flex justify-end pt-2">
          <button 
            type="submit" 
            disabled={isSubmitting}
            className="px-6 py-2 bg-brand-600 hover:bg-brand-700 text-white font-medium rounded-md shadow-sm transition-colors disabled:opacity-50"
          >
            {isSubmitting ? 'Saving...' : 'Save Field Sample'}
          </button>
        </div>
      </form>
    </div>
  );
}
