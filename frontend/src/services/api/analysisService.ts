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
};

