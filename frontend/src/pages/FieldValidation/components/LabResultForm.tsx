import React, { useState } from 'react';
import { LabResultCreate } from '../../../../types/validation';

interface LabResultFormProps {
  validationId: string;
  onSubmit: (data: LabResultCreate) => Promise<void>;
  isSubmitting?: boolean;
}

export function LabResultForm({ validationId, onSubmit, isSubmitting }: LabResultFormProps) {
  const [formData, setFormData] = useState<Partial<LabResultCreate>>({
    validation_id: validationId,
    parameter_name: '',
    value: undefined,
    unit: '',
    method: '',
    laboratory_name: '',
    laboratory_report_id: '',
    notes: ''
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.parameter_name) {
      alert("Parameter Name is required.");
      return;
    }
    onSubmit(formData as LabResultCreate);
    // Reset form after successful submit
    setFormData({
      validation_id: validationId,
      parameter_name: '',
      value: undefined,
      unit: '',
      method: '',
      laboratory_name: '',
      laboratory_report_id: '',
      notes: ''
    });
  };

  return (
    <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-200 mt-6">
      <h2 className="text-lg font-bold text-slate-800 mb-4">Add Lab Result</h2>
      <form onSubmit={handleSubmit} className="space-y-4">
        
        <div className="grid grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Parameter *</label>
            <input 
              type="text" 
              placeholder="e.g., Turbidity"
              className="w-full px-3 py-2 border border-slate-300 rounded-md focus:outline-none focus:ring-1 focus:ring-brand-500"
              value={formData.parameter_name}
              onChange={(e) => setFormData({...formData, parameter_name: e.target.value})}
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Value</label>
            <input 
              type="number" 
              step="any"
              className="w-full px-3 py-2 border border-slate-300 rounded-md focus:outline-none focus:ring-1 focus:ring-brand-500"
              value={formData.value || ''}
              onChange={(e) => setFormData({...formData, value: e.target.value ? parseFloat(e.target.value) : undefined})}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Unit</label>
            <input 
              type="text" 
              placeholder="e.g., NTU"
              className="w-full px-3 py-2 border border-slate-300 rounded-md focus:outline-none focus:ring-1 focus:ring-brand-500"
              value={formData.unit}
              onChange={(e) => setFormData({...formData, unit: e.target.value})}
            />
          </div>
        </div>

        <div className="grid grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Method</label>
            <input 
              type="text" 
              className="w-full px-3 py-2 border border-slate-300 rounded-md focus:outline-none focus:ring-1 focus:ring-brand-500"
              value={formData.method}
              onChange={(e) => setFormData({...formData, method: e.target.value})}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Laboratory Name</label>
            <input 
              type="text" 
              className="w-full px-3 py-2 border border-slate-300 rounded-md focus:outline-none focus:ring-1 focus:ring-brand-500"
              value={formData.laboratory_name}
              onChange={(e) => setFormData({...formData, laboratory_name: e.target.value})}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Report ID</label>
            <input 
              type="text" 
              className="w-full px-3 py-2 border border-slate-300 rounded-md focus:outline-none focus:ring-1 focus:ring-brand-500"
              value={formData.laboratory_report_id}
              onChange={(e) => setFormData({...formData, laboratory_report_id: e.target.value})}
            />
          </div>
        </div>

        <div className="flex justify-end pt-2">
          <button 
            type="submit" 
            disabled={isSubmitting}
            className="px-6 py-2 bg-slate-800 hover:bg-slate-900 text-white font-medium rounded-md shadow-sm transition-colors disabled:opacity-50"
          >
            {isSubmitting ? 'Saving...' : 'Add Result'}
          </button>
        </div>
      </form>
    </div>
  );
}
