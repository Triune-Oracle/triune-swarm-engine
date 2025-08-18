"""
Unit tests for ShadowScrolls Report Generator module.
"""

import pytest
import json
from datetime import datetime

from mirror_watcher.report_generator import ShadowScrollsReporter


class TestShadowScrollsReporter:
    """Test the ShadowScrolls Report Generator functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.reporter = ShadowScrollsReporter()
        self.sample_analysis_data = {
            "success": True,
            "timestamp": "2024-01-15T14:30:00Z",
            "analysis": {
                "success": True,
                "confidence": 0.85,
                "patterns": [
                    "Normal operation pattern detected",
                    "High task completion efficiency",
                    "Optimal resource utilization"
                ],
                "anomalies": [
                    "Minor response time variation in Gemini agent"
                ],
                "recommendations": [
                    "Continue current monitoring protocols",
                    "Consider optimizing Gemini response algorithms"
                ],
                "metadata": {
                    "analysis_timestamp": "2024-01-15T14:30:00Z",
                    "data_hash": "abc123def456",
                    "metrics_count": 15,
                    "pattern_matches": 3,
                    "anomaly_count": 1
                }
            }
        }
    
    def test_reporter_initialization(self):
        """Test reporter initialization."""
        assert isinstance(self.reporter.scroll_template, dict)
        assert self.reporter.format_version == "ShadowScrolls-1.0"
        assert "scroll_id" in self.reporter.scroll_template
        assert "triumvirate_status" in self.reporter.scroll_template
        assert "nexus_analysis" in self.reporter.scroll_template
    
    def test_generate_report_success(self):
        """Test successful report generation."""
        report = self.reporter.generate_report(self.sample_analysis_data)
        
        assert isinstance(report, dict)
        assert "scroll_id" in report
        assert "oracle_directive" in report
        assert "timestamp" in report
        assert "format_version" in report
        assert report["format_version"] == "ShadowScrolls-1.0"
        assert "triumvirate_status" in report
        assert "nexus_analysis" in report
        assert "legio_recommendations" in report
        assert "memory_scrolls" in report
        assert "nft_triggers" in report
        assert "validation_seal" in report
    
    def test_scroll_id_uniqueness(self):
        """Test that scroll IDs are unique."""
        report1 = self.reporter.generate_report(self.sample_analysis_data)
        report2 = self.reporter.generate_report(self.sample_analysis_data)
        
        assert report1["scroll_id"] != report2["scroll_id"]
        assert report1["scroll_id"].startswith("SCROLL_")
        assert report2["scroll_id"].startswith("SCROLL_")
    
    def test_extract_oracle_directive(self):
        """Test Oracle directive extraction."""
        # High confidence data
        high_confidence_data = self.sample_analysis_data.copy()
        high_confidence_data["analysis"]["confidence"] = 0.9
        
        directive = self.reporter._extract_oracle_directive(high_confidence_data)
        assert directive == "MAINTAIN_OPERATIONAL_EXCELLENCE"
        
        # Data with anomalies
        anomaly_data = self.sample_analysis_data.copy()
        anomaly_data["analysis"]["anomalies"] = ["Critical system error", "Memory leak detected"]
        
        directive = self.reporter._extract_oracle_directive(anomaly_data)
        assert directive == "INVESTIGATE_ANOMALOUS_PATTERNS"
        
        # Data with many patterns
        pattern_data = self.sample_analysis_data.copy()
        pattern_data["analysis"]["patterns"] = [f"Pattern {i}" for i in range(10)]
        
        directive = self.reporter._extract_oracle_directive(pattern_data)
        assert directive == "OPTIMIZE_DETECTED_PATTERNS"
    
    def test_process_triumvirate_status(self):
        """Test Triumvirate status processing."""
        triumvirate = self.reporter._process_triumvirate_status(self.sample_analysis_data)
        
        assert isinstance(triumvirate, dict)
        assert "Oracle" in triumvirate
        assert "Gemini" in triumvirate
        assert "Capri" in triumvirate
        assert "Aria" in triumvirate
        
        for agent_name, agent_data in triumvirate.items():
            assert "status" in agent_data
            assert "confidence" in agent_data
            assert isinstance(agent_data["confidence"], float)
            assert 0.0 <= agent_data["confidence"] <= 1.0
            assert agent_data["status"] in ["optimal", "operational", "degraded", "critical"]
    
    def test_process_nexus_analysis(self):
        """Test Nexus analysis processing."""
        nexus = self.reporter._process_nexus_analysis(self.sample_analysis_data)
        
        assert isinstance(nexus, dict)
        assert "pattern_detection" in nexus
        assert "anomaly_alerts" in nexus
        assert "system_health" in nexus
        assert "confidence_score" in nexus
        
        # Check pattern detection structure
        assert isinstance(nexus["pattern_detection"], list)
        if len(nexus["pattern_detection"]) > 0:
            pattern = nexus["pattern_detection"][0]
            assert "pattern" in pattern
            assert "detected_at" in pattern
            assert "classification" in pattern
        
        # Check anomaly alerts structure
        assert isinstance(nexus["anomaly_alerts"], list)
        if len(nexus["anomaly_alerts"]) > 0:
            alert = nexus["anomaly_alerts"][0]
            assert "anomaly" in alert
            assert "severity" in alert
            assert "detected_at" in alert
            assert "requires_attention" in alert
        
        # Check system health
        assert nexus["system_health"] in ["optimal", "good", "degraded", "critical"]
        assert isinstance(nexus["confidence_score"], float)
    
    def test_generate_legio_recommendations(self):
        """Test Legio recommendations generation."""
        recommendations = self.reporter._generate_legio_recommendations(self.sample_analysis_data)
        
        assert isinstance(recommendations, list)
        assert len(recommendations) > 0
        
        for rec in recommendations:
            assert isinstance(rec, dict)
            assert "recommendation" in rec
            assert "priority" in rec
            assert "assigned_to" in rec
            assert "timeline" in rec
            assert "impact" in rec
            
            assert rec["priority"] in ["high", "medium", "low"]
            assert rec["assigned_to"] in ["Oracle", "Gemini", "Capri", "Aria"]
            assert rec["impact"] in ["high", "medium", "low", "maintenance"]
    
    def test_create_memory_scrolls(self):
        """Test memory scroll creation."""
        memory_scrolls = self.reporter._create_memory_scrolls(self.sample_analysis_data)
        
        assert isinstance(memory_scrolls, list)
        assert len(memory_scrolls) > 0
        
        scroll = memory_scrolls[0]
        assert "memory_id" in scroll
        assert "content_type" in scroll
        assert "content" in scroll
        assert "timestamp" in scroll
        assert "relevance_score" in scroll
        assert "archive_ready" in scroll
        
        assert scroll["content_type"] == "analysis_result"
        assert isinstance(scroll["relevance_score"], float)
        assert 0.0 <= scroll["relevance_score"] <= 1.0
        assert scroll["memory_id"].startswith("MEM_")
    
    def test_check_nft_triggers(self):
        """Test NFT trigger detection."""
        # High value analysis data
        high_value_data = self.sample_analysis_data.copy()
        high_value_data["analysis"]["confidence"] = 0.95
        high_value_data["analysis"]["patterns"] = [f"Pattern {i}" for i in range(15)]
        high_value_data["analysis"]["anomalies"] = [f"Anomaly {i}" for i in range(8)]
        
        nft_triggers = self.reporter._check_nft_triggers(high_value_data)
        
        assert isinstance(nft_triggers, list)
        
        if len(nft_triggers) > 0:
            trigger = nft_triggers[0]
            assert "trigger_type" in trigger
            assert "rarity_score" in trigger
            assert "trigger_conditions" in trigger
            assert "estimated_value" in trigger
            assert "mint_recommendation" in trigger
            
            assert isinstance(trigger["rarity_score"], float)
            assert 0.0 <= trigger["rarity_score"] <= 1.0
            assert trigger["estimated_value"] in ["premium", "high", "medium", "standard"]
    
    def test_apply_validation_seal(self):
        """Test validation seal application."""
        sample_scroll = {
            "scroll_id": "test_scroll",
            "oracle_directive": "TEST_DIRECTIVE",
            "timestamp": "2024-01-15T14:30:00Z"
        }
        
        seal = self.reporter._apply_validation_seal(sample_scroll)
        
        assert isinstance(seal, dict)
        assert "validated" in seal
        assert "validator" in seal
        assert "seal_timestamp" in seal
        assert "validation_hash" in seal
        assert "oracle_approved" in seal
        
        assert seal["validated"] is True
        assert "Mirror Watcher CLI" in seal["validator"]
        assert seal["oracle_approved"] is True
    
    def test_create_error_scroll(self):
        """Test error scroll creation."""
        error_message = "Test error occurred"
        error_scroll = self.reporter._create_error_scroll(error_message)
        
        assert isinstance(error_scroll, dict)
        assert error_scroll["scroll_id"].startswith("ERROR_")
        assert error_scroll["oracle_directive"] == "ERROR_RECOVERY_REQUIRED"
        assert error_scroll["report_type"] == "error_report"
        assert "error" in error_scroll
        assert error_scroll["error"]["message"] == error_message
        assert "recovery_actions" in error_scroll["error"]
        assert error_scroll["validation_seal"]["validated"] is False
    
    def test_classification_methods(self):
        """Test pattern and anomaly classification methods."""
        # Test pattern classification
        normal_pattern = "System within normal operating parameters"
        assert self.reporter._classify_pattern(normal_pattern) == "normal_operation"
        
        performance_pattern = "High efficiency optimization detected"
        assert self.reporter._classify_pattern(performance_pattern) == "performance_optimization"
        
        degradation_pattern = "Low response time detected"
        assert self.reporter._classify_pattern(degradation_pattern) == "performance_degradation"
        
        # Test anomaly severity classification
        critical_anomaly = "Critical system failure detected"
        assert self.reporter._classify_anomaly_severity(critical_anomaly) == "high"
        
        moderate_anomaly = "Moderate performance degradation"
        assert self.reporter._classify_anomaly_severity(moderate_anomaly) == "medium"
        
        minor_anomaly = "Minor configuration issue"
        assert self.reporter._classify_anomaly_severity(minor_anomaly) == "low"
    
    def test_recommendation_assessment_methods(self):
        """Test recommendation assessment methods."""
        # Test priority assessment
        critical_rec = "Critical system optimization required"
        assert self.reporter._assess_recommendation_priority(critical_rec) == "high"
        
        optimization_rec = "Optimize memory allocation algorithms"
        assert self.reporter._assess_recommendation_priority(optimization_rec) == "medium"
        
        maintenance_rec = "Continue standard monitoring"
        assert self.reporter._assess_recommendation_priority(maintenance_rec) == "low"
        
        # Test agent assignment
        memory_rec = "Optimize memory usage patterns"
        assert self.reporter._assign_recommendation_agent(memory_rec) == "Capri"
        
        network_rec = "Improve network communication protocols"
        assert self.reporter._assign_recommendation_agent(network_rec) == "Aria"
        
        analysis_rec = "Analyze pattern detection algorithms"
        assert self.reporter._assign_recommendation_agent(analysis_rec) == "Gemini"
        
        general_rec = "Review system architecture"
        assert self.reporter._assign_recommendation_agent(general_rec) == "Oracle"
    
    def test_hash_calculation_methods(self):
        """Test hash calculation methods."""
        # Test data hash calculation
        test_data = {"test": "data", "value": 123}
        hash1 = self.reporter._calculate_data_hash(test_data)
        hash2 = self.reporter._calculate_data_hash(test_data)
        
        assert hash1 == hash2  # Same data should produce same hash
        assert isinstance(hash1, str)
        assert len(hash1) == 16  # Should be truncated to 16 characters
        
        # Test validation hash calculation
        test_scroll = {"scroll_id": "test", "content": "test content"}
        val_hash1 = self.reporter._calculate_validation_hash(test_scroll)
        val_hash2 = self.reporter._calculate_validation_hash(test_scroll)
        
        assert val_hash1 == val_hash2
        assert isinstance(val_hash1, str)
        assert len(val_hash1) == 16
    
    def test_analysis_summary_creation(self):
        """Test analysis summary creation."""
        summary = self.reporter._create_analysis_summary(self.sample_analysis_data)
        
        assert isinstance(summary, str)
        assert "confidence" in summary.lower()
        assert "patterns" in summary.lower() or "anomalies" in summary.lower()
    
    def test_key_findings_extraction(self):
        """Test key findings extraction."""
        findings = self.reporter._extract_key_findings(self.sample_analysis_data)
        
        assert isinstance(findings, list)
        assert len(findings) > 0
        
        findings_text = " ".join(findings).lower()
        assert "pattern" in findings_text or "anomaly" in findings_text or "confidence" in findings_text
    
    def test_relevance_score_calculation(self):
        """Test relevance score calculation."""
        score = self.reporter._calculate_relevance_score(self.sample_analysis_data)
        
        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0
        
        # High confidence and anomalies should increase relevance
        high_value_data = self.sample_analysis_data.copy()
        high_value_data["analysis"]["confidence"] = 0.95
        high_value_data["analysis"]["anomalies"] = ["Anomaly 1", "Anomaly 2", "Anomaly 3"]
        
        high_score = self.reporter._calculate_relevance_score(high_value_data)
        assert high_score >= score
    
    def test_nft_value_estimation(self):
        """Test NFT value estimation."""
        premium_score = 0.95
        assert self.reporter._estimate_nft_value(premium_score) == "premium"
        
        high_score = 0.85
        assert self.reporter._estimate_nft_value(high_score) == "high"
        
        medium_score = 0.75
        assert self.reporter._estimate_nft_value(medium_score) == "medium"
        
        standard_score = 0.65
        assert self.reporter._estimate_nft_value(standard_score) == "standard"
    
    def test_report_with_minimal_data(self):
        """Test report generation with minimal analysis data."""
        minimal_data = {
            "success": True,
            "analysis": {
                "confidence": 0.5,
                "patterns": [],
                "anomalies": [],
                "recommendations": []
            }
        }
        
        report = self.reporter.generate_report(minimal_data)
        
        assert isinstance(report, dict)
        assert "scroll_id" in report
        assert report["format_version"] == "ShadowScrolls-1.0"
        # Should handle minimal data gracefully
        assert len(report["legio_recommendations"]) > 0  # Should have default recommendations
    
    def test_report_with_exception_handling(self):
        """Test report generation handles exceptions gracefully."""
        # Test with problematic data
        problematic_data = {
            "analysis": {
                "confidence": "not_a_number",
                "patterns": "not_a_list",
                "invalid_field": object()
            }
        }
        
        report = self.reporter.generate_report(problematic_data)
        
        # Should either generate a report or an error scroll
        assert isinstance(report, dict)
        assert "scroll_id" in report
        
        if "error" in report:
            # Error scroll
            assert report["scroll_id"].startswith("ERROR_")
            assert report["oracle_directive"] == "ERROR_RECOVERY_REQUIRED"
        else:
            # Regular report (handled gracefully)
            assert report["format_version"] == "ShadowScrolls-1.0"


if __name__ == "__main__":
    pytest.main([__file__])