"""Tests for metrics service."""
import pytest
import time
from app.services.metrics_service import Metrics


class TestMetrics:
    """Test cases for Metrics class."""
    
    def test_initial_state(self):
        """Test initial metrics state."""
        metrics = Metrics()
        
        assert metrics.request_count == 0
        assert metrics.error_count == 0
        assert len(metrics.response_times) == 0
    
    def test_increment_request(self):
        """Test incrementing request count."""
        metrics = Metrics()
        
        metrics.increment_request()
        assert metrics.request_count == 1
        
        metrics.increment_request()
        assert metrics.request_count == 2
    
    def test_increment_request_with_endpoint(self):
        """Test incrementing request with endpoint tracking."""
        metrics = Metrics()
        
        metrics.increment_request("/api/hit")
        metrics.increment_request("/api/hit")
        metrics.increment_request("/api/stand")
        
        assert metrics.endpoint_counts["/api/hit"] == 2
        assert metrics.endpoint_counts["/api/stand"] == 1
    
    def test_increment_error(self):
        """Test incrementing error count."""
        metrics = Metrics()
        
        metrics.increment_error()
        assert metrics.error_count == 1
    
    def test_record_response_time(self):
        """Test recording response times."""
        metrics = Metrics()
        
        metrics.record_response_time(10.5)
        metrics.record_response_time(20.5)
        
        assert len(metrics.response_times) == 2
    
    def test_get_avg_response_time(self):
        """Test average response time calculation."""
        metrics = Metrics()
        
        metrics.record_response_time(10.0)
        metrics.record_response_time(20.0)
        metrics.record_response_time(30.0)
        
        assert metrics.get_avg_response_time() == 20.0
    
    def test_get_avg_response_time_empty(self):
        """Test average response time with no data."""
        metrics = Metrics()
        
        assert metrics.get_avg_response_time() == 0.0
    
    def test_response_time_limit(self):
        """Test response times limited to 1000 entries."""
        metrics = Metrics()
        
        for i in range(1500):
            metrics.record_response_time(float(i))
        
        assert len(metrics.response_times) == 1000
    
    def test_get_uptime(self):
        """Test uptime calculation."""
        metrics = Metrics()
        
        time.sleep(0.1)
        uptime = metrics.get_uptime()
        
        assert uptime >= 0.1
    
    def test_to_dict(self):
        """Test dictionary conversion."""
        metrics = Metrics()
        metrics.increment_request("/api/hit")
        metrics.increment_error()
        metrics.record_response_time(15.0)
        
        data = metrics.to_dict()
        
        assert data["request_count"] == 1
        assert data["error_count"] == 1
        assert data["avg_response_time_ms"] == 15.0
        assert "/api/hit" in data["endpoints"]
    
    def test_prometheus_format(self):
        """Test Prometheus format output."""
        metrics = Metrics()
        metrics.increment_request()
        metrics.increment_error()
        
        output = metrics.get_prometheus_format()
        
        assert "blackjack_requests_total 1" in output
        assert "blackjack_errors_total 1" in output
        assert "# HELP" in output
        assert "# TYPE" in output
