import time
from datetime import datetime, timezone
import collections
from typing import List, Dict, Any

# Bounded deque storing up to 50 entries
_request_logs = collections.deque(maxlen=50)

def log_request(endpoint: str, provider_source: str, latency_ms: float, results_count: int, mode: str = "LIVE"):
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "endpoint": endpoint,
        "provider_source": provider_source,
        "latency_ms": round(latency_ms, 2),
        "results_count": results_count,
        "mode": mode
    }
    _request_logs.appendleft(entry)

def get_logs() -> List[Dict[str, Any]]:
    return list(_request_logs)
