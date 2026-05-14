# backend/app/api/routes/metrics.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.metrics import MetricPayload
from app.services.metrics_service import write_metrics, query_metrics
from app.services.alert_service import check_alerts

router = APIRouter()

@router.post("/ingest")
def ingest_metrics(payload: MetricPayload, db: Session = Depends(get_db)):
    write_metrics(payload)
    check_alerts(payload, db)
    return {"status": "ok", "host": payload.hostname}

@router.get("/query/{measurement}")
def get_metrics(
    measurement: str,
    host: str,
    minutes: int = 30,
):
    data = query_metrics(measurement, host, minutes)
    return {"measurement": measurement, "host": host, "data": data}