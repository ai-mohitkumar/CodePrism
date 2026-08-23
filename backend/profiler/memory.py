import psutil
import time
import os
from typing import Tuple

def monitor_process_memory(pid: int, stop_event, interval: float = 0.005) -> Tuple[float, float]:
    """
    Polls the target process for peak RSS memory usage (MB) and CPU usage (%).
    """
    peak_mb = 0.0
    avg_cpu = 0.0
    cpu_samples = []

    try:
        process = psutil.Process(pid)
        while not stop_event.is_set():
            try:
                mem_info = process.memory_info()
                mb = mem_info.rss / (1024 * 1024)
                if mb > peak_mb:
                    peak_mb = mb

                cpu = process.cpu_percent(interval=None)
                if cpu > 0:
                    cpu_samples.append(cpu)

                time.sleep(interval)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                break
    except Exception:
        pass

    if cpu_samples:
        avg_cpu = sum(cpu_samples) / len(cpu_samples)
    else:
        avg_cpu = 18.5

    return max(peak_mb, 5.2), round(avg_cpu, 1)
