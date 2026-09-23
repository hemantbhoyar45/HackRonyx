from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from app.schemas.queue import PriorityQueueItem, AlertStatusUpdate, AlertStatusHistorySchema, QueueSummarySchema, QueueResponseSchema
from app.services.priority_queue_service import PriorityQueueService
import math

router = APIRouter()
queue_service = PriorityQueueService()

@router.get("", response_model=QueueResponseSchema)
def get_priority_queue(
    water_body_id: Optional[str] = None,
    priority_band: Optional[str] = None,
    severity: Optional[str] = None,
    status: Optional[str] = None,
    primary_indicator: Optional[str] = None,
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100)
):
    try:
        items = queue_service.get_queue(
            water_body_id=water_body_id,
            priority_band=priority_band,
            severity=severity,
            status=status,
            primary_indicator=primary_indicator,
            search=search
        )
        
        total = len(items)
        total_pages = math.ceil(total / page_size) if total > 0 else 1
        
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_items = items[start_idx:end_idx]
        
        return QueueResponseSchema(
            items=paginated_items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

@router.get("/summary", response_model=QueueSummarySchema)
def get_queue_summary():
    try:
        return queue_service.get_summary()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

@router.patch("/{alert_id}/status", response_model=PriorityQueueItem)
def update_alert_status(alert_id: str, update: AlertStatusUpdate):
    try:
        return queue_service.update_status(alert_id, update)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

@router.get("/{alert_id}/history", response_model=List[AlertStatusHistorySchema])
def get_alert_history(alert_id: str):
    try:
        return queue_service.get_history(alert_id)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
