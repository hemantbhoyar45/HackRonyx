import { create } from 'zustand';
import { WATER_BODIES_REGISTRY } from '../data/waterBodies';
import type { AnalysisRequest, SceneSearchResponse, PreprocessingResult, WaterMaskResult, IndicatorsResponse, HistoricalResponse } from '../types/analysis';

interface AnalysisState {
  selectedWaterBody: string;
  selectedWaterBodyName: string;
  startDate: string;
  endDate: string;
  customAOI: GeoJSON.Feature | GeoJSON.FeatureCollection | null;
  isAnalyzing: boolean;
  analysisReady: boolean;
  
  // Pipeline State
  sceneSearchStatus: 'idle' | 'searching' | 'done' | 'error';
  sceneSearchResult: SceneSearchResponse | null;
  selectedSceneId: string | null;
  preprocessingStatus: 'idle' | 'processing' | 'done' | 'error';
  preprocessingResult: PreprocessingResult | null;
  waterDetectionStatus: 'idle' | 'processing' | 'done' | 'error';
  waterMaskResult: WaterMaskResult | null;
  indicatorsStatus: 'idle' | 'processing' | 'done' | 'error';
  indicatorsResult: IndicatorsResponse | null;
  activeMapLayer: string | null; // e.g., 'water_mask', 'ndti', 'fai'

  // Prompt 07 — Historical Baseline
  historicalStatus: 'idle' | 'loading' | 'done' | 'error';
  historicalResult: HistoricalResponse | null;
  historicalLookback: '1yr' | '2yr'; // selector UI state
  
  // Actions
  setSelectedWaterBody: (name: string) => void;
  setStartDate: (date: string) => void;
  setEndDate: (date: string) => void;
  setCustomAOI: (aoi: GeoJSON.Feature | GeoJSON.FeatureCollection | null) => void;
  setIsAnalyzing: (isAnalyzing: boolean) => void;
  getAnalysisRequest: () => AnalysisRequest | null;
  
  setSceneSearchStatus: (status: 'idle' | 'searching' | 'done' | 'error') => void;
  setSceneSearchResult: (result: SceneSearchResponse | null) => void;
  setSelectedSceneId: (id: string | null) => void;
  setPreprocessingStatus: (status: 'idle' | 'processing' | 'done' | 'error') => void;
  setPreprocessingResult: (result: PreprocessingResult | null) => void;
  setWaterDetectionStatus: (status: 'idle' | 'processing' | 'done' | 'error') => void;
  setWaterMaskResult: (result: WaterMaskResult | null) => void;
  setIndicatorsStatus: (status: 'idle' | 'processing' | 'done' | 'error') => void;
  setIndicatorsResult: (result: IndicatorsResponse | null) => void;
  setActiveMapLayer: (layerId: string | null) => void;

  // Prompt 07 actions
  setHistoricalStatus: (status: 'idle' | 'loading' | 'done' | 'error') => void;
  setHistoricalResult: (result: HistoricalResponse | null) => void;
  setHistoricalLookback: (v: '1yr' | '2yr') => void;

  resetPipeline: () => void;
}

export const useAnalysisStore = create<AnalysisState>((set, get) => ({
  selectedWaterBody: "Gosikhurd Reservoir",
  selectedWaterBodyName: "Gosikhurd Reservoir",
  // Default to last 7 days
  startDate: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
  endDate: new Date().toISOString().split('T')[0],
  customAOI: null,
  isAnalyzing: false,
  analysisReady: false,

  sceneSearchStatus: 'idle',
  sceneSearchResult: null,
  selectedSceneId: null,
  preprocessingStatus: 'idle',
  preprocessingResult: null,
  waterDetectionStatus: 'idle',
  waterMaskResult: null,
  indicatorsStatus: 'idle',
  indicatorsResult: null,
  activeMapLayer: 'water_mask',

  historicalStatus: 'idle',
  historicalResult: null,
  historicalLookback: '2yr',

  setSelectedWaterBody: (name) => {
    // We get the name from the selector, find the corresponding ID
    const entry = Object.values(WATER_BODIES_REGISTRY).find(wb => wb.name === name);
    if (entry) {
      set({ 
        selectedWaterBody: entry.id,
        selectedWaterBodyName: name,
        // Reset custom AOI if we switch to predefined
        customAOI: name === "Custom AOI" ? get().customAOI : null
      });
    }
  },

  setStartDate: (date) => set({ startDate: date }),
  setEndDate: (date) => set({ endDate: date }),
  
  setCustomAOI: (aoi) => set({ customAOI: aoi }),

  setIsAnalyzing: (isAnalyzing) => set({ isAnalyzing }),

  setSceneSearchStatus: (status) => set({ sceneSearchStatus: status }),
  setSceneSearchResult: (result) => set({ sceneSearchResult: result }),
  setSelectedSceneId: (id) => set({ selectedSceneId: id }),
  setPreprocessingStatus: (status) => set({ preprocessingStatus: status }),
  setPreprocessingResult: (result) => set({ preprocessingResult: result }),
  setWaterDetectionStatus: (status) => set({ waterDetectionStatus: status }),
  setWaterMaskResult: (result) => set({ waterMaskResult: result }),
  setIndicatorsStatus: (status) => set({ indicatorsStatus: status }),
  setIndicatorsResult: (result) => set({ indicatorsResult: result }),
  setActiveMapLayer: (layerId) => set({ activeMapLayer: layerId }),

  setHistoricalStatus: (status) => set({ historicalStatus: status }),
  setHistoricalResult: (result) => set({ historicalResult: result }),
  setHistoricalLookback: (v) => set({ historicalLookback: v }),

  resetPipeline: () => set({
    sceneSearchStatus: 'idle',
    sceneSearchResult: null,
    selectedSceneId: null,
    preprocessingStatus: 'idle',
    preprocessingResult: null,
    waterDetectionStatus: 'idle',
    waterMaskResult: null,
    indicatorsStatus: 'idle',
    indicatorsResult: null,
    activeMapLayer: 'water_mask',
    historicalStatus: 'idle',
    historicalResult: null,
    analysisReady: false,
  }),

  getAnalysisRequest: () => {
    const state = get();
    const config = WATER_BODIES_REGISTRY[state.selectedWaterBody];
    
    if (!config) return null;

    let aoiToUse = config.aoi;
    if (config.type === "custom") {
      aoiToUse = state.customAOI;
    }

    if (!aoiToUse) return null; // Cannot create request without AOI

    return {
      waterBodyId: config.id,
      waterBodyName: config.name,
      aoi: aoiToUse,
      startDate: state.startDate,
      endDate: state.endDate
    };
  }
}));
