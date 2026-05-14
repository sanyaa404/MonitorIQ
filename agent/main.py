# agent/main.py
import time
import json
import logging
from datetime import datetime, timezone
import requests

from config import BACKEND_URL, AGENT_INTERVAL_SECONDS, HOSTNAME
from collectors import cpu, memory, disk, network, process

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [AGENT] %(levelname)s %(message)s"
)
log = logging.getLogger(__name__)

def collect_all():
    return {
        "hostname": HOSTNAME,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "cpu": cpu.collect(),
        "memory": memory.collect(),
        "disk": disk.collect(),
        "network": network.collect(),
        "processes": process.collect(),
    }

def ship(payload: dict):
    try:
        resp = requests.post(
            f"{BACKEND_URL}/api/v1/metrics/ingest",
            json=payload,
            timeout=5
        )
        resp.raise_for_status()
        log.info(f"Shipped metrics | CPU: {payload['cpu']['cpu_percent_total']}% | RAM: {payload['memory']['ram_percent']}%")
    except requests.exceptions.ConnectionError:
        log.warning("Backend not reachable — will retry next interval")
    except requests.exceptions.HTTPError as e:
        log.error(f"Backend rejected payload: {e}")
    except Exception as e:
        log.error(f"Unexpected error: {e}")

def main():
    log.info(f"Agent starting on host: {HOSTNAME}")
    log.info(f"Shipping to: {BACKEND_URL} every {AGENT_INTERVAL_SECONDS}s")

    while True:
        try:
            payload = collect_all()
            ship(payload)
        except Exception as e:
            log.error(f"Collection error: {e}")
        time.sleep(AGENT_INTERVAL_SECONDS)

if __name__ == "__main__":
    main()