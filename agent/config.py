import os
from dotenv import load_dotenv

load_dotenv(dotenv_path="../.env")

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
AGENT_INTERVAL_SECONDS = int(os.getenv("AGENT_INTERVAL_SECONDS", 5))
HOSTNAME = os.uname().nodename

KAFKA_BROKER = os.getenv("KAFKA_BROKER", "localhost:9092")
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "metrics")