from typing import Dict, List
from datetime import datetime, timedelta
from app.schemas.anomaly import AnomalyRequest, AnomalyResponse, AnomalyZoneResultSchema, AnomalyFeatureSchema, MLAnomalySchema
from app.intelligence.anomaly.orchestrator import analyze_zone_anomaly
from app.services.historical_service import HistoricalService
from app.intelligence.baseline.repository import HistoricalRepository

class AnomalyService:
    def __init__(self):
        # We need historical data to run the orchestrator
        self.repo = HistoricalRepository()
        self.historical_service = HistoricalService()
        
    async def detect_anomalies(self, request: AnomalyRequest) -> AnomalyResponse:
        
        # In a real app we'd fetch the current indicators from DB.
        # For this hackathon MVP, we can recalculate them or mock them via the historical service demo logic.
        # Since Prompt 07 generates demo historical data, let's grab it.
        # Note: The request needs current indicator values. For simplicity, we'll ask the historical service 
        # to generate a single "current" observation.
        
        results = []
        for zone_id in request.zones:
            # 1. Get historical baseline and observations
            # 2 year lookback
            end_date = datetime.strptime(request.current_date, "%Y-%m-%d")
            start_date = end_date - timedelta(days=365*2)
            
            # This generates observations and calculates the baseline
            hist_res = await self.historical_service.get_historical_analysis(
                water_body_id=request.water_body_id,
                zone_id=zone_id,
                start_date=start_date.strftime("%Y-%m-%d"),
                end_date=request.current_date
            )
            
            # The last observation in hist_res.time_series is NOT necessarily today's date if we just use the API,
            # actually we need the current observation.
            # To mock the current observation reliably, we generate one for the exact requested date.
            current_obs = self.historical_service._generate_demo_observation(
                water_body_id=request.water_body_id,
                zone_id=zone_id,
                date_str=request.current_date
            )
            
            current_indicators = {
                k: {"mean": v, "valid_pixel_percentage": 95.0} 
                for k, v in current_obs.indicators.items()
            }
            
            baseline_indicators = hist_res.baseline
            
            # Convert repo format to list of dicts for orchestrator
            historical_obs_dicts = []
            for t in hist_res.time_series:
                if t.date == request.current_date:
                    continue # LEAKAGE PREVENTION: do not include current date in history
                obs_dict = {
                    "date": t.date,
                    "indicators": {
                        "ndti": {"mean": t.ndti},
                        "suspended_sediment": {"mean": t.suspended_sediment},
                        "ndci": {"mean": t.ndci},
                        "fai": {"mean": t.fai}
                    }
                }
                historical_obs_dicts.append(obs_dict)
                
            # Run orchestrator
            zone_result = analyze_zone_anomaly(
                water_body_id=request.water_body_id,
                zone_id=zone_id,
                scene_id=request.scene_id,
                acquisition_date=request.current_date,
                current_indicators=current_indicators,
                baseline_indicators=baseline_indicators,
                historical_observations=historical_obs_dicts,
                robust_threshold=3.0
            )
            
            # Map to Pydantic
            schema_indicators = {
                k: AnomalyFeatureSchema(
                    indicator_name=v.indicator_name,
                    current_value=v.current_value,
                    baseline_median=v.baseline_median,
                    absolute_deviation=v.absolute_deviation,
                    relative_deviation=v.relative_deviation,
                    robust_deviation=v.robust_deviation,
                    valid_percentage=v.valid_percentage
                ) for k, v in zone_result.indicators.items()
            }
            
            res_schema = AnomalyZoneResultSchema(
                zone_id=zone_id,
                indicators=schema_indicators,
                statistical_anomaly=zone_result.statistical_anomaly,
                statistical_threshold=zone_result.statistical_threshold,
                ml=MLAnomalySchema(
                    model=zone_result.ml.model,
                    status=zone_result.ml.status,
                    prediction=zone_result.ml.prediction,
                    anomaly_score=zone_result.ml.anomaly_score
                ),
                combined_status=zone_result.combined_status,
                anomaly_score=zone_result.anomaly_score,
                quality=zone_result.quality,
                affected_area=zone_result.affected_area,
                affected_percentage=zone_result.affected_percentage
            )
            results.append(res_schema)
            
        return AnomalyResponse(
            water_body_id=request.water_body_id,
            scene_id=request.scene_id,
            acquisition_date=request.current_date,
            results=results
        )
