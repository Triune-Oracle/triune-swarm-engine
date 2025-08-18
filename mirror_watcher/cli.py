"""
Mirror Watcher CLI - ShadowScrolls Integration for Triune Projects
Automates CLI mirroring, analysis, and immutable logging
"""

import json
import argparse
import sys
import os
from datetime import datetime, timezone
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any
import tempfile

from .analyzer import TriuneAnalyzer


class ShadowScrollsLogger:
    """Handles ShadowScrolls integration with Scroll ID #004 – Root of Witnessing"""
    
    SCROLL_ID = "#004"
    TITLE = "Root of Witnessing"
    TRACEABILITY = "MirrorLineage-Δ"
    
    def __init__(self, output_dir: str = "."):
        self.output_dir = Path(output_dir)
        self.execution_metadata = {
            "scroll_id": self.SCROLL_ID,
            "title": self.TITLE,
            "traceability": self.TRACEABILITY,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "execution_id": self._generate_execution_id(),
            "events": [],
            "artifacts": []
        }
    
    def _generate_execution_id(self) -> str:
        """Generate unique execution ID for traceability"""
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
        return f"mirror-{timestamp}-{os.getpid()}"
    
    def log_event(self, event_type: str, description: str, data: Optional[Dict] = None):
        """Log event to ShadowScrolls"""
        event = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "type": event_type,
            "description": description,
            "data": data or {}
        }
        self.execution_metadata["events"].append(event)
        print(f"📜 [{self.SCROLL_ID}] {event_type}: {description}")
    
    def add_artifact(self, name: str, path: str, artifact_type: str = "file"):
        """Add artifact to attestation"""
        artifact = {
            "name": name,
            "path": str(path),
            "type": artifact_type,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "size": os.path.getsize(path) if os.path.exists(path) else 0
        }
        self.execution_metadata["artifacts"].append(artifact)
    
    def generate_attestation(self) -> Dict[str, Any]:
        """Generate final ShadowScrolls attestation"""
        self.execution_metadata["completion_timestamp"] = datetime.now(timezone.utc).isoformat()
        self.execution_metadata["total_events"] = len(self.execution_metadata["events"])
        self.execution_metadata["total_artifacts"] = len(self.execution_metadata["artifacts"])
        
        attestation_file = self.output_dir / f"shadowscrolls_attestation_{self.execution_metadata['execution_id']}.json"
        
        with open(attestation_file, 'w') as f:
            json.dump(self.execution_metadata, f, indent=2)
        
        print(f"🔮 ShadowScrolls attestation generated: {attestation_file}")
        return self.execution_metadata


