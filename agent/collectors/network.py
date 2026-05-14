# agent/collectors/network.py
import psutil
import platform

def collect():
    net = psutil.net_io_counters()
    interfaces = []
    for name, stats in psutil.net_if_stats().items():
        iface = {
            "name": name,
            "is_up": stats.isup,
            "mtu": stats.mtu,
        }
        # speed_mbps is unreliable on macOS, only include on Linux
        if platform.system() == "Linux":
            iface["speed_mbps"] = stats.speed

        interfaces.append(iface)

    return {
        "bytes_sent_mb": round(net.bytes_sent / (1024 ** 2), 2),
        "bytes_recv_mb": round(net.bytes_recv / (1024 ** 2), 2),
        "packets_sent": net.packets_sent,
        "packets_recv": net.packets_recv,
        "errors_in": net.errin,
        "errors_out": net.errout,
        "drop_in": net.dropin,
        "drop_out": net.dropout,
        "interfaces": interfaces,
    }