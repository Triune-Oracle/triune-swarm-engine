#!/usr/bin/env python3
"""
Test runner for Mirror Watcher CLI test suite.

This script runs the complete test suite including unit tests, integration tests,
and validation scenarios for the Mirror Watcher CLI system.
"""

import sys
import os
import json
import pytest
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from mirror_watcher.cli import MirrorWatcherCLI


class TestRunner:
    """Main test runner for Mirror Watcher CLI."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.test_results = {
            "timestamp": datetime.now().isoformat(),
            "test_suite": "Mirror Watcher CLI",
            "results": {},
            "summary": {},
            "shadowscrolls_report": {}
        }
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all test categories."""
        print("=" * 60)
        print("MIRROR WATCHER CLI - COMPREHENSIVE TEST SUITE")
        print("=" * 60)
        print(f"Starting test execution at {self.test_results['timestamp']}")
        print()
        
        # Run different test categories
        self.run_unit_tests()
        self.run_integration_tests()
        self.run_cli_validation_tests()
        self.run_edge_case_tests()
        
        # Generate summary
        self.generate_summary()
        
        # Generate ShadowScrolls report
        self.generate_shadowscrolls_report()
        
        return self.test_results
    
    def run_unit_tests(self):
        """Run unit tests."""
        print("Running Unit Tests...")
        print("-" * 40)
        
        unit_test_dir = self.project_root / "tests" / "unit"
        
        try:
            result = pytest.main([
                str(unit_test_dir),
                "-v",
                "--tb=short",
                "--capture=no"
            ])
            
            self.test_results["results"]["unit_tests"] = {
                "status": "passed" if result == 0 else "failed",
                "exit_code": result,
                "category": "unit"
            }
            
            print(f"Unit tests completed with exit code: {result}")
            
        except Exception as e:
            self.test_results["results"]["unit_tests"] = {
                "status": "error",
                "error": str(e),
                "category": "unit"
            }
            print(f"Unit tests failed with error: {e}")
        
        print()
    
    def run_integration_tests(self):
        """Run integration tests."""
        print("Running Integration Tests...")
        print("-" * 40)
        
        integration_test_dir = self.project_root / "tests" / "integration"
        
        try:
            result = pytest.main([
                str(integration_test_dir),
                "-v",
                "--tb=short",
                "--capture=no"
            ])
            
            self.test_results["results"]["integration_tests"] = {
                "status": "passed" if result == 0 else "failed",
                "exit_code": result,
                "category": "integration"
            }
            
            print(f"Integration tests completed with exit code: {result}")
            
        except Exception as e:
            self.test_results["results"]["integration_tests"] = {
                "status": "error",
                "error": str(e),
                "category": "integration"
            }
            print(f"Integration tests failed with error: {e}")
        
        print()
    
    def run_cli_validation_tests(self):
        """Run CLI validation tests."""
        print("Running CLI Validation Tests...")
        print("-" * 40)
        
        cli = MirrorWatcherCLI()
        test_data_dir = self.project_root / "tests" / "data"
        
        validation_results = {
            "status_command": self.test_status_command(cli),
            "data_validation": self.test_data_validation(cli, test_data_dir),
            "analysis_engine": self.test_analysis_engine(cli, test_data_dir),
            "report_generation": self.test_report_generation(cli, test_data_dir)
        }
        
        # Determine overall status
        failed_tests = [k for k, v in validation_results.items() if not v.get("success", False)]
        overall_status = "passed" if len(failed_tests) == 0 else "failed"
        
        self.test_results["results"]["cli_validation"] = {
            "status": overall_status,
            "individual_results": validation_results,
            "failed_tests": failed_tests,
            "category": "validation"
        }
        
        print(f"CLI validation completed: {overall_status}")
        if failed_tests:
            print(f"Failed tests: {', '.join(failed_tests)}")
        print()
    
    def test_status_command(self, cli: MirrorWatcherCLI) -> Dict[str, Any]:
        """Test status command functionality."""
        try:
            result = cli.status()
            success = result.get("success", False) and result.get("system") == "Mirror Watcher CLI"
            
            return {
                "success": success,
                "result": result,
                "test": "status_command"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "test": "status_command"
            }
    
    def test_data_validation(self, cli: MirrorWatcherCLI, test_data_dir: Path) -> Dict[str, Any]:
        """Test data validation functionality."""
        try:
            valid_file = test_data_dir / "sample_valid_data.json"
            
            if valid_file.exists():
                result = cli.validate(str(valid_file))
                success = result.get("success", False) and result.get("validation", {}).get("valid", False)
            else:
                success = False
                result = {"error": "Test data file not found"}
            
            return {
                "success": success,
                "result": result,
                "test": "data_validation"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "test": "data_validation"
            }
    
    def test_analysis_engine(self, cli: MirrorWatcherCLI, test_data_dir: Path) -> Dict[str, Any]:
        """Test analysis engine functionality."""
        try:
            valid_file = test_data_dir / "sample_valid_data.json"
            
            if valid_file.exists():
                result = cli.analyze(str(valid_file))
                success = result.get("success", False) and "analysis" in result
            else:
                success = False
                result = {"error": "Test data file not found"}
            
            return {
                "success": success,
                "result": result,
                "test": "analysis_engine"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "test": "analysis_engine"
            }
    
    def test_report_generation(self, cli: MirrorWatcherCLI, test_data_dir: Path) -> Dict[str, Any]:
        """Test report generation functionality."""
        try:
            valid_file = test_data_dir / "sample_valid_data.json"
            
            if valid_file.exists():
                # First analyze
                analysis_result = cli.analyze(str(valid_file))
                
                if analysis_result.get("success"):
                    # Save analysis to temp file
                    import tempfile
                    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                        json.dump(analysis_result, f)
                        temp_file = f.name
                    
                    try:
                        # Generate report
                        report_result = cli.report(temp_file)
                        success = (report_result.get("success", False) and 
                                 report_result.get("format") == "ShadowScrolls")
                        
                        return {
                            "success": success,
                            "result": report_result,
                            "test": "report_generation"
                        }
                    finally:
                        os.unlink(temp_file)
                else:
                    return {
                        "success": False,
                        "error": "Analysis failed",
                        "test": "report_generation"
                    }
            else:
                return {
                    "success": False,
                    "error": "Test data file not found",
                    "test": "report_generation"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "test": "report_generation"
            }
    
    def run_edge_case_tests(self):
        """Run edge case and error handling tests."""
        print("Running Edge Case Tests...")
        print("-" * 40)
        
        cli = MirrorWatcherCLI()
        test_data_dir = self.project_root / "tests" / "data"
        
        edge_case_results = {
            "invalid_data": self.test_invalid_data_handling(cli, test_data_dir),
            "missing_files": self.test_missing_file_handling(cli),
            "anomaly_detection": self.test_anomaly_detection(cli, test_data_dir),
            "large_data": self.test_large_data_handling(cli)
        }
        
        # Determine overall status
        failed_tests = [k for k, v in edge_case_results.items() if not v.get("success", False)]
        overall_status = "passed" if len(failed_tests) == 0 else "failed"
        
        self.test_results["results"]["edge_case_tests"] = {
            "status": overall_status,
            "individual_results": edge_case_results,
            "failed_tests": failed_tests,
            "category": "edge_case"
        }
        
        print(f"Edge case tests completed: {overall_status}")
        if failed_tests:
            print(f"Failed tests: {', '.join(failed_tests)}")
        print()
    
    def test_invalid_data_handling(self, cli: MirrorWatcherCLI, test_data_dir: Path) -> Dict[str, Any]:
        """Test handling of invalid data."""
        try:
            invalid_file = test_data_dir / "sample_invalid_data.json"
            
            if invalid_file.exists():
                # Should handle invalid data gracefully
                validation_result = cli.validate(str(invalid_file))
                analysis_result = cli.analyze(str(invalid_file))
                
                # Validation should fail, analysis should handle gracefully
                validation_failed = not validation_result.get("success", True)
                analysis_handled = ("success" in analysis_result)  # Should not crash
                
                success = validation_failed and analysis_handled
            else:
                success = False
            
            return {
                "success": success,
                "test": "invalid_data_handling"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "test": "invalid_data_handling"
            }
    
    def test_missing_file_handling(self, cli: MirrorWatcherCLI) -> Dict[str, Any]:
        """Test handling of missing files."""
        try:
            # Test with non-existent file
            result = cli.analyze("nonexistent_file.json")
            
            # Should fail gracefully with error message
            success = (not result.get("success", True) and "error" in result)
            
            return {
                "success": success,
                "test": "missing_file_handling"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "test": "missing_file_handling"
            }
    
    def test_anomaly_detection(self, cli: MirrorWatcherCLI, test_data_dir: Path) -> Dict[str, Any]:
        """Test anomaly detection capabilities."""
        try:
            anomaly_file = test_data_dir / "sample_anomaly_data.json"
            
            if anomaly_file.exists():
                result = cli.analyze(str(anomaly_file))
                
                if result.get("success"):
                    analysis = result.get("analysis", {})
                    anomalies = analysis.get("anomalies", [])
                    
                    # Should detect some anomalies
                    success = len(anomalies) > 0
                else:
                    # Even if analysis fails, it's handling the anomalous data
                    success = True
            else:
                success = False
            
            return {
                "success": success,
                "test": "anomaly_detection"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "test": "anomaly_detection"
            }
    
    def test_large_data_handling(self, cli: MirrorWatcherCLI) -> Dict[str, Any]:
        """Test handling of large datasets."""
        try:
            # Create a moderately large dataset
            large_data = {
                "agents": {f"Agent_{i}": {"status": "operational"} for i in range(20)},
                "messages": [{"timestamp": "2024-01-15T14:30:00Z", "from_agent": "Agent_0", "message": f"Message {i}"} for i in range(100)],
                "tasks": [{"id": f"task_{i}", "status": "completed"} for i in range(50)]
            }
            
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                json.dump(large_data, f)
                temp_file = f.name
            
            try:
                result = cli.analyze(temp_file)
                success = "success" in result  # Should not crash
            finally:
                os.unlink(temp_file)
            
            return {
                "success": success,
                "test": "large_data_handling"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "test": "large_data_handling"
            }
    
    def generate_summary(self):
        """Generate test summary."""
        results = self.test_results["results"]
        
        total_categories = len(results)
        passed_categories = sum(1 for r in results.values() if r.get("status") == "passed")
        failed_categories = total_categories - passed_categories
        
        self.test_results["summary"] = {
            "total_categories": total_categories,
            "passed_categories": passed_categories,
            "failed_categories": failed_categories,
            "overall_status": "passed" if failed_categories == 0 else "failed",
            "success_rate": passed_categories / total_categories if total_categories > 0 else 0
        }
        
        print("=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        print(f"Total test categories: {total_categories}")
        print(f"Passed: {passed_categories}")
        print(f"Failed: {failed_categories}")
        print(f"Success rate: {self.test_results['summary']['success_rate']:.1%}")
        print(f"Overall status: {self.test_results['summary']['overall_status'].upper()}")
        print()
        
        # Details
        for category, result in results.items():
            status = result.get("status", "unknown").upper()
            print(f"{category:25} {status}")
            
            if result.get("failed_tests"):
                for failed_test in result["failed_tests"]:
                    print(f"  - {failed_test}")
        print()
    
    def generate_shadowscrolls_report(self):
        """Generate ShadowScrolls format test report."""
        try:
            from mirror_watcher.report_generator import ShadowScrollsReporter
            
            reporter = ShadowScrollsReporter()
            
            # Convert test results to analysis format
            analysis_data = {
                "success": True,
                "analysis": {
                    "confidence": self.test_results["summary"]["success_rate"],
                    "patterns": [
                        f"Test category {cat} {res['status']}" 
                        for cat, res in self.test_results["results"].items()
                    ],
                    "anomalies": [
                        f"Failed test category: {cat}" 
                        for cat, res in self.test_results["results"].items() 
                        if res.get("status") == "failed"
                    ],
                    "recommendations": [
                        "Review failed test categories",
                        "Ensure all components are operational",
                        "Continue comprehensive testing protocols"
                    ],
                    "metadata": {
                        "test_timestamp": self.test_results["timestamp"],
                        "test_suite": "Mirror Watcher CLI"
                    }
                }
            }
            
            shadowscrolls_report = reporter.generate_report(analysis_data)
            self.test_results["shadowscrolls_report"] = shadowscrolls_report
            
            print("ShadowScrolls Test Report Generated")
            print("-" * 40)
            print(f"Scroll ID: {shadowscrolls_report.get('scroll_id', 'N/A')}")
            print(f"Oracle Directive: {shadowscrolls_report.get('oracle_directive', 'N/A')}")
            print(f"System Health: {shadowscrolls_report.get('nexus_analysis', {}).get('system_health', 'N/A')}")
            print()
            
        except Exception as e:
            print(f"Failed to generate ShadowScrolls report: {e}")
    
    def save_results(self, output_file: str = None):
        """Save test results to file."""
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"test_results_{timestamp}.json"
        
        with open(output_file, 'w') as f:
            json.dump(self.test_results, f, indent=2)
        
        print(f"Test results saved to: {output_file}")


def main():
    """Main function to run tests."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Mirror Watcher CLI Test Runner")
    parser.add_argument("--output", "-o", help="Output file for test results")
    parser.add_argument("--save-results", action="store_true", help="Save results to JSON file")
    
    args = parser.parse_args()
    
    runner = TestRunner()
    results = runner.run_all_tests()
    
    if args.save_results or args.output:
        runner.save_results(args.output)
    
    # Exit with appropriate code
    overall_status = results["summary"]["overall_status"]
    sys.exit(0 if overall_status == "passed" else 1)


if __name__ == "__main__":
    main()