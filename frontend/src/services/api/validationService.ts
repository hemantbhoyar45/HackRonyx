import type {
  FieldSample,
  FieldSampleCreate,
  LabResult,
  LabResultCreate,
  ValidationRecord,
  ValidationResult,
  ValidationStatusUpdate,
  ValidationStatusHistory,
  ValidationListResponse
} from '../../types/validation';

const API_BASE = 'http://localhost:8000/api/validation';

export const validationService = {
  // Field Samples
  createSample: async (data: FieldSampleCreate): Promise<FieldSample> => {
    const response = await fetch(`${API_BASE}/samples`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    if (!response.ok) throw new Error('Failed to create field sample');
    return response.json();
  },

  getSample: async (sampleId: string): Promise<FieldSample> => {
    const response = await fetch(`${API_BASE}/samples/${sampleId}`);
    if (!response.ok) throw new Error('Failed to fetch field sample');
    return response.json();
  },

  listSamples: async (): Promise<FieldSample[]> => {
    const response = await fetch(`${API_BASE}/samples`);
    if (!response.ok) throw new Error('Failed to list field samples');
    return response.json();
  },

  // Lab Results
  addLabResult: async (sampleId: string, data: LabResultCreate): Promise<LabResult> => {
    const response = await fetch(`${API_BASE}/samples/${sampleId}/lab-results`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    if (!response.ok) throw new Error('Failed to add lab result');
    return response.json();
  },

  getLabResults: async (sampleId: string): Promise<LabResult[]> => {
    const response = await fetch(`${API_BASE}/samples/${sampleId}/lab-results`);
    if (!response.ok) throw new Error('Failed to fetch lab results');
    return response.json();
  },

  // Validation Records
  listValidations: async (): Promise<ValidationListResponse> => {
    const response = await fetch(`${API_BASE}/validations`);
    if (!response.ok) throw new Error('Failed to fetch validations');
    return response.json();
  },

  getValidation: async (validationId: string): Promise<ValidationRecord> => {
    const response = await fetch(`${API_BASE}/${validationId}`);
    if (!response.ok) throw new Error('Failed to fetch validation record');
    return response.json();
  },

  updateStatus: async (validationId: string, data: ValidationStatusUpdate): Promise<ValidationRecord> => {
    const response = await fetch(`${API_BASE}/${validationId}/status`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    if (!response.ok) throw new Error('Failed to update validation status');
    return response.json();
  },

  getHistory: async (validationId: string): Promise<ValidationStatusHistory[]> => {
    const response = await fetch(`${API_BASE}/${validationId}/history`);
    if (!response.ok) throw new Error('Failed to fetch validation history');
    return response.json();
  },

  runComparison: async (validationId: string, anomalyContext?: any): Promise<ValidationResult> => {
    const response = await fetch(`${API_BASE}/${validationId}/compare`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(anomalyContext || {})
    });
    if (!response.ok) throw new Error('Failed to run comparison');
    return response.json();
  },

  // Lookups
  getValidationsByAlert: async (alertId: string): Promise<ValidationRecord[]> => {
    const response = await fetch(`${API_BASE}/by-alert/${alertId}`);
    if (!response.ok) throw new Error('Failed to fetch validations by alert');
    return response.json();
  },

  // Demo
  getDemoValidation: async (): Promise<any> => {
    const response = await fetch(`${API_BASE}/demo`);
    if (!response.ok) throw new Error('Failed to fetch demo validation');
    return response.json();
  }
};
