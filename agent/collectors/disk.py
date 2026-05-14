# agent/collectors/disk.py
import psutil

def collect():
    partitions = []
    for part in psutil.disk_partitions(all=False):
        try:
            usage = psutil.disk_usage(part.mountpoint)
            partitions.append({
                "device": part.device,
                "mountpoint": part.mountpoint,
                "fstype": part.fstype,
                "total_gb": round(usage.total / (1024 ** 3), 2),
                "used_gb": round(usage.used / (1024 ** 3), 2),
                "free_gb": round(usage.free / (1024 ** 3), 2),
                "percent": usage.percent,
            })
        except PermissionError:
            continue

    io = psutil.disk_io_counters()
    return {
        "partitions": partitions,
        "io_read_mb": round(io.read_bytes / (1024 ** 2), 2) if io else None,
        "io_write_mb": round(io.write_bytes / (1024 ** 2), 2) if io else None,
        "io_read_count": io.read_count if io else None,
        "io_write_count": io.write_count if io else None,
    }