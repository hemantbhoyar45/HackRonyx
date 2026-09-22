import React, { useState } from 'react';
import WaterBodySelector from '../../components/dashboard/WaterBodySelector';
import DateRangeSelector from '../../components/dashboard/DateRangeSelector';
import MapView from '../../components/map/MapView';
import AOIInfoPanel from '../../components/dashboard/AOIInfoPanel';
import SatelliteDataStatus from '../../components/dashboard/SatelliteDataStatus';
import PreprocessingStatus from '../../components/dashboard/PreprocessingStatus';
import { WaterDetectionStatus } from '../../components/dashboard/WaterDetectionStatus';
import { SpectralIndicatorsPanel } from '../../components/dashboard/SpectralIndicatorsPanel';
import { HistoricalAnalysisPanel } from '../../components/dashboard/HistoricalAnalysisPanel';
import { AnomalySummaryPanel } from '../../components/dashboard/AnomalySummaryPanel';
import { ZoneDetailView } from '../../components/dashboard/ZoneDetailView';
import { AlertTriangle, Activity, Info, CheckCircle2 } from 'lucide-react';
import { useAnalysisStore } from '../../store/analysisStore';
import { analysisService } from '../../services/api/analysisService';

export default function Dashboard() {
  const { 
    getAnalysisRequest, 
    isAnalyzing, 
    setIsAnalyzing,
    sceneSearchStatus,
    setSceneSearchStatus,
    sceneSearchResult,
    setSceneSearchResult,
    preprocessingStatus,
    setPreprocessingStatus,
    preprocessingResult,
    setPreprocessingResult,
    waterDetectionStatus,
    setWaterDetectionStatus,
    waterMaskResult,
    setWaterMaskResult,
    indicatorsStatus,
    setIndicatorsStatus,
    indicatorsResult,
    setIndicatorsResult,
    activeMapLayer,
    setActiveMapLayer,
    historicalStatus,
    setHistoricalStatus,
    historicalResult,
    setHistoricalResult,
    historicalLookback,
    setHistoricalLookback,
    anomalyStatus,
    setAnomalyStatus,
    anomalyResult,
    setAnomalyResult,
    selectedZoneResult,
    setSelectedZoneResult,
    resetPipeline
  } = useAnalysisStore();
  
  const [statusMessage, setStatusMessage] = useState<{type: 'error' | 'success', text: string} | null>(null);

  const handleAnalyze = async () => {
    setStatusMessage(null);
    resetPipeline();
    const request = getAnalysisRequest();
    
    if (!request) {
      setStatusMessage({ type: 'error', text: 'Please complete your selection and ensure a valid AOI is selected.' });
      return;
    }

    if (new Date(request.startDate) > new Date(request.endDate)) {
      setStatusMessage({ type: 'error', text: 'Start date must be earlier than or equal to the end date.' });
      return;
    }

    setIsAnalyzing(true);
    setSceneSearchStatus('searching');
    
    try {
      // 1. Scene Discovery
      const sceneResponse = await analysisService.searchScenes(request);
      setSceneSearchResult(sceneResponse);
      
      if (sceneResponse.scene_count === 0) {
        setSceneSearchStatus('done');
        setPreprocessingStatus('idle');
        return;
      }
      
      setSceneSearchStatus('done');
      
      // 2. Select lowest-cloud scene
      const bestScene = [...sceneResponse.scenes].sort((a, b) => 
        (a.cloud_percentage || 100) - (b.cloud_percentage || 100)
      )[0];
      
      // 3. Preprocessing Pipeline
      setPreprocessingStatus('processing');
      
      const preprocessRequest = {
        ...request,
        scene_id: bestScene.scene_id
      };
      
      const prepResponse = await analysisService.preprocessScene(preprocessRequest);
      setPreprocessingResult(prepResponse);
      
      if (prepResponse.status === 'success') {
        setPreprocessingStatus('done');
        
        // 4. Water Body Detection
        setWaterDetectionStatus('processing');
        const waterMaskRequest = {
          ...request,
          scene_id: bestScene.scene_id,
          method: 'combined', // Default MVP
          threshold_method: 'otsu'
        };
        
        const waterResponse = await analysisService.detectWater(waterMaskRequest);
        setWaterMaskResult(waterResponse);
        
        if (waterResponse.status === 'success') {
          setWaterDetectionStatus('done');

          // 5. Spectral Indicator Engine
          setIndicatorsStatus('processing');
          const indicatorsRequest = {
            water_body_id: request.waterBodyId,
            scene_id: bestScene.scene_id,
            aoi: request.aoi,
            indicators: ['ndti', 'suspended_sediment', 'ndci', 'fai']
          };

          const indicatorsResponse = await analysisService.calculateIndicators(indicatorsRequest);
          setIndicatorsResult(indicatorsResponse);

          if (indicatorsResponse.status === 'success') {
            setIndicatorsStatus('done');

            // 6. Historical Baseline & Time-Series
            setHistoricalStatus('loading');
            try {
              // Lookback period: 1yr or 2yr before the selected start date
              const endHist = request.startDate;
              const lookbackYears = historicalLookback === '1yr' ? 1 : 2;
              const startHist = new Date(request.startDate);
              startHist.setFullYear(startHist.getFullYear() - lookbackYears);
              const startHistStr = startHist.toISOString().split('T')[0];

              const histResponse = await analysisService.getHistorical({
                water_body_id: request.waterBodyId,
                aoi: request.aoi,
                start_date: startHistStr,
                end_date: endHist,
                zone_id: 'zone-main',
              });
              setHistoricalResult(histResponse);
              setHistoricalStatus('done');

              // 7. Anomaly Detection
              setAnomalyStatus('loading');
              try {
                const anomalyResponse = await analysisService.detectAnomalies({
                  water_body_id: request.waterBodyId,
                  scene_id: bestScene.scene_id,
                  current_date: request.endDate,
                  zones: ['zone-main']
                });
                setAnomalyResult(anomalyResponse);
                setAnomalyStatus('done');
              } catch (anomErr: any) {
                console.error('Anomaly analysis error:', anomErr);
                setAnomalyStatus('error');
              }

            } catch (histErr: any) {
              console.error('Historical analysis error:', histErr);
              setHistoricalStatus('error');
            }
          } else {
            setIndicatorsStatus('error');
            setStatusMessage({ type: 'error', text: indicatorsResponse.message });
          }
        } else {
          setWaterDetectionStatus('error');
          setStatusMessage({ type: 'error', text: waterResponse.message });
        }
      } else {
        setPreprocessingStatus('error');
        setStatusMessage({ type: 'error', text: prepResponse.message });
      }
      
    } catch (err: any) {
      console.error(err);
      if (sceneSearchStatus === 'searching') {
        setSceneSearchStatus('error');
      } else if (preprocessingStatus === 'processing') {
        setPreprocessingStatus('error');
      } else if (waterDetectionStatus === 'processing') {
        setWaterDetectionStatus('error');
      } else {
        setIndicatorsStatus('error');
      }
      setStatusMessage({ type: 'error', text: err.message || 'An error occurred during analysis.' });
    } finally {
      setIsAnalyzing(false);
    }
  };

  return (
    <div className="flex flex-col h-full gap-4">
      {/* Top Controls */}
      <div className="bg-white p-4 rounded-xl shadow-sm border border-slate-200 flex items-end gap-6 shrink-0">
        <div className="w-80">
          <WaterBodySelector />
        </div>
        <div className="w-[400px]">
          <DateRangeSelector />
        </div>
        <button 
          onClick={handleAnalyze}
          disabled={isAnalyzing}
          className="h-[38px] px-6 bg-brand-600 hover:bg-brand-700 disabled:bg-brand-400 text-white text-sm font-semibold rounded-md shadow-sm transition-colors ml-auto flex items-center justify-center min-w-[120px]"
        >
          {isAnalyzing ? "Preparing..." : "Analyze Area"}
        </button>
      </div>
      
      {statusMessage && (
        <div className={`p-4 rounded-lg shadow-sm text-sm font-semibold flex items-center gap-2 ${statusMessage.type === 'error' ? 'bg-red-50 text-red-700 border border-red-200' : 'bg-green-50 text-green-700 border border-green-200'}`}>
          {statusMessage.type === 'error' ? <AlertTriangle className="w-5 h-5" /> : <CheckCircle2 className="w-5 h-5" />}
          {statusMessage.text}
        </div>
      )}

      <div className="flex flex-1 gap-4 min-h-0">
        {/* Main Map Area */}
        <div className="flex-[2] bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden flex flex-col relative">
          <MapView />
        </div>

        {/* Right Info Panels */}
        <div className="flex-1 flex flex-col gap-4 overflow-y-auto pr-1">
          <AOIInfoPanel />

          <SatelliteDataStatus 
            data={sceneSearchResult} 
            status={sceneSearchStatus} 
            errorMessage={statusMessage?.text}
          />

          <PreprocessingStatus 
            data={preprocessingResult} 
            status={preprocessingStatus} 
            errorMessage={statusMessage?.text} 
          />

          <WaterDetectionStatus
            data={waterMaskResult}
            status={waterDetectionStatus}
          />

          <SpectralIndicatorsPanel
            data={indicatorsResult}
            status={indicatorsStatus}
            activeLayer={activeMapLayer}
            onLayerToggle={(layerId) => setActiveMapLayer(layerId)}
          />

          <HistoricalAnalysisPanel
            data={historicalResult}
            status={historicalStatus}
            lookback={historicalLookback}
            onLookbackChange={setHistoricalLookback}
          />

          <AnomalySummaryPanel 
            data={anomalyResult}
            status={anomalyStatus}
          />

          {selectedZoneResult && (
            <div className="fixed inset-0 z-[2000] flex items-center justify-center bg-slate-900/40 backdrop-blur-sm p-4">
              <div className="w-full max-w-2xl max-h-screen">
                <ZoneDetailView 
                  zone={selectedZoneResult} 
                  onClose={() => setSelectedZoneResult(null)} 
                />
              </div>
            </div>
          )}

          {anomalyStatus === 'idle' && (
            <div className="opacity-50 pointer-events-none mt-4 border-t border-slate-200 pt-4">
              <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-3">Future Processing Stages</h3>
              <div className="text-sm text-slate-500 italic">Multi-indicator evidence fusion &amp; alerts (Prompts 09–10).</div>
            </div>
          )}

        </div>
      </div>
    </div>
  );
}
