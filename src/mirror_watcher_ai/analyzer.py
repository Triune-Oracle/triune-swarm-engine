"""
TriuneAnalyzer - Core Analysis Engine

Provides comprehensive analysis capabilities for the Triune Oracle ecosystem,
including repository mirroring, code analysis, and integration assessment.
"""

import asyncio
import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any
import aiohttp
import subprocess


class TriuneAnalyzer:
    """Core analysis engine for Triune ecosystem repositories."""
    
    def __init__(self, config_path: Optional[str] = None):
        self.logger = logging.getLogger(__name__)
        self.config_path = config_path
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file or defaults."""
        if self.config_path and Path(self.config_path).exists():
            with open(self.config_path, 'r') as f:
                return json.load(f)
        
        # Default configuration
        return {
            'repositories': [
                'Triune-Oracle/triune-swarm-engine',
                'Triune-Oracle/Legio-Cognito', 
                'Triune-Oracle/TtriumvirateMonitor-Mobile',
                'Triune-Oracle/Triune-retrieval-node'
            ],
            'analysis_depth': 'comprehensive',
            'include_metrics': True,
            'parallel_processing': True,
            'timeout': 300
        }
    
    async def validate(self) -> bool:
        """Validate analyzer setup and connectivity."""
        try:
            # Check GitHub token
            token = os.getenv('REPO_SYNC_TOKEN')
            if not token:
                self.logger.error("REPO_SYNC_TOKEN not found")
                return False
            
            # Test GitHub API connectivity
            async with aiohttp.ClientSession() as session:
                headers = {
                    'Authorization': f'token {token}',
                    'Accept': 'application/vnd.github.v3+json'
                }
                
                async with session.get('https://api.github.com/user', headers=headers) as resp:
                    if resp.status != 200:
                        self.logger.error(f"GitHub API test failed: {resp.status}")
                        return False
            
            self.logger.info("Analyzer validation passed")
            return True
            
        except Exception as e:
            self.logger.error(f"Analyzer validation failed: {e}")
            return False
    
    async def analyze_repositories(self, repositories: List[str]) -> Dict[str, Any]:
        """Analyze list of repositories for Triune ecosystem integration."""
        self.logger.info(f"Starting analysis of {len(repositories)} repositories")
        
        results = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'repositories': {},
            'ecosystem_health': {},
            'integration_status': {},
            'recommendations': []
        }
        
        async with aiohttp.ClientSession() as session:
            self.session = session
            
            # Analyze repositories in parallel if configured
            config = self.load_config()
            if config.get('parallel_processing', True):
                tasks = [self._analyze_repository(repo) for repo in repositories]
                repo_results = await asyncio.gather(*tasks, return_exceptions=True)
            else:
                repo_results = []
                for repo in repositories:
                    result = await self._analyze_repository(repo)
                    repo_results.append(result)
            
            # Process results
            for repo, result in zip(repositories, repo_results):
                if isinstance(result, Exception):
                    results['repositories'][repo] = {
                        'status': 'error',
                        'error': str(result)
                    }
                else:
                    results['repositories'][repo] = result
        
        # Analyze ecosystem health
        results['ecosystem_health'] = await self._analyze_ecosystem_health(results['repositories'])
        
        # Check integration status
        results['integration_status'] = await self._check_integration_status(results['repositories'])
        
        # Generate recommendations
        results['recommendations'] = await self._generate_recommendations(results)
        
        self.logger.info("Repository analysis completed")
        return results
    
    async def _analyze_repository(self, repo: str) -> Dict[str, Any]:
        """Analyze individual repository."""
        self.logger.debug(f"Analyzing repository: {repo}")
        
        try:
            token = os.getenv('REPO_SYNC_TOKEN')
            headers = {
                'Authorization': f'token {token}',
                'Accept': 'application/vnd.github.v3+json'
            }
            
            # Get repository information
            repo_url = f'https://api.github.com/repos/{repo}'
            async with self.session.get(repo_url, headers=headers) as resp:
                if resp.status != 200:
                    return {
                        'status': 'error',
                        'error': f'Failed to fetch repository: {resp.status}'
                    }
                repo_data = await resp.json()
            
            # Get repository languages
            languages_url = f'https://api.github.com/repos/{repo}/languages'
            async with self.session.get(languages_url, headers=headers) as resp:
                languages = await resp.json() if resp.status == 200 else {}
            
            # Get recent commits
            commits_url = f'https://api.github.com/repos/{repo}/commits?per_page=10'
            async with self.session.get(commits_url, headers=headers) as resp:
                commits = await resp.json() if resp.status == 200 else []
            
            # Get workflow runs
            workflows_url = f'https://api.github.com/repos/{repo}/actions/runs?per_page=5'
            async with self.session.get(workflows_url, headers=headers) as resp:
                workflows = await resp.json() if resp.status == 200 else {}
            
            # Analyze repository structure
            structure_analysis = await self._analyze_structure(repo, headers)
            
            # Calculate metrics
            metrics = self._calculate_metrics(repo_data, languages, commits, workflows)
            
            return {
                'status': 'success',
                'name': repo_data.get('name'),
                'description': repo_data.get('description'),
                'private': repo_data.get('private'),
                'language': repo_data.get('language'),
                'languages': languages,
                'size': repo_data.get('size'),
                'stars': repo_data.get('stargazers_count'),
                'forks': repo_data.get('forks_count'),
                'issues': repo_data.get('open_issues_count'),
                'updated_at': repo_data.get('updated_at'),
                'commits': len(commits),
                'recent_activity': commits[:3] if commits else [],
                'workflows': workflows.get('total_count', 0),
                'structure': structure_analysis,
                'metrics': metrics,
                'triune_compliance': self._check_triune_compliance(structure_analysis)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to analyze repository {repo}: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    async def _analyze_structure(self, repo: str, headers: Dict[str, str]) -> Dict[str, Any]:
        """Analyze repository structure for Triune patterns."""
        try:
            contents_url = f'https://api.github.com/repos/{repo}/contents'
            async with self.session.get(contents_url, headers=headers) as resp:
                if resp.status != 200:
                    return {'error': f'Failed to fetch contents: {resp.status}'}
                
                contents = await resp.json()
                
            structure = {
                'has_readme': any(f.get('name', '').lower().startswith('readme') for f in contents),
                'has_license': any(f.get('name', '').lower().startswith('license') for f in contents),
                'has_gitignore': any(f.get('name') == '.gitignore' for f in contents),
                'has_github_dir': any(f.get('name') == '.github' for f in contents),
                'has_scripts': any(f.get('name') == 'scripts' for f in contents),
                'has_docs': any(f.get('name') == 'docs' for f in contents),
                'has_config': any(f.get('name') == 'config' for f in contents),
                'has_src': any(f.get('name') == 'src' for f in contents),
                'files': [f.get('name') for f in contents if f.get('type') == 'file'],
                'directories': [f.get('name') for f in contents if f.get('type') == 'dir']
            }
            
            # Check for Triune-specific patterns
            structure['triune_patterns'] = {
                'has_triumvirate': any('triumvirate' in f.get('name', '').lower() for f in contents),
                'has_shadow_scrolls': any('shadow' in f.get('name', '').lower() for f in contents),
                'has_legio': any('legio' in f.get('name', '').lower() for f in contents),
                'has_oracle': any('oracle' in f.get('name', '').lower() for f in contents),
                'has_triune': any('triune' in f.get('name', '').lower() for f in contents)
            }
            
            return structure
            
        except Exception as e:
            return {'error': str(e)}
    
    def _calculate_metrics(self, repo_data: Dict, languages: Dict, commits: List, workflows: Dict) -> Dict[str, Any]:
        """Calculate repository metrics."""
        total_languages = sum(languages.values()) if languages else 1
        
        return {
            'activity_score': len(commits) * 10,  # Simple activity metric
            'language_diversity': len(languages),
            'primary_language_ratio': max(languages.values()) / total_languages if languages else 0,
            'automation_score': workflows.get('total_count', 0) * 5,
            'community_score': (repo_data.get('stargazers_count', 0) + 
                              repo_data.get('forks_count', 0) * 2 + 
                              repo_data.get('watchers_count', 0)),
            'maintenance_score': 100 if commits else 0  # Simple check for recent commits
        }
    
    def _check_triune_compliance(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Check repository compliance with Triune ecosystem standards."""
        compliance_score = 0
        checks = {
            'has_documentation': structure.get('has_readme', False),
            'has_automation': structure.get('has_github_dir', False),
            'has_organization': structure.get('has_scripts', False) or structure.get('has_src', False),
            'triune_integration': any(structure.get('triune_patterns', {}).values()),
            'proper_structure': structure.get('has_config', False) or structure.get('has_docs', False)
        }
        
        compliance_score = sum(checks.values()) / len(checks) * 100
        
        return {
            'score': compliance_score,
            'checks': checks,
            'status': 'compliant' if compliance_score >= 80 else 'needs_improvement'
        }
    
    async def _analyze_ecosystem_health(self, repositories: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze overall ecosystem health."""
        total_repos = len(repositories)
        successful_analyses = sum(1 for r in repositories.values() if r.get('status') == 'success')
        
        avg_compliance = 0
        active_repos = 0
        
        for repo_data in repositories.values():
            if repo_data.get('status') == 'success':
                compliance = repo_data.get('triune_compliance', {}).get('score', 0)
                avg_compliance += compliance
                
                if repo_data.get('commits', 0) > 0:
                    active_repos += 1
        
        avg_compliance = avg_compliance / successful_analyses if successful_analyses > 0 else 0
        
        return {
            'total_repositories': total_repos,
            'analyzed_successfully': successful_analyses,
            'analysis_success_rate': (successful_analyses / total_repos * 100) if total_repos > 0 else 0,
            'average_compliance_score': avg_compliance,
            'active_repositories': active_repos,
            'ecosystem_status': 'healthy' if avg_compliance >= 70 and successful_analyses >= total_repos * 0.8 else 'needs_attention'
        }
    
    async def _check_integration_status(self, repositories: Dict[str, Any]) -> Dict[str, Any]:
        """Check integration status across Triune ecosystem."""
        integration_patterns = {
            'shadowscrolls_integration': 0,
            'legio_integration': 0,
            'triumvirate_integration': 0,
            'automation_integration': 0
        }
        
        for repo_data in repositories.values():
            if repo_data.get('status') == 'success':
                patterns = repo_data.get('structure', {}).get('triune_patterns', {})
                
                if patterns.get('has_shadow_scrolls'):
                    integration_patterns['shadowscrolls_integration'] += 1
                if patterns.get('has_legio'):
                    integration_patterns['legio_integration'] += 1
                if patterns.get('has_triumvirate'):
                    integration_patterns['triumvirate_integration'] += 1
                if repo_data.get('workflows', 0) > 0:
                    integration_patterns['automation_integration'] += 1
        
        return {
            'integration_counts': integration_patterns,
            'integration_coverage': {
                k: (v / len(repositories) * 100) if repositories else 0 
                for k, v in integration_patterns.items()
            },
            'status': 'integrated' if all(v > 0 for v in integration_patterns.values()) else 'partial'
        }
    
    async def _generate_recommendations(self, results: Dict[str, Any]) -> List[Dict[str, str]]:
        """Generate recommendations based on analysis results."""
        recommendations = []
        
        # Ecosystem health recommendations
        health = results.get('ecosystem_health', {})
        if health.get('average_compliance_score', 0) < 70:
            recommendations.append({
                'type': 'compliance',
                'priority': 'high',
                'message': 'Average Triune compliance score is below 70%. Consider updating repositories to follow Triune standards.'
            })
        
        # Integration recommendations
        integration = results.get('integration_status', {})
        coverage = integration.get('integration_coverage', {})
        
        if coverage.get('shadowscrolls_integration', 0) < 50:
            recommendations.append({
                'type': 'integration',
                'priority': 'medium',
                'message': 'Less than 50% of repositories have ShadowScrolls integration. Consider adding ShadowScrolls support.'
            })
        
        if coverage.get('automation_integration', 0) < 80:
            recommendations.append({
                'type': 'automation',
                'priority': 'medium', 
                'message': 'Less than 80% of repositories have automation workflows. Consider adding GitHub Actions.'
            })
        
        # Repository-specific recommendations
        for repo, data in results.get('repositories', {}).items():
            if data.get('status') == 'success':
                compliance = data.get('triune_compliance', {})
                if compliance.get('score', 0) < 60:
                    recommendations.append({
                        'type': 'repository',
                        'priority': 'medium',
                        'message': f'Repository {repo} has low Triune compliance score. Review structure and documentation.'
                    })
        
        return recommendations