import type { AnalysisRequest, SceneSearchResponse } from '../../types/analysis';

const API_BASE = 'http://localhost:8000/api';

export const analysisService = {
  prepareAnalysis: async (request: AnalysisRequest) => {
    try {
      const response = await fetch(`${API_BASE}/analysis/prepare`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          water_body_id: request.waterBodyId,
          water_body_name: request.waterBodyName,
          start_date: request.startDate,
          end_date: request.endDate,
          custom_aoi: request.aoi
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to prepare analysis');
      }

      return await response.json();
    } catch (error) {
      console.error('API Error:', error);
      throw error;
    }
  },

  searchScenes: async (request: AnalysisRequest): Promise<SceneSearchResponse> => {
    try {
      const response = await fetch(`${API_BASE}/analysis/scenes`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          water_body_id: request.waterBodyId,
          water_body_name: request.waterBodyName,
          start_date: request.startDate,
          end_date: request.endDate,
          custom_aoi: request.aoi,
        }),
      });

      if (!response.ok) {
        const errorBody = await response.json().catch(() => ({}));
        throw new Error(errorBody.detail || 'Failed to search satellite scenes');
      }

      return await response.json();
    } catch (error) {
      console.error('Scene search error:', error);
      throw error;
    }
  },

  preprocessScene: async (request: import('../../types/analysis').PreprocessingRequest): Promise<import('../../types/analysis').PreprocessingResult> => {
    try {
      const response = await fetch(`${API_BASE}/analysis/preprocess`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          scene_id: request.scene_id,
          water_body_id: request.water_body_id,
          start_date: request.start_date,
          end_date: request.end_date,
          aoi: request.aoi,
        }),
      });

      if (!response.ok) {
        const errorBody = await response.json().catch(() => ({}));
        throw new Error(errorBody.detail || 'Failed to preprocess satellite scene');
      }

      return await response.json();
    } catch (error) {
      console.error('Preprocessing error:', error);
      throw error;
    }
  },

  detectWater: async (request: import('../../types/analysis').WaterMaskRequest): Promise<import('../../types/analysis').WaterMaskResult> => {
    try {
      const response = await fetch(`${API_BASE}/analysis/water-mask`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        const errorBody = await response.json().catch(() => ({}));
        throw new Error(errorBody.detail || 'Failed to detect water body');
      }

      return await response.json();
    } catch (error) {
      console.error('Water detection error:', error);
      throw error;
    }
  },

  calculateIndicators: async (request: import('../../types/analysis').IndicatorsRequest): Promise<import('../../types/analysis').IndicatorsResponse> => {
    try {
      const response = await fetch(`${API_BASE}/analysis/indicators`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        const errorBody = await response.json().catch(() => ({}));
        throw new Error(errorBody.detail || 'Failed to calculate spectral indicators');
      }

      return await response.json();
    } catch (error) {
      console.error('Indicators error:', error);
      throw error;
    }
  },

  getHistorical: async (request: import('../../types/analysis').HistoricalRequest): Promise<import('../../types/analysis').HistoricalResponse> => {
    try {
      const response = await fetch(`${API_BASE}/analysis/historical`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(request),
      });
      if (!response.ok) {
        const errorBody = await response.json().catch(() => ({}));
        throw new Error(errorBody.detail || 'Failed to retrieve historical observations');
      }
      return await response.json();
    } catch (error) {
      console.error('Historical error:', error);
      throw error;
    }
  },

  compareBaseline: async (
    water_body_id: string,
    zone_id: string,
    indicator: string,
    current_value: number,
    current_date: string,
  ): Promise<import('../../types/analysis').BaselineCompareResponse> => {
    try {
      const response = await fetch(`${API_BASE}/analysis/baseline/compare`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ water_body_id, zone_id, indicator, current_value, current_date }),
      });
      if (!response.ok) {
        const errorBody = await response.json().catch(() => ({}));
        throw new Error(errorBody.detail || 'Baseline comparison failed');
      }
      return await response.json();
    } catch (error) {
      console.error('Baseline compare error:', error);
      throw error;
    }
  },

  detectAnomalies: async (request: import('../../types/analysis').AnomalyRequest): Promise<import('../../types/analysis').AnomalyResponse> => {
    try {
      const response = await fetch(`${API_BASE}/analysis/anomaly`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        const errorBody = await response.json().catch(() => ({}));
        throw new Error(errorBody.detail || 'Failed to detect anomalies');
      }

      return await response.json();
    } catch (error) {
      console.error('Anomaly detection error:', error);
      throw error;
    }
  },

  calculatePriority: async (anomalyResult: import('../../types/analysis').AnomalyResponse): Promise<import('../../types/analysis').PriorityResponse> => {
    try {
      const response = await fetch(`${API_BASE}/analysis/priority`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          water_body_id: anomalyResult.water_body_id,
          scene_id: anomalyResult.scene_id,
          acquisition_date: anomalyResult.acquisition_date,
          anomaly_result: anomalyResult,
        }),
      });

      if (!response.ok) {
        const errorBody = await response.json().catch(() => ({}));
        throw new Error(errorBody.detail || 'Failed to calculate priority score');
      }

      return await response.json();
    } catch (error) {
      console.error('Priority calculation error:', error);
      throw error;
    }
  },

  generateAlerts: async (request: import('../../types/analysis').AlertRequest): Promise<import('../../types/analysis').AlertResponse> => {
    try {
      const response = await fetch(`${API_BASE}/analysis/alert`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        const errorBody = await response.json().catch(() => ({}));
        throw new Error(errorBody.detail || 'Failed to generate explainable alerts');
      }

      return await response.json();
    } catch (error) {
      console.error('Alert generation error:', error);
      throw error;
    }
  },
};
