# backend/app/api/routes/metrics.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.metrics import MetricPayload
from app.services.metrics_service import write_metrics, query_metrics
from app.services.alert_service import check_alerts
from app.services.anomaly_detector import _detectors

router = APIRouter()


@router.post("/ingest")
def ingest_metrics(payload: MetricPayload, db: Session = Depends(get_db)):
    write_metrics(payload)
    check_alerts(payload, db)
    return {"status": "ok", "host": payload.hostname}


@router.get("/query/{measurement}")
def get_metrics(measurement: str, host: str, minutes: int = 30):
    data = query_metrics(measurement, host, minutes)
    return {"measurement": measurement, "host": host, "data": data}


@router.get("/anomaly/status")
def get_anomaly_status():
    """Returns current ML detector status for all hosts"""
    status = {}
    for hostname, detector in _detectors.items():
        status[hostname] = {
            "is_trained": detector.is_trained,
            "total_points": detector.total_points,
            "anomaly_count": detector.anomaly_count,
            "buffer_size": len(detector.buffer),
        }
    return status

@router.get("/hosts")
def get_hosts():
    from app.services.metrics_service import query_metrics
    from app.core.config import get_settings
    from app.core.influx import get_query_api
    settings = get_settings()
    query_api = get_query_api()
    query = f'''
        from(bucket: "{settings.INFLUXDB_BUCKET}")
        |> range(start: -1h)
        |> filter(fn: (r) => r._measurement == "cpu")
        |> keep(columns: ["host"])
        |> distinct(column: "host")
    '''
    try:
        tables = query_api.query(query, org=settings.INFLUXDB_ORG)
        hosts = []
        for table in tables:
            for record in table.records:
                host = record.values.get("host")
                if host and host not in hosts:
                    hosts.append(host)
        return {"hosts": hosts}
    except Exception as e:
        return {"hosts": []}