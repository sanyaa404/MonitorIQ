# backend/app/services/metrics_service.py
from influxdb_client import Point, WritePrecision
from app.core.influx import get_write_api, get_query_api
from app.core.config import get_settings
from app.schemas.metrics import MetricPayload
import logging

log = logging.getLogger(__name__)
settings = get_settings()

def write_metrics(payload: MetricPayload):
    write_api = get_write_api()
    points = []
    ts = payload.timestamp
    host = payload.hostname

    # CPU points
    points.append(
        Point("cpu")
        .tag("host", host)
        .field("percent_total", payload.cpu.cpu_percent_total)
        .field("load_avg_1m", payload.cpu.load_avg_1m)
        .field("load_avg_5m", payload.cpu.load_avg_5m)
        .field("load_avg_15m", payload.cpu.load_avg_15m)
        .field("times_user", payload.cpu.cpu_times_user)
        .field("times_system", payload.cpu.cpu_times_system)
        .field("times_idle", payload.cpu.cpu_times_idle)
        .time(ts, WritePrecision.NS)
    )

    # Per-core CPU
    for i, core_pct in enumerate(payload.cpu.cpu_percent_per_core):
        points.append(
            Point("cpu_core")
            .tag("host", host)
            .tag("core", str(i))
            .field("percent", core_pct)
            .time(ts, WritePrecision.NS)
        )

    # Memory points
    points.append(
        Point("memory")
        .tag("host", host)
        .field("ram_percent", payload.memory.ram_percent)
        .field("ram_used_gb", payload.memory.ram_used_gb)
        .field("ram_available_gb", payload.memory.ram_available_gb)
        .field("swap_percent", payload.memory.swap_percent)
        .field("swap_used_gb", payload.memory.swap_used_gb)
        .time(ts, WritePrecision.NS)
    )

    # Disk points
    for part in payload.disk.partitions:
        points.append(
            Point("disk")
            .tag("host", host)
            .tag("mountpoint", part.mountpoint)
            .field("percent", part.percent)
            .field("used_gb", part.used_gb)
            .field("free_gb", part.free_gb)
            .time(ts, WritePrecision.NS)
        )

    # Network points
    points.append(
        Point("network")
        .tag("host", host)
        .field("bytes_sent_mb", payload.network.bytes_sent_mb)
        .field("bytes_recv_mb", payload.network.bytes_recv_mb)
        .field("packets_sent", payload.network.packets_sent)
        .field("packets_recv", payload.network.packets_recv)
        .field("errors_in", payload.network.errors_in)
        .field("errors_out", payload.network.errors_out)
        .time(ts, WritePrecision.NS)
    )

    # Process points
    points.append(
        Point("processes")
        .tag("host", host)
        .field("total", payload.processes.total_processes)
        .time(ts, WritePrecision.NS)
    )

    write_api.write(
        bucket=settings.INFLUXDB_BUCKET,
        org=settings.INFLUXDB_ORG,
        record=points
    )
    log.info(f"Wrote {len(points)} points to InfluxDB for host: {host}")


def query_metrics(measurement: str, host: str, minutes: int = 30):
    query_api = get_query_api()
    query = f'''
        from(bucket: "{settings.INFLUXDB_BUCKET}")
        |> range(start: -{minutes}m)
        |> filter(fn: (r) => r._measurement == "{measurement}")
        |> filter(fn: (r) => r.host == "{host}")
        |> aggregateWindow(every: 30s, fn: mean, createEmpty: false)
        |> yield(name: "mean")
    '''
    tables = query_api.query(query, org=settings.INFLUXDB_ORG)
    results = []
    for table in tables:
        for record in table.records:
            results.append({
                "time": record.get_time().isoformat(),
                "field": record.get_field(),
                "value": record.get_value(),
                "host": record.values.get("host"),
            })
    return results