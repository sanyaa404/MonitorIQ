# agent/collectors/process.py
import psutil

def collect():
    # First call to initialize CPU measurement
    procs = list(psutil.process_iter(
        ['pid', 'name', 'cpu_percent', 'memory_percent', 'status']
    ))

    # Small pause so psutil can measure CPU delta
    import time
    time.sleep(0.5)

    # Second call gives accurate CPU readings
    processes = []
    for proc in sorted(
        psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status']),
        key=lambda p: p.info['cpu_percent'] or 0,
        reverse=True
    )[:10]:
        try:
            processes.append({
                "pid": proc.info['pid'],
                "name": proc.info['name'],
                "cpu_percent": proc.info['cpu_percent'],
                "memory_percent": round(proc.info['memory_percent'] or 0, 2),
                "status": proc.info['status'],
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    return {
        "total_processes": len(psutil.pids()),
        "top_processes": processes,
    }