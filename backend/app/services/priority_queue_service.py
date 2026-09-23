import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from app.database.repositories.alert_repository import AlertRepository
from app.schemas.queue import PriorityQueueItem, AlertStatusUpdate, AlertStatusHistorySchema, QueueSummarySchema
from app.schemas.alert import AlertSchema

class PriorityQueueService:
    def __init__(self):
        self.repo = AlertRepository()

    def get_queue(
        self,
        water_body_id: Optional[str] = None,
        priority_band: Optional[str] = None,
        severity: Optional[str] = None,
        status: Optional[str] = None,
        primary_indicator: Optional[str] = None,
        search: Optional[str] = None
    ) -> List[PriorityQueueItem]:
        
        alerts = self.repo.get_all_alerts()
        
        filtered = []
        for a in alerts:
            # apply filters
            if water_body_id and a.get("water_body_id") != water_body_id:
                continue
            if priority_band and a.get("priority_band") != priority_band:
                continue
            if severity and a.get("severity") != severity:
                continue
            if status and a.get("status") != status:
                continue
            
            # Text search
            if search:
                s = search.lower()
                matches = (
                    s in a.get("water_body_id", "").lower() or
                    s in a.get("zone_id", "").lower() or
                    s in a.get("alert_id", "").lower() or
                    s in a.get("primary_reason", "").lower()
                )
                if not matches:
                    continue
                    
            filtered.append(a)
            
        # Sort by investigation_priority_score DESC
        filtered.sort(key=lambda x: x.get("investigation_priority_score", 0.0), reverse=True)
        
        results = []
        for idx, a in enumerate(filtered):
            # Parse full AlertSchema
            alert_obj = AlertSchema(**a)
            
            # Extract primary driver from evidence statements if possible
            primary_driver = "Unknown"
            if alert_obj.evidence_statements:
                primary_driver = alert_obj.evidence_statements[0].indicator
                
            if primary_indicator and primary_indicator.lower() != primary_driver.lower():
                continue
                
            item = PriorityQueueItem(
                rank=idx + 1,
                alert_id=alert_obj.alert_id,
                water_body_id=alert_obj.water_body_id,
                zone_id=alert_obj.zone_id,
                scene_id=alert_obj.scene_id,
                analysis_date=alert_obj.analysis_date,
                investigation_priority_score=alert_obj.investigation_priority_score,
                priority_band=alert_obj.priority_band,
                severity=alert_obj.severity,
                confidence=alert_obj.confidence,
                primary_driver=primary_driver,
                alert_details=alert_obj,
                investigation_status=alert_obj.status,
                updated_at=alert_obj.updated_at,
                created_at=alert_obj.created_at
            )
            results.append(item)
            
        return results

    def get_summary(self) -> QueueSummarySchema:
        alerts = self.repo.get_all_alerts()
        active = sum(1 for a in alerts if a.get("status") == "ACTIVE")
        acknowledged = sum(1 for a in alerts if a.get("status") == "ACKNOWLEDGED")
        under_inv = sum(1 for a in alerts if a.get("status") == "UNDER_INVESTIGATION")
        resolved = sum(1 for a in alerts if a.get("status") == "RESOLVED")
        very_high = sum(1 for a in alerts if a.get("priority_band") == "VERY HIGH" or a.get("priority_band") == "CRITICAL")
        high = sum(1 for a in alerts if a.get("priority_band") == "HIGH")
        
        return QueueSummarySchema(
            active=active,
            acknowledged=acknowledged,
            under_investigation=under_inv,
            resolved=resolved,
            very_high_priority=very_high,
            high_priority=high
        )
        
    def update_status(self, alert_id: str, update: AlertStatusUpdate, changed_by: str = "System Operator") -> PriorityQueueItem:
        alert_data = self.repo.get_alert_by_id(alert_id)
        if not alert_data:
            raise ValueError("Alert not found")
            
        old_status = alert_data.get("status", "ACTIVE")
        new_status = update.status
        
        valid_transitions = {
            "ACTIVE": ["ACKNOWLEDGED", "DISMISSED"],
            "ACKNOWLEDGED": ["UNDER_INVESTIGATION", "DISMISSED", "RESOLVED"],
            "UNDER_INVESTIGATION": ["RESOLVED"],
            "RESOLVED": ["ACTIVE"], # Allowed to reopen explicitly
            "DISMISSED": ["ACTIVE"]
        }
        
        # We allow transitions if old == new (no-op) or if it's in the valid list
        if new_status != old_status and new_status not in valid_transitions.get(old_status, []):
            raise ValueError(f"Invalid transition from {old_status} to {new_status}")
            
        alert_data["status"] = new_status
        alert_data["updated_at"] = datetime.utcnow().isoformat()
        
        self.repo.save_alert(alert_data)
        
        if new_status != old_status:
            history_record = {
                "id": f"HST-{uuid.uuid4().hex[:8].upper()}",
                "alert_id": alert_id,
                "previous_status": old_status,
                "new_status": new_status,
                "changed_at": datetime.utcnow().isoformat(),
                "changed_by": changed_by,
                "reason": update.reason
            }
            self.repo.save_history_record(history_record)
        
        # Fetch it again to return the item
        queue = self.get_queue()
        for item in queue:
            if item.alert_id == alert_id:
                return item
                
        raise ValueError("Error returning updated alert")

    def get_history(self, alert_id: str) -> List[AlertStatusHistorySchema]:
        hist_data = self.repo.get_alert_history(alert_id)
        # Sort by changed_at DESC
        hist_data.sort(key=lambda x: x.get("changed_at", ""), reverse=True)
        return [AlertStatusHistorySchema(**h) for h in hist_data]
