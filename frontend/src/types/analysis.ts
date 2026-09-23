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

// ──────────────────────────────────────────────────────────────
// Prompt 08 — Anomaly Detection
// ──────────────────────────────────────────────────────────────

export interface AnomalyRequest {
  water_body_id: string;
  scene_id: string;
  current_date: string;
  zones?: string[];
}

export interface AnomalyFeature {
  indicator_name: string;
  current_value: number;
  baseline_median: number;
  absolute_deviation: number;
  relative_deviation: number;
  robust_deviation: number;
  valid_percentage?: number;
}

export interface MLAnomaly {
  model: string;
  status: string;
  prediction?: number;
  anomaly_score?: number;
}

export interface AnomalyZoneResult {
  zone_id: string;
  indicators: Record<string, AnomalyFeature>;
  statistical_anomaly: boolean;
  statistical_threshold: number;
  ml: MLAnomaly;
  combined_status: 'POTENTIAL_ANOMALY' | 'NO_ANOMALY_SIGNAL' | 'MIXED_EVIDENCE' | 'LOW_QUALITY_OBSERVATION' | 'INSUFFICIENT_HISTORY' | 'INSUFFICIENT_DATA';
  anomaly_score: number;
  quality: Record<string, number>;
  affected_area?: number;
  affected_percentage?: number;
}

export interface AnomalyResponse {
  water_body_id: string;
  scene_id: string;
  acquisition_date: string;
  results: AnomalyZoneResult[];
}

// ──────────────────────────────────────────────────────────────
// Prompt 09 — Multi-Indicator Evidence Fusion & Priority Score
// ──────────────────────────────────────────────────────────────

export interface IndicatorEvidence {
  indicator_name: string;
  current_value: number | null;
  baseline_value: number | null;
  absolute_deviation: number | null;
  relative_deviation: number | null;
  robust_deviation: number | null;
  direction: 'INCREASE' | 'DECREASE' | 'STABLE' | 'UNKNOWN';
  evidence_score: number;
  weight: number;
  weighted_contribution: number;
  available: boolean;
}

export interface PriorityResult {
  water_body_id: string;
  zone_id: string;
  scene_id: string;
  analysis_date: string;
  combined_status?: string;
  combined_evidence: number;
  indicator_agreement_score: number;
  quality_factor: number;
  indicator_completeness: number;
  historical_support: number;
  model_agreement_score: number | null;
  severity: 'LOW' | 'MODERATE-LOW' | 'MODERATE' | 'HIGH' | 'VERY HIGH';
  severity_normalized?: number;
  confidence: number;
  confidence_normalized?: number;
  investigation_priority_score: number;
  priority_band: 'LOW PRIORITY' | 'MEDIUM PRIORITY' | 'HIGH PRIORITY' | 'VERY HIGH PRIORITY';
  primary_driver: string | null;
  supporting_indicators: string[];
  indicators: IndicatorEvidence[];
  evidence_trace?: Record<string, any>;
  affected_area?: number;
}

export interface PriorityRequest {
  water_body_id: string;
  scene_id?: string;
  acquisition_date?: string;
  anomaly_result?: AnomalyResponse | Record<string, any>;
  results?: AnomalyZoneResult[] | Record<string, any>[];
}

export interface PriorityResponse {
  water_body_id: string;
  scene_id: string;
  acquisition_date: string;
  results: PriorityResult[];
}



// --------------------------------------------------------------
// Prompt 10 � Explainability & Alert System
// --------------------------------------------------------------

export interface AlertEvidence {
  indicator: string;
  description: string;
  significance: 'LOW' | 'MODERATE' | 'HIGH';
}

export interface AlertRecommendation {
  action: string;
  urgency: 'LOW' | 'MODERATE' | 'HIGH' | 'IMMEDIATE';
}

export interface Alert {
  alert_id: string;
  water_body_id: string;
  zone_id: string;
  scene_id: string;
  analysis_date: string;
  
  title: string;
  summary: string;
  
  status: string;
  investigation_priority_score: number;
  priority_band: string;
  severity: string;
  confidence: number;
  
  primary_reason: string;
  evidence_statements: AlertEvidence[];
  recommended_actions: AlertRecommendation[];
  
  created_at: string;
  updated_at: string;
}

export interface AlertRequest {
  water_body_id: string;
  scene_id: string;
  acquisition_date: string;
  results: PriorityResult[] | Record<string, any>[];
}

export interface AlertResponse {
  alerts: Alert[];
}
