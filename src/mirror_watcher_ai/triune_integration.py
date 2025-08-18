"""
TriuneIntegrator - Integration with Triune ecosystem components.
Provides seamless connectivity with Legio-Cognito, Triumvirate Monitor, and Swarm Engine.
"""

import asyncio
import aiohttp
import json
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
import os
from pathlib import Path

logger = logging.getLogger(__name__)


class TriuneIntegrator:
    """Integration manager for Triune ecosystem services."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.legio_cognito_enabled = config.get('legio_cognito', True)
        self.triumvirate_monitor_enabled = config.get('triumvirate_monitor', True)
        self.auto_archive_enabled = config.get('auto_archive', True)
        self.session = None
        
        # Load endpoint configuration
        self.endpoints = self._load_endpoints()
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def sync_results(self, analysis_results: Dict[str, Any], attestation_result: Dict[str, Any]) -> Dict[str, Any]:
        """Synchronize analysis results with all Triune ecosystem services."""
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            sync_tasks = []
            
            # Legio-Cognito scroll archival
            if self.legio_cognito_enabled:
                task = asyncio.create_task(
                    self._sync_legio_cognito(analysis_results, attestation_result)
                )
                sync_tasks.append(('legio_cognito', task))
            
            # Triumvirate Monitor dashboard sync
            if self.triumvirate_monitor_enabled:
                task = asyncio.create_task(
                    self._sync_triumvirate_monitor(analysis_results, attestation_result)
                )
                sync_tasks.append(('triumvirate_monitor', task))
            
            # Swarm Engine integration
            task = asyncio.create_task(
                self._sync_swarm_engine(analysis_results, attestation_result)
            )
            sync_tasks.append(('swarm_engine', task))
            
            # Execute all sync tasks
            sync_results = {}
            for service_name, task in sync_tasks:
                try:
                    result = await task
                    sync_results[service_name] = result
                except Exception as e:
                    logger.error(f"Sync failed for {service_name}: {str(e)}")
                    sync_results[service_name] = {
                        'status': 'failed',
                        'error': str(e)
                    }
            
            # Compile integration results
            integration_summary = {
                'sync_timestamp': datetime.now(timezone.utc).isoformat(),
                'services_synced': len([r for r in sync_results.values() if r.get('status') == 'success']),
                'services_failed': len([r for r in sync_results.values() if r.get('status') == 'failed']),
                'service_results': sync_results,
                'integration_status': 'completed'
            }
            
            logger.info(f"Triune ecosystem sync completed: {integration_summary['services_synced']} successful, {integration_summary['services_failed']} failed")
            
            return integration_summary
            
        except Exception as e:
            logger.error(f"Triune ecosystem sync failed: {str(e)}")
            return {
                'integration_status': 'failed',
                'error': str(e),
                'sync_timestamp': datetime.now(timezone.utc).isoformat()
            }
    
    async def _sync_legio_cognito(self, analysis_results: Dict[str, Any], attestation_result: Dict[str, Any]) -> Dict[str, Any]:
        """Sync analysis results with Legio-Cognito scroll archival system."""
        try:
            endpoint = self.endpoints.get('legio_cognito')
            if not endpoint:
                logger.warning("Legio-Cognito endpoint not configured")
                return self._create_mock_sync_result('legio_cognito', 'not_configured')
            
            # Prepare scroll data for archival
            scroll_data = {
                'scroll_type': 'mirror_watcher_analysis',
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'analysis_summary': self._create_scroll_summary(analysis_results),
                'attestation_reference': {
                    'attestation_id': attestation_result.get('attestation_id'),
                    'witness_hash': attestation_result.get('witness_hash'),
                    'submission_hash': attestation_result.get('submission_hash')
                },
                'metadata': {
                    'repositories_analyzed': len(analysis_results.get('repositories', {})),
                    'quality_metrics': analysis_results.get('metrics', {}),
                    'analysis_duration': analysis_results.get('execution_time', 0)
                }
            }
            
            # Submit to Legio-Cognito
            headers = self._get_auth_headers('legio_cognito')
            
            async with self.session.post(
                f'{endpoint}/scrolls/archive',
                json=scroll_data,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                
                if response.status in [200, 201]:
                    result = await response.json()
                    return {
                        'status': 'success',
                        'scroll_id': result.get('scroll_id'),
                        'archive_url': result.get('archive_url'),
                        'timestamp': datetime.now(timezone.utc).isoformat()
                    }
                else:
                    error_text = await response.text()
                    return {
                        'status': 'failed',
                        'error': f'HTTP {response.status}: {error_text}'
                    }
        
        except asyncio.TimeoutError:
            return {
                'status': 'timeout',
                'error': 'Request timeout after 30 seconds'
            }
        except Exception as e:
            logger.error(f"Legio-Cognito sync error: {str(e)}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    async def _sync_triumvirate_monitor(self, analysis_results: Dict[str, Any], attestation_result: Dict[str, Any]) -> Dict[str, Any]:
        """Sync analysis results with Triumvirate Monitor mobile dashboard."""
        try:
            endpoint = self.endpoints.get('triumvirate_monitor')
            if not endpoint:
                logger.warning("Triumvirate Monitor endpoint not configured")
                return self._create_mock_sync_result('triumvirate_monitor', 'not_configured')
            
            # Prepare dashboard update data
            dashboard_data = {
                'update_type': 'mirror_watcher_analysis',
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'status': {
                    'analysis_completed': True,
                    'repositories_analyzed': len(analysis_results.get('repositories', {})),
                    'success_rate': self._calculate_success_rate(analysis_results),
                    'overall_quality_score': analysis_results.get('metrics', {}).get('average_quality_score', 0)
                },
                'metrics': {
                    'execution_time': analysis_results.get('execution_time', 0),
                    'successful_analyses': analysis_results.get('summary', {}).get('successful_analyses', 0),
                    'failed_analyses': analysis_results.get('summary', {}).get('failed_analyses', 0)
                },
                'attestation': {
                    'verified': attestation_result.get('status') == 'success',
                    'attestation_id': attestation_result.get('attestation_id'),
                    'verification_url': attestation_result.get('verification_url')
                },
                'next_scheduled_run': self._calculate_next_run_time()
            }
            
            # Submit to Triumvirate Monitor
            headers = self._get_auth_headers('triumvirate_monitor')
            
            async with self.session.post(
                f'{endpoint}/dashboard/update',
                json=dashboard_data,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=20)
            ) as response:
                
                if response.status in [200, 201]:
                    result = await response.json()
                    return {
                        'status': 'success',
                        'update_id': result.get('update_id'),
                        'dashboard_url': result.get('dashboard_url'),
                        'timestamp': datetime.now(timezone.utc).isoformat()
                    }
                else:
                    error_text = await response.text()
                    return {
                        'status': 'failed',
                        'error': f'HTTP {response.status}: {error_text}'
                    }
        
        except asyncio.TimeoutError:
            return {
                'status': 'timeout',
                'error': 'Request timeout after 20 seconds'
            }
        except Exception as e:
            logger.error(f"Triumvirate Monitor sync error: {str(e)}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    async def _sync_swarm_engine(self, analysis_results: Dict[str, Any], attestation_result: Dict[str, Any]) -> Dict[str, Any]:
        """Sync analysis results with local Swarm Engine infrastructure."""
        try:
            # Local file-based integration for swarm engine
            swarm_data_dir = Path('./swarm_data')
            swarm_data_dir.mkdir(exist_ok=True)
            
            # Create integration payload
            integration_payload = {
                'source': 'mirror_watcher_ai',
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'analysis_results': analysis_results,
                'attestation_result': attestation_result,
                'integration_metadata': {
                    'version': '1.0.0',
                    'repositories_count': len(analysis_results.get('repositories', {})),
                    'analysis_quality_score': analysis_results.get('metrics', {}).get('average_quality_score', 0)
                }
            }
            
            # Save to swarm engine data file
            timestamp = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
            output_file = swarm_data_dir / f'mirror_analysis_{timestamp}.json'
            
            with open(output_file, 'w') as f:
                json.dump(integration_payload, f, indent=2, default=str)
            
            # Update latest results link
            latest_link = swarm_data_dir / 'latest_mirror_analysis.json'
            if latest_link.exists():
                latest_link.unlink()
            latest_link.symlink_to(output_file.name)
            
            # Update swarm memory log if it exists
            await self._update_swarm_memory_log(analysis_results, attestation_result)
            
            return {
                'status': 'success',
                'output_file': str(output_file),
                'integration_type': 'file_based',
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Swarm Engine sync error: {str(e)}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    async def _update_swarm_memory_log(self, analysis_results: Dict[str, Any], attestation_result: Dict[str, Any]) -> None:
        """Update swarm memory log with analysis results."""
        try:
            memory_log_file = Path('./swarm_memory_log.json')
            
            # Load existing memory log or create new one
            if memory_log_file.exists():
                with open(memory_log_file, 'r') as f:
                    memory_log = json.load(f)
            else:
                memory_log = {
                    'initialized': datetime.now(timezone.utc).isoformat(),
                    'entries': []
                }
            
            # Add new memory entry
            memory_entry = {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'type': 'mirror_watcher_analysis',
                'summary': {
                    'repositories_analyzed': len(analysis_results.get('repositories', {})),
                    'successful_analyses': analysis_results.get('summary', {}).get('successful_analyses', 0),
                    'average_quality_score': analysis_results.get('metrics', {}).get('average_quality_score', 0),
                    'attestation_verified': attestation_result.get('status') == 'success'
                },
                'attestation_id': attestation_result.get('attestation_id')
            }
            
            memory_log['entries'].append(memory_entry)
            memory_log['last_updated'] = datetime.now(timezone.utc).isoformat()
            
            # Keep only last 100 entries
            if len(memory_log['entries']) > 100:
                memory_log['entries'] = memory_log['entries'][-100:]
            
            # Save updated memory log
            with open(memory_log_file, 'w') as f:
                json.dump(memory_log, f, indent=2, default=str)
            
        except Exception as e:
            logger.error(f"Failed to update swarm memory log: {str(e)}")
    
    def _load_endpoints(self) -> Dict[str, str]:
        """Load endpoint configuration."""
        try:
            # Try to load from configuration file
            config_file = Path('./config/triune_endpoints.json')
            if config_file.exists():
                with open(config_file, 'r') as f:
                    return json.load(f)
            
            # Fall back to environment variables
            return {
                'legio_cognito': os.environ.get('LEGIO_COGNITO_ENDPOINT'),
                'triumvirate_monitor': os.environ.get('TRIUMVIRATE_MONITOR_ENDPOINT'),
                'swarm_engine': os.environ.get('SWARM_ENGINE_ENDPOINT', 'local')
            }
        
        except Exception as e:
            logger.error(f"Failed to load endpoints configuration: {str(e)}")
            return {}
    
    def _get_auth_headers(self, service: str) -> Dict[str, str]:
        """Get authentication headers for a service."""
        headers = {'Content-Type': 'application/json'}
        
        # Add service-specific authentication
        if service == 'legio_cognito':
            api_key = os.environ.get('LEGIO_COGNITO_API_KEY')
            if api_key:
                headers['Authorization'] = f'Bearer {api_key}'
        
        elif service == 'triumvirate_monitor':
            api_key = os.environ.get('TRIUMVIRATE_MONITOR_API_KEY')
            if api_key:
                headers['Authorization'] = f'Bearer {api_key}'
        
        return headers
    
    def _create_scroll_summary(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Create summary for Legio-Cognito scroll archival."""
        try:
            repositories = analysis_results.get('repositories', {})
            
            # Extract key insights
            top_quality_repos = []
            issues_found = []
            
            for repo_name, repo_data in repositories.items():
                if repo_data.get('status') == 'completed':
                    quality_score = repo_data.get('quality_score', 0)
                    if quality_score >= 8.0:
                        top_quality_repos.append({
                            'repository': repo_name,
                            'quality_score': quality_score,
                            'language': repo_data.get('info', {}).get('language')
                        })
                    
                    # Check for security issues
                    security_data = repo_data.get('security', {})
                    potential_issues = security_data.get('potential_issues', [])
                    if potential_issues:
                        issues_found.extend(potential_issues)
            
            return {
                'analysis_overview': {
                    'total_repositories': len(repositories),
                    'successful_analyses': len([r for r in repositories.values() if r.get('status') == 'completed']),
                    'average_quality_score': analysis_results.get('metrics', {}).get('average_quality_score', 0)
                },
                'insights': {
                    'high_quality_repositories': top_quality_repos[:5],  # Top 5
                    'security_issues_count': len(issues_found),
                    'language_distribution': analysis_results.get('metrics', {}).get('language_distribution', {})
                },
                'recommendations': self._generate_ecosystem_recommendations(analysis_results)
            }
        
        except Exception as e:
            logger.error(f"Failed to create scroll summary: {str(e)}")
            return {'error': str(e)}
    
    def _calculate_success_rate(self, analysis_results: Dict[str, Any]) -> float:
        """Calculate analysis success rate."""
        try:
            summary = analysis_results.get('summary', {})
            total = summary.get('total_repositories', 0)
            successful = summary.get('successful_analyses', 0)
            
            if total > 0:
                return round((successful / total) * 100, 2)
            return 0.0
        
        except Exception:
            return 0.0
    
    def _calculate_next_run_time(self) -> str:
        """Calculate next scheduled run time (06:00 UTC)."""
        try:
            now = datetime.now(timezone.utc)
            
            # Calculate next 06:00 UTC
            next_run = now.replace(hour=6, minute=0, second=0, microsecond=0)
            
            # If we've already passed 06:00 today, schedule for tomorrow
            if now.hour >= 6:
                from datetime import timedelta
                next_run += timedelta(days=1)
            
            return next_run.isoformat()
        
        except Exception:
            return datetime.now(timezone.utc).isoformat()
    
    def _generate_ecosystem_recommendations(self, analysis_results: Dict[str, Any]) -> List[str]:
        """Generate recommendations for the Triune ecosystem."""
        recommendations = []
        
        try:
            metrics = analysis_results.get('metrics', {})
            avg_quality = metrics.get('average_quality_score', 0)
            
            if avg_quality < 7.0:
                recommendations.append("Consider implementing automated code quality checks across repositories")
            
            language_dist = metrics.get('language_distribution', {})
            if 'Python' in language_dist and language_dist['Python'].get('percentage', 0) > 70:
                recommendations.append("Leverage Python ecosystem tools for enhanced automation")
            
            repositories = analysis_results.get('repositories', {})
            security_issues = sum(
                len(repo.get('security', {}).get('potential_issues', []))
                for repo in repositories.values()
                if repo.get('status') == 'completed'
            )
            
            if security_issues > 0:
                recommendations.append("Implement automated security scanning in CI/CD pipelines")
            
            recommendations.append("Continue automated daily monitoring for ecosystem health")
            
        except Exception as e:
            logger.error(f"Failed to generate recommendations: {str(e)}")
            recommendations.append("Review analysis results for improvement opportunities")
        
        return recommendations
    
    def _create_mock_sync_result(self, service: str, reason: str) -> Dict[str, Any]:
        """Create mock sync result when service is not available."""
        return {
            'status': 'mock',
            'service': service,
            'reason': reason,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'note': f'Mock result generated - {service} {reason}'
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Check health of all Triune ecosystem services."""
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            health_results = {}
            
            # Check each service
            for service, endpoint in self.endpoints.items():
                if not endpoint or endpoint == 'local':
                    health_results[service] = {
                        'status': 'local' if endpoint == 'local' else 'not_configured',
                        'endpoint': endpoint
                    }
                    continue
                
                try:
                    async with self.session.get(
                        f'{endpoint}/health',
                        timeout=aiohttp.ClientTimeout(total=10)
                    ) as response:
                        
                        health_results[service] = {
                            'status': 'healthy' if response.status == 200 else 'unhealthy',
                            'endpoint': endpoint,
                            'http_status': response.status,
                            'response_time': response.headers.get('X-Response-Time')
                        }
                
                except Exception as e:
                    health_results[service] = {
                        'status': 'error',
                        'endpoint': endpoint,
                        'error': str(e)
                    }
            
            return {
                'overall_status': 'healthy' if all(
                    r.get('status') in ['healthy', 'local'] 
                    for r in health_results.values()
                ) else 'degraded',
                'services': health_results,
                'check_timestamp': datetime.now(timezone.utc).isoformat()
            }
        
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return {
                'overall_status': 'error',
                'error': str(e),
                'check_timestamp': datetime.now(timezone.utc).isoformat()
            }