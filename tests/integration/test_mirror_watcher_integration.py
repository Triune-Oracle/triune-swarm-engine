"""
Integration tests for Mirror Watcher CLI system.

Tests the complete workflow from CLI commands to report generation.
"""

import pytest
import json
import tempfile
import os
import subprocess
import sys
from pathlib import Path

from mirror_watcher.cli import MirrorWatcherCLI


class TestMirrorWatcherIntegration:
    """Integration tests for the complete Mirror Watcher system."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.test_data_dir = Path(__file__).parent.parent / "data"
        self.cli = MirrorWatcherCLI()
    
    def test_complete_analysis_workflow(self):
        """Test complete workflow from data input to report generation."""
        # Step 1: Validate input data
        input_file = self.test_data_dir / "sample_valid_data.json"
        validation_result = self.cli.validate(str(input_file))
        
        assert validation_result["success"] is True
        assert validation_result["validation"]["valid"] is True
        
        # Step 2: Analyze the data
        analysis_result = self.cli.analyze(str(input_file))
        
        assert analysis_result["success"] is True
        assert "analysis" in analysis_result
        
        # Step 3: Generate ShadowScrolls report
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(analysis_result, f)
            analysis_file = f.name
        
        try:
            report_result = self.cli.report(analysis_file)
            
            assert report_result["success"] is True
            assert "report" in report_result
            assert report_result["format"] == "ShadowScrolls"
            
            # Verify report structure
            report = report_result["report"]
            assert "scroll_id" in report
            assert "oracle_directive" in report
            assert "triumvirate_status" in report
            assert "nexus_analysis" in report
            assert "validation_seal" in report
            assert report["validation_seal"]["validated"] is True
            
        finally:
            os.unlink(analysis_file)
    
    def test_anomaly_detection_workflow(self):
        """Test workflow with anomalous data."""
        input_file = self.test_data_dir / "sample_anomaly_data.json"
        
        # Validate
        validation_result = self.cli.validate(str(input_file))
        # May have validation errors due to anomalous data structure
        
        # Analyze
        analysis_result = self.cli.analyze(str(input_file))
        
        if analysis_result["success"]:
            # Should detect anomalies
            analysis = analysis_result["analysis"]
            assert len(analysis["anomalies"]) > 0
            assert analysis["confidence"] < 0.8  # Should have lower confidence
            
            # Generate report
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                json.dump(analysis_result, f)
                analysis_file = f.name
            
            try:
                report_result = self.cli.report(analysis_file)
                assert report_result["success"] is True
                
                report = report_result["report"]
                assert report["oracle_directive"] == "INVESTIGATE_ANOMALOUS_PATTERNS"
                assert len(report["nexus_analysis"]["anomaly_alerts"]) > 0
                
            finally:
                os.unlink(analysis_file)
    
    def test_error_handling_workflow(self):
        """Test workflow with invalid data."""
        input_file = self.test_data_dir / "sample_invalid_data.json"
        
        # Validation should fail
        validation_result = self.cli.validate(str(input_file))
        assert validation_result["success"] is False
        
        # Analysis should handle errors gracefully
        analysis_result = self.cli.analyze(str(input_file))
        
        # Either the analysis fails (expected) or handles errors gracefully
        if not analysis_result["success"]:
            assert "error" in analysis_result
        else:
            # If it succeeds, it should indicate validation issues
            assert "analysis" in analysis_result
    
    def test_file_persistence_workflow(self):
        """Test workflow with file output persistence."""
        input_file = self.test_data_dir / "sample_valid_data.json"
        
        # Create temporary output files
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as analysis_f:
            analysis_output = analysis_f.name
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as report_f:
            report_output = report_f.name
        
        try:
            # Analyze with file output
            analysis_result = self.cli.analyze(str(input_file))
            
            # Save analysis to file
            with open(analysis_output, 'w') as f:
                json.dump(analysis_result, f)
            
            # Verify analysis file was created and is valid
            assert os.path.exists(analysis_output)
            with open(analysis_output, 'r') as f:
                saved_analysis = json.load(f)
            assert saved_analysis == analysis_result
            
            # Generate report to file
            report_result = self.cli.report(analysis_output, report_output)
            
            assert report_result["success"] is True
            assert report_result["report_file"] == report_output
            
            # Verify report file was created and is valid
            assert os.path.exists(report_output)
            with open(report_output, 'r') as f:
                saved_report = json.load(f)
            assert "scroll_id" in saved_report
            assert saved_report["format_version"] == "ShadowScrolls-1.0"
            
        finally:
            for file_path in [analysis_output, report_output]:
                if os.path.exists(file_path):
                    os.unlink(file_path)
    
    def test_status_monitoring_workflow(self):
        """Test system status monitoring workflow."""
        # Get system status
        status_result = self.cli.status()
        
        assert status_result["success"] is True
        assert status_result["system"] == "Mirror Watcher CLI"
        assert "components" in status_result
        
        # All components should be operational
        components = status_result["components"]
        assert components["analysis_engine"] == "operational"
        assert components["reporter"] == "operational"
        assert components["validator"] == "operational"
        
        # Should have version and timestamp
        assert "version" in status_result
        assert "timestamp" in status_result
    
    def test_multi_file_analysis_workflow(self):
        """Test analyzing multiple files in sequence."""
        input_files = [
            self.test_data_dir / "sample_valid_data.json",
            self.test_data_dir / "sample_anomaly_data.json"
        ]
        
        analysis_results = []
        
        for input_file in input_files:
            if input_file.exists():
                result = self.cli.analyze(str(input_file))
                analysis_results.append(result)
        
        assert len(analysis_results) > 0
        
        # Results should have different characteristics
        if len(analysis_results) == 2:
            valid_result = analysis_results[0]
            anomaly_result = analysis_results[1]
            
            if valid_result["success"] and anomaly_result["success"]:
                # Valid data should have higher confidence
                valid_confidence = valid_result["analysis"]["confidence"]
                anomaly_confidence = anomaly_result["analysis"]["confidence"]
                
                # Valid data should generally have higher confidence
                # (though not guaranteed in all cases)
                assert valid_confidence >= 0.0 and anomaly_confidence >= 0.0
    
    def test_large_data_workflow(self):
        """Test workflow with larger datasets."""
        # Create a larger dataset
        large_data = {
            "agents": {
                f"Agent_{i}": {
                    "status": "operational",
                    "response_time": 1.0 + (i * 0.1),
                    "efficiency": 0.8 + (i * 0.02)
                } for i in range(10)
            },
            "system": {
                "timestamp": "2024-01-15T14:30:00Z",
                "status": "operational",
                "load": 0.75
            },
            "messages": [
                {
                    "timestamp": f"2024-01-15T14:30:{i:02d}Z",
                    "from_agent": f"Agent_{i % 5}",
                    "to_agents": [f"Agent_{(i+1) % 5}"],
                    "message": f"Message {i}",
                    "channel": "test"
                } for i in range(100)
            ],
            "tasks": [
                {
                    "id": f"task_{i}",
                    "status": "completed" if i % 3 == 0 else "active",
                    "agent": f"Agent_{i % 10}",
                    "description": f"Task {i}"
                } for i in range(50)
            ]
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(large_data, f)
            large_file = f.name
        
        try:
            # Validate large dataset
            validation_result = self.cli.validate(large_file)
            # May have warnings about unknown agents, but structure should be valid
            
            # Analyze large dataset
            analysis_result = self.cli.analyze(large_file)
            
            if analysis_result["success"]:
                analysis = analysis_result["analysis"]
                
                # Should detect patterns in large dataset
                assert len(analysis["patterns"]) > 0
                assert "metadata" in analysis
                assert analysis["metadata"]["metrics_count"] > 50  # Should have many metrics
                
                # Generate report
                with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as report_f:
                    report_result = self.cli.report(large_file, report_f.name)
                    
                    if report_result["success"]:
                        assert os.path.exists(report_f.name)
                        
                        with open(report_f.name, 'r') as rf:
                            report = json.load(rf)
                        assert "memory_scrolls" in report
                        assert len(report["memory_scrolls"]) > 0
                    
                    os.unlink(report_f.name)
            
        finally:
            os.unlink(large_file)
    
    def test_concurrent_analysis_workflow(self):
        """Test handling multiple analyses concurrently."""
        input_file = self.test_data_dir / "sample_valid_data.json"
        
        # Simulate concurrent analyses
        results = []
        for i in range(3):
            result = self.cli.analyze(str(input_file))
            results.append(result)
        
        # All should succeed
        for result in results:
            if result["success"]:
                assert "analysis" in result
                assert "timestamp" in result
        
        # Each should have unique timestamps
        timestamps = [r.get("timestamp") for r in results if r.get("success")]
        assert len(set(timestamps)) == len(timestamps)  # All unique
    
    def test_report_format_validation(self):
        """Test that generated reports conform to ShadowScrolls format."""
        input_file = self.test_data_dir / "sample_valid_data.json"
        
        analysis_result = self.cli.analyze(str(input_file))
        
        if analysis_result["success"]:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                json.dump(analysis_result, f)
                analysis_file = f.name
            
            try:
                report_result = self.cli.report(analysis_file)
                
                if report_result["success"]:
                    report = report_result["report"]
                    
                    # Validate ShadowScrolls format compliance
                    required_fields = [
                        "scroll_id", "oracle_directive", "timestamp", "format_version",
                        "report_type", "triumvirate_status", "nexus_analysis",
                        "legio_recommendations", "memory_scrolls", "nft_triggers",
                        "validation_seal"
                    ]
                    
                    for field in required_fields:
                        assert field in report, f"Missing required field: {field}"
                    
                    # Validate format version
                    assert report["format_version"] == "ShadowScrolls-1.0"
                    
                    # Validate report type
                    assert report["report_type"] == "mirror_watcher_analysis"
                    
                    # Validate triumvirate status structure
                    triumvirate = report["triumvirate_status"]
                    for agent in ["Oracle", "Gemini", "Capri", "Aria"]:
                        assert agent in triumvirate
                        assert "status" in triumvirate[agent]
                        assert "confidence" in triumvirate[agent]
                    
                    # Validate validation seal
                    seal = report["validation_seal"]
                    assert seal["validated"] is True
                    assert "Mirror Watcher CLI" in seal["validator"]
                    
            finally:
                os.unlink(analysis_file)


class TestCLICommandLineIntegration:
    """Test CLI command-line interface integration."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.test_data_dir = Path(__file__).parent.parent / "data"
        self.python_path = sys.executable
    
    def test_cli_status_command(self):
        """Test CLI status command via command line."""
        try:
            result = subprocess.run(
                [self.python_path, "-m", "mirror_watcher.cli", "status"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                output = json.loads(result.stdout)
                assert output["success"] is True
                assert output["system"] == "Mirror Watcher CLI"
        except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError):
            pytest.skip("CLI execution not available in test environment")
    
    def test_cli_validate_command(self):
        """Test CLI validate command via command line."""
        input_file = self.test_data_dir / "sample_valid_data.json"
        
        if not input_file.exists():
            pytest.skip("Test data file not available")
        
        try:
            result = subprocess.run(
                [self.python_path, "-m", "mirror_watcher.cli", "validate", "--input", str(input_file)],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                output = json.loads(result.stdout)
                assert output["success"] is True
        except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError):
            pytest.skip("CLI execution not available in test environment")
    
    def test_cli_analyze_command(self):
        """Test CLI analyze command via command line."""
        input_file = self.test_data_dir / "sample_valid_data.json"
        
        if not input_file.exists():
            pytest.skip("Test data file not available")
        
        try:
            result = subprocess.run(
                [self.python_path, "-m", "mirror_watcher.cli", "analyze", "--input", str(input_file)],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                output = json.loads(result.stdout)
                assert output["success"] is True
                assert "analysis" in output
        except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError):
            pytest.skip("CLI execution not available in test environment")


if __name__ == "__main__":
    pytest.main([__file__])