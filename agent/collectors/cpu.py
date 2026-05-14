import psutil

def collect():
    cpu_times = psutil.cpu_times_percent(interval=1)
    return {
        "cpu_percent_total": psutil.cpu_percent(interval=None),
        "cpu_percent_per_core": psutil.cpu_percent(percpu=True),
        "cpu_count_logical": psutil.cpu_count(logical=True),
        "cpu_count_physical": psutil.cpu_count(logical=False),
        "cpu_freq_mhz": psutil.cpu_freq().current if psutil.cpu_freq() else None,
        "cpu_times_user": cpu_times.user,
        "cpu_times_system": cpu_times.system,
        "cpu_times_idle": cpu_times.idle,
        "load_avg_1m": psutil.getloadavg()[0],
        "load_avg_5m": psutil.getloadavg()[1],
        "load_avg_15m": psutil.getloadavg()[2],
    }