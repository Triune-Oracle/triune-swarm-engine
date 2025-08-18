"""
Triune Monitor Integration Module

Provides integration with TtriumvirateMonitor-Mobile for real-time
status updates and mobile monitoring of MirrorWatcherAI operations.
"""

import asyncio
import json
import logging
import os
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
import aiohttp


class TriuneMonitor:
    """Integration with TtriumvirateMonitor-Mobile for status monitoring."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.monitor_endpoint = os.getenv('TRIUNE_MONITOR_ENDPOINT', 'https://api.triune-monitor.com/v1')
        self.monitor_api_key = os.getenv('TRIUNE_MONITOR_API_KEY')
        self.monitor_enabled = bool(self.monitor_api_key)
        
        # Status tracking
        self.status_file = '.triune_monitor/status.json'
        self._ensure_status_directory()
        
    def _ensure_status_directory(self):
        """Ensure status directory exists."""
        os.makedirs('.triune_monitor', exist_ok=True)
    
    async def update_status(self, analysis_results: Dict[str, Any], archive_result: Dict[str, Any]) -> Dict[str, Any]:
        """Update status in Triune Monitor system."""
        self.logger.info("Updating Triune Monitor status...")
        
        try:
            # Create status update
            status_update = await self._create_status_update(analysis_results, archive_result)
            
            # Send to monitor if enabled
            if self.monitor_enabled:
                monitor_result = await self._send_to_monitor(status_update)
            else:
                monitor_result = await self._store_status_locally(status_update)
            
            # Update local status
            await self._update_local_status(status_update, monitor_result)
            
            self.logger.info("Triune Monitor status updated successfully")
            return monitor_result
            
        except Exception as e:
            self.logger.error(f"Failed to update Triune Monitor status: {e}")
            return {
                'status': 'failed',
                'error': str(e),
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
    
    async def _create_status_update(self, analysis_results: Dict[str, Any], archive_result: Dict[str, Any]) -> Dict[str, Any]:
        """Create comprehensive status update for Triune Monitor."""
        timestamp = datetime.now(timezone.utc)
        
        # Calculate overall health score
        ecosystem_health = analysis_results.get('ecosystem_health', {})
        health_score = ecosystem_health.get('average_compliance_score', 0)
        
        # Determine status level
        status_level = self._determine_status_level(health_score, analysis_results)
        
        # Create status update
        status_update = {
            'system': 'MirrorWatcherAI',
            'timestamp': timestamp.isoformat(),
            'status': {
                'level': status_level,
                'health_score': health_score,
                'ecosystem_status': ecosystem_health.get('ecosystem_status', 'unknown'),
                'message': self._create_status_message(analysis_results, health_score)
            },
            'metrics': {
                'repositories_analyzed': len(analysis_results.get('repositories', {})),
                'successful_analyses': sum(
                    1 for r in analysis_results.get('repositories', {}).values() 
                    if r.get('status') == 'success'
                ),
                'failed_analyses': sum(
                    1 for r in analysis_results.get('repositories', {}).values() 
                    if r.get('status') != 'success'
                ),
                'recommendations_count': len(analysis_results.get('recommendations', [])),
                'critical_recommendations': len([
                    r for r in analysis_results.get('recommendations', [])
                    if r.get('priority') == 'high'
                ]),
                'analysis_success_rate': ecosystem_health.get('analysis_success_rate', 0),
                'active_repositories': ecosystem_health.get('active_repositories', 0)
            },
            'integration_status': {
                'shadowscrolls': self._check_shadowscrolls_status(analysis_results),
                'legio_cognito': self._check_legio_status(archive_result),
                'automation': self._check_automation_status(analysis_results)
            },
            'alerts': await self._generate_alerts(analysis_results),
            'next_execution': self._calculate_next_execution(),
            'dashboard_data': await self._create_dashboard_data(analysis_results)
        }
        
        return status_update
    
    def _determine_status_level(self, health_score: float, analysis_results: Dict[str, Any]) -> str:
        """Determine overall status level."""
        recommendations = analysis_results.get('recommendations', [])
        critical_recommendations = [r for r in recommendations if r.get('priority') == 'high']
        
        if health_score < 50 or len(critical_recommendations) > 2:
            return 'critical'
        elif health_score < 70 or len(critical_recommendations) > 0:
            return 'warning'
        elif health_score < 90:
            return 'info'
        else:
            return 'success'
    
    def _create_status_message(self, analysis_results: Dict[str, Any], health_score: float) -> str:
        """Create human-readable status message."""
        repos_count = len(analysis_results.get('repositories', {}))
        recommendations_count = len(analysis_results.get('recommendations', []))
        
        if health_score >= 90:
            return f"✅ Ecosystem healthy - {repos_count} repositories analyzed, compliance at {health_score:.1f}%"
        elif health_score >= 70:
            return f"⚠️ Ecosystem stable - {repos_count} repositories, {recommendations_count} recommendations"
        elif health_score >= 50:
            return f"🔶 Ecosystem needs attention - {health_score:.1f}% compliance, {recommendations_count} recommendations"
        else:
            return f"🚨 Ecosystem critical - {health_score:.1f}% compliance, immediate action required"
    
    def _check_shadowscrolls_status(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Check ShadowScrolls integration status."""
        # This would check if ShadowScrolls attestation was successful
        return {
            'enabled': True,
            'status': 'operational',
            'last_attestation': analysis_results.get('timestamp')
        }
    
    def _check_legio_status(self, archive_result: Dict[str, Any]) -> Dict[str, Any]:
        """Check Legio-Cognito integration status."""
        status = archive_result.get('status', 'unknown')
        
        return {
            'enabled': status != 'failed',
            'status': 'operational' if status == 'archived' else 'degraded',
            'last_archive': archive_result.get('timestamp')
        }
    
    def _check_automation_status(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Check automation status across repositories."""
        repos = analysis_results.get('repositories', {})
        automated_count = sum(
            1 for r in repos.values() 
            if r.get('status') == 'success' and r.get('workflows', 0) > 0
        )
        
        automation_coverage = (automated_count / len(repos) * 100) if repos else 0
        
        return {
            'coverage': automation_coverage,
            'status': 'good' if automation_coverage >= 80 else 'needs_improvement',
            'automated_repositories': automated_count,
            'total_repositories': len(repos)
        }
    
    async def _generate_alerts(self, analysis_results: Dict[str, Any]) -> List[Dict[str, str]]:
        """Generate alerts for Triune Monitor."""
        alerts = []
        
        # Health-based alerts
        ecosystem_health = analysis_results.get('ecosystem_health', {})
        health_score = ecosystem_health.get('average_compliance_score', 0)
        
        if health_score < 50:
            alerts.append({
                'type': 'critical',
                'message': f'Ecosystem health critical: {health_score:.1f}% compliance',
                'action': 'Immediate review required'
            })
        elif health_score < 70:
            alerts.append({
                'type': 'warning', 
                'message': f'Ecosystem health degraded: {health_score:.1f}% compliance',
                'action': 'Review recommendations'
            })
        
        # Repository-specific alerts
        repos = analysis_results.get('repositories', {})
        failed_repos = [name for name, data in repos.items() if data.get('status') != 'success']
        
        if failed_repos:
            alerts.append({
                'type': 'warning',
                'message': f'{len(failed_repos)} repositories failed analysis',
                'action': f'Check: {", ".join(failed_repos[:3])}{"..." if len(failed_repos) > 3 else ""}'
            })
        
        # Recommendation-based alerts
        recommendations = analysis_results.get('recommendations', [])
        high_priority = [r for r in recommendations if r.get('priority') == 'high']
        
        if high_priority:
            alerts.append({
                'type': 'warning',
                'message': f'{len(high_priority)} high-priority recommendations',
                'action': 'Review and implement recommendations'
            })
        
        return alerts
    
    def _calculate_next_execution(self) -> str:
        """Calculate next scheduled execution time."""
        # MirrorWatcherAI runs daily at 06:00 UTC
        now = datetime.now(timezone.utc)
        next_run = now.replace(hour=6, minute=0, second=0, microsecond=0)
        
        # If we've passed today's 06:00, schedule for tomorrow
        if now >= next_run:
            next_run = next_run.replace(day=next_run.day + 1)
        
        return next_run.isoformat()
    
    async def _create_dashboard_data(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Create data for mobile dashboard display."""
        repos = analysis_results.get('repositories', {})
        ecosystem_health = analysis_results.get('ecosystem_health', {})
        
        # Repository summary
        repo_summary = []
        for name, data in repos.items():
            if data.get('status') == 'success':
                repo_summary.append({
                    'name': name.split('/')[-1],  # Just repo name without org
                    'language': data.get('language'),
                    'stars': data.get('stars', 0),
                    'compliance_score': data.get('triune_compliance', {}).get('score', 0),
                    'last_updated': data.get('updated_at')
                })
        
        # Sort by compliance score (descending)
        repo_summary.sort(key=lambda x: x['compliance_score'], reverse=True)
        
        # Language distribution
        language_counts = {}
        for data in repos.values():
            if data.get('status') == 'success':
                languages = data.get('languages', {})
                for lang, count in languages.items():
                    language_counts[lang] = language_counts.get(lang, 0) + count
        
        # Top languages
        top_languages = sorted(language_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            'ecosystem_overview': {
                'total_repositories': len(repos),
                'health_score': ecosystem_health.get('average_compliance_score', 0),
                'active_repositories': ecosystem_health.get('active_repositories', 0),
                'status': ecosystem_health.get('ecosystem_status', 'unknown')
            },
            'repository_summary': repo_summary[:10],  # Top 10 repositories
            'language_distribution': [{'language': lang, 'usage': count} for lang, count in top_languages],
            'recent_recommendations': analysis_results.get('recommendations', [])[:5],
            'trends': await self._calculate_trends(analysis_results)
        }
    
    async def _calculate_trends(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate trends for dashboard."""
        # This would compare with historical data
        # For now, return basic trend indicators
        
        return {
            'health_trend': 'stable',  # Would be calculated from historical data
            'repository_growth': 'stable',
            'automation_trend': 'improving',
            'compliance_trend': 'stable'
        }
    
    async def _send_to_monitor(self, status_update: Dict[str, Any]) -> Dict[str, Any]:
        """Send status update to Triune Monitor service."""
        try:
            headers = {
                'Authorization': f'Bearer {self.monitor_api_key}',
                'Content-Type': 'application/json',
                'X-Monitor-Source': 'MirrorWatcherAI'
            }
            
            update_url = f"{self.monitor_endpoint.rstrip('/')}/status/mirror-watcher"
            
            async with aiohttp.ClientSession() as session:
                async with session.post(update_url, json=status_update, headers=headers, timeout=30) as resp:
                    if resp.status in [200, 201]:
                        result = await resp.json()
                        self.logger.info("Successfully sent status to Triune Monitor")
                        return {
                            'status': 'sent',
                            'monitor_response': result,
                            'timestamp': datetime.now(timezone.utc).isoformat()
                        }
                    else:
                        error_text = await resp.text()
                        self.logger.warning(f"Triune Monitor update failed: {resp.status} - {error_text}")
                        
                        # Store locally as fallback
                        local_result = await self._store_status_locally(status_update)
                        return {
                            'status': 'failed_stored_locally',
                            'error': f"HTTP {resp.status}: {error_text}",
                            'local_storage': local_result,
                            'timestamp': datetime.now(timezone.utc).isoformat()
                        }
        
        except asyncio.TimeoutError:
            self.logger.warning("Triune Monitor update timeout, storing locally")
            local_result = await self._store_status_locally(status_update)
            return {
                'status': 'timeout_stored_locally',
                'error': 'Update timed out after 30 seconds',
                'local_storage': local_result,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            self.logger.error(f"Triune Monitor update error: {e}")
            local_result = await self._store_status_locally(status_update)
            return {
                'status': 'error_stored_locally',
                'error': str(e),
                'local_storage': local_result,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
    
    async def _store_status_locally(self, status_update: Dict[str, Any]) -> Dict[str, Any]:
        """Store status update locally as fallback."""
        try:
            timestamp = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
            filename = f"status_update_{timestamp}.json"
            filepath = os.path.join('.triune_monitor', filename)
            
            with open(filepath, 'w') as f:
                json.dump(status_update, f, indent=2, default=str)
            
            self.logger.info(f"Status update stored locally: {filepath}")
            return {
                'status': 'stored_locally',
                'filepath': filepath,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Local status storage failed: {e}")
            return {
                'status': 'failed',
                'error': str(e),
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
    
    async def _update_local_status(self, status_update: Dict[str, Any], monitor_result: Dict[str, Any]) -> None:
        """Update local status file."""
        try:
            current_status = {
                'last_update': datetime.now(timezone.utc).isoformat(),
                'status': status_update['status'],
                'metrics': status_update['metrics'],
                'integration_status': status_update['integration_status'],
                'alerts': status_update['alerts'],
                'next_execution': status_update['next_execution'],
                'monitor_result': monitor_result
            }
            
            with open(self.status_file, 'w') as f:
                json.dump(current_status, f, indent=2, default=str)
                
        except Exception as e:
            self.logger.error(f"Failed to update local status: {e}")
    
    async def get_current_status(self) -> Optional[Dict[str, Any]]:
        """Get current status from local storage."""
        try:
            if os.path.exists(self.status_file):
                with open(self.status_file, 'r') as f:
                    return json.load(f)
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to get current status: {e}")
            return None
    
    async def send_alert(self, alert_type: str, message: str, priority: str = 'medium') -> Dict[str, Any]:
        """Send immediate alert to Triune Monitor."""
        try:
            alert_data = {
                'system': 'MirrorWatcherAI',
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'alert': {
                    'type': alert_type,
                    'priority': priority,
                    'message': message
                }
            }
            
            if self.monitor_enabled:
                headers = {
                    'Authorization': f'Bearer {self.monitor_api_key}',
                    'Content-Type': 'application/json'
                }
                
                alert_url = f"{self.monitor_endpoint.rstrip('/')}/alerts"
                
                async with aiohttp.ClientSession() as session:
                    async with session.post(alert_url, json=alert_data, headers=headers, timeout=10) as resp:
                        if resp.status in [200, 201]:
                            result = await resp.json()
                            return {
                                'status': 'sent',
                                'response': result
                            }
                        else:
                            return {
                                'status': 'failed',
                                'error': f"HTTP {resp.status}"
                            }
            else:
                # Store alert locally
                alert_file = f".triune_monitor/alert_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
                with open(alert_file, 'w') as f:
                    json.dump(alert_data, f, indent=2, default=str)
                
                return {
                    'status': 'stored_locally',
                    'filepath': alert_file
                }
                
        except Exception as e:
            self.logger.error(f"Failed to send alert: {e}")
            return {
                'status': 'failed',
                'error': str(e)
            }