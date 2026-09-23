import type { Alert } from './analysis';

export interface PriorityQueueItem {
  rank: number | null;
  alert_id: string;
  water_body_id: string;
  zone_id: string;
  scene_id: string | null;
  analysis_date: string;
  investigation_priority_score: number;
  priority_band: string;
  severity: string;
  confidence: number;
  primary_driver: string | null;
  alert_details: Alert;
  investigation_status: string;
  updated_at: string;
  created_at: string;
}

export interface AlertStatusHistory {
  id: string;
  alert_id: string;
  previous_status: string;
  new_status: string;
  changed_at: string;
  changed_by: string;
  reason: string | null;
}

export interface QueueResponse {
  items: PriorityQueueItem[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface QueueSummary {
  active: number;
  acknowledged: number;
  under_investigation: number;
  resolved: number;
  very_high_priority: number;
  high_priority: number;
}
