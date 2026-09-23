import type { QueueResponse, QueueSummary, PriorityQueueItem, AlertStatusHistory } from '../../types/queue';

const API_BASE = 'http://localhost:8000/api';

export const queueService = {
  getQueue: async (params?: Record<string, any>): Promise<QueueResponse> => {
    const url = new URL(`${API_BASE}/priority-queue`);
    if (params) {
      Object.keys(params).forEach(key => {
        if (params[key] !== undefined && params[key] !== '') {
          url.searchParams.append(key, String(params[key]));
        }
      });
    }
    const response = await fetch(url.toString());
    if (!response.ok) throw new Error('Failed to fetch queue');
    return response.json();
  },

  getSummary: async (): Promise<QueueSummary> => {
    const response = await fetch(`${API_BASE}/priority-queue/summary`);
    if (!response.ok) throw new Error('Failed to fetch summary');
    return response.json();
  },

  updateStatus: async (alertId: string, status: string, reason?: string): Promise<PriorityQueueItem> => {
    const response = await fetch(`${API_BASE}/priority-queue/${alertId}/status`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status, reason })
    });
    if (!response.ok) throw new Error('Failed to update status');
    return response.json();
  },

  getHistory: async (alertId: string): Promise<AlertStatusHistory[]> => {
    const response = await fetch(`${API_BASE}/priority-queue/${alertId}/history`);
    if (!response.ok) throw new Error('Failed to fetch history');
    return response.json();
  }
};
