"""Metrics service for application monitoring."""
import time
from dataclasses import dataclass, field
from threading import Lock
from typing import Dict, List
from collections import deque


@dataclass
class Metrics:
    """Application metrics container."""
    request_count: int = 0
    error_count: int = 0
    response_times: deque = field(default_factory=lambda: deque(maxlen=1000))
    endpoint_counts: Dict[str, int] = field(default_factory=dict)
    start_time: float = field(default_factory=time.time)
    _lock: Lock = field(default_factory=Lock)
    
    def increment_request(self, endpoint: str = None):
        """Increment request counter."""
        with self._lock:
            self.request_count += 1
            if endpoint:
                self.endpoint_counts[endpoint] = self.endpoint_counts.get(endpoint, 0) + 1
    
    def increment_error(self):
        """Increment error counter."""
        with self._lock:
            self.error_count += 1
    
    def record_response_time(self, duration_ms: float):
        """Record a response time."""
        with self._lock:
            self.response_times.append(duration_ms)
    
    def get_avg_response_time(self) -> float:
        """Get average response time in milliseconds."""
        with self._lock:
            if not self.response_times:
                return 0.0
            return sum(self.response_times) / len(self.response_times)
    
    def get_uptime(self) -> float:
        """Get application uptime in seconds."""
        return time.time() - self.start_time
    
    def to_dict(self) -> dict:
        """Convert metrics to dictionary."""
        return {
            "request_count": self.request_count,
            "error_count": self.error_count,
            "avg_response_time_ms": round(self.get_avg_response_time(), 2),
            "uptime_seconds": round(self.get_uptime(), 2),
            "endpoints": dict(self.endpoint_counts)
        }
    
    def get_prometheus_format(self) -> str:
        """Return metrics in Prometheus format."""
        lines = [
            f"# HELP blackjack_requests_total Total number of requests",
            f"# TYPE blackjack_requests_total counter",
            f"blackjack_requests_total {self.request_count}",
            f"",
            f"# HELP blackjack_errors_total Total number of errors",
            f"# TYPE blackjack_errors_total counter",
            f"blackjack_errors_total {self.error_count}",
            f"",
            f"# HELP blackjack_response_time_ms Average response time in milliseconds",
            f"# TYPE blackjack_response_time_ms gauge",
            f"blackjack_response_time_ms {round(self.get_avg_response_time(), 2)}",
            f"",
            f"# HELP blackjack_uptime_seconds Application uptime in seconds",
            f"# TYPE blackjack_uptime_seconds counter",
            f"blackjack_uptime_seconds {round(self.get_uptime(), 2)}",
        ]
        
        # Add endpoint-specific metrics
        for endpoint, count in self.endpoint_counts.items():
            safe_endpoint = endpoint.replace("/", "_").replace("-", "_").strip("_")
            lines.extend([
                f"",
                f"# HELP blackjack_endpoint_{safe_endpoint}_total Requests to {endpoint}",
                f"# TYPE blackjack_endpoint_{safe_endpoint}_total counter",
                f"blackjack_endpoint_{safe_endpoint}_total {count}",
            ])
        
        return "\n".join(lines)


# Global metrics instance
metrics = Metrics()


def get_metrics() -> Metrics:
    """Get global metrics instance."""
    return metrics
