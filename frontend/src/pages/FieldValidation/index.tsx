import React, { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { FieldSampleForm } from './components/FieldSampleForm';
import { LabResultForm } from './components/LabResultForm';
import { LabResultsTable } from './components/LabResultsTable';
import { ValidationStatusPanel } from './components/ValidationStatusPanel';
import { validationService } from '../../services/api/validationService';
import { queueService } from '../../services/api/queueService';
import {
  FieldSampleCreate,
  LabResultCreate,
  ValidationRecord,
  LabResult,
  ValidationResult
} from '../../types/validation';
import { ArrowLeft } from 'lucide-react';

export default function FieldValidationPage() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  
  const alertId = searchParams.get('alert_id') || '';
  const waterBodyId = searchParams.get('water_body_id') || '';
  const zoneId = searchParams.get('zone_id') || '';
  
  const [record, setRecord] = useState<ValidationRecord | null>(null);
  const [labResults, setLabResults] = useState<LabResult[]>([]);
  const [comparisonResult, setComparisonResult] = useState<ValidationResult | null>(null);
  const [anomalyContext, setAnomalyContext] = useState<any>(null);
  
  const [isSubmittingSample, setIsSubmittingSample] = useState(false);
  const [isSubmittingLab, setIsSubmittingLab] = useState(false);
  const [isComparing, setIsComparing] = useState(false);
  const [loading, setLoading] = useState(false);

  // Load existing validation if alertId is provided
  useEffect(() => {
    if (alertId) {
      loadValidationForAlert(alertId);
    }
  }, [alertId]);

  const loadValidationForAlert = async (aid: string) => {
    setLoading(true);
    try {
      const records = await validationService.getValidationsByAlert(aid);
      if (records.length > 0) {
        const val = records[0];
        setRecord(val);
        const results = await validationService.getLabResults(val.sample_id);
        setLabResults(results);
        
        // Also fetch the alert to get anomaly context
        const queueItems = await queueService.getQueue({ alert_id: aid });
        if (queueItems.items.length > 0) {
          const alertData = queueItems.items[0].alert_details;
          setAnomalyContext({
            indicator: alertData.primary_reason?.split(' ')[0]?.toLowerCase() || 'ndti',
            current_value: 0, // placeholder, ideally would come from actual analysis
            baseline_median: 0,
            deviation_relative: 0.25, // placeholder
            analysis_date: alertData.analysis_date
          });
        }

        // Auto-run comparison if there are lab results
        if (results.length > 0) {
          await runComparison(val.validation_id);
        }
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSampleSubmit = async (data: FieldSampleCreate) => {
    setIsSubmittingSample(true);
    try {
      const newSample = await validationService.createSample(data);
      const newRecord = await validationService.getValidation(newSample.validation_id);
      setRecord(newRecord);
    } catch (err) {
      console.error(err);
      alert('Failed to save field sample.');
    } finally {
      setIsSubmittingSample(false);
    }
  };

  const handleLabSubmit = async (data: LabResultCreate) => {
    if (!record) return;
    setIsSubmittingLab(true);
    try {
      await validationService.addLabResult(record.sample_id, data);
      const results = await validationService.getLabResults(record.sample_id);
      setLabResults(results);
      
      // Auto run comparison
      await runComparison(record.validation_id);
    } catch (err) {
      console.error(err);
      alert('Failed to save lab result.');
    } finally {
      setIsSubmittingLab(false);
    }
  };

  const runComparison = async (vid: string) => {
    setIsComparing(true);
    try {
      const res = await validationService.runComparison(vid, anomalyContext);
      setComparisonResult(res);
      const updatedRecord = await validationService.getValidation(vid);
      setRecord(updatedRecord);
    } catch (err) {
      console.error(err);
    } finally {
      setIsComparing(false);
    }
  };

  return (
    <div className="h-full flex flex-col max-w-5xl mx-auto py-6">
      <div className="mb-6 flex items-center gap-4">
        <button 
          onClick={() => navigate('/priority-queue')}
          className="p-2 hover:bg-slate-200 rounded-full transition-colors"
        >
          <ArrowLeft className="w-5 h-5 text-slate-600" />
        </button>
        <div>
          <h1 className="text-2xl font-bold text-slate-800">Ground / Lab Validation</h1>
          <p className="text-slate-500 mt-1">Record field samples and laboratory results for satellite anomaly validation.</p>
        </div>
      </div>

      {loading ? (
        <div className="flex-1 flex justify-center items-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-brand-600"></div>
        </div>
      ) : (
        <div className="flex-1 overflow-y-auto pb-12">
          
          {/* 1. Field Sample Form (or Display if created) */}
          {!record ? (
            <FieldSampleForm 
              initialAlertId={alertId}
              initialWaterBodyId={waterBodyId}
              initialZoneId={zoneId}
              onSubmit={handleSampleSubmit}
              isSubmitting={isSubmittingSample}
            />
          ) : (
            <div className="bg-slate-50 p-6 rounded-xl shadow-sm border border-slate-200">
              <div className="flex justify-between items-start mb-4">
                <h2 className="text-lg font-bold text-slate-800">Field Sample: {record.sample_id}</h2>
                <span className="px-3 py-1 bg-brand-100 text-brand-800 text-xs font-bold rounded-full">
                  {record.validation_status.replace('_', ' ')}
                </span>
              </div>
              <div className="grid grid-cols-3 gap-6 text-sm">
                <div>
                  <span className="block text-slate-500 mb-1">Water Body</span>
                  <strong className="text-slate-800">{record.water_body_id}</strong>
                </div>
                <div>
                  <span className="block text-slate-500 mb-1">Zone</span>
                  <strong className="text-slate-800">{record.zone_id}</strong>
                </div>
                <div>
                  <span className="block text-slate-500 mb-1">Alert ID</span>
                  <strong className="text-slate-800">{record.alert_id || '-'}</strong>
                </div>
                <div>
                  <span className="block text-slate-500 mb-1">Sample Date</span>
                  <strong className="text-slate-800">{record.sample_date}</strong>
                </div>
                <div>
                  <span className="block text-slate-500 mb-1">Location</span>
                  <strong className="text-slate-800">{record.latitude?.toFixed(4)}, {record.longitude?.toFixed(4)}</strong>
                </div>
                <div>
                  <span className="block text-slate-500 mb-1">Type</span>
                  <strong className="text-slate-800">{record.sample_type.replace('_', ' ')}</strong>
                </div>
              </div>
            </div>
          )}

          {/* 2. Lab Results Section */}
          {record && (
            <>
              <LabResultsTable results={labResults} />
              
              <LabResultForm 
                validationId={record.validation_id}
                onSubmit={handleLabSubmit}
                isSubmitting={isSubmittingLab}
              />
            </>
          )}

          {/* 3. Validation Comparison Section */}
          {record && labResults.length > 0 && (
            <ValidationStatusPanel 
              result={comparisonResult} 
              onRunComparison={() => runComparison(record.validation_id)}
              isComparing={isComparing}
            />
          )}

        </div>
      )}
    </div>
  );
}
