import React, { useState, useEffect } from 'react';
import { QueueSummaryCards } from './components/QueueSummaryCards';
import { QueueFilters } from './components/QueueFilters';
import { QueueTable } from './components/QueueTable';
import { InvestigationDetail } from './components/InvestigationDetail';
import { queueService } from '../../services/api/queueService';
import type { FiltersState } from './components/QueueFilters';
import type { PriorityQueueItem, QueueSummary } from '../../types/queue';

const initialFilters: FiltersState = {
  search: '',
  water_body_id: '',
  priority_band: '',
  severity: '',
  status: '',
  primary_indicator: ''
};

export default function PriorityQueue() {
  const [filters, setFilters] = useState<FiltersState>(initialFilters);
  const [items, setItems] = useState<PriorityQueueItem[]>([]);
  const [summary, setSummary] = useState<QueueSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedItem, setSelectedItem] = useState<PriorityQueueItem | null>(null);

  const loadData = async () => {
    setLoading(true);
    try {
      const [queueData, summaryData] = await Promise.all([
        queueService.getQueue(filters),
        queueService.getSummary()
      ]);
      setItems(queueData.items);
      setSummary(summaryData);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [filters]);

  const handleResetFilters = () => setFilters(initialFilters);

  const handleStatusChange = async (alertId: string, status: string, reason?: string) => {
    try {
      const updatedItem = await queueService.updateStatus(alertId, status, reason);
      setSelectedItem(updatedItem);
      // Reload queue and summary to reflect new state
      loadData();
    } catch (err) {
      console.error('Failed to update status', err);
      window.alert('Failed to update status.');
    }
  };

  return (
    <div className="h-full flex flex-col">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-slate-800">Priority Queue</h1>
        <p className="text-slate-500 mt-1">Operational interface to review and prioritize investigation candidates.</p>
      </div>

      <QueueSummaryCards summary={summary} loading={loading} />

      <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden flex flex-col flex-1">
        <QueueFilters 
          filters={filters} 
          onFilterChange={setFilters} 
          onReset={handleResetFilters} 
        />
        
        <div className="flex-1 overflow-auto relative">
          <QueueTable 
            items={items} 
            loading={loading} 
            onViewItem={setSelectedItem} 
          />
        </div>
      </div>

      <InvestigationDetail
        item={selectedItem}
        onClose={() => setSelectedItem(null)}
        onStatusChange={handleStatusChange}
      />
    </div>
  );
}
