import uuid
from datetime import datetime
from typing import List, Dict, Any
from app.schemas.alert import AlertSchema, AlertEvidenceSchema, AlertActionRecommendationSchema

class ExplainabilityService:
    
    @staticmethod
    def generate_alerts(priority_results: List[Dict[str, Any]]) -> List[AlertSchema]:
        alerts = []
        for pr in priority_results:
            zone_id = pr.get("zone_id", "unknown-zone")
            band = pr.get("priority_band", "LOW")
            score = pr.get("investigation_priority_score", 0.0)
            
            # Generate alert if priority band is elevated or score is above a threshold
            if band == "LOW" and score < 20.0:
                continue
                
            alert_id = f"ALT-{uuid.uuid4().hex[:8].upper()}"
            primary_driver = pr.get("primary_driver", "Unknown Indicator")
            
            # 1. Generate Evidence Statements
            evidence_statements = ExplainabilityService._generate_evidence_statements(pr.get("indicators", []))
            
            # 2. Generate Action Recommendations
            recommendations = ExplainabilityService._generate_recommendations(band, primary_driver)
            
            # 3. Generate Summary ("WHY WAS THIS ZONE FLAGGED?")
            summary = ExplainabilityService._generate_summary(pr, primary_driver, evidence_statements)
            
            # 4. Generate Title
            title = f"Potential Water Quality Anomaly in {zone_id}"
            
            alert = AlertSchema(
                alert_id=alert_id,
                water_body_id=pr.get("water_body_id", "unknown"),
                zone_id=zone_id,
                scene_id=pr.get("scene_id", "unknown"),
                analysis_date=pr.get("analysis_date", datetime.utcnow().isoformat()),
                title=title,
                summary=summary,
                status="ACTIVE",
                investigation_priority_score=score,
                priority_band=band,
                severity=pr.get("severity", "LOW"),
                confidence=pr.get("confidence", 0.0),
                primary_reason=f"Significant deviation detected in {primary_driver}",
                evidence_statements=evidence_statements,
                recommended_actions=recommendations,
                created_at=datetime.utcnow().isoformat(),
                updated_at=datetime.utcnow().isoformat()
            )
            alerts.append(alert)
            
        return alerts

    @staticmethod
    def _generate_evidence_statements(indicators: List[Dict[str, Any]]) -> List[AlertEvidenceSchema]:
        statements = []
        for ind in indicators:
            name = ind.get("indicator_name", "Unknown")
            r_dev = ind.get("robust_deviation") or 0.0
            w_score = ind.get("weighted_contribution") or 0.0
            
            if abs(r_dev) < 1.0:
                continue
                
            sig = "HIGH" if abs(r_dev) > 3.0 else ("MODERATE" if abs(r_dev) > 2.0 else "LOW")
            direction = "elevated" if r_dev > 0 else "depressed"
            
            desc = f"{name} is significantly {direction} ({abs(r_dev):.1f} MAD from historical baseline), contributing {w_score:.1f} to priority score."
            
            statements.append(AlertEvidenceSchema(
                indicator=name,
                description=desc,
                significance=sig
            ))
            
        # Sort evidence by significance (HIGH first) and contribution
        statements.sort(key=lambda x: (0 if x.significance == "HIGH" else 1 if x.significance == "MODERATE" else 2))
        return statements

    @staticmethod
    def _generate_recommendations(band: str, primary_driver: str) -> List[AlertActionRecommendationSchema]:
        recs = []
        if band == "CRITICAL":
            recs.append(AlertActionRecommendationSchema(action="Dispatch field team for immediate water sampling.", urgency="IMMEDIATE"))
            recs.append(AlertActionRecommendationSchema(action="Notify local environmental protection authorities.", urgency="HIGH"))
        elif band == "HIGH":
            recs.append(AlertActionRecommendationSchema(action="Schedule field sampling within 48 hours.", urgency="HIGH"))
            recs.append(AlertActionRecommendationSchema(action="Review upstream satellite imagery for potential sources.", urgency="MODERATE"))
        elif band == "MODERATE":
            recs.append(AlertActionRecommendationSchema(action="Monitor indicator trends in next satellite pass.", urgency="LOW"))
            
        if primary_driver.upper() == "NDTI":
            recs.append(AlertActionRecommendationSchema(action="Check for recent heavy rainfall or upstream dredging operations.", urgency="MODERATE"))
        elif primary_driver.upper() == "NDCI":
            recs.append(AlertActionRecommendationSchema(action="Investigate potential agricultural runoff or algal bloom conditions.", urgency="MODERATE"))
            
        return recs

    @staticmethod
    def _generate_summary(pr: Dict[str, Any], primary_driver: str, evidence: List[AlertEvidenceSchema]) -> str:
        score = pr.get("investigation_priority_score", 0.0)
        confidence = pr.get("confidence", 0.0)
        
        strong_evidence = [e.indicator for e in evidence if e.significance == "HIGH"]
        
        summary = (
            f"This zone was flagged with an Investigation Priority Score of {score:.1f}/100 "
            f"(Confidence: {confidence:.0%}). The primary driver for this anomaly is {primary_driver}. "
        )
        
        if strong_evidence:
            summary += f"Strong supporting evidence was found in: {', '.join(strong_evidence)}. "
            
        summary += "These deviations are statistically significant compared to the seasonal historical baseline."
        return summary
