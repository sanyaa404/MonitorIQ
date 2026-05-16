# backend/app/services/kafka_consumer.py
import json
import logging
import threading
import asyncio
from kafka import KafkaConsumer
from kafka.errors import NoBrokersAvailable

from app.core.config import get_settings
from app.core.database import SessionLocal
from app.schemas.metrics import MetricPayload
from app.services.metrics_service import write_metrics
from app.services.alert_service import check_alerts
from app.services.ws_manager import manager
from app.services.anomaly_detector import run_anomaly_detection

log = logging.getLogger(__name__)
settings = get_settings()

KAFKA_BROKER = "localhost:9092"
KAFKA_TOPIC = "metrics"
CONSUMER_GROUP = "monitoring-backend"

_loop = None


def set_event_loop(loop):
    global _loop
    _loop = loop


def broadcast_to_clients(payload: MetricPayload, anomaly_result: dict):
    """Broadcast metric snapshot + anomaly result to WebSocket clients"""
    if _loop is None or not manager.active_connections:
        return

    data = {
        "type": "metrics",
        "hostname": payload.hostname,
        "timestamp": payload.timestamp.isoformat(),
        "cpu": {
            "percent_total": payload.cpu.cpu_percent_total,
            "load_avg_1m": payload.cpu.load_avg_1m,
            "load_avg_5m": payload.cpu.load_avg_5m,
        },
        "memory": {
            "ram_percent": payload.memory.ram_percent,
            "ram_used_gb": payload.memory.ram_used_gb,
            "ram_available_gb": payload.memory.ram_available_gb,
            "swap_percent": payload.memory.swap_percent,
        },
        "disk": {
            "partitions": [
                {
                    "mountpoint": p.mountpoint,
                    "percent": p.percent,
                    "used_gb": p.used_gb,
                    "free_gb": p.free_gb,
                }
                for p in payload.disk.partitions
            ]
        },
        "network": {
            "bytes_sent_mb": payload.network.bytes_sent_mb,
            "bytes_recv_mb": payload.network.bytes_recv_mb,
            "packets_sent": payload.network.packets_sent,
            "packets_recv": payload.network.packets_recv,
        },
        "processes": {
            "total": payload.processes.total_processes,
            "top": [
                {
                    "pid": p.pid,
                    "name": p.name,
                    "cpu_percent": p.cpu_percent,
                    "memory_percent": p.memory_percent,
                    "status": p.status,
                }
                for p in payload.processes.top_processes
            ],
        },
        # Anomaly detection result included in every broadcast
        "anomaly": anomaly_result,
    }

    asyncio.run_coroutine_threadsafe(manager.broadcast(data), _loop)


def process_message(raw_value: bytes):
    try:
        data = json.loads(raw_value.decode("utf-8"))
        payload = MetricPayload(**data)

        # 1. Write to InfluxDB
        write_metrics(payload)

        # 2. Check threshold alert rules
        db = SessionLocal()
        try:
            check_alerts(payload, db)
        finally:
            db.close()

        # 3. Run ML anomaly detection
        anomaly_result = run_anomaly_detection(payload)

        # 4. Push everything to WebSocket clients
        broadcast_to_clients(payload, anomaly_result)

        # Log anomalies prominently
        if anomaly_result.get("is_anomaly"):
            log.warning(
                f"🚨 ANOMALY | host={payload.hostname} | "
                f"score={anomaly_result.get('score')} | "
                f"CPU={payload.cpu.cpu_percent_total}%"
            )
        else:
            log.info(
                f"Processed | host={payload.hostname} | "
                f"CPU={payload.cpu.cpu_percent_total}% | "
                f"ML={anomaly_result.get('status')} | "
                f"score={anomaly_result.get('score')}"
            )

    except Exception as e:
        log.error(f"Failed to process message: {e}")


def consume_loop():
    log.info(f"Starting Kafka consumer | broker={KAFKA_BROKER} | topic={KAFKA_TOPIC}")

    while True:
        try:
            consumer = KafkaConsumer(
                KAFKA_TOPIC,
                bootstrap_servers=[KAFKA_BROKER],
                group_id=CONSUMER_GROUP,
                value_deserializer=lambda v: v,
                auto_offset_reset="latest",
                enable_auto_commit=True,
                auto_commit_interval_ms=1000,
                consumer_timeout_ms=-1,
                session_timeout_ms=30000,
                heartbeat_interval_ms=10000,
            )
            log.info("Kafka consumer connected")

            for message in consumer:
                process_message(message.value)

        except NoBrokersAvailable:
            log.warning("Kafka not available — retrying in 5s")
            import time; time.sleep(5)
        except Exception as e:
            log.error(f"Consumer error: {e} — restarting in 5s")
            import time; time.sleep(5)


def start_consumer():
    thread = threading.Thread(
        target=consume_loop,
        name="kafka-consumer",
        daemon=True
    )
    thread.start()
    log.info("Kafka consumer thread started")
    return thread