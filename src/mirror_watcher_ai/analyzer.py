"""
Triune Analysis Engine

Comprehensive repository analysis with async execution patterns,
providing detailed insights for the MirrorWatcherAI automation system.
"""

import asyncio
import logging
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
import subprocess
import tempfile
import shutil
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = logging.getLogger(__name__)

class TriuneAnalyzer:
    """Main analyzer for Triune ecosystem repositories"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.parallel_analysis = self.config.get('parallel_analysis', True)
        self.max_workers = self.config.get('max_workers', 4)
        self.timeout_seconds = self.config.get('timeout_seconds', 300)
        
    async def analyze_repository(self, repository: str) -> Dict[str, Any]:
        """Analyze a single repository comprehensively"""
        start_time = time.time()
        
        try:
            logger.info(f"Starting analysis of repository: {repository}")
            
            # Initialize analysis result structure
            result = {
                "repository": repository,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "analysis_version": "1.0.0",
                "status": "in_progress",
                "metrics": {},
                "structure": {},
                "quality": {},
                "security": {},
                "triune_integration": {},
                "errors": []
            }
            
            # If it's a local path, analyze directly
            if Path(repository).exists():
                repo_path = Path(repository)
                result.update(await self._analyze_local_repository(repo_path))
            else:
                # Clone and analyze remote repository
                result.update(await self._analyze_remote_repository(repository))
            
            # Calculate execution time
            execution_time = time.time() - start_time
            result["execution_time_seconds"] = execution_time
            result["status"] = "completed"
            
            logger.info(f"Completed analysis of {repository} in {execution_time:.2f} seconds")
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Failed to analyze repository {repository}: {e}")
            
            return {
                "repository": repository,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "status": "failed",
                "error": str(e),
                "execution_time_seconds": execution_time
            }
    
    async def _analyze_remote_repository(self, repository: str) -> Dict[str, Any]:
        """Clone and analyze a remote repository"""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir) / "repo"
            
            try:
                # Clone repository
                logger.info(f"Cloning repository {repository}")
                clone_cmd = ["git", "clone", "--depth", "1", repository, str(repo_path)]
                
                process = await asyncio.create_subprocess_exec(
                    *clone_cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=self.timeout_seconds
                )
                
                if process.returncode != 0:
                    raise Exception(f"Git clone failed: {stderr.decode()}")
                
                # Analyze cloned repository
                return await self._analyze_local_repository(repo_path)
                
            except asyncio.TimeoutError:
                raise Exception(f"Repository clone timed out after {self.timeout_seconds} seconds")
    
    async def _analyze_local_repository(self, repo_path: Path) -> Dict[str, Any]:
        """Analyze a local repository"""
        analysis_tasks = []
        
        if self.parallel_analysis:
            # Run analysis components in parallel
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                # Submit all analysis tasks
                analysis_tasks = {
                    "structure": executor.submit(self._analyze_structure, repo_path),
                    "metrics": executor.submit(self._analyze_metrics, repo_path),
                    "quality": executor.submit(self._analyze_quality, repo_path),
                    "security": executor.submit(self._analyze_security, repo_path),
                    "triune_integration": executor.submit(self._analyze_triune_integration, repo_path)
                }
                
                # Collect results
                results = {}
                for task_name, future in analysis_tasks.items():
                    try:
                        results[task_name] = future.result(timeout=self.timeout_seconds)
                    except Exception as e:
                        logger.error(f"Analysis task {task_name} failed: {e}")
                        results[task_name] = {"error": str(e)}
                
                return results
        else:
            # Run analysis components sequentially
            return {
                "structure": self._analyze_structure(repo_path),
                "metrics": self._analyze_metrics(repo_path),
                "quality": self._analyze_quality(repo_path),
                "security": self._analyze_security(repo_path),
                "triune_integration": self._analyze_triune_integration(repo_path)
            }
    
    def _analyze_structure(self, repo_path: Path) -> Dict[str, Any]:
        """Analyze repository structure and organization"""
        try:
            structure = {
                "total_files": 0,
                "total_directories": 0,
                "file_types": {},
                "key_files": {},
                "directory_structure": {},
                "size_bytes": 0
            }
            
            # Walk through repository
            for item in repo_path.rglob("*"):
                if item.is_file():
                    structure["total_files"] += 1
                    structure["size_bytes"] += item.stat().st_size
                    
                    # Analyze file types
                    suffix = item.suffix.lower()
                    if suffix:
                        structure["file_types"][suffix] = structure["file_types"].get(suffix, 0) + 1
                    
                    # Check for key files
                    filename = item.name.lower()
                    if filename in ["readme.md", "package.json", "requirements.txt", "dockerfile", "makefile"]:
                        structure["key_files"][filename] = str(item.relative_to(repo_path))
                
                elif item.is_dir():
                    structure["total_directories"] += 1
            
            # Analyze top-level structure
            top_level = []
            for item in repo_path.iterdir():
                if not item.name.startswith('.'):
                    top_level.append({
                        "name": item.name,
                        "type": "directory" if item.is_dir() else "file",
                        "size": item.stat().st_size if item.is_file() else None
                    })
            
            structure["top_level"] = top_level
            
            return structure
            
        except Exception as e:
            logger.error(f"Structure analysis failed: {e}")
            return {"error": str(e)}
    
    def _analyze_metrics(self, repo_path: Path) -> Dict[str, Any]:
        """Analyze code metrics and statistics"""
        try:
            metrics = {
                "lines_of_code": 0,
                "comment_lines": 0,
                "blank_lines": 0,
                "functions": 0,
                "classes": 0,
                "complexity_score": 0,
                "language_breakdown": {}
            }
            
            # Language patterns for counting
            code_patterns = {
                '.py': {'comment': '#', 'multiline_start': '"""', 'multiline_end': '"""'},
                '.js': {'comment': '//', 'multiline_start': '/*', 'multiline_end': '*/'},
                '.ts': {'comment': '//', 'multiline_start': '/*', 'multiline_end': '*/'},
                '.java': {'comment': '//', 'multiline_start': '/*', 'multiline_end': '*/'},
                '.cpp': {'comment': '//', 'multiline_start': '/*', 'multiline_end': '*/'},
                '.c': {'comment': '//', 'multiline_start': '/*', 'multiline_end': '*/'},
                '.go': {'comment': '//', 'multiline_start': '/*', 'multiline_end': '*/'},
                '.rs': {'comment': '//', 'multiline_start': '/*', 'multiline_end': '*/'},
                '.sh': {'comment': '#'},
                '.yml': {'comment': '#'},
                '.yaml': {'comment': '#'}
            }
            
            # Analyze each code file
            for file_path in repo_path.rglob("*"):
                if file_path.is_file() and file_path.suffix in code_patterns:
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            lines = f.readlines()
                        
                        lang_stats = self._analyze_file_metrics(lines, code_patterns[file_path.suffix])
                        
                        # Update totals
                        metrics["lines_of_code"] += lang_stats["code_lines"]
                        metrics["comment_lines"] += lang_stats["comment_lines"]
                        metrics["blank_lines"] += lang_stats["blank_lines"]
                        metrics["functions"] += lang_stats["functions"]
                        metrics["classes"] += lang_stats["classes"]
                        
                        # Update language breakdown
                        lang = file_path.suffix[1:]  # Remove the dot
                        if lang not in metrics["language_breakdown"]:
                            metrics["language_breakdown"][lang] = {
                                "files": 0,
                                "lines": 0,
                                "functions": 0,
                                "classes": 0
                            }
                        
                        metrics["language_breakdown"][lang]["files"] += 1
                        metrics["language_breakdown"][lang]["lines"] += len(lines)
                        metrics["language_breakdown"][lang]["functions"] += lang_stats["functions"]
                        metrics["language_breakdown"][lang]["classes"] += lang_stats["classes"]
                        
                    except Exception as e:
                        logger.debug(f"Failed to analyze file {file_path}: {e}")
            
            # Calculate complexity score (simple heuristic)
            total_lines = metrics["lines_of_code"] + metrics["comment_lines"] + metrics["blank_lines"]
            if total_lines > 0:
                metrics["complexity_score"] = (
                    metrics["functions"] * 2 + 
                    metrics["classes"] * 5 + 
                    metrics["lines_of_code"] / 100
                ) / total_lines * 1000
            
            return metrics
            
        except Exception as e:
            logger.error(f"Metrics analysis failed: {e}")
            return {"error": str(e)}
    
    def _analyze_file_metrics(self, lines: List[str], patterns: Dict[str, str]) -> Dict[str, int]:
        """Analyze metrics for a single file"""
        stats = {
            "code_lines": 0,
            "comment_lines": 0,
            "blank_lines": 0,
            "functions": 0,
            "classes": 0
        }
        
        in_multiline_comment = False
        comment_char = patterns.get('comment', '#')
        
        for line in lines:
            stripped = line.strip()
            
            if not stripped:
                stats["blank_lines"] += 1
                continue
            
            # Handle multiline comments
            if patterns.get('multiline_start') and patterns['multiline_start'] in stripped:
                in_multiline_comment = True
            
            if in_multiline_comment:
                stats["comment_lines"] += 1
                if patterns.get('multiline_end') and patterns['multiline_end'] in stripped:
                    in_multiline_comment = False
                continue
            
            # Check for single line comments
            if stripped.startswith(comment_char):
                stats["comment_lines"] += 1
                continue
            
            # Count functions and classes (basic patterns)
            if 'def ' in stripped or 'function ' in stripped or 'func ' in stripped:
                stats["functions"] += 1
            
            if 'class ' in stripped or 'struct ' in stripped or 'interface ' in stripped:
                stats["classes"] += 1
            
            stats["code_lines"] += 1
        
        return stats
    
    def _analyze_quality(self, repo_path: Path) -> Dict[str, Any]:
        """Analyze code quality indicators"""
        try:
            quality = {
                "documentation_score": 0,
                "test_coverage_estimated": 0,
                "configuration_quality": 0,
                "best_practices_score": 0,
                "issues": []
            }
            
            # Check for documentation
            doc_files = [
                "README.md", "README.rst", "README.txt",
                "CONTRIBUTING.md", "LICENSE", "CHANGELOG.md"
            ]
            
            doc_score = 0
            for doc_file in doc_files:
                if (repo_path / doc_file).exists() or (repo_path / doc_file.lower()).exists():
                    doc_score += 1
            
            quality["documentation_score"] = (doc_score / len(doc_files)) * 100
            
            # Estimate test coverage by counting test files
            test_files = list(repo_path.rglob("*test*")) + list(repo_path.rglob("*spec*"))
            total_code_files = len(list(repo_path.rglob("*.py"))) + len(list(repo_path.rglob("*.js"))) + len(list(repo_path.rglob("*.ts")))
            
            if total_code_files > 0:
                quality["test_coverage_estimated"] = min((len(test_files) / total_code_files) * 100, 100)
            
            # Check configuration quality
            config_files = [
                ".gitignore", "package.json", "requirements.txt",
                "Dockerfile", "docker-compose.yml", ".github/workflows"
            ]
            
            config_score = 0
            for config_file in config_files:
                if (repo_path / config_file).exists():
                    config_score += 1
            
            quality["configuration_quality"] = (config_score / len(config_files)) * 100
            
            # Best practices check
            best_practices = 0
            
            # Check for version control ignore
            if (repo_path / ".gitignore").exists():
                best_practices += 1
            
            # Check for dependency management
            if any((repo_path / f).exists() for f in ["package.json", "requirements.txt", "Pipfile", "go.mod"]):
                best_practices += 1
            
            # Check for CI/CD
            if (repo_path / ".github" / "workflows").exists():
                best_practices += 1
            
            quality["best_practices_score"] = (best_practices / 3) * 100
            
            return quality
            
        except Exception as e:
            logger.error(f"Quality analysis failed: {e}")
            return {"error": str(e)}
    
    def _analyze_security(self, repo_path: Path) -> Dict[str, Any]:
        """Analyze security aspects of the repository"""
        try:
            security = {
                "security_score": 0,
                "vulnerabilities": [],
                "sensitive_files": [],
                "security_features": [],
                "recommendations": []
            }
            
            # Check for sensitive files that shouldn't be committed
            sensitive_patterns = [
                "*.key", "*.pem", "*.p12", "*.pfx",
                ".env", "*.env", "config.json", "secrets.json",
                "id_rsa", "id_dsa", "*.secret"
            ]
            
            for pattern in sensitive_patterns:
                for file_path in repo_path.rglob(pattern):
                    security["sensitive_files"].append(str(file_path.relative_to(repo_path)))
            
            # Check for security configuration files
            security_files = [
                ".github/security.md", "SECURITY.md",
                ".dependabot.yml", ".github/dependabot.yml"
            ]
            
            for sec_file in security_files:
                if (repo_path / sec_file).exists():
                    security["security_features"].append(sec_file)
            
            # Calculate security score
            base_score = 100
            
            # Deduct points for sensitive files
            base_score -= len(security["sensitive_files"]) * 10
            
            # Add points for security features
            base_score += len(security["security_features"]) * 15
            
            security["security_score"] = max(0, min(100, base_score))
            
            # Generate recommendations
            if security["sensitive_files"]:
                security["recommendations"].append("Remove sensitive files and add them to .gitignore")
            
            if not security["security_features"]:
                security["recommendations"].append("Add security documentation and dependency scanning")
            
            return security
            
        except Exception as e:
            logger.error(f"Security analysis failed: {e}")
            return {"error": str(e)}
    
    def _analyze_triune_integration(self, repo_path: Path) -> Dict[str, Any]:
        """Analyze Triune ecosystem integration aspects"""
        try:
            integration = {
                "triune_compatibility": 0,
                "ecosystem_components": [],
                "integration_score": 0,
                "swarm_engine_features": [],
                "mirror_watcher_ready": False
            }
            
            # Check for Triune-specific files and patterns
            triune_indicators = [
                "triumvirate", "triune", "oracle", "swarm",
                "shadowscrolls", "legio-cognito", "mirror-watcher"
            ]
            
            # Scan for Triune references in files
            triune_matches = 0
            for file_path in repo_path.rglob("*"):
                if file_path.is_file() and file_path.suffix in ['.py', '.js', '.ts', '.md', '.json', '.yml', '.yaml']:
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read().lower()
                            for indicator in triune_indicators:
                                if indicator in content:
                                    triune_matches += 1
                                    if indicator not in integration["ecosystem_components"]:
                                        integration["ecosystem_components"].append(indicator)
                    except Exception:
                        continue
            
            # Check for specific Triune configuration files
            triune_configs = [
                "triune_config.json", "swarm_config.json",
                "triumvirate_config.yml", "oracle_config.yaml"
            ]
            
            for config_file in triune_configs:
                if (repo_path / config_file).exists():
                    integration["swarm_engine_features"].append(config_file)
            
            # Calculate integration scores
            integration["triune_compatibility"] = min(100, triune_matches * 10)
            integration["integration_score"] = (
                len(integration["ecosystem_components"]) * 20 +
                len(integration["swarm_engine_features"]) * 30
            )
            
            # Check if ready for MirrorWatcher automation
            integration["mirror_watcher_ready"] = (
                integration["integration_score"] > 50 and
                len(integration["ecosystem_components"]) >= 2
            )
            
            return integration
            
        except Exception as e:
            logger.error(f"Triune integration analysis failed: {e}")
            return {"error": str(e)}

class MirrorAnalysisEngine:
    """Advanced analysis engine for complex repository insights"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.analyzer = TriuneAnalyzer(config)
    
    async def analyze_multiple_repositories(self, repositories: List[str]) -> Dict[str, Any]:
        """Analyze multiple repositories with comparative insights"""
        
        results = {
            "repositories": {},
            "comparative_analysis": {},
            "recommendations": []
        }
        
        # Analyze each repository
        for repo in repositories:
            results["repositories"][repo] = await self.analyzer.analyze_repository(repo)
        
        # Generate comparative analysis
        results["comparative_analysis"] = self._generate_comparative_analysis(
            results["repositories"]
        )
        
        return results
    
    def _generate_comparative_analysis(self, repository_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comparative analysis across repositories"""
        
        comparative = {
            "total_repositories": len(repository_results),
            "average_metrics": {},
            "best_practices_summary": {},
            "security_overview": {},
            "triune_readiness": {}
        }
        
        # Calculate averages and summaries
        if repository_results:
            # Extract metrics for averaging
            all_metrics = []
            for repo_data in repository_results.values():
                if isinstance(repo_data, dict) and "metrics" in repo_data:
                    all_metrics.append(repo_data["metrics"])
            
            if all_metrics:
                comparative["average_metrics"] = {
                    "avg_lines_of_code": sum(m.get("lines_of_code", 0) for m in all_metrics) / len(all_metrics),
                    "avg_functions": sum(m.get("functions", 0) for m in all_metrics) / len(all_metrics),
                    "avg_classes": sum(m.get("classes", 0) for m in all_metrics) / len(all_metrics)
                }
        
        return comparative