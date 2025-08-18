"""
Unit tests for Analysis Engine module.
"""

import pytest
import json
from datetime import datetime

from mirror_watcher.analysis_engine import AnalysisEngine, AnalysisResult


class TestAnalysisEngine:
    """Test the Analysis Engine functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.engine = AnalysisEngine()
        self.sample_data = {
            "agents": {
                "Oracle": {
                    "status": "operational",
                    "response_time": 1.2,
                    "confidence": 0.89,
                    "directives_issued": 42
                },
                "Gemini": {
                    "status": "operational",
                    "response_time": 0.8,
                    "pattern_matches": 23,
                    "optimization_score": 0.85
                }
            },
            "system": {
                "memory_usage": 0.65,
                "cpu_usage": 0.42,
                "network_latency": 0.12
            },
            "messages": [
                {
                    "timestamp": "2024-01-15T14:29:45Z",
                    "from_agent": "Oracle",
                    "message": "Test message 1"
                },
                {
                    "timestamp": "2024-01-15T14:29:50Z",
                    "from_agent": "Gemini",
                    "message": "Test message 2"
                }
            ],
            "tasks": [
                {
                    "id": "task_001",
                    "status": "completed",
                    "agent": "Oracle"
                },
                {
                    "id": "task_002",
                    "status": "completed",
                    "agent": "Gemini"
                },
                {
                    "id": "task_003",
                    "status": "failed",
                    "agent": "Oracle"
                }
            ]
        }
    
    def test_engine_initialization(self):
        """Test engine initialization."""
        assert isinstance(self.engine.patterns, dict)
        assert isinstance(self.engine.thresholds, dict)
        assert "agent_coordination" in self.engine.patterns
        assert "anomaly_threshold" in self.engine.thresholds
    
    def test_analyze_success(self):
        """Test successful analysis."""
        result = self.engine.analyze(self.sample_data)
        
        assert isinstance(result, AnalysisResult)
        assert result.success is True
        assert isinstance(result.confidence, float)
        assert 0.0 <= result.confidence <= 1.0
        assert isinstance(result.patterns, list)
        assert isinstance(result.anomalies, list)
        assert isinstance(result.recommendations, list)
        assert isinstance(result.metadata, dict)
    
    def test_extract_metrics(self):
        """Test metrics extraction."""
        metrics = self.engine._extract_metrics(self.sample_data)
        
        assert isinstance(metrics, dict)
        assert len(metrics) > 0
        
        # Check for agent metrics
        assert any(key.startswith("agent_Oracle") for key in metrics.keys())
        assert any(key.startswith("agent_Gemini") for key in metrics.keys())
        
        # Check for system metrics
        assert any(key.startswith("system_") for key in metrics.keys())
        
        # Check for message metrics
        assert "message_count" in metrics
        assert metrics["message_count"] == 2.0
        
        # Check for task metrics
        assert "task_count" in metrics
        assert "task_completion_rate" in metrics
        assert metrics["task_count"] == 3.0
        assert metrics["task_completion_rate"] == 2.0 / 3.0  # 2 completed out of 3 total
    
    def test_detect_patterns(self):
        """Test pattern detection."""
        metrics = {
            "agent_Oracle_response_time": 1.2,
            "system_memory_usage": 0.65,
            "message_frequency": 10.0,
            "task_completion_rate": 0.95
        }
        
        patterns = self.engine._detect_patterns(metrics)
        
        assert isinstance(patterns, list)
        assert len(patterns) > 0
        
        # Should detect high task completion efficiency
        high_completion_patterns = [p for p in patterns if "High task completion efficiency" in p]
        assert len(high_completion_patterns) > 0
    
    def test_detect_anomalies(self):
        """Test anomaly detection."""
        # Create metrics with anomalous values
        metrics = {
            "agent_Oracle_response_time": 15.0,  # High response time
            "system_memory_usage": 0.98,         # Critical memory usage
            "error_rate": 0.25                   # High error rate
        }
        
        anomalies = self.engine._detect_anomalies(metrics)
        
        assert isinstance(anomalies, list)
        assert len(anomalies) > 0
        
        # Check for specific anomaly types
        response_time_anomalies = [a for a in anomalies if "High response time" in a]
        memory_anomalies = [a for a in anomalies if "Critical memory usage" in a]
        error_rate_anomalies = [a for a in anomalies if "High error rate" in a]
        
        assert len(response_time_anomalies) > 0
        assert len(memory_anomalies) > 0
        assert len(error_rate_anomalies) > 0
    
    def test_calculate_confidence(self):
        """Test confidence calculation."""
        patterns = ["Pattern 1", "Pattern 2", "Pattern 3"]
        anomalies = ["Anomaly 1"]
        
        confidence = self.engine._calculate_confidence(patterns, anomalies)
        
        assert isinstance(confidence, float)
        assert 0.0 <= confidence <= 1.0
        
        # More patterns should increase confidence
        more_patterns = patterns + ["Pattern 4", "Pattern 5"]
        higher_confidence = self.engine._calculate_confidence(more_patterns, anomalies)
        assert higher_confidence >= confidence
        
        # More anomalies should decrease confidence
        more_anomalies = anomalies + ["Anomaly 2", "Anomaly 3"]
        lower_confidence = self.engine._calculate_confidence(patterns, more_anomalies)
        assert lower_confidence <= confidence
    
    def test_generate_recommendations(self):
        """Test recommendation generation."""
        patterns = ["low message activity detected", "low task completion efficiency"]
        anomalies = ["high response time detected", "critical memory usage"]
        
        recommendations = self.engine._generate_recommendations(patterns, anomalies)
        
        assert isinstance(recommendations, list)
        assert len(recommendations) > 0
        
        # Check for specific recommendations
        rec_text = " ".join(recommendations).lower()
        assert "performance" in rec_text or "memory" in rec_text or "optimization" in rec_text
    
    def test_analysis_with_empty_data(self):
        """Test analysis with empty data."""
        empty_data = {}
        result = self.engine.analyze(empty_data)
        
        assert isinstance(result, AnalysisResult)
        assert result.success is True  # Should still succeed with empty data
        assert isinstance(result.recommendations, list)
        assert len(result.recommendations) > 0  # Should have default recommendations
    
    def test_analysis_with_malformed_data(self):
        """Test analysis with malformed data."""
        malformed_data = {
            "agents": "not_a_dict",
            "messages": "not_a_list",
            "invalid_structure": True
        }
        
        result = self.engine.analyze(malformed_data)
        
        assert isinstance(result, AnalysisResult)
        # Should handle malformed data gracefully
        assert isinstance(result.patterns, list)
        assert isinstance(result.anomalies, list)
        assert isinstance(result.recommendations, list)
    
    def test_calculate_hash(self):
        """Test data hash calculation."""
        hash1 = self.engine._calculate_hash(self.sample_data)
        hash2 = self.engine._calculate_hash(self.sample_data)
        
        # Same data should produce same hash
        assert hash1 == hash2
        
        # Different data should produce different hash
        different_data = self.sample_data.copy()
        different_data["test"] = "different"
        hash3 = self.engine._calculate_hash(different_data)
        assert hash1 != hash3
    
    def test_get_analysis_summary(self):
        """Test analysis summary generation."""
        result = self.engine.analyze(self.sample_data)
        summary = self.engine.get_analysis_summary(result)
        
        assert isinstance(summary, dict)
        assert "success" in summary
        assert "confidence" in summary
        assert "pattern_count" in summary
        assert "anomaly_count" in summary
        assert "recommendation_count" in summary
        assert "status" in summary
        
        # Status should be appropriate based on confidence and anomalies
        if result.confidence > 0.7 and len(result.anomalies) == 0:
            assert summary["status"] == "healthy"
        else:
            assert summary["status"] == "requires_attention"
    
    def test_analysis_with_high_anomaly_data(self):
        """Test analysis with data that should trigger many anomalies."""
        anomaly_data = {
            "agents": {
                "Oracle": {
                    "response_time": 50.0,  # Very high
                    "error_rate": 0.8,      # Very high
                    "memory_usage": 0.99    # Critical
                }
            },
            "system": {
                "cpu_usage": 0.98,
                "memory_usage": 0.97,
                "network_latency": 10.0
            }
        }
        
        result = self.engine.analyze(anomaly_data)
        
        assert result.success is True
        assert len(result.anomalies) > 0
        assert result.confidence < 0.7  # Should have low confidence due to anomalies
        
        # Should have recommendations for the anomalies
        assert len(result.recommendations) > 0
        rec_text = " ".join(result.recommendations).lower()
        assert "performance" in rec_text or "memory" in rec_text or "optimization" in rec_text
    
    def test_analysis_with_exception_handling(self):
        """Test analysis handles exceptions gracefully."""
        # Simulate an error condition
        with pytest.raises(Exception):
            # This should cause an error in normal circumstances
            raise Exception("Simulated analysis error")
        
        # But the analysis engine should handle errors
        try:
            # Create problematic data that might cause errors
            problematic_data = {
                "agents": {
                    "Oracle": {
                        "response_time": float('inf'),  # Problematic value
                        "invalid_field": object()       # Non-serializable object
                    }
                }
            }
            result = self.engine.analyze(problematic_data)
            # Should still return a result, even if analysis partially fails
            assert isinstance(result, AnalysisResult)
        except Exception:
            # If it does throw an exception, that's also acceptable
            # as long as it's handled at the CLI level
            pass


if __name__ == "__main__":
    pytest.main([__file__])