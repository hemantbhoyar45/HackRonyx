from typing import Dict, Any, List, Optional
from app.intelligence.fusion.evidence import compute_indicator_evidences, IndicatorEvidenceResult
from app.intelligence.fusion.agreement import calculate_indicator_agreement
from app.intelligence.fusion.confidence import (
    calculate_quality_factor,
    calculate_historical_support,
    calculate_model_support,
    calculate_confidence_score
)
from app.intelligence.fusion.priority import (
    calculate_severity,
    calculate_priority_score,
    identify_drivers
)

class MultiIndicatorFusionService:
    """
    Central service orchestrating Multi-Indicator Evidence Fusion & Investigation Priority Scoring.
    """

    @staticmethod
    def process_zone_anomaly(
        water_body_id: str,
        zone_id: str,
        scene_id: str,
        analysis_date: str,
        zone_anomaly_data: Dict[str, Any],
        historical_count: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Processes an anomaly result for a single zone and generates the PriorityResult and Evidence Trace.
        """
        # Extract inputs from anomaly result dictionary/object
        if hasattr(zone_anomaly_data, "dict"):
            data_dict = zone_anomaly_data.dict()
        elif isinstance(zone_anomaly_data, dict):
            data_dict = zone_anomaly_data
        else:
            data_dict = {}

        indicators_data = data_dict.get("indicators", {})
        combined_status = data_dict.get("combined_status", "NO_ANOMALY_SIGNAL")
        statistical_anomaly = bool(data_dict.get("statistical_anomaly", False))
        ml_data = data_dict.get("ml", {})
        quality_info = data_dict.get("quality", {})
        affected_area = data_dict.get("affected_area", 0.0)

        # 1. Indicator Evidences & Combined Evidence
        evidence_objects, combined_evidence, indicator_completeness = compute_indicator_evidences(indicators_data)

        # Handle NO_ANOMALY_SIGNAL status or LOW_QUALITY_OBSERVATION status edge cases
        if combined_status == "NO_ANOMALY_SIGNAL":
            # Zero out anomaly evidence if overall status was confirmed normal
            combined_evidence = 0.0
        elif combined_status == "LOW_QUALITY_OBSERVATION":
            # Cap evidence if quality was poor
            combined_evidence = min(combined_evidence, 0.35)

        # 2. Multi-Indicator Agreement
        indicator_agreement_score = calculate_indicator_agreement(evidence_objects)

        # 3. Quality Factor & Historical Support & Model Support
        quality_factor = calculate_quality_factor(quality_info)
        if combined_status == "LOW_QUALITY_OBSERVATION":
            quality_factor = min(quality_factor, 0.35)

        # Check observation count if passed or inside indicators
        if historical_count is None:
            # Try to estimate from indicator valid_percentage or default
            historical_count = 6 # Default sufficient if not specified
        historical_support = calculate_historical_support(historical_count)
        if combined_status == "INSUFFICIENT_HISTORY":
            historical_support = 0.20

        model_support_factor, model_agreement_score = calculate_model_support(
            statistical_anomaly=statistical_anomaly,
            ml_data=ml_data
        )

        if combined_status == "NO_ANOMALY_SIGNAL":
            model_support_factor = 0.20
            max_rob_dev = 0.0
        else:
            # 4. Max Robust Deviation for Severity calculation
            max_rob_dev = 0.0
            for ev in evidence_objects:
                if ev.robust_deviation is not None:
                    max_rob_dev = max(max_rob_dev, abs(float(ev.robust_deviation)))

        # 5. Severity Calculation
        severity_category, severity_normalized = calculate_severity(combined_evidence, max_rob_dev)

        # 6. Confidence Score Calculation
        confidence_normalized, confidence_score = calculate_confidence_score(
            quality_factor=quality_factor,
            indicator_completeness=indicator_completeness,
            historical_support=historical_support,
            model_support_factor=model_support_factor
        )

        # 7. Investigation Priority Score Calculation
        investigation_priority_score, priority_band = calculate_priority_score(
            combined_evidence=combined_evidence,
            severity_normalized=severity_normalized,
            confidence_normalized=confidence_normalized,
            model_support_factor=model_support_factor
        )

        # 8. Primary Driver & Supporting Indicators
        primary_driver, supporting_indicators = identify_drivers(evidence_objects)

        # 9. Evidence Trace Structure (for Prompt 10 consumption)
        evidence_trace = {
            "water_body_id": water_body_id,
            "zone_id": zone_id,
            "scene_id": scene_id,
            "analysis_date": analysis_date,
            "combined_status": combined_status,
            "indicators": [e.to_dict() for e in evidence_objects],
            "combined_evidence": round(combined_evidence, 4),
            "indicator_agreement_score": round(indicator_agreement_score, 4),
            "quality_factor": round(quality_factor, 4),
            "indicator_completeness": round(indicator_completeness, 4),
            "historical_support": round(historical_support, 4),
            "model_agreement_score": model_agreement_score,
            "severity": severity_category,
            "severity_normalized": round(severity_normalized, 4),
            "confidence": confidence_score,
            "confidence_normalized": round(confidence_normalized, 4),
            "investigation_priority_score": investigation_priority_score,
            "priority_band": priority_band,
            "primary_driver": primary_driver,
            "supporting_indicators": supporting_indicators,
            "affected_area": affected_area
        }

        return evidence_trace
