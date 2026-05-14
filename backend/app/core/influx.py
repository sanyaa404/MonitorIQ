# backend/app/core/influx.py
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
from app.core.config import get_settings

settings = get_settings()

client = InfluxDBClient(
    url=settings.INFLUXDB_URL,
    token=settings.INFLUXDB_TOKEN,
    org=settings.INFLUXDB_ORG
)

write_api = client.write_api(write_options=SYNCHRONOUS)
query_api = client.query_api()

def get_write_api():
    return write_api

def get_query_api():
    return query_api