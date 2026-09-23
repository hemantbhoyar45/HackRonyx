export interface FieldSampleCreate {
  alert_id?: string;
  analysis_id?: string;
  report_id?: string;
  water_body_id: string;
  zone_id?: string;
  scene_id?: string;
  sample_date: string;
  sample_time?: string;
  latitude: number;
  longitude: number;
  sample_type: string;
  collected_by?: string;
  notes?: string;
}

export interface FieldSample extends FieldSampleCreate {
  sample_id: string;
  validation_id: string;
  validation_status: string;
  created_at: string;
  updated_at: string;
}

export interface LabResultCreate {
  validation_id: string;
  parameter_name: string;
  value?: number;
  unit: string;
  detection_limit?: number;
  qualifier?: string;
  method?: string;
  measured_at?: string;
  laboratory_name?: string;
  laboratory_report_id?: string;
  reference_min?: number;
  reference_max?: number;
  notes?: string;
}

export interface LabResult extends LabResultCreate {
  lab_result_id: string;
  created_at: string;
}

export interface ValidationRecord {
  validation_id: string;
  alert_id?: string;
  analysis_id?: string;
  report_id?: string;
  water_body_id: string;
  zone_id: string;
  scene_id?: string;
  sample_id: string;
  sample_date: string;
  sample_time?: string;
  latitude?: number;
  longitude?: number;
  sample_type: string;
  collected_by?: string;
  laboratory_name?: string;
  laboratory_report_id?: string;
  validation_status: string;
  notes?: string;
  created_at: string;
  updated_at: string;
}

export interface ValidationResult {
  validation_id: string;
  validation_status: string;
  satellite_indicator?: string;
  related_lab_parameter?: string;
  satellite_value?: number;
  satellite_baseline?: number;
  satellite_deviation?: number;
  lab_value?: number;
  lab_unit?: string;
  temporal_relation?: string;
  temporal_difference_days?: number;
  spatial_relation?: string;
  spatial_distance_m?: number;
  validation_evidence_score?: number;
  explanation: string;
  scientific_note: string;
  data_quality?: Record<string, string>;
}

export interface ValidationStatusUpdate {
  status: string;
  changed_by?: string;
  reason?: string;
}

export interface ValidationStatusHistory {
  id: string;
  validation_id: string;
  previous_status: string;
  new_status: string;
  changed_at: string;
  changed_by: string;
  reason?: string;
}

export interface ValidationListResponse {
  items: ValidationRecord[];
  total: number;
}
