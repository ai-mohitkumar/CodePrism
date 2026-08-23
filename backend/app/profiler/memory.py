import psutil
import time
import os
from typing import Tuple

def monitor_process_memory(pid: int, stop_event, interval: float = 0.005) -> float:
    """
    Polls the target process for peak RSS memory usage in Megabytes (MB).
    """
    peak_mb = 0.0
    try:
        process = psutil.Process(pid)
        while not stop_event.is_set():
            try:
                mem_info = process.memory_info()
                mb = mem_info.rss / (1024 * 1024)
                if mb > peak_mb:
                    peak_mb = mb
                time.sleep(interval)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                break
    except Exception:
        pass
    return max(peak_mb, 4.0)  # Baseline process footprint
