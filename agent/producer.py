# agent/producer.py
import json
import logging
from kafka import KafkaProducer
from kafka.errors import KafkaError, NoBrokersAvailable
from config import KAFKA_BROKER, KAFKA_TOPIC, HOSTNAME

log = logging.getLogger(__name__)

_producer = None

def get_producer():
    global _producer
    if _producer is None:
        try:
            _producer = KafkaProducer(
                bootstrap_servers=[KAFKA_BROKER],
                value_serializer=lambda v: json.dumps(v, default=str).encode("utf-8"),
                key_serializer=lambda k: k.encode("utf-8"),
                acks="all",
                retries=3,
                retry_backoff_ms=500,
                request_timeout_ms=10000,
            )
            log.info(f"Kafka producer connected to {KAFKA_BROKER}")
        except NoBrokersAvailable:
            log.error("Kafka not reachable — falling back to HTTP")
            return None
    return _producer


def publish(payload: dict) -> bool:
    producer = get_producer()
    if producer is None:
        return False
    try:
        future = producer.send(
            KAFKA_TOPIC,
            key=HOSTNAME,
            value=payload,
        )
        producer.flush(timeout=5)
        record_metadata = future.get(timeout=5)
        log.info(
            f"Published to Kafka | "
            f"topic={record_metadata.topic} "
            f"partition={record_metadata.partition} "
            f"offset={record_metadata.offset}"
        )
        return True
    except KafkaError as e:
        log.error(f"Kafka publish failed: {e}")
        return False