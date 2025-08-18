"""
TriuneAnalyzer - Core Analysis Engine for MirrorWatcherAI

Provides comprehensive repository analysis capabilities including:
- Multi-repository concurrent analysis
- Deep code scanning and metrics collection
- Integration with GitHub API
- Performance monitoring and optimization
- Error handling and recovery mechanisms
"""

import asyncio
import aiohttp
import json
import os
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
import subprocess
import tempfile
import shutil
import hashlib
import time


class TriuneAnalyzer:
    """Core analysis engine for the Triune Oracle ecosystem."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.timeout = config.get("timeout", 300)
        self.concurrent_repos = config.get("concurrent_repos", 3)
        self.output_format = config.get("output_format", "json")
        self.logger = logging.getLogger("TriuneAnalyzer")
        
        # GitHub API configuration
        self.github_token = os.getenv("REPO_SYNC_TOKEN", "")
        self.github_headers = {
            "Authorization": f"token {self.github_token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "MirrorWatcherAI/1.0.0"
        } if self.github_token else {}
        
        # Analysis metrics
        self.metrics = {
            "sessions": 0,
            "repositories_analyzed": 0,
            "total_analysis_time": 0,
            "errors": 0,
            "last_analysis": None
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on the analyzer."""
        try:
            # Test GitHub API connectivity
            if self.github_token:
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        "https://api.github.com/user",
                        headers=self.github_headers,
                        timeout=aiohttp.ClientTimeout(total=10)
                    ) as response:
                        if response.status != 200:
                            raise Exception(f"GitHub API returned {response.status}")
            
            return {
                "status": "healthy",
                "github_api": "connected" if self.github_token else "no_token",
                "metrics": self.metrics
            }
        except Exception as e:
            raise Exception(f"Health check failed: {e}")
    
    async def analyze_repositories(
        self, 
        repositories: List[str], 
        parallel: bool = True,
        deep_scan: bool = False
    ) -> Dict[str, Any]:
        """Analyze multiple repositories with optional parallel execution."""
        start_time = time.time()
        session_id = f"analysis-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}"
        
        self.logger.info(f"🔍 Starting repository analysis session: {session_id}")
        self.logger.info(f"📊 Repositories to analyze: {len(repositories)}")
        self.logger.info(f"⚡ Parallel execution: {parallel}")
        self.logger.info(f"🔬 Deep scan mode: {deep_scan}")
        
        session_results = {
            "session_id": session_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "config": {
                "parallel": parallel,
                "deep_scan": deep_scan,
                "timeout": self.timeout,
                "concurrent_repos": self.concurrent_repos
            },
            "repositories": {},
            "summary": {
                "total_repositories": len(repositories),
                "successful": 0,
                "failed": 0,
                "skipped": 0,
                "total_analysis_time": 0
            },
            "errors": []
        }
        
        try:
            if parallel and len(repositories) > 1:
                # Parallel analysis with concurrency limit
                semaphore = asyncio.Semaphore(self.concurrent_repos)
                tasks = [
                    self._analyze_repository_with_semaphore(
                        semaphore, repo, deep_scan, session_results
                    )
                    for repo in repositories
                ]
                await asyncio.gather(*tasks, return_exceptions=True)
            else:
                # Sequential analysis
                for repo in repositories:
                    await self._analyze_single_repository(repo, deep_scan, session_results)
            
            # Calculate final metrics
            session_results["summary"]["total_analysis_time"] = time.time() - start_time
            
            # Update global metrics
            self.metrics["sessions"] += 1
            self.metrics["repositories_analyzed"] += session_results["summary"]["successful"]
            self.metrics["total_analysis_time"] += session_results["summary"]["total_analysis_time"]
            self.metrics["last_analysis"] = session_results["timestamp"]
            
            self.logger.info(f"✅ Analysis session completed: {session_id}")
            self.logger.info(f"📈 Results: {session_results['summary']['successful']} successful, "
                           f"{session_results['summary']['failed']} failed")
            
            return session_results
            
        except Exception as e:
            self.logger.error(f"❌ Analysis session failed: {e}")
            session_results["errors"].append({
                "type": "session_error",
                "message": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
            self.metrics["errors"] += 1
            raise
    
    async def _analyze_repository_with_semaphore(
        self, 
        semaphore: asyncio.Semaphore, 
        repository: str, 
        deep_scan: bool,
        session_results: Dict[str, Any]
    ):
        """Analyze repository with concurrency control."""
        async with semaphore:
            return await self._analyze_single_repository(repository, deep_scan, session_results)
    
    async def _analyze_single_repository(
        self, 
        repository: str, 
        deep_scan: bool,
        session_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze a single repository."""
        repo_start_time = time.time()
        repo_key = repository.replace("/", "_")
        
        self.logger.info(f"🔎 Analyzing repository: {repository}")
        
        repo_result = {
            "repository": repository,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status": "analyzing",
            "metrics": {},
            "analysis": {},
            "errors": []
        }
        
        session_results["repositories"][repo_key] = repo_result
        
        try:
            # Fetch repository metadata
            metadata = await self._fetch_repository_metadata(repository)
            repo_result["metadata"] = metadata
            
            # Clone repository for analysis
            with tempfile.TemporaryDirectory() as temp_dir:
                repo_path = Path(temp_dir) / "repo"
                
                # Clone the repository
                await self._clone_repository(repository, repo_path)
                
                # Perform basic analysis
                basic_analysis = await self._perform_basic_analysis(repo_path)
                repo_result["analysis"]["basic"] = basic_analysis
                
                # Perform deep scan if requested
                if deep_scan:
                    deep_analysis = await self._perform_deep_analysis(repo_path)
                    repo_result["analysis"]["deep"] = deep_analysis
                
                # Calculate metrics
                metrics = await self._calculate_repository_metrics(
                    repo_path, metadata, basic_analysis
                )
                repo_result["metrics"] = metrics
            
            # Mark as successful
            repo_result["status"] = "completed"
            repo_result["analysis_time"] = time.time() - repo_start_time
            session_results["summary"]["successful"] += 1
            
            self.logger.info(f"✅ Repository analysis completed: {repository}")
            
        except Exception as e:
            self.logger.error(f"❌ Repository analysis failed: {repository} - {e}")
            repo_result["status"] = "failed"
            repo_result["analysis_time"] = time.time() - repo_start_time
            repo_result["errors"].append({
                "type": "analysis_error",
                "message": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
            session_results["summary"]["failed"] += 1
            session_results["errors"].append({
                "repository": repository,
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
        
        return repo_result
    
    async def _fetch_repository_metadata(self, repository: str) -> Dict[str, Any]:
        """Fetch repository metadata from GitHub API."""
        if not self.github_token:
            return {"error": "No GitHub token provided"}
        
        async with aiohttp.ClientSession() as session:
            # Get basic repository info
            async with session.get(
                f"https://api.github.com/repos/{repository}",
                headers=self.github_headers,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                if response.status != 200:
                    raise Exception(f"GitHub API error: {response.status}")
                repo_data = await response.json()
            
            # Get additional statistics
            stats = {}
            
            # Get languages
            async with session.get(
                f"https://api.github.com/repos/{repository}/languages",
                headers=self.github_headers
            ) as response:
                if response.status == 200:
                    stats["languages"] = await response.json()
            
            # Get recent commits
            async with session.get(
                f"https://api.github.com/repos/{repository}/commits",
                headers=self.github_headers,
                params={"per_page": 10}
            ) as response:
                if response.status == 200:
                    commits = await response.json()
                    stats["recent_commits"] = len(commits)
                    if commits:
                        stats["last_commit"] = commits[0]["commit"]["author"]["date"]
            
            return {
                "name": repo_data.get("name"),
                "full_name": repo_data.get("full_name"),
                "description": repo_data.get("description"),
                "private": repo_data.get("private"),
                "size": repo_data.get("size"),
                "stargazers_count": repo_data.get("stargazers_count"),
                "watchers_count": repo_data.get("watchers_count"),
                "forks_count": repo_data.get("forks_count"),
                "open_issues_count": repo_data.get("open_issues_count"),
                "default_branch": repo_data.get("default_branch"),
                "created_at": repo_data.get("created_at"),
                "updated_at": repo_data.get("updated_at"),
                "pushed_at": repo_data.get("pushed_at"),
                "statistics": stats
            }
    
    async def _clone_repository(self, repository: str, target_path: Path):
        """Clone repository to local path."""
        clone_url = f"https://github.com/{repository}.git"
        
        if self.github_token:
            # Use token for authentication
            clone_url = f"https://{self.github_token}@github.com/{repository}.git"
        
        process = await asyncio.create_subprocess_exec(
            "git", "clone", "--depth", "1", clone_url, str(target_path),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            raise Exception(f"Git clone failed: {stderr.decode()}")
    
    async def _perform_basic_analysis(self, repo_path: Path) -> Dict[str, Any]:
        """Perform basic repository analysis."""
        analysis = {
            "file_count": 0,
            "total_size": 0,
            "file_types": {},
            "directory_structure": {},
            "config_files": [],
            "documentation_files": [],
            "code_files": []
        }
        
        # Count files and analyze structure
        for file_path in repo_path.rglob("*"):
            if file_path.is_file():
                analysis["file_count"] += 1
                file_size = file_path.stat().st_size
                analysis["total_size"] += file_size
                
                # File type analysis
                suffix = file_path.suffix.lower()
                if suffix:
                    analysis["file_types"][suffix] = analysis["file_types"].get(suffix, 0) + 1
                
                # Categorize files
                filename = file_path.name.lower()
                if filename in ["readme.md", "readme.txt", "readme.rst", "readme"]:
                    analysis["documentation_files"].append(str(file_path.relative_to(repo_path)))
                elif filename in ["package.json", "requirements.txt", "cargo.toml", "pom.xml", "build.gradle"]:
                    analysis["config_files"].append(str(file_path.relative_to(repo_path)))
                elif suffix in [".py", ".js", ".ts", ".java", ".go", ".rs", ".cpp", ".c", ".h"]:
                    analysis["code_files"].append(str(file_path.relative_to(repo_path)))
        
        # Directory structure analysis
        for dir_path in repo_path.rglob("*"):
            if dir_path.is_dir():
                rel_path = str(dir_path.relative_to(repo_path))
                if rel_path != ".":
                    depth = len(rel_path.split("/"))
                    analysis["directory_structure"][rel_path] = {
                        "depth": depth,
                        "file_count": len(list(dir_path.glob("*")))
                    }
        
        return analysis
    
    async def _perform_deep_analysis(self, repo_path: Path) -> Dict[str, Any]:
        """Perform deep repository analysis."""
        analysis = {
            "code_metrics": {},
            "dependencies": {},
            "security_scan": {},
            "quality_metrics": {}
        }
        
        # Language-specific analysis
        analysis["code_metrics"] = await self._analyze_code_metrics(repo_path)
        
        # Dependency analysis
        analysis["dependencies"] = await self._analyze_dependencies(repo_path)
        
        # Basic security scan
        analysis["security_scan"] = await self._perform_security_scan(repo_path)
        
        # Quality metrics
        analysis["quality_metrics"] = await self._calculate_quality_metrics(repo_path)
        
        return analysis
    
    async def _analyze_code_metrics(self, repo_path: Path) -> Dict[str, Any]:
        """Analyze code metrics like LOC, complexity, etc."""
        metrics = {
            "lines_of_code": 0,
            "lines_of_comments": 0,
            "blank_lines": 0,
            "function_count": 0,
            "class_count": 0
        }
        
        # Simple line counting for common file types
        code_extensions = {".py", ".js", ".ts", ".java", ".go", ".rs", ".cpp", ".c", ".h"}
        
        for file_path in repo_path.rglob("*"):
            if file_path.is_file() and file_path.suffix in code_extensions:
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = f.readlines()
                        
                    for line in lines:
                        line = line.strip()
                        if not line:
                            metrics["blank_lines"] += 1
                        elif line.startswith("#") or line.startswith("//"):
                            metrics["lines_of_comments"] += 1
                        else:
                            metrics["lines_of_code"] += 1
                            
                            # Simple pattern matching for functions and classes
                            if any(pattern in line for pattern in ["def ", "function ", "func "]):
                                metrics["function_count"] += 1
                            if any(pattern in line for pattern in ["class ", "struct ", "interface "]):
                                metrics["class_count"] += 1
                                
                except Exception:
                    continue  # Skip files that can't be read
        
        return metrics
    
    async def _analyze_dependencies(self, repo_path: Path) -> Dict[str, Any]:
        """Analyze project dependencies."""
        dependencies = {
            "package_managers": [],
            "dependency_files": [],
            "total_dependencies": 0
        }
        
        # Check for various dependency files
        dependency_files = {
            "package.json": "npm",
            "requirements.txt": "pip",
            "Cargo.toml": "cargo",
            "pom.xml": "maven",
            "build.gradle": "gradle",
            "go.mod": "go",
            "composer.json": "composer"
        }
        
        for filename, manager in dependency_files.items():
            file_path = repo_path / filename
            if file_path.exists():
                dependencies["package_managers"].append(manager)
                dependencies["dependency_files"].append(filename)
                
                # Try to count dependencies
                try:
                    if filename == "package.json":
                        with open(file_path, 'r') as f:
                            package_data = json.load(f)
                        deps = len(package_data.get("dependencies", {}))
                        dev_deps = len(package_data.get("devDependencies", {}))
                        dependencies["total_dependencies"] += deps + dev_deps
                    elif filename == "requirements.txt":
                        with open(file_path, 'r') as f:
                            lines = [line.strip() for line in f if line.strip() and not line.startswith("#")]
                        dependencies["total_dependencies"] += len(lines)
                except Exception:
                    continue
        
        return dependencies
    
    async def _perform_security_scan(self, repo_path: Path) -> Dict[str, Any]:
        """Perform basic security scanning."""
        security = {
            "potential_secrets": [],
            "suspicious_files": [],
            "insecure_patterns": []
        }
        
        # Patterns that might indicate secrets or security issues
        secret_patterns = [
            "password", "secret", "key", "token", "api_key", "private_key"
        ]
        
        suspicious_extensions = {".pem", ".key", ".p12", ".pfx"}
        
        for file_path in repo_path.rglob("*"):
            if file_path.is_file():
                filename = file_path.name.lower()
                
                # Check for suspicious files
                if file_path.suffix in suspicious_extensions:
                    security["suspicious_files"].append(str(file_path.relative_to(repo_path)))
                
                # Check for potential secrets in file content
                if file_path.suffix in {".py", ".js", ".ts", ".java", ".go", ".env", ".config"}:
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read().lower()
                        
                        for pattern in secret_patterns:
                            if pattern in content and "=" in content:
                                security["potential_secrets"].append({
                                    "file": str(file_path.relative_to(repo_path)),
                                    "pattern": pattern
                                })
                                break
                    except Exception:
                        continue
        
        return security
    
    async def _calculate_quality_metrics(self, repo_path: Path) -> Dict[str, Any]:
        """Calculate code quality metrics."""
        quality = {
            "documentation_coverage": 0.0,
            "test_coverage_estimate": 0.0,
            "configuration_completeness": 0.0
        }
        
        total_files = 0
        documented_files = 0
        test_files = 0
        config_files = 0
        
        for file_path in repo_path.rglob("*"):
            if file_path.is_file():
                total_files += 1
                filename = file_path.name.lower()
                
                # Documentation
                if any(doc in filename for doc in ["readme", "doc", "guide", "manual"]):
                    documented_files += 1
                
                # Tests
                if any(test in filename for test in ["test", "spec", "_test", ".test"]):
                    test_files += 1
                
                # Configuration
                if any(config in filename for config in ["config", "settings", ".env", "package.json"]):
                    config_files += 1
        
        if total_files > 0:
            quality["documentation_coverage"] = documented_files / total_files
            quality["test_coverage_estimate"] = test_files / total_files
            quality["configuration_completeness"] = config_files / total_files
        
        return quality
    
    async def _calculate_repository_metrics(
        self, 
        repo_path: Path, 
        metadata: Dict[str, Any], 
        analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate comprehensive repository metrics."""
        metrics = {
            "repository_health_score": 0.0,
            "activity_score": 0.0,
            "code_quality_score": 0.0,
            "maintainability_score": 0.0,
            "timestamps": {
                "calculated_at": datetime.now(timezone.utc).isoformat()
            }
        }
        
        # Calculate health score based on various factors
        health_factors = []
        
        # Metadata factors
        if metadata.get("description"):
            health_factors.append(0.1)  # Has description
        if metadata.get("stargazers_count", 0) > 0:
            health_factors.append(0.1)  # Has stars
        if metadata.get("open_issues_count", 0) < 10:
            health_factors.append(0.1)  # Low issues
        
        # Analysis factors
        if analysis.get("file_count", 0) > 5:
            health_factors.append(0.15)  # Sufficient files
        if len(analysis.get("documentation_files", [])) > 0:
            health_factors.append(0.2)  # Has documentation
        if len(analysis.get("config_files", [])) > 0:
            health_factors.append(0.15)  # Has configuration
        
        metrics["repository_health_score"] = min(1.0, sum(health_factors))
        
        # Activity score based on recent updates
        if metadata.get("pushed_at"):
            try:
                last_push = datetime.fromisoformat(metadata["pushed_at"].replace("Z", "+00:00"))
                days_since_push = (datetime.now(timezone.utc) - last_push).days
                metrics["activity_score"] = max(0.0, 1.0 - (days_since_push / 365))
            except:
                metrics["activity_score"] = 0.0
        
        # Code quality score
        code_files = len(analysis.get("code_files", []))
        total_files = analysis.get("file_count", 1)
        code_ratio = code_files / total_files if total_files > 0 else 0
        metrics["code_quality_score"] = min(1.0, code_ratio * 2)
        
        # Maintainability score
        maintainability_factors = [
            len(analysis.get("documentation_files", [])) > 0,  # Has docs
            len(analysis.get("config_files", [])) > 0,         # Has config
            analysis.get("file_count", 0) < 1000,             # Not too large
            metadata.get("open_issues_count", 0) < 20         # Manageable issues
        ]
        metrics["maintainability_score"] = sum(maintainability_factors) / len(maintainability_factors)
        
        return metrics