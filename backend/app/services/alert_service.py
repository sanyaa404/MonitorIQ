# backend/app/services/alert_service.py
from sqlalchemy.orm import Session
from app.models.alert import AlertRule, AlertEvent
from app.schemas.metrics import MetricPayload
import logging

log = logging.getLogger(__name__)

OPERATORS = {
    "gt": lambda v, t: v > t,
    "lt": lambda v, t: v < t,
    "gte": lambda v, t: v >= t,
    "lte": lambda v, t: v <= t,
}

def get_metric_value(payload: MetricPayload, metric: str):
    metric_map = {
        "cpu_percent_total": payload.cpu.cpu_percent_total,
        "load_avg_1m": payload.cpu.load_avg_1m,
        "ram_percent": payload.memory.ram_percent,
        "swap_percent": payload.memory.swap_percent,
        "ram_available_gb": payload.memory.ram_available_gb,
        "total_processes": payload.processes.total_processes,
    }
    return metric_map.get(metric)

def check_alerts(payload: MetricPayload, db: Session):
    rules = db.query(AlertRule).filter(
        AlertRule.is_active == True,
    ).all()

    for rule in rules:
        # Skip if rule is for a specific host that doesn't match
        if rule.hostname and rule.hostname != payload.hostname:
            continue

        value = get_metric_value(payload, rule.metric)
        if value is None:
            continue

        op_fn = OPERATORS.get(rule.operator)
        if op_fn and op_fn(value, rule.threshold):
            event = AlertEvent(
                rule_id=rule.id,
                rule_name=rule.name,
                hostname=payload.hostname,
                metric=rule.metric,
                value=value,
                threshold=rule.threshold,
            )
            db.add(event)
            db.commit()
            log.warning(
                f"ALERT: {rule.name} | {rule.metric}={value} "
                f"{rule.operator} {rule.threshold} on {payload.hostname}"
            )