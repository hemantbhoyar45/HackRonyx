from typing import Dict, Any, List, Tuple
from app.intelligence.fusion.config import TARGET_INDICATORS, INDICATOR_WEIGHTS, ROBUST_DEVIATION_THRESHOLD
from app.intelligence.fusion.normalization import normalize_robust_deviation, determine_direction

class IndicatorEvidenceResult:
    def __init__(
        self,
        indicator_name: str,
        current_value: float | None,
        baseline_value: float | None,
        absolute_deviation: float | None,
        relative_deviation: float | None,
        robust_deviation: float | None,
        direction: str,
        evidence_score: float,
        weight: float,
        weighted_contribution: float,
        available: bool
    ):
        self.indicator_name = indicator_name
        self.current_value = current_value
        self.baseline_value = baseline_value
        self.absolute_deviation = absolute_deviation
        self.relative_deviation = relative_deviation
        self.robust_deviation = robust_deviation
        self.direction = direction
        self.evidence_score = evidence_score
        self.weight = weight
        self.weighted_contribution = weighted_contribution
        self.available = available

    def to_dict(self) -> Dict[str, Any]:
        return {
            "indicator_name": self.indicator_name,
            "current_value": self.current_value,
            "baseline_value": self.baseline_value,
            "absolute_deviation": self.absolute_deviation,
            "relative_deviation": self.relative_deviation,
            "robust_deviation": self.robust_deviation,
            "direction": self.direction,
            "evidence_score": round(self.evidence_score, 4),
            "weight": self.weight,
            "weighted_contribution": round(self.weighted_contribution, 4),
            "available": self.available
        }

def compute_indicator_evidences(
    indicators_data: Dict[str, Any]
) -> Tuple[List[IndicatorEvidenceResult], float, float]:
    """
    Computes evidence scores, weighted contributions, combined evidence, and completeness.
    
    Returns:
    - List of IndicatorEvidenceResult
    - combined_evidence (0.0 to 1.0)
    - indicator_completeness (0.0 to 1.0)
    """
    evidence_results: List[IndicatorEvidenceResult] = []
    total_weighted_contribution = 0.0
    available_count = 0

    for ind in TARGET_INDICATORS:
        weight = INDICATOR_WEIGHTS.get(ind, 0.25)
        raw_feat = indicators_data.get(ind)

        if raw_feat is None:
            # Missing indicator
            evidence_results.append(
                IndicatorEvidenceResult(
                    indicator_name=ind,
                    current_value=None,
                    baseline_value=None,
                    absolute_deviation=None,
                    relative_deviation=None,
                    robust_deviation=None,
                    direction="UNKNOWN",
                    evidence_score=0.0,
                    weight=weight,
                    weighted_contribution=0.0,
                    available=False
                )
            )
            continue

        # Extract values (handling dictionary or object)
        if isinstance(raw_feat, dict):
            curr_val = raw_feat.get("current_value")
            base_val = raw_feat.get("baseline_median") or raw_feat.get("baseline_value")
            abs_dev = raw_feat.get("absolute_deviation")
            rel_dev = raw_feat.get("relative_deviation")
            rob_dev = raw_feat.get("robust_deviation")
        else:
            curr_val = getattr(raw_feat, "current_value", None)
            base_val = getattr(raw_feat, "baseline_median", getattr(raw_feat, "baseline_value", None))
            abs_dev = getattr(raw_feat, "absolute_deviation", None)
            rel_dev = getattr(raw_feat, "relative_deviation", None)
            rob_dev = getattr(raw_feat, "robust_deviation", None)

        available_count += 1
        direction = determine_direction(curr_val, base_val)
        ev_score = normalize_robust_deviation(rob_dev, ROBUST_DEVIATION_THRESHOLD)
        contribution = ev_score * weight
        total_weighted_contribution += contribution

        evidence_results.append(
            IndicatorEvidenceResult(
                indicator_name=ind,
                current_value=curr_val,
                baseline_value=base_val,
                absolute_deviation=abs_dev,
                relative_deviation=rel_dev,
                robust_deviation=rob_dev,
                direction=direction,
                evidence_score=ev_score,
                weight=weight,
                weighted_contribution=contribution,
                available=True
            )
        )

    indicator_completeness = float(available_count) / float(len(TARGET_INDICATORS))
    combined_evidence = max(0.0, min(1.0, total_weighted_contribution))

    return evidence_results, combined_evidence, indicator_completeness