class MirrorWatcherCLI:
    """Main CLI interface for Mirror Watcher"""
    
    def __init__(self):
        self.logger = None
        self.analyzer = TriuneAnalyzer()
    
    def setup_logger(self, output_dir: str = "."):
        """Initialize ShadowScrolls logger"""
        self.logger = ShadowScrollsLogger(output_dir)
        self.logger.log_event("INITIALIZATION", "Mirror Watcher CLI started")
    
    def mirror_repository(self, source_repo: str, target_dir: str, use_ssh: bool = True) -> bool:
        """Mirror repository using SSH or HTTPS fallback"""
        try:
            self.logger.log_event("MIRROR_START", f"Starting mirror of {source_repo}")
            
            # Prepare clone command
            if use_ssh and not source_repo.startswith("http"):
                # Assume GitHub format: owner/repo
                clone_url = f"git@github.com:{source_repo}.git"
            else:
                # HTTPS fallback
                if not source_repo.startswith("http"):
                    clone_url = f"https://github.com/{source_repo}.git"
                else:
                    clone_url = source_repo
            
            # Clone repository
            cmd = ["git", "clone", "--depth", "1", clone_url, target_dir]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.logger.log_event("MIRROR_SUCCESS", f"Successfully mirrored {source_repo}", {
                    "target_dir": target_dir,
                    "clone_url": clone_url
                })
                return True
            else:
                self.logger.log_event("MIRROR_ERROR", f"Failed to mirror {source_repo}", {
                    "error": result.stderr,
                    "clone_url": clone_url
                })
                
                # Try HTTPS fallback if SSH failed
                if use_ssh and not source_repo.startswith("http"):
                    self.logger.log_event("FALLBACK_ATTEMPT", "Attempting HTTPS fallback")
                    return self.mirror_repository(source_repo, target_dir, use_ssh=False)
                
                return False
                
        except Exception as e:
            self.logger.log_event("MIRROR_EXCEPTION", f"Exception during mirroring: {str(e)}")
            return False
    
    def analyze_repository(self, repo_path: str) -> Dict[str, Any]:
        """Analyze mirrored repository"""
        try:
            self.logger.log_event("ANALYSIS_START", f"Starting analysis of {repo_path}")
            
            analysis_result = self.analyzer.analyze_repository(repo_path)
            
            self.logger.log_event("ANALYSIS_COMPLETE", "Repository analysis completed", {
                "files_analyzed": analysis_result.get("file_count", 0),
                "languages_detected": len(analysis_result.get("languages", [])),
                "total_lines": analysis_result.get("total_lines", 0)
            })
            
            return analysis_result
            
        except Exception as e:
            self.logger.log_event("ANALYSIS_ERROR", f"Analysis failed: {str(e)}")
            return {"error": str(e)}
    
    def run_cli_tests(self, repo_path: str) -> Dict[str, Any]:
        """Run CLI tests in the mirrored repository"""
        try:
            self.logger.log_event("CLI_TEST_START", f"Starting CLI tests for {repo_path}")
            
            test_results = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "tests_run": [],
                "success_count": 0,
                "failure_count": 0
            }
            
            # Check for common test commands
            repo_path = Path(repo_path)
            
            # Python tests
            if (repo_path / "requirements.txt").exists() or (repo_path / "setup.py").exists():
                python_result = self._run_python_tests(repo_path)
                test_results["tests_run"].append(python_result)
            
            # Node.js tests
            if (repo_path / "package.json").exists():
                node_result = self._run_node_tests(repo_path)
                test_results["tests_run"].append(node_result)
            
            # Calculate totals
            test_results["success_count"] = sum(1 for test in test_results["tests_run"] if test["success"])
            test_results["failure_count"] = len(test_results["tests_run"]) - test_results["success_count"]
            
            self.logger.log_event("CLI_TEST_COMPLETE", "CLI tests completed", {
                "total_tests": len(test_results["tests_run"]),
                "successes": test_results["success_count"],
                "failures": test_results["failure_count"]
            })
            
            return test_results
            
        except Exception as e:
            self.logger.log_event("CLI_TEST_ERROR", f"CLI tests failed: {str(e)}")
            return {"error": str(e)}
    
    def _run_python_tests(self, repo_path: Path) -> Dict[str, Any]:
        """Run Python-specific tests"""
        try:
            # Try pytest first, then unittest
            for test_cmd in [["python", "-m", "pytest", "--version"], ["python", "-m", "unittest", "--help"]]:
                result = subprocess.run(test_cmd, cwd=repo_path, capture_output=True, text=True, timeout=30)
                if result.returncode == 0:
                    test_type = test_cmd[2]  # pytest or unittest
                    actual_test = subprocess.run([test_cmd[0], "-m", test_type], 
                                                cwd=repo_path, capture_output=True, text=True, timeout=120)
                    return {
                        "type": "python",
                        "command": " ".join(test_cmd[:3]),
                        "success": actual_test.returncode == 0,
                        "output": actual_test.stdout[:1000],  # Limit output
                        "error": actual_test.stderr[:500] if actual_test.returncode != 0 else None
                    }
            
            return {"type": "python", "success": False, "error": "No test framework found"}
            
        except Exception as e:
            return {"type": "python", "success": False, "error": str(e)}
    
    def _run_node_tests(self, repo_path: Path) -> Dict[str, Any]:
        """Run Node.js-specific tests"""
        try:
            # Check package.json for test script
            package_json = repo_path / "package.json"
            if package_json.exists():
                with open(package_json) as f:
                    package_data = json.load(f)
                
                if "scripts" in package_data and "test" in package_data["scripts"]:
                    result = subprocess.run(["npm", "test"], cwd=repo_path, 
                                          capture_output=True, text=True, timeout=120)
                    return {
                        "type": "nodejs",
                        "command": "npm test",
                        "success": result.returncode == 0,
                        "output": result.stdout[:1000],
                        "error": result.stderr[:500] if result.returncode != 0 else None
                    }
            
            return {"type": "nodejs", "success": False, "error": "No test script found in package.json"}
            
        except Exception as e:
            return {"type": "nodejs", "success": False, "error": str(e)}
    
    def save_artifacts(self, artifacts: Dict[str, Any], output_dir: str):
        """Save analysis and test artifacts"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Save analysis results
        if "analysis" in artifacts:
            analysis_file = output_path / "analysis_results.json"
            with open(analysis_file, 'w') as f:
                json.dump(artifacts["analysis"], f, indent=2)
            self.logger.add_artifact("analysis_results", str(analysis_file), "analysis")
        
        # Save test results
        if "tests" in artifacts:
            test_file = output_path / "test_results.json"
            with open(test_file, 'w') as f:
                json.dump(artifacts["tests"], f, indent=2)
            self.logger.add_artifact("test_results", str(test_file), "test_results")
    
    def run_complete_workflow(self, source_repo: str, output_dir: str = ".", 
                            cleanup: bool = True) -> Dict[str, Any]:
        """Run complete mirroring, analysis, and testing workflow"""
        
        self.setup_logger(output_dir)
        
        try:
            # Create temporary directory for mirroring
            with tempfile.TemporaryDirectory() as temp_dir:
                mirror_dir = os.path.join(temp_dir, "mirrored_repo")
                
                # Step 1: Mirror repository
                if not self.mirror_repository(source_repo, mirror_dir):
                    raise Exception("Failed to mirror repository")
                
                # Step 2: Analyze repository
                analysis_results = self.analyze_repository(mirror_dir)
                
                # Step 3: Run CLI tests
                test_results = self.run_cli_tests(mirror_dir)
                
                # Step 4: Save artifacts
                artifacts = {
                    "analysis": analysis_results,
                    "tests": test_results
                }
                self.save_artifacts(artifacts, output_dir)
                
                # Step 5: Generate ShadowScrolls attestation
                attestation = self.logger.generate_attestation()
                
                return {
                    "success": True,
                    "execution_id": self.logger.execution_metadata["execution_id"],
                    "attestation": attestation,
                    "artifacts": artifacts
                }
                
        except Exception as e:
            self.logger.log_event("WORKFLOW_ERROR", f"Workflow failed: {str(e)}")
            attestation = self.logger.generate_attestation()
            return {
                "success": False,
                "error": str(e),
                "execution_id": self.logger.execution_metadata["execution_id"],
                "attestation": attestation
            }


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(description="Triune Mirror Watcher - Automated CLI Mirroring & Analysis")
    
    parser.add_argument("source_repo", help="Source repository (owner/repo or full URL)")
    parser.add_argument("--output-dir", "-o", default=".", 
                       help="Output directory for artifacts and logs")
    parser.add_argument("--no-ssh", action="store_true", 
                       help="Use HTTPS instead of SSH for cloning")
    parser.add_argument("--no-cleanup", action="store_true",
                       help="Keep temporary files after completion")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Enable verbose output")
    
    args = parser.parse_args()
    
    # Initialize CLI
    cli = MirrorWatcherCLI()
    
    # Run workflow
    result = cli.run_complete_workflow(
        source_repo=args.source_repo,
        output_dir=args.output_dir,
        cleanup=not args.no_cleanup
    )
    
    # Output results
    if args.verbose:
        print(json.dumps(result, indent=2))
    
    if result["success"]:
        print(f"✅ Mirror Watcher completed successfully!")
        print(f"🔮 Execution ID: {result['execution_id']}")
        print(f"📜 ShadowScrolls attestation generated")
        sys.exit(0)
    else:
        print(f"❌ Mirror Watcher failed: {result.get('error', 'Unknown error')}")
        print(f"🔮 Execution ID: {result['execution_id']}")
        sys.exit(1)


if __name__ == "__main__":
    main()