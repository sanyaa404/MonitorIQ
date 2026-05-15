# backend/app/services/kafka_consumer.py
import json
import logging
import threading
from kafka import KafkaConsumer
from kafka.errors import NoBrokersAvailable

from app.core.config import get_settings
from app.core.database import SessionLocal
from app.schemas.metrics import MetricPayload
from app.services.metrics_service import write_metrics
from app.services.alert_service import check_alerts

log = logging.getLogger(__name__)
settings = get_settings()

KAFKA_BROKER = "localhost:9092"
KAFKA_TOPIC = "metrics"
CONSUMER_GROUP = "monitoring-backend"


def process_message(raw_value: bytes):
    """Parse one Kafka message and process it"""
    try:
        data = json.loads(raw_value.decode("utf-8"))
        payload = MetricPayload(**data)

        # Write to InfluxDB
        write_metrics(payload)

        # Check alert rules against PostgreSQL
        db = SessionLocal()
        try:
            check_alerts(payload, db)
        finally:
            db.close()

        log.info(f"Processed metrics from {payload.hostname} | CPU: {payload.cpu.cpu_percent_total}%")

    except Exception as e:
        log.error(f"Failed to process message: {e}")


def consume_loop():
    """Main consumer loop — runs in a background thread"""
    log.info(f"Starting Kafka consumer | broker={KAFKA_BROKER} | topic={KAFKA_TOPIC} | group={CONSUMER_GROUP}")

    while True:
        try:
            consumer = KafkaConsumer(
                KAFKA_TOPIC,
                bootstrap_servers=[KAFKA_BROKER],
                group_id=CONSUMER_GROUP,
                value_deserializer=lambda v: v,  # raw bytes, we parse manually
                auto_offset_reset="latest",
                enable_auto_commit=True,
                auto_commit_interval_ms=1000,
                consumer_timeout_ms=-1,  # block forever waiting for messages
                session_timeout_ms=30000,
                heartbeat_interval_ms=10000,
            )
            log.info("Kafka consumer connected successfully")

            for message in consumer:
                process_message(message.value)

        except NoBrokersAvailable:
            log.warning("Kafka not available — retrying in 5s")
            import time
            time.sleep(5)
        except Exception as e:
            log.error(f"Consumer error: {e} — restarting in 5s")
            import time
            time.sleep(5)


def start_consumer():
    """Start the consumer in a background daemon thread"""
    thread = threading.Thread(
        target=consume_loop,
        name="kafka-consumer",
        daemon=True  # dies when main process dies
    )
    thread.start()
    log.info("Kafka consumer thread started")
    return thread