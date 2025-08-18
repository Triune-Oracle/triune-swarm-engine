"""
TriuneAnalyzer - Comprehensive analysis engine for repository monitoring.
Provides deep analysis capabilities with performance metrics and security scanning.
"""

import asyncio
import aiohttp
import hashlib
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import subprocess
import os
import tempfile

logger = logging.getLogger(__name__)


class TriuneAnalyzer:
    """Comprehensive analyzer for Triune ecosystem repositories."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.session = None
        self.analysis_depth = config.get('depth', 'comprehensive')
        self.include_dependencies = config.get('include_dependencies', True)
        self.security_scan = config.get('security_scan', True)
        self.performance_metrics = config.get('performance_metrics', True)
        
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def analyze_repositories(self, repositories: List[str]) -> Dict[str, Any]:
        """Analyze multiple repositories concurrently."""
        if not self.session:
            self.session = aiohttp.ClientSession()
            
        try:
            analysis_tasks = []
            for repo in repositories:
                task = asyncio.create_task(self.analyze_single_repository(repo))
                analysis_tasks.append(task)
            
            results = await asyncio.gather(*analysis_tasks, return_exceptions=True)
            
            # Compile results
            compiled_results = {
                'repositories': {},
                'summary': {
                    'total_repositories': len(repositories),
                    'successful_analyses': 0,
                    'failed_analyses': 0,
                    'analysis_timestamp': datetime.now(timezone.utc).isoformat(),
                    'analyzer_version': '1.0.0'
                },
                'metrics': await self.calculate_aggregate_metrics(results)
            }
            
            for i, (repo, result) in enumerate(zip(repositories, results)):
                if isinstance(result, Exception):
                    compiled_results['repositories'][repo] = {
                        'status': 'failed',
                        'error': str(result),
                        'timestamp': datetime.now(timezone.utc).isoformat()
                    }
                    compiled_results['summary']['failed_analyses'] += 1
                else:
                    compiled_results['repositories'][repo] = result
                    compiled_results['summary']['successful_analyses'] += 1
            
            return compiled_results
            
        except Exception as e:
            logger.error(f"Repository analysis failed: {str(e)}")
            raise
    
    async def analyze_single_repository(self, repository: str) -> Dict[str, Any]:
        """Perform comprehensive analysis of a single repository."""
        logger.info(f"Starting analysis of repository: {repository}")
        
        try:
            # Parse repository identifier
            owner, repo_name = repository.split('/', 1)
            
            # Gather repository information
            repo_info = await self.get_repository_info(owner, repo_name)
            
            # Clone repository for local analysis
            with tempfile.TemporaryDirectory() as temp_dir:
                clone_path = await self.clone_repository(repository, temp_dir)
                
                # Perform various analyses
                analysis_results = {
                    'repository': repository,
                    'info': repo_info,
                    'structure': await self.analyze_structure(clone_path),
                    'code_metrics': await self.analyze_code_metrics(clone_path),
                    'dependencies': await self.analyze_dependencies(clone_path) if self.include_dependencies else None,
                    'security': await self.analyze_security(clone_path) if self.security_scan else None,
                    'performance': await self.analyze_performance(clone_path) if self.performance_metrics else None,
                    'git_metrics': await self.analyze_git_metrics(clone_path),
                    'quality_score': 0,  # Will be calculated
                    'recommendations': [],
                    'analysis_timestamp': datetime.now(timezone.utc).isoformat(),
                    'status': 'completed'
                }
                
                # Calculate quality score
                analysis_results['quality_score'] = self.calculate_quality_score(analysis_results)
                
                # Generate recommendations
                analysis_results['recommendations'] = self.generate_recommendations(analysis_results)
                
                logger.info(f"Analysis completed for {repository}")
                return analysis_results
                
        except Exception as e:
            logger.error(f"Failed to analyze {repository}: {str(e)}")
            return {
                'repository': repository,
                'status': 'failed',
                'error': str(e),
                'analysis_timestamp': datetime.now(timezone.utc).isoformat()
            }
    
    async def get_repository_info(self, owner: str, repo: str) -> Dict[str, Any]:
        """Fetch repository information from GitHub API."""
        try:
            github_token = os.environ.get('GITHUB_TOKEN') or os.environ.get('REPO_SYNC_TOKEN')
            headers = {}
            if github_token:
                headers['Authorization'] = f'token {github_token}'
            
            url = f'https://api.github.com/repos/{owner}/{repo}'
            
            async with self.session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        'name': data.get('name'),
                        'full_name': data.get('full_name'),
                        'description': data.get('description'),
                        'language': data.get('language'),
                        'size': data.get('size'),
                        'stars': data.get('stargazers_count'),
                        'forks': data.get('forks_count'),
                        'issues': data.get('open_issues_count'),
                        'created_at': data.get('created_at'),
                        'updated_at': data.get('updated_at'),
                        'pushed_at': data.get('pushed_at'),
                        'license': data.get('license', {}).get('name') if data.get('license') else None,
                        'default_branch': data.get('default_branch')
                    }
                else:
                    logger.warning(f"Failed to fetch repository info: {response.status}")
                    return {'error': f'API request failed with status {response.status}'}
                    
        except Exception as e:
            logger.error(f"Error fetching repository info: {str(e)}")
            return {'error': str(e)}
    
    async def clone_repository(self, repository: str, temp_dir: str) -> str:
        """Clone repository to temporary directory."""
        clone_path = Path(temp_dir) / 'repo'
        
        try:
            # Use GitHub token if available
            github_token = os.environ.get('GITHUB_TOKEN') or os.environ.get('REPO_SYNC_TOKEN')
            if github_token:
                clone_url = f'https://{github_token}@github.com/{repository}.git'
            else:
                clone_url = f'https://github.com/{repository}.git'
            
            # Clone repository
            process = await asyncio.create_subprocess_exec(
                'git', 'clone', '--depth', '1', clone_url, str(clone_path),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                raise Exception(f"Git clone failed: {stderr.decode()}")
            
            return str(clone_path)
            
        except Exception as e:
            logger.error(f"Failed to clone repository: {str(e)}")
            raise
    
    async def analyze_structure(self, repo_path: str) -> Dict[str, Any]:
        """Analyze repository structure and file organization."""
        try:
            repo_path = Path(repo_path)
            
            # Count files by extension
            file_counts = {}
            total_files = 0
            total_size = 0
            
            for file_path in repo_path.rglob('*'):
                if file_path.is_file() and not any(part.startswith('.') for part in file_path.parts):
                    total_files += 1
                    try:
                        file_size = file_path.stat().st_size
                        total_size += file_size
                        
                        extension = file_path.suffix.lower()
                        if extension:
                            file_counts[extension] = file_counts.get(extension, 0) + 1
                        else:
                            file_counts['[no extension]'] = file_counts.get('[no extension]', 0) + 1
                    except (OSError, PermissionError):
                        pass
            
            # Identify key files
            key_files = []
            for key_file in ['README.md', 'LICENSE', 'requirements.txt', 'package.json', 'Dockerfile', '.gitignore']:
                if (repo_path / key_file).exists():
                    key_files.append(key_file)
            
            # Calculate language composition
            total_code_files = sum(count for ext, count in file_counts.items() if ext in ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.go', '.rs', '.rb', '.php'])
            language_composition = {}
            
            language_extensions = {
                '.py': 'Python',
                '.js': 'JavaScript', 
                '.ts': 'TypeScript',
                '.java': 'Java',
                '.cpp': 'C++',
                '.c': 'C',
                '.go': 'Go',
                '.rs': 'Rust',
                '.rb': 'Ruby',
                '.php': 'PHP'
            }
            
            for ext, lang in language_extensions.items():
                if ext in file_counts and total_code_files > 0:
                    percentage = (file_counts[ext] / total_code_files) * 100
                    language_composition[lang] = {
                        'files': file_counts[ext],
                        'percentage': round(percentage, 2)
                    }
            
            return {
                'total_files': total_files,
                'total_size_bytes': total_size,
                'file_counts_by_extension': file_counts,
                'key_files_present': key_files,
                'language_composition': language_composition,
                'analysis_timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Structure analysis failed: {str(e)}")
            return {'error': str(e)}
    
    async def analyze_code_metrics(self, repo_path: str) -> Dict[str, Any]:
        """Analyze code quality metrics."""
        try:
            repo_path = Path(repo_path)
            
            # Basic line counting
            total_lines = 0
            code_lines = 0
            comment_lines = 0
            blank_lines = 0
            
            python_files = list(repo_path.rglob('*.py'))
            
            for py_file in python_files:
                try:
                    with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = f.readlines()
                        total_lines += len(lines)
                        
                        for line in lines:
                            stripped = line.strip()
                            if not stripped:
                                blank_lines += 1
                            elif stripped.startswith('#'):
                                comment_lines += 1
                            else:
                                code_lines += 1
                except (OSError, UnicodeDecodeError):
                    pass
            
            # Calculate complexity indicators
            complexity_score = 0
            if python_files:
                complexity_score = min(len(python_files) / 10, 10)  # Simple heuristic
            
            return {
                'total_lines': total_lines,
                'code_lines': code_lines,
                'comment_lines': comment_lines,
                'blank_lines': blank_lines,
                'python_files_count': len(python_files),
                'comment_ratio': round((comment_lines / max(total_lines, 1)) * 100, 2),
                'complexity_score': round(complexity_score, 2),
                'analysis_timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Code metrics analysis failed: {str(e)}")
            return {'error': str(e)}
    
    async def analyze_dependencies(self, repo_path: str) -> Dict[str, Any]:
        """Analyze project dependencies."""
        try:
            repo_path = Path(repo_path)
            dependencies = {}
            
            # Python dependencies
            requirements_file = repo_path / 'requirements.txt'
            if requirements_file.exists():
                try:
                    with open(requirements_file, 'r') as f:
                        python_deps = []
                        for line in f:
                            line = line.strip()
                            if line and not line.startswith('#'):
                                python_deps.append(line)
                        dependencies['python'] = python_deps
                except Exception as e:
                    dependencies['python'] = [f'Error reading requirements.txt: {str(e)}']
            
            # Node.js dependencies
            package_json = repo_path / 'package.json'
            if package_json.exists():
                try:
                    with open(package_json, 'r') as f:
                        package_data = json.load(f)
                        dependencies['nodejs'] = {
                            'dependencies': package_data.get('dependencies', {}),
                            'devDependencies': package_data.get('devDependencies', {})
                        }
                except Exception as e:
                    dependencies['nodejs'] = [f'Error reading package.json: {str(e)}']
            
            return {
                'dependencies': dependencies,
                'dependency_count': sum(len(deps) if isinstance(deps, (list, dict)) else 0 for deps in dependencies.values()),
                'analysis_timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Dependencies analysis failed: {str(e)}")
            return {'error': str(e)}
    
    async def analyze_security(self, repo_path: str) -> Dict[str, Any]:
        """Perform basic security analysis."""
        try:
            repo_path = Path(repo_path)
            security_issues = []
            
            # Check for common security files
            security_files = []
            for sec_file in ['SECURITY.md', '.github/SECURITY.md', 'security.txt']:
                if (repo_path / sec_file).exists():
                    security_files.append(sec_file)
            
            # Basic pattern matching for potential issues
            for py_file in repo_path.rglob('*.py'):
                try:
                    with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read().lower()
                        
                        # Check for hardcoded secrets patterns
                        if any(pattern in content for pattern in ['password =', 'api_key =', 'secret =', 'token =']):
                            security_issues.append(f"Potential hardcoded credential in {py_file.name}")
                        
                        # Check for SQL injection patterns
                        if 'execute(' in content and ('format(' in content or '%' in content):
                            security_issues.append(f"Potential SQL injection vulnerability in {py_file.name}")
                            
                except Exception:
                    pass
            
            return {
                'security_files_present': security_files,
                'potential_issues': security_issues,
                'security_score': max(0, 10 - len(security_issues)),
                'analysis_timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Security analysis failed: {str(e)}")
            return {'error': str(e)}
    
    async def analyze_performance(self, repo_path: str) -> Dict[str, Any]:
        """Analyze performance characteristics."""
        try:
            repo_path = Path(repo_path)
            
            # Repository size metrics
            total_size = sum(f.stat().st_size for f in repo_path.rglob('*') if f.is_file())
            
            # File count metrics
            file_count = len(list(repo_path.rglob('*')))
            
            # Calculate performance score based on size and complexity
            performance_score = 10
            if total_size > 100 * 1024 * 1024:  # > 100MB
                performance_score -= 2
            if file_count > 1000:
                performance_score -= 1
            
            return {
                'repository_size_bytes': total_size,
                'file_count': file_count,
                'performance_score': max(0, performance_score),
                'size_category': 'large' if total_size > 10*1024*1024 else 'medium' if total_size > 1024*1024 else 'small',
                'analysis_timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Performance analysis failed: {str(e)}")
            return {'error': str(e)}
    
    async def analyze_git_metrics(self, repo_path: str) -> Dict[str, Any]:
        """Analyze Git repository metrics."""
        try:
            # Get commit count
            process = await asyncio.create_subprocess_exec(
                'git', 'rev-list', '--count', 'HEAD',
                cwd=repo_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            commit_count = 0
            if process.returncode == 0:
                commit_count = int(stdout.decode().strip())
            
            # Get branch count
            process = await asyncio.create_subprocess_exec(
                'git', 'branch', '-r',
                cwd=repo_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            branch_count = 0
            if process.returncode == 0:
                branch_count = len(stdout.decode().strip().split('\n'))
            
            return {
                'commit_count': commit_count,
                'branch_count': branch_count,
                'analysis_timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Git metrics analysis failed: {str(e)}")
            return {'error': str(e)}
    
    def calculate_quality_score(self, analysis: Dict[str, Any]) -> float:
        """Calculate overall quality score based on analysis results."""
        try:
            score = 0.0
            weight_sum = 0.0
            
            # Code metrics weight
            if 'code_metrics' in analysis and 'comment_ratio' in analysis['code_metrics']:
                comment_ratio = analysis['code_metrics']['comment_ratio']
                score += min(comment_ratio / 20 * 10, 10) * 0.2  # Max 10 points for 20%+ comments
                weight_sum += 0.2
            
            # Security weight
            if 'security' in analysis and 'security_score' in analysis['security']:
                score += analysis['security']['security_score'] * 0.3
                weight_sum += 0.3
            
            # Performance weight
            if 'performance' in analysis and 'performance_score' in analysis['performance']:
                score += analysis['performance']['performance_score'] * 0.2
                weight_sum += 0.2
            
            # Structure weight
            if 'structure' in analysis and 'key_files_present' in analysis['structure']:
                key_files_score = min(len(analysis['structure']['key_files_present']) / 4 * 10, 10)
                score += key_files_score * 0.3
                weight_sum += 0.3
            
            return round(score / max(weight_sum, 1), 2)
            
        except Exception as e:
            logger.error(f"Quality score calculation failed: {str(e)}")
            return 0.0
    
    def generate_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate improvement recommendations based on analysis."""
        recommendations = []
        
        try:
            # Code quality recommendations
            if 'code_metrics' in analysis:
                comment_ratio = analysis['code_metrics'].get('comment_ratio', 0)
                if comment_ratio < 10:
                    recommendations.append("Consider adding more code comments to improve maintainability")
            
            # Security recommendations
            if 'security' in analysis:
                if not analysis['security'].get('security_files_present'):
                    recommendations.append("Add a SECURITY.md file to document security policies")
                    
                if analysis['security'].get('potential_issues'):
                    recommendations.append("Review and address potential security issues found in code")
            
            # Structure recommendations
            if 'structure' in analysis:
                key_files = analysis['structure'].get('key_files_present', [])
                if 'README.md' not in key_files:
                    recommendations.append("Add a comprehensive README.md file")
                if 'LICENSE' not in key_files:
                    recommendations.append("Consider adding a license file")
            
            # Performance recommendations
            if 'performance' in analysis:
                if analysis['performance'].get('size_category') == 'large':
                    recommendations.append("Consider optimizing repository size and file organization")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Recommendations generation failed: {str(e)}")
            return ["Error generating recommendations"]
    
    async def calculate_aggregate_metrics(self, results: List[Any]) -> Dict[str, Any]:
        """Calculate aggregate metrics across all analyzed repositories."""
        try:
            successful_results = [r for r in results if not isinstance(r, Exception) and r.get('status') == 'completed']
            
            if not successful_results:
                return {'error': 'No successful analyses to aggregate'}
            
            # Calculate averages
            total_quality = sum(r.get('quality_score', 0) for r in successful_results)
            avg_quality = total_quality / len(successful_results)
            
            # Language distribution
            language_stats = {}
            for result in successful_results:
                structure = result.get('structure', {})
                languages = structure.get('language_composition', {})
                for lang, data in languages.items():
                    if lang not in language_stats:
                        language_stats[lang] = {'total_files': 0, 'repositories': 0}
                    language_stats[lang]['total_files'] += data.get('files', 0)
                    language_stats[lang]['repositories'] += 1
            
            return {
                'average_quality_score': round(avg_quality, 2),
                'language_distribution': language_stats,
                'total_successful_analyses': len(successful_results),
                'analysis_timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Aggregate metrics calculation failed: {str(e)}")
            return {'error': str(e)}