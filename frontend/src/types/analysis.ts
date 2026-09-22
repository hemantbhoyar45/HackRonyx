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


export interface IndicatorStatistics {
  mean: number;
  median: number;
  min: number;
  max: number;
  std: number;
  percentile_10: number;
  percentile_25: number;
  percentile_75: number;
  percentile_90: number;
  valid_pixel_count: number;
}

export interface IndicatorResult {
  indicator_name: string;
  indicator_type: string;
  formula: string;
  bands_used: string[];
  units: string;
  calibration_status: string;
  statistics: IndicatorStatistics;
  valid_percentage: number;
  raster_reference?: string;
}

export interface ZoneIndicatorResult {
  zone_id: string;
  water_area_km2: number;
  valid_pixel_count: number;
  geometry: GeoJSON.Feature | GeoJSON.FeatureCollection | null;
  indicators: Record<string, IndicatorResult>;
}

export interface QualityMetadata {
  total_water_pixels: number;
  acquisition_date?: string;
  sensor: string;
  scene_id: string;
  water_body_id: string;
}

export interface IndicatorsRequest {
  water_body_id: string;
  scene_id: string;
  aoi: GeoJSON.Feature | GeoJSON.FeatureCollection | null;
  indicators?: string[];
}

export interface IndicatorsResponse {
  status: "success" | "error";
  message: string;
  data_source_mode: "live" | "demo";
  quality_metadata: QualityMetadata;
  global_indicators: Record<string, IndicatorResult>;
  zones: ZoneIndicatorResult[];
}

// ──────────────────────────────────────────────────────────
//  Prompt 07 — Historical Baseline & Time-Series
// ──────────────────────────────────────────────────────────

export interface HistoricalRequest {
  water_body_id: string;
  aoi?: GeoJSON.Feature | GeoJSON.FeatureCollection | null;
  start_date: string;
  end_date: string;
  zone_id?: string;
  max_cloud_pct?: number;
  min_valid_water_pixels?: number;
}

export interface HistoricalObservationRecord {
  scene_id: string;
  acquisition_date: string;
  sensor: string;
  water_area_km2: number;
  valid_pixel_count: number;
  observation_status: string;
  ndti_median: number;
  ndci_median: number;
  fai_median: number;
  suspended_sediment_median: number;
}

export interface TimeSeriesPoint {
  date: string;
  scene_id: string;
  median: number;
  mean: number;
  std: number;
  observation_status: string;
}

export interface HistoricalResponse {
  status: string;
  data_source_mode: string;
  water_body_id: string;
  zone_id: string;
  start_date: string;
  end_date: string;
  total_scenes_found: number;
  valid_observations: number;
  rejected_observations: number;
  observations: HistoricalObservationRecord[];
  time_series: Record<string, TimeSeriesPoint[]>;
  message: string;
}

export interface BaselineStats {
  month: number;
  observation_count: number;
  median: number | null;
  mean: number | null;
  std: number | null;
  mad: number | null;
  p10: number | null;
  p25: number | null;
  p75: number | null;
  p90: number | null;
  baseline_status: "available" | "insufficient_history";
}

export interface DeviationResult {
  absolute: number | null;
  relative: number | null;
  robust: number | null;
}

export interface BaselineCompareResponse {
  water_body_id: string;
  zone_id: string;
  indicator: string;
  current_value: number;
  current_date: string;
  baseline: BaselineStats;
  deviation: DeviationResult;
}


