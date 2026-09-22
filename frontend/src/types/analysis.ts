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

export interface SceneMetadata {
  scene_id: string;
  acquisition_date: string | null;
  cloud_percentage: number | null;
  platform: string | null;
  product_id: string | null;
  processing_baseline: string | null;
}

export interface SceneSearchResponse {
  analysis_id: string;
  status: "scenes_found" | "no_data" | "error";
  data_source_mode: "live" | "demo";
  provider: string;
  source: string;
  collection: string;
  water_body_id: string;
  water_body_name?: string;
  start_date: string;
  end_date: string;
  max_cloud_percent: number;
  scene_count: number;
  scenes: SceneMetadata[];
  message: string;
}

export interface PreprocessingRequest {
  scene_id: string;
  water_body_id: string;
  start_date: string;
  end_date: string;
  aoi: GeoJSON.Feature | GeoJSON.FeatureCollection | null;
}

export interface QualityMetadata {
  valid_pixel_percentage: number;
  masked_pixel_percentage: number;
  scene_cloud_percentage: number | null;
  cloud_mask_applied: boolean;
  shadow_mask_applied: boolean;
  snow_mask_applied: boolean;
  aoi_pixel_count: number;
  valid_pixel_count: number;
  quality_status: "good" | "low_quality" | "insufficient";
}

export interface PreprocessingResult {
  scene_id: string;
  acquisition_date: string | null;
  satellite: string;
  dataset: string;
  aoi_id: string;
  start_date: string;
  end_date: string;
  quality: QualityMetadata;
  bands: string[];
  bands_extended: string[];
  reflectance_corrected: boolean;
  status: "success" | "low_quality" | "error";
  data_source_mode: "live" | "demo";
  message: string;
}


export interface WaterMaskRequest {
  scene_id: string;
  water_body_id: string;
  aoi: GeoJSON.Feature | GeoJSON.FeatureCollection | null;
  method?: string;
  threshold_method?: string;
  ndwi_threshold?: number | null;
  mndwi_threshold?: number | null;
  min_component_pixels?: number;
}

export interface IndexMetadata {
  available: boolean;
  threshold: number | null;
}

export interface WaterMaskResult {
  status: "success" | "error" | "low_quality";
  scene_id: string;
  method: string;
  threshold_method: string;
  ndwi: IndexMetadata;
  mndwi: IndexMetadata;
  water_area_km2: number;
  aoi_area_km2: number;
  water_coverage_percentage: number;
  geometry: GeoJSON.FeatureCollection;
  quality_status: string | null;
  message: string;
  data_source_mode: "live" | "demo";
}

