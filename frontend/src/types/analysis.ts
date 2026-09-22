export interface AnalysisRequest {
  waterBodyId: string;
  waterBodyName: string;
  aoi: GeoJSON.Feature | GeoJSON.FeatureCollection | null;
  startDate: string;
  endDate: string;
}

export interface WaterBodyConfig {
  id: string;
  name: string;
  type: "reservoir" | "river_segment" | "custom";
  description: string;
  aoi: GeoJSON.Feature | GeoJSON.FeatureCollection | null;
  defaultCenter: [number, number];
  defaultZoom: number;
  aoiStatus: "demo" | "validated" | "drawing" | "ready";
}
