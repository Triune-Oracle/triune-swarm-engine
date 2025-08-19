"""
Triune Analyzer - Core Analysis Engine
======================================

High-performance async analyzer for comprehensive repository analysis
across the Triune Oracle ecosystem.
"""

import asyncio
import aiohttp
import json
import os
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
import logging
import hashlib
import base64

logger = logging.getLogger(__name__)


class TriuneAnalyzer:
    """
    Core analysis engine for Triune Oracle repositories.
    
    Provides comprehensive async analysis capabilities including:
    - Multi-repository scanning and analysis
    - Security vulnerability assessment
    - Performance metrics collection
    - Code quality analysis
    - Integration with Triune ecosystem services
    """
    
    def __init__(self):
        self.github_token = os.getenv("REPO_SYNC_TOKEN")
        self.github_api_base = "https://api.github.com"
        self.triune_repositories = [
            "triune-swarm-engine",
            "legio-cognito", 
            "triumvirate-monitor",
            "shadowscrolls-api",
            "triune-oracle-core"
        ]
        self.session = None
        
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession(
            headers={
                "Authorization": f"token {self.github_token}",
                "Accept": "application/vnd.github.v3+json",
                "User-Agent": "MirrorWatcherAI/1.0.0"
            }
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def analyze_all_repositories(self, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Analyze all Triune repositories comprehensively.
        
        Args:
            config: Optional configuration for analysis parameters
            
        Returns:
            Comprehensive analysis results
        """
        logger.info("Starting comprehensive analysis of all Triune repositories")
        
        async with self:
            analysis_start = datetime.now(timezone.utc)
            
            # Initialize results structure
            results = {
                "analysis_id": f"full_{analysis_start.strftime('%Y%m%d_%H%M%S')}",
                "timestamp": analysis_start.isoformat(),
                "repositories": {},
                "summary": {},
                "security_assessment": {},
                "performance_metrics": {},
                "recommendations": []
            }
            
            # Analyze each repository
            analysis_tasks = []
            for repo in self.triune_repositories:
                task = self._analyze_single_repository(repo, config)
                analysis_tasks.append(task)
            
            # Execute analysis in parallel
            repository_results = await asyncio.gather(*analysis_tasks, return_exceptions=True)
            
            # Process results
            for i, result in enumerate(repository_results):
                repo_name = self.triune_repositories[i]
                
                if isinstance(result, Exception):
                    logger.error(f"Analysis failed for {repo_name}: {str(result)}")
                    results["repositories"][repo_name] = {
                        "status": "error",
                        "error": str(result),
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    }
                else:
                    results["repositories"][repo_name] = result
            
            # Generate summary and assessments
            results["summary"] = await self._generate_analysis_summary(results["repositories"])
            results["security_assessment"] = await self._generate_security_assessment(results["repositories"])
            results["performance_metrics"] = await self._generate_performance_metrics(results["repositories"])
            results["recommendations"] = await self._generate_recommendations(results)
            
            # Calculate execution time
            analysis_end = datetime.now(timezone.utc)
            results["execution_time_seconds"] = (analysis_end - analysis_start).total_seconds()
            
            logger.info(f"Analysis completed in {results['execution_time_seconds']:.2f} seconds")
            return results
    
    async def analyze_specific_repositories(self, repositories: List[str]) -> Dict[str, Any]:
        """
        Analyze specific repositories.
        
        Args:
            repositories: List of repository names to analyze
            
        Returns:
            Analysis results for specified repositories
        """
        logger.info(f"Analyzing specific repositories: {repositories}")
        
        async with self:
            analysis_start = datetime.now(timezone.utc)
            
            results = {
                "analysis_id": f"specific_{analysis_start.strftime('%Y%m%d_%H%M%S')}",
                "timestamp": analysis_start.isoformat(),
                "repositories": {},
                "summary": {}
            }
            
            # Analyze each specified repository
            analysis_tasks = []
            for repo in repositories:
                if repo in self.triune_repositories:
                    task = self._analyze_single_repository(repo)
                    analysis_tasks.append(task)
                else:
                    logger.warning(f"Repository {repo} not in Triune ecosystem")
                    results["repositories"][repo] = {
                        "status": "not_found",
                        "message": "Repository not in Triune ecosystem"
                    }
            
            # Execute analysis
            if analysis_tasks:
                repository_results = await asyncio.gather(*analysis_tasks, return_exceptions=True)
                
                for i, result in enumerate(repository_results):
                    repo_name = repositories[i]
                    if isinstance(result, Exception):
                        results["repositories"][repo_name] = {
                            "status": "error", 
                            "error": str(result)
                        }
                    else:
                        results["repositories"][repo_name] = result
            
            # Generate summary
            results["summary"] = await self._generate_analysis_summary(results["repositories"])
            
            analysis_end = datetime.now(timezone.utc)
            results["execution_time_seconds"] = (analysis_end - analysis_start).total_seconds()
            
            return results
    
    async def _analyze_single_repository(self, repo_name: str, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Perform comprehensive analysis of a single repository.
        
        Args:
            repo_name: Name of the repository to analyze
            config: Optional configuration parameters
            
        Returns:
            Detailed analysis results for the repository
        """
        logger.info(f"Analyzing repository: {repo_name}")
        
        analysis_start = datetime.now(timezone.utc)
        
        try:
            # Repository metadata
            repo_info = await self._get_repository_info(repo_name)
            
            # Recent commits analysis
            commits_analysis = await self._analyze_recent_commits(repo_name)
            
            # Code analysis
            code_analysis = await self._analyze_code_structure(repo_name)
            
            # Security scanning
            security_scan = await self._perform_security_scan(repo_name)
            
            # Performance metrics
            performance_metrics = await self._collect_performance_metrics(repo_name)
            
            # Dependency analysis
            dependency_analysis = await self._analyze_dependencies(repo_name)
            
            # Calculate repository health score
            health_score = await self._calculate_health_score(
                repo_info, commits_analysis, code_analysis, 
                security_scan, performance_metrics, dependency_analysis
            )
            
            result = {
                "repository": repo_name,
                "analysis_timestamp": analysis_start.isoformat(),
                "status": "completed",
                "repository_info": repo_info,
                "commits_analysis": commits_analysis,
                "code_analysis": code_analysis,
                "security_scan": security_scan,
                "performance_metrics": performance_metrics,
                "dependency_analysis": dependency_analysis,
                "health_score": health_score,
                "analysis_duration_seconds": (datetime.now(timezone.utc) - analysis_start).total_seconds()
            }
            
            logger.info(f"Repository {repo_name} analysis completed (score: {health_score}/100)")
            return result
            
        except Exception as e:
            logger.error(f"Failed to analyze repository {repo_name}: {str(e)}")
            raise
    
    async def _get_repository_info(self, repo_name: str) -> Dict[str, Any]:
        """Get basic repository information from GitHub API."""
        
        url = f"{self.github_api_base}/repos/Triune-Oracle/{repo_name}"
        
        async with self.session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                return {
                    "name": data["name"],
                    "full_name": data["full_name"],
                    "description": data.get("description", ""),
                    "language": data.get("language"),
                    "size": data["size"],
                    "stargazers_count": data["stargazers_count"],
                    "watchers_count": data["watchers_count"],
                    "forks_count": data["forks_count"],
                    "open_issues_count": data["open_issues_count"],
                    "created_at": data["created_at"],
                    "updated_at": data["updated_at"],
                    "pushed_at": data["pushed_at"],
                    "default_branch": data["default_branch"],
                    "topics": data.get("topics", [])
                }
            else:
                raise Exception(f"Failed to get repository info: {response.status}")
    
    async def _analyze_recent_commits(self, repo_name: str, limit: int = 100) -> Dict[str, Any]:
        """Analyze recent commits for patterns and metrics."""
        
        url = f"{self.github_api_base}/repos/Triune-Oracle/{repo_name}/commits"
        params = {"per_page": limit}
        
        async with self.session.get(url, params=params) as response:
            if response.status == 200:
                commits = await response.json()
                
                if not commits:
                    return {"total_commits": 0, "analysis": "No commits found"}
                
                # Analyze commit patterns
                authors = {}
                commit_times = []
                commit_messages = []
                
                for commit in commits:
                    # Author analysis
                    author = commit["commit"]["author"]["name"]
                    authors[author] = authors.get(author, 0) + 1
                    
                    # Time analysis
                    commit_times.append(commit["commit"]["author"]["date"])
                    
                    # Message analysis
                    commit_messages.append(commit["commit"]["message"])
                
                return {
                    "total_commits_analyzed": len(commits),
                    "unique_authors": len(authors),
                    "most_active_author": max(authors, key=authors.get) if authors else None,
                    "author_distribution": authors,
                    "recent_activity": {
                        "last_commit": commits[0]["commit"]["author"]["date"] if commits else None,
                        "commit_frequency": len(commits)  # commits in last period
                    },
                    "commit_message_analysis": {
                        "avg_length": sum(len(msg) for msg in commit_messages) / len(commit_messages) if commit_messages else 0,
                        "conventional_commits": sum(1 for msg in commit_messages if self._is_conventional_commit(msg))
                    }
                }
            else:
                raise Exception(f"Failed to get commits: {response.status}")
    
    async def _analyze_code_structure(self, repo_name: str) -> Dict[str, Any]:
        """Analyze repository code structure and composition."""
        
        # Get repository languages
        url = f"{self.github_api_base}/repos/Triune-Oracle/{repo_name}/languages"
        
        async with self.session.get(url) as response:
            if response.status == 200:
                languages = await response.json()
                
                total_bytes = sum(languages.values())
                language_percentages = {
                    lang: (bytes_count / total_bytes) * 100 
                    for lang, bytes_count in languages.items()
                } if total_bytes > 0 else {}
                
                # Get repository tree to analyze structure
                tree_analysis = await self._analyze_repository_tree(repo_name)
                
                return {
                    "languages": languages,
                    "language_percentages": language_percentages,
                    "primary_language": max(languages, key=languages.get) if languages else None,
                    "total_code_bytes": total_bytes,
                    "file_structure": tree_analysis
                }
            else:
                raise Exception(f"Failed to get code structure: {response.status}")
    
    async def _analyze_repository_tree(self, repo_name: str) -> Dict[str, Any]:
        """Analyze repository file tree structure."""
        
        url = f"{self.github_api_base}/repos/Triune-Oracle/{repo_name}/git/trees/HEAD?recursive=1"
        
        async with self.session.get(url) as response:
            if response.status == 200:
                tree_data = await response.json()
                tree = tree_data.get("tree", [])
                
                file_types = {}
                directories = set()
                total_files = 0
                
                for item in tree:
                    if item["type"] == "blob":  # file
                        total_files += 1
                        ext = item["path"].split(".")[-1] if "." in item["path"] else "no_extension"
                        file_types[ext] = file_types.get(ext, 0) + 1
                    elif item["type"] == "tree":  # directory
                        directories.add(item["path"])
                
                return {
                    "total_files": total_files,
                    "total_directories": len(directories),
                    "file_types": file_types,
                    "depth_analysis": {
                        "max_depth": max(len(d.split("/")) for d in directories) if directories else 0,
                        "avg_depth": sum(len(d.split("/")) for d in directories) / len(directories) if directories else 0
                    }
                }
            else:
                return {"error": f"Failed to get tree: {response.status}"}
    
    async def _perform_security_scan(self, repo_name: str) -> Dict[str, Any]:
        """Perform basic security scanning."""
        
        # Check for security advisories
        url = f"{self.github_api_base}/repos/Triune-Oracle/{repo_name}/security-advisories"
        
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    advisories = await response.json()
                else:
                    advisories = []  # Endpoint might not be available
        except:
            advisories = []
        
        # Check for known security files
        security_files = await self._check_security_files(repo_name)
        
        # Basic vulnerability assessment
        vulnerability_assessment = await self._assess_vulnerabilities(repo_name)
        
        return {
            "security_advisories": len(advisories),
            "security_files_present": security_files,
            "vulnerability_assessment": vulnerability_assessment,
            "security_score": self._calculate_security_score(advisories, security_files, vulnerability_assessment)
        }
    
    async def _check_security_files(self, repo_name: str) -> Dict[str, bool]:
        """Check for presence of important security files."""
        
        security_files = [
            "SECURITY.md",
            ".github/SECURITY.md", 
            "security.md",
            ".gitignore",
            "requirements.txt",
            "package.json",
            "Dockerfile",
            ".dockerignore"
        ]
        
        results = {}
        
        for file_path in security_files:
            url = f"{self.github_api_base}/repos/Triune-Oracle/{repo_name}/contents/{file_path}"
            
            try:
                async with self.session.get(url) as response:
                    results[file_path] = response.status == 200
            except:
                results[file_path] = False
        
        return results
    
    async def _assess_vulnerabilities(self, repo_name: str) -> Dict[str, Any]:
        """Perform basic vulnerability assessment."""
        
        # This is a simplified assessment - in production, you'd integrate with
        # tools like Snyk, GitHub Security Advisories, etc.
        
        assessment = {
            "high_risk_patterns": 0,
            "medium_risk_patterns": 0,
            "low_risk_patterns": 0,
            "recommendations": []
        }
        
        # Check for common risk indicators in repository
        # This is a basic implementation - would be expanded with real security tools
        
        return assessment
    
    async def _collect_performance_metrics(self, repo_name: str) -> Dict[str, Any]:
        """Collect repository performance metrics."""
        
        # Repository size and activity metrics
        url = f"{self.github_api_base}/repos/Triune-Oracle/{repo_name}"
        
        async with self.session.get(url) as response:
            if response.status == 200:
                repo_data = await response.json()
                
                return {
                    "repository_size_kb": repo_data["size"],
                    "clone_performance": {
                        "estimated_clone_time_seconds": self._estimate_clone_time(repo_data["size"]),
                        "size_category": self._categorize_repo_size(repo_data["size"])
                    },
                    "activity_metrics": {
                        "stars_per_day": self._calculate_stars_per_day(repo_data),
                        "commits_frequency": "daily"  # Would calculate from commit history
                    },
                    "health_indicators": {
                        "has_recent_activity": self._has_recent_activity(repo_data["pushed_at"]),
                        "maintenance_status": self._assess_maintenance_status(repo_data)
                    }
                }
            else:
                raise Exception(f"Failed to collect performance metrics: {response.status}")
    
    async def _analyze_dependencies(self, repo_name: str) -> Dict[str, Any]:
        """Analyze repository dependencies."""
        
        dependency_files = {
            "requirements.txt": "python",
            "package.json": "nodejs", 
            "Cargo.toml": "rust",
            "go.mod": "go",
            "pom.xml": "java",
            "Gemfile": "ruby"
        }
        
        found_dependencies = {}
        
        for file_name, ecosystem in dependency_files.items():
            url = f"{self.github_api_base}/repos/Triune-Oracle/{repo_name}/contents/{file_name}"
            
            try:
                async with self.session.get(url) as response:
                    if response.status == 200:
                        content = await response.json()
                        # Decode base64 content
                        decoded_content = base64.b64decode(content["content"]).decode('utf-8')
                        found_dependencies[ecosystem] = self._parse_dependencies(decoded_content, ecosystem)
            except:
                continue
        
        return {
            "ecosystems_found": list(found_dependencies.keys()),
            "dependencies": found_dependencies,
            "dependency_count": sum(len(deps) for deps in found_dependencies.values()),
            "security_assessment": "requires_detailed_scan"  # Would integrate with security scanners
        }
    
    async def _calculate_health_score(self, *analysis_components) -> int:
        """Calculate overall repository health score (0-100)."""
        
        repo_info, commits_analysis, code_analysis, security_scan, performance_metrics, dependency_analysis = analysis_components
        
        score = 100  # Start with perfect score
        
        # Deduct for issues
        if repo_info.get("open_issues_count", 0) > 10:
            score -= 10
        
        if security_scan.get("security_score", 100) < 80:
            score -= 15
        
        if not commits_analysis.get("recent_activity", {}).get("last_commit"):
            score -= 20
        
        # Add points for good practices
        if security_scan.get("security_files_present", {}).get("SECURITY.md"):
            score += 5
        
        if commits_analysis.get("commit_message_analysis", {}).get("conventional_commits", 0) > 5:
            score += 5
        
        return max(0, min(100, score))
    
    def _is_conventional_commit(self, message: str) -> bool:
        """Check if commit message follows conventional commit format."""
        import re
        pattern = r'^(feat|fix|docs|style|refactor|test|chore)(\(.+\))?: .+'
        return bool(re.match(pattern, message))
    
    def _estimate_clone_time(self, size_kb: int) -> float:
        """Estimate clone time based on repository size."""
        # Simple estimation: 1MB per second on average connection
        return size_kb / 1024  # seconds
    
    def _categorize_repo_size(self, size_kb: int) -> str:
        """Categorize repository size."""
        if size_kb < 1024:  # < 1MB
            return "small"
        elif size_kb < 10240:  # < 10MB
            return "medium"
        elif size_kb < 102400:  # < 100MB
            return "large"
        else:
            return "very_large"
    
    def _calculate_stars_per_day(self, repo_data: Dict[str, Any]) -> float:
        """Calculate average stars per day since creation."""
        from datetime import datetime
        
        created = datetime.fromisoformat(repo_data["created_at"].replace("Z", "+00:00"))
        days_since_creation = (datetime.now(timezone.utc) - created).days
        
        if days_since_creation > 0:
            return repo_data["stargazers_count"] / days_since_creation
        return 0
    
    def _has_recent_activity(self, pushed_at: str) -> bool:
        """Check if repository has recent activity (within 30 days)."""
        from datetime import datetime, timedelta
        
        last_push = datetime.fromisoformat(pushed_at.replace("Z", "+00:00"))
        thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
        
        return last_push > thirty_days_ago
    
    def _assess_maintenance_status(self, repo_data: Dict[str, Any]) -> str:
        """Assess repository maintenance status."""
        if self._has_recent_activity(repo_data["pushed_at"]):
            return "active"
        elif repo_data["open_issues_count"] > 20:
            return "needs_attention"
        else:
            return "stable"
    
    def _parse_dependencies(self, content: str, ecosystem: str) -> List[str]:
        """Parse dependencies from file content."""
        dependencies = []
        
        if ecosystem == "python":
            for line in content.split('\n'):
                if line.strip() and not line.startswith('#'):
                    dep = line.split('==')[0].split('>=')[0].split('<=')[0].strip()
                    if dep:
                        dependencies.append(dep)
        elif ecosystem == "nodejs":
            try:
                import json
                package_data = json.loads(content)
                dependencies.extend(package_data.get("dependencies", {}).keys())
                dependencies.extend(package_data.get("devDependencies", {}).keys())
            except:
                pass
        
        return dependencies
    
    def _calculate_security_score(self, advisories: List, security_files: Dict, vulnerability_assessment: Dict) -> int:
        """Calculate security score for repository."""
        score = 100
        
        # Deduct for security advisories
        score -= len(advisories) * 20
        
        # Deduct for missing security files
        important_files = ["SECURITY.md", ".gitignore"]
        for file in important_files:
            if not security_files.get(file, False):
                score -= 10
        
        # Consider vulnerability assessment
        score -= vulnerability_assessment.get("high_risk_patterns", 0) * 25
        score -= vulnerability_assessment.get("medium_risk_patterns", 0) * 10
        
        return max(0, min(100, score))
    
    async def _generate_analysis_summary(self, repositories: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary of analysis results."""
        
        total_repos = len(repositories)
        successful_analyses = len([r for r in repositories.values() if r.get("status") == "completed"])
        
        health_scores = [
            r.get("health_score", 0) for r in repositories.values() 
            if r.get("status") == "completed"
        ]
        
        return {
            "total_repositories": total_repos,
            "successful_analyses": successful_analyses,
            "failed_analyses": total_repos - successful_analyses,
            "average_health_score": sum(health_scores) / len(health_scores) if health_scores else 0,
            "highest_health_score": max(health_scores) if health_scores else 0,
            "lowest_health_score": min(health_scores) if health_scores else 0,
        }
    
    async def _generate_security_assessment(self, repositories: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive security assessment."""
        
        total_advisories = 0
        security_scores = []
        
        for repo_data in repositories.values():
            if repo_data.get("status") == "completed":
                security_scan = repo_data.get("security_scan", {})
                total_advisories += security_scan.get("security_advisories", 0)
                security_scores.append(security_scan.get("security_score", 100))
        
        return {
            "total_security_advisories": total_advisories,
            "average_security_score": sum(security_scores) / len(security_scores) if security_scores else 100,
            "repositories_needing_attention": len([s for s in security_scores if s < 80]),
            "overall_security_status": "good" if all(s >= 80 for s in security_scores) else "needs_attention"
        }
    
    async def _generate_performance_metrics(self, repositories: Dict[str, Any]) -> Dict[str, Any]:
        """Generate performance metrics summary."""
        
        total_size = 0
        active_repos = 0
        
        for repo_data in repositories.values():
            if repo_data.get("status") == "completed":
                perf_metrics = repo_data.get("performance_metrics", {})
                total_size += perf_metrics.get("repository_size_kb", 0)
                
                if perf_metrics.get("health_indicators", {}).get("has_recent_activity"):
                    active_repos += 1
        
        return {
            "total_ecosystem_size_mb": total_size / 1024,
            "active_repositories": active_repos,
            "ecosystem_activity_rate": active_repos / len(repositories) if repositories else 0
        }
    
    async def _generate_recommendations(self, analysis_results: Dict[str, Any]) -> List[str]:
        """Generate actionable recommendations based on analysis."""
        
        recommendations = []
        
        # Security recommendations
        security_assessment = analysis_results.get("security_assessment", {})
        if security_assessment.get("overall_security_status") == "needs_attention":
            recommendations.append("Review and address security vulnerabilities across repositories")
        
        # Performance recommendations
        summary = analysis_results.get("summary", {})
        if summary.get("average_health_score", 100) < 80:
            recommendations.append("Focus on improving repository health scores through better maintenance")
        
        # Activity recommendations
        performance_metrics = analysis_results.get("performance_metrics", {})
        if performance_metrics.get("ecosystem_activity_rate", 1) < 0.8:
            recommendations.append("Increase development activity in inactive repositories")
        
        return recommendations
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check of analyzer system."""
        
        health_status = {
            "status": "healthy",
            "checks": {},
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        # Check GitHub API connectivity
        try:
            if not self.github_token:
                raise Exception("GitHub token not configured")
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.github_api_base}/user",
                    headers={"Authorization": f"token {self.github_token}"}
                ) as response:
                    if response.status == 200:
                        health_status["checks"]["github_api"] = {"status": "healthy"}
                    else:
                        health_status["checks"]["github_api"] = {"status": "error", "code": response.status}
                        health_status["status"] = "degraded"
        
        except Exception as e:
            health_status["checks"]["github_api"] = {"status": "error", "error": str(e)}
            health_status["status"] = "unhealthy"
        
        # Check repository access
        try:
            test_repo = self.triune_repositories[0]  # Test with first repository
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.github_api_base}/repos/Triune-Oracle/{test_repo}",
                    headers={"Authorization": f"token {self.github_token}"}
                ) as response:
                    if response.status == 200:
                        health_status["checks"]["repository_access"] = {"status": "healthy"}
                    else:
                        health_status["checks"]["repository_access"] = {"status": "error", "code": response.status}
                        health_status["status"] = "degraded"
        
        except Exception as e:
            health_status["checks"]["repository_access"] = {"status": "error", "error": str(e)}
            health_status["status"] = "unhealthy"
        
        return health_status