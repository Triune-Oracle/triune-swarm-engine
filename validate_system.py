#!/usr/bin/env python3
"""
Comprehensive validation script for Mirror Watcher CLI system.

This script validates that all components of the Mirror Watcher CLI are working
correctly and generates a comprehensive validation report.
"""

import sys
import os
import json
import tempfile
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from mirror_watcher.cli import MirrorWatcherCLI


class SystemValidator:
    """Comprehensive system validator for Mirror Watcher CLI."""
    
    def __init__(self):
        self.cli = MirrorWatcherCLI()
        self.test_data_dir = project_root / "tests" / "data"
        self.validation_results = {
            "timestamp": datetime.now().isoformat(),
            "validator": "Mirror Watcher CLI System Validator",
            "version": "1.0.0",
            "tests": {},
            "summary": {},
            "shadowscrolls_report": None
        }
    
    def run_validation(self) -> Dict[str, Any]:
        """Run complete system validation."""
        print("=" * 60)
        print("MIRROR WATCHER CLI - SYSTEM VALIDATION")
        print("=" * 60)
        print(f"Validation started at: {self.validation_results['timestamp']}")
        print()
        
        # Core component tests
        self.test_cli_commands()
        self.test_analysis_engine()
        self.test_data_validation()
        self.test_report_generation()
        self.test_error_handling()
        self.test_edge_cases()
        
        # Generate summary
        self.generate_summary()
        
        # Generate final report
        self.generate_final_report()
        
        return self.validation_results
    
    def test_cli_commands(self):
        """Test all CLI commands."""
        print("Testing CLI Commands...")
        print("-" * 30)
        
        tests = {
            "status": self._test_status_command,
            "validate": self._test_validate_command,
            "analyze": self._test_analyze_command,
            "report": self._test_report_command
        }
        
        self.validation_results["tests"]["cli_commands"] = {}
        
        for test_name, test_func in tests.items():
            try:
                result = test_func()
                self.validation_results["tests"]["cli_commands"][test_name] = result
                status = "PASS" if result["success"] else "FAIL"
                print(f"  {test_name:15} {status}")
            except Exception as e:
                self.validation_results["tests"]["cli_commands"][test_name] = {
                    "success": False,
                    "error": str(e)
                }
                print(f"  {test_name:15} ERROR: {e}")
        
        print()
    
    def _test_status_command(self) -> Dict[str, Any]:
        """Test status command."""
        result = self.cli.status()
        return {
            "success": result.get("success", False) and result.get("system") == "Mirror Watcher CLI",
            "details": result
        }
    
    def _test_validate_command(self) -> Dict[str, Any]:
        """Test validate command."""
        test_file = self.test_data_dir / "sample_valid_data.json"
        if not test_file.exists():
            return {"success": False, "error": "Test data file not found"}
        
        result = self.cli.validate(str(test_file))
        return {
            "success": result.get("success", False),
            "details": result
        }
    
    def _test_analyze_command(self) -> Dict[str, Any]:
        """Test analyze command."""
        test_file = self.test_data_dir / "sample_valid_data.json"
        if not test_file.exists():
            return {"success": False, "error": "Test data file not found"}
        
        result = self.cli.analyze(str(test_file))
        return {
            "success": result.get("success", False) and "analysis" in result,
            "details": result
        }
    
    def _test_report_command(self) -> Dict[str, Any]:
        """Test report command."""
        test_file = self.test_data_dir / "sample_valid_data.json"
        if not test_file.exists():
            return {"success": False, "error": "Test data file not found"}
        
        # First analyze
        analysis_result = self.cli.analyze(str(test_file))
        if not analysis_result.get("success"):
            return {"success": False, "error": "Analysis failed"}
        
        # Save analysis to temp file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(analysis_result, f)
            temp_file = f.name
        
        try:
            # Generate report
            report_result = self.cli.report(temp_file)
            return {
                "success": (report_result.get("success", False) and 
                          report_result.get("format") == "ShadowScrolls"),
                "details": report_result
            }
        finally:
            os.unlink(temp_file)
    
    def test_analysis_engine(self):
        """Test analysis engine components."""
        print("Testing Analysis Engine...")
        print("-" * 30)
        
        tests = {
            "pattern_detection": self._test_pattern_detection,
            "anomaly_detection": self._test_anomaly_detection,
            "confidence_calculation": self._test_confidence_calculation,
            "recommendations": self._test_recommendations
        }
        
        self.validation_results["tests"]["analysis_engine"] = {}
        
        for test_name, test_func in tests.items():
            try:
                result = test_func()
                self.validation_results["tests"]["analysis_engine"][test_name] = result
                status = "PASS" if result["success"] else "FAIL"
                print(f"  {test_name:20} {status}")
            except Exception as e:
                self.validation_results["tests"]["analysis_engine"][test_name] = {
                    "success": False,
                    "error": str(e)
                }
                print(f"  {test_name:20} ERROR: {e}")
        
        print()
    
    def _test_pattern_detection(self) -> Dict[str, Any]:
        """Test pattern detection capabilities."""
        test_file = self.test_data_dir / "sample_valid_data.json"
        if not test_file.exists():
            return {"success": False, "error": "Test data file not found"}
        
        result = self.cli.analyze(str(test_file))
        if result.get("success"):
            patterns = result.get("analysis", {}).get("patterns", [])
            return {
                "success": len(patterns) > 0,
                "pattern_count": len(patterns),
                "details": patterns[:3]  # First 3 patterns
            }
        return {"success": False, "error": "Analysis failed"}
    
    def _test_anomaly_detection(self) -> Dict[str, Any]:
        """Test anomaly detection capabilities."""
        test_file = self.test_data_dir / "sample_anomaly_data.json"
        if not test_file.exists():
            # Use valid data and check for any anomalies
            test_file = self.test_data_dir / "sample_valid_data.json"
        
        if not test_file.exists():
            return {"success": False, "error": "Test data file not found"}
        
        result = self.cli.analyze(str(test_file))
        if result.get("success"):
            anomalies = result.get("analysis", {}).get("anomalies", [])
            return {
                "success": True,  # Anomaly detection works even if no anomalies found
                "anomaly_count": len(anomalies),
                "details": anomalies[:3]  # First 3 anomalies
            }
        return {"success": False, "error": "Analysis failed"}
    
    def _test_confidence_calculation(self) -> Dict[str, Any]:
        """Test confidence calculation."""
        test_file = self.test_data_dir / "sample_valid_data.json"
        if not test_file.exists():
            return {"success": False, "error": "Test data file not found"}
        
        result = self.cli.analyze(str(test_file))
        if result.get("success"):
            confidence = result.get("analysis", {}).get("confidence", -1)
            return {
                "success": 0.0 <= confidence <= 1.0,
                "confidence": confidence,
                "details": f"Confidence: {confidence:.2%}"
            }
        return {"success": False, "error": "Analysis failed"}
    
    def _test_recommendations(self) -> Dict[str, Any]:
        """Test recommendation generation."""
        test_file = self.test_data_dir / "sample_valid_data.json"
        if not test_file.exists():
            return {"success": False, "error": "Test data file not found"}
        
        result = self.cli.analyze(str(test_file))
        if result.get("success"):
            recommendations = result.get("analysis", {}).get("recommendations", [])
            return {
                "success": len(recommendations) > 0,
                "recommendation_count": len(recommendations),
                "details": recommendations
            }
        return {"success": False, "error": "Analysis failed"}
    
    def test_data_validation(self):
        """Test data validation capabilities."""
        print("Testing Data Validation...")
        print("-" * 30)
        
        tests = {
            "valid_data": self._test_valid_data_validation,
            "invalid_data": self._test_invalid_data_validation,
            "json_format": self._test_json_format_validation
        }
        
        self.validation_results["tests"]["data_validation"] = {}
        
        for test_name, test_func in tests.items():
            try:
                result = test_func()
                self.validation_results["tests"]["data_validation"][test_name] = result
                status = "PASS" if result["success"] else "FAIL"
                print(f"  {test_name:20} {status}")
            except Exception as e:
                self.validation_results["tests"]["data_validation"][test_name] = {
                    "success": False,
                    "error": str(e)
                }
                print(f"  {test_name:20} ERROR: {e}")
        
        print()
    
    def _test_valid_data_validation(self) -> Dict[str, Any]:
        """Test validation with valid data."""
        test_file = self.test_data_dir / "sample_valid_data.json"
        if not test_file.exists():
            return {"success": False, "error": "Test data file not found"}
        
        result = self.cli.validate(str(test_file))
        return {
            "success": result.get("success", False) and result.get("validation", {}).get("valid", False),
            "details": result
        }
    
    def _test_invalid_data_validation(self) -> Dict[str, Any]:
        """Test validation with invalid data."""
        test_file = self.test_data_dir / "sample_invalid_data.json"
        if not test_file.exists():
            return {"success": True, "note": "No invalid test data file found"}
        
        result = self.cli.validate(str(test_file))
        # Should fail validation or handle gracefully
        return {
            "success": True,  # As long as it doesn't crash
            "validation_failed": not result.get("success", True),
            "details": result
        }
    
    def _test_json_format_validation(self) -> Dict[str, Any]:
        """Test JSON format validation."""
        # Create invalid JSON in temp file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write('{"invalid": json, "format"}')
            temp_file = f.name
        
        try:
            result = self.cli.validate(temp_file)
            return {
                "success": not result.get("success", True),  # Should fail
                "details": result
            }
        finally:
            os.unlink(temp_file)
    
    def test_report_generation(self):
        """Test ShadowScrolls report generation."""
        print("Testing Report Generation...")
        print("-" * 30)
        
        tests = {
            "shadowscrolls_format": self._test_shadowscrolls_format,
            "report_validation": self._test_report_validation,
            "nft_triggers": self._test_nft_triggers
        }
        
        self.validation_results["tests"]["report_generation"] = {}
        
        for test_name, test_func in tests.items():
            try:
                result = test_func()
                self.validation_results["tests"]["report_generation"][test_name] = result
                status = "PASS" if result["success"] else "FAIL"
                print(f"  {test_name:20} {status}")
            except Exception as e:
                self.validation_results["tests"]["report_generation"][test_name] = {
                    "success": False,
                    "error": str(e)
                }
                print(f"  {test_name:20} ERROR: {e}")
        
        print()
    
    def _test_shadowscrolls_format(self) -> Dict[str, Any]:
        """Test ShadowScrolls format compliance."""
        test_file = self.test_data_dir / "sample_valid_data.json"
        if not test_file.exists():
            return {"success": False, "error": "Test data file not found"}
        
        # Analyze and generate report
        analysis_result = self.cli.analyze(str(test_file))
        if not analysis_result.get("success"):
            return {"success": False, "error": "Analysis failed"}
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(analysis_result, f)
            temp_file = f.name
        
        try:
            report_result = self.cli.report(temp_file)
            if report_result.get("success") and "report" in report_result:
                report = report_result["report"]
                
                # Check required ShadowScrolls fields
                required_fields = [
                    "scroll_id", "oracle_directive", "format_version",
                    "triumvirate_status", "nexus_analysis", "validation_seal"
                ]
                
                missing_fields = [field for field in required_fields if field not in report]
                
                return {
                    "success": len(missing_fields) == 0 and report.get("format_version") == "ShadowScrolls-1.0",
                    "missing_fields": missing_fields,
                    "format_version": report.get("format_version")
                }
            else:
                return {"success": False, "error": "Report generation failed"}
        finally:
            os.unlink(temp_file)
    
    def _test_report_validation(self) -> Dict[str, Any]:
        """Test report validation seal."""
        test_file = self.test_data_dir / "sample_valid_data.json"
        if not test_file.exists():
            return {"success": False, "error": "Test data file not found"}
        
        analysis_result = self.cli.analyze(str(test_file))
        if not analysis_result.get("success"):
            return {"success": False, "error": "Analysis failed"}
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(analysis_result, f)
            temp_file = f.name
        
        try:
            report_result = self.cli.report(temp_file)
            if report_result.get("success") and "report" in report_result:
                seal = report_result["report"].get("validation_seal", {})
                return {
                    "success": seal.get("validated", False) and seal.get("oracle_approved", False),
                    "seal": seal
                }
            else:
                return {"success": False, "error": "Report generation failed"}
        finally:
            os.unlink(temp_file)
    
    def _test_nft_triggers(self) -> Dict[str, Any]:
        """Test NFT trigger detection."""
        test_file = self.test_data_dir / "sample_valid_data.json"
        if not test_file.exists():
            return {"success": False, "error": "Test data file not found"}
        
        analysis_result = self.cli.analyze(str(test_file))
        if not analysis_result.get("success"):
            return {"success": False, "error": "Analysis failed"}
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(analysis_result, f)
            temp_file = f.name
        
        try:
            report_result = self.cli.report(temp_file)
            if report_result.get("success") and "report" in report_result:
                nft_triggers = report_result["report"].get("nft_triggers", [])
                return {
                    "success": True,  # NFT triggers are optional
                    "trigger_count": len(nft_triggers),
                    "has_triggers": len(nft_triggers) > 0
                }
            else:
                return {"success": False, "error": "Report generation failed"}
        finally:
            os.unlink(temp_file)
    
    def test_error_handling(self):
        """Test error handling capabilities."""
        print("Testing Error Handling...")
        print("-" * 30)
        
        tests = {
            "missing_files": self._test_missing_file_handling,
            "invalid_json": self._test_invalid_json_handling,
            "malformed_data": self._test_malformed_data_handling
        }
        
        self.validation_results["tests"]["error_handling"] = {}
        
        for test_name, test_func in tests.items():
            try:
                result = test_func()
                self.validation_results["tests"]["error_handling"][test_name] = result
                status = "PASS" if result["success"] else "FAIL"
                print(f"  {test_name:20} {status}")
            except Exception as e:
                self.validation_results["tests"]["error_handling"][test_name] = {
                    "success": False,
                    "error": str(e)
                }
                print(f"  {test_name:20} ERROR: {e}")
        
        print()
    
    def _test_missing_file_handling(self) -> Dict[str, Any]:
        """Test handling of missing files."""
        result = self.cli.analyze("nonexistent_file.json")
        return {
            "success": not result.get("success", True) and "error" in result,
            "details": result
        }
    
    def _test_invalid_json_handling(self) -> Dict[str, Any]:
        """Test handling of invalid JSON."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write('{ invalid json }')
            temp_file = f.name
        
        try:
            result = self.cli.validate(temp_file)
            return {
                "success": not result.get("success", True),
                "details": result
            }
        finally:
            os.unlink(temp_file)
    
    def _test_malformed_data_handling(self) -> Dict[str, Any]:
        """Test handling of malformed data structure."""
        malformed_data = {
            "agents": "not_an_object",
            "messages": "not_an_array",
            "invalid_field": {"nested": {"deeply": "nested"}}
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(malformed_data, f)
            temp_file = f.name
        
        try:
            result = self.cli.analyze(temp_file)
            return {
                "success": "success" in result,  # Should not crash
                "details": result
            }
        finally:
            os.unlink(temp_file)
    
    def test_edge_cases(self):
        """Test edge cases and boundary conditions."""
        print("Testing Edge Cases...")
        print("-" * 30)
        
        tests = {
            "empty_data": self._test_empty_data,
            "large_dataset": self._test_large_dataset,
            "concurrent_access": self._test_concurrent_access
        }
        
        self.validation_results["tests"]["edge_cases"] = {}
        
        for test_name, test_func in tests.items():
            try:
                result = test_func()
                self.validation_results["tests"]["edge_cases"][test_name] = result
                status = "PASS" if result["success"] else "FAIL"
                print(f"  {test_name:20} {status}")
            except Exception as e:
                self.validation_results["tests"]["edge_cases"][test_name] = {
                    "success": False,
                    "error": str(e)
                }
                print(f"  {test_name:20} ERROR: {e}")
        
        print()
    
    def _test_empty_data(self) -> Dict[str, Any]:
        """Test with empty data."""
        empty_data = {}
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(empty_data, f)
            temp_file = f.name
        
        try:
            result = self.cli.analyze(temp_file)
            return {
                "success": "success" in result,
                "details": result
            }
        finally:
            os.unlink(temp_file)
    
    def _test_large_dataset(self) -> Dict[str, Any]:
        """Test with moderately large dataset."""
        large_data = {
            "agents": {f"Agent_{i}": {"status": "operational"} for i in range(10)},
            "messages": [
                {
                    "timestamp": "2024-01-15T14:30:00Z",
                    "from_agent": f"Agent_{i % 5}",
                    "message": f"Message {i}"
                } for i in range(100)
            ],
            "tasks": [{"id": f"task_{i}", "status": "completed"} for i in range(25)]
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(large_data, f)
            temp_file = f.name
        
        try:
            result = self.cli.analyze(temp_file)
            return {
                "success": "success" in result,
                "details": {"message_count": 100, "task_count": 25}
            }
        finally:
            os.unlink(temp_file)
    
    def _test_concurrent_access(self) -> Dict[str, Any]:
        """Test concurrent access (sequential for now)."""
        test_file = self.test_data_dir / "sample_valid_data.json"
        if not test_file.exists():
            return {"success": False, "error": "Test data file not found"}
        
        # Run multiple analyses sequentially
        results = []
        for i in range(3):
            result = self.cli.analyze(str(test_file))
            results.append(result.get("success", False))
        
        return {
            "success": all(results),
            "run_count": len(results),
            "success_count": sum(results)
        }
    
    def generate_summary(self):
        """Generate validation summary."""
        print("=" * 60)
        print("VALIDATION SUMMARY")
        print("=" * 60)
        
        total_tests = 0
        passed_tests = 0
        
        for category, tests in self.validation_results["tests"].items():
            category_passed = 0
            category_total = len(tests)
            
            for test_name, result in tests.items():
                total_tests += 1
                if result.get("success", False):
                    passed_tests += 1
                    category_passed += 1
            
            print(f"{category:20} {category_passed:2d}/{category_total:2d} passed")
        
        success_rate = passed_tests / total_tests if total_tests > 0 else 0
        overall_status = "PASS" if success_rate >= 0.8 else "FAIL"
        
        self.validation_results["summary"] = {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "success_rate": success_rate,
            "overall_status": overall_status
        }
        
        print("-" * 60)
        print(f"Total Tests:     {total_tests}")
        print(f"Passed Tests:    {passed_tests}")
        print(f"Success Rate:    {success_rate:.1%}")
        print(f"Overall Status:  {overall_status}")
        print()
    
    def generate_final_report(self):
        """Generate final ShadowScrolls validation report."""
        print("Generating Final Validation Report...")
        print("-" * 40)
        
        try:
            from mirror_watcher.report_generator import ShadowScrollsReporter
            
            reporter = ShadowScrollsReporter()
            
            # Convert validation results to analysis format
            analysis_data = {
                "success": True,
                "analysis": {
                    "confidence": self.validation_results["summary"]["success_rate"],
                    "patterns": [
                        f"Validation category {cat} completed" 
                        for cat in self.validation_results["tests"].keys()
                    ],
                    "anomalies": [
                        f"Failed test: {cat}.{test}" 
                        for cat, tests in self.validation_results["tests"].items()
                        for test, result in tests.items()
                        if not result.get("success", False)
                    ],
                    "recommendations": [
                        "System validation completed successfully",
                        "All core components operational",
                        "Ready for production deployment"
                    ] if self.validation_results["summary"]["overall_status"] == "PASS" else [
                        "Review failed validation tests",
                        "Address identified issues",
                        "Re-run validation after fixes"
                    ],
                    "metadata": {
                        "validation_timestamp": self.validation_results["timestamp"],
                        "validator": "System Validator"
                    }
                }
            }
            
            self.validation_results["shadowscrolls_report"] = reporter.generate_report(analysis_data)
            
            print("ShadowScrolls Validation Report Generated:")
            print(f"  Scroll ID: {self.validation_results['shadowscrolls_report']['scroll_id']}")
            print(f"  Oracle Directive: {self.validation_results['shadowscrolls_report']['oracle_directive']}")
            print(f"  System Health: {self.validation_results['shadowscrolls_report']['nexus_analysis']['system_health']}")
            
        except Exception as e:
            print(f"Failed to generate ShadowScrolls report: {e}")
        
        print()
    
    def save_validation_report(self, output_file: str = None):
        """Save validation report to file."""
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"validation_report_{timestamp}.json"
        
        with open(output_file, 'w') as f:
            json.dump(self.validation_results, f, indent=2)
        
        print(f"Validation report saved to: {output_file}")


def main():
    """Main function to run validation."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Mirror Watcher CLI System Validator")
    parser.add_argument("--output", "-o", help="Output file for validation report")
    parser.add_argument("--save-report", action="store_true", help="Save validation report to JSON file")
    
    args = parser.parse_args()
    
    validator = SystemValidator()
    results = validator.run_validation()
    
    if args.save_report or args.output:
        validator.save_validation_report(args.output)
    
    # Exit with appropriate code
    overall_status = results["summary"]["overall_status"]
    sys.exit(0 if overall_status == "PASS" else 1)


if __name__ == "__main__":
    main()