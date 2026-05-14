# backend/app/schemas/metrics.py
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class CPUMetrics(BaseModel):
    cpu_percent_total: float
    cpu_percent_per_core: List[float]
    cpu_count_logical: int
    cpu_count_physical: Optional[int]
    cpu_freq_mhz: Optional[float]
    cpu_times_user: float
    cpu_times_system: float
    cpu_times_idle: float
    load_avg_1m: float
    load_avg_5m: float
    load_avg_15m: float

class MemoryMetrics(BaseModel):
    ram_total_gb: float
    ram_used_gb: float
    ram_available_gb: float
    ram_percent: float
    swap_total_gb: float
    swap_used_gb: float
    swap_percent: float

class DiskPartition(BaseModel):
    device: str
    mountpoint: str
    fstype: str
    total_gb: float
    used_gb: float
    free_gb: float
    percent: float

class DiskMetrics(BaseModel):
    partitions: List[DiskPartition]
    io_read_mb: Optional[float]
    io_write_mb: Optional[float]
    io_read_count: Optional[int]
    io_write_count: Optional[int]

class NetworkMetrics(BaseModel):
    bytes_sent_mb: float
    bytes_recv_mb: float
    packets_sent: int
    packets_recv: int
    errors_in: int
    errors_out: int
    drop_in: int
    drop_out: int
    interfaces: List[dict]

class ProcessInfo(BaseModel):
    pid: int
    name: str
    cpu_percent: Optional[float]
    memory_percent: float
    status: str

class ProcessMetrics(BaseModel):
    total_processes: int
    top_processes: List[ProcessInfo]

class MetricPayload(BaseModel):
    hostname: str
    timestamp: datetime
    cpu: CPUMetrics
    memory: MemoryMetrics
    disk: DiskMetrics
    network: NetworkMetrics
    processes: ProcessMetrics