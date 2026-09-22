import { AnalysisRequest } from '../../types/analysis';

export const analysisService = {
  prepareAnalysis: async (request: AnalysisRequest) => {
    try {
      const response = await fetch('http://localhost:8000/api/analysis/prepare', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          water_body_id: request.waterBodyId,
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
  }
};
