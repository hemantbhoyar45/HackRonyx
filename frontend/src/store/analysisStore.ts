import { create } from 'zustand';
import { WATER_BODIES_REGISTRY } from '../data/waterBodies';
import { AnalysisRequest } from '../types/analysis';

interface AnalysisState {
  selectedWaterBody: string;
  selectedWaterBodyName: string;
  startDate: string;
  endDate: string;
  customAOI: GeoJSON.Feature | GeoJSON.FeatureCollection | null;
  isAnalyzing: boolean;
  analysisReady: boolean;
  
  // Actions
  setSelectedWaterBody: (name: string) => void;
  setStartDate: (date: string) => void;
  setEndDate: (date: string) => void;
  setCustomAOI: (aoi: GeoJSON.Feature | GeoJSON.FeatureCollection | null) => void;
  setIsAnalyzing: (isAnalyzing: boolean) => void;
  getAnalysisRequest: () => AnalysisRequest | null;
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
