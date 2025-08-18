#!/usr/bin/env python3
"""
Triune Sync - Ecosystem synchronization script
Synchronizes data between MirrorWatcherAI and Triune ecosystem services
"""

import asyncio
import aiohttp
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List
import os
import argparse

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class TriuneSync:
    """Synchronization manager for Triune ecosystem services."""
    
    def __init__(self, config_path: str = './config/triune_endpoints.json'):
        self.config_path = Path(config_path)
        self.session = None
        self.endpoints = self.load_endpoints()
        
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    def load_endpoints(self) -> Dict[str, str]:
        """Load endpoint configuration."""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r') as f:
                    data = json.load(f)
                    return {
                        'legio_cognito': data.get('legio_cognito'),
                        'triumvirate_monitor': data.get('triumvirate_monitor'),
                        'shadowscrolls': data.get('shadowscrolls'),
                        'swarm_engine': data.get('swarm_engine', 'local')
                    }
            else:
                logger.warning(f"Endpoints config not found: {self.config_path}")
                return {}
        except Exception as e:
            logger.error(f"Failed to load endpoints: {str(e)}")
            return {}
    
    async def sync_latest_analysis(self) -> Dict[str, Any]:
        """Sync the latest analysis results with all services."""
        try:
            # Find latest analysis results
            results_dir = Path('./results')
            if not results_dir.exists():
                return {'error': 'Results directory not found'}
            
            # Find the most recent analysis file
            analysis_files = list(results_dir.glob('mirror_analysis_*.json'))
            if not analysis_files:
                return {'error': 'No analysis results found'}
            
            latest_file = max(analysis_files, key=lambda x: x.stat().st_mtime)
            
            # Load analysis results
            with open(latest_file, 'r') as f:
                analysis_results = json.load(f)
            
            logger.info(f"Syncing analysis from: {latest_file.name}")
            
            # Sync with each service
            sync_results = {}
            
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            # Sync with Legio-Cognito
            if self.endpoints.get('legio_cognito'):
                sync_results['legio_cognito'] = await self.sync_legio_cognito(analysis_results)
            
            # Sync with Triumvirate Monitor
            if self.endpoints.get('triumvirate_monitor'):
                sync_results['triumvirate_monitor'] = await self.sync_triumvirate_monitor(analysis_results)
            
            # Sync with ShadowScrolls
            if self.endpoints.get('shadowscrolls'):
                sync_results['shadowscrolls'] = await self.sync_shadowscrolls(analysis_results)
            
            # Always sync with local swarm engine
            sync_results['swarm_engine'] = await self.sync_swarm_engine(analysis_results)
            
            return {
                'status': 'completed',
                'analysis_file': latest_file.name,
                'sync_timestamp': datetime.now(timezone.utc).isoformat(),
                'services': sync_results
            }
            
        except Exception as e:
            logger.error(f"Sync failed: {str(e)}")
            return {
                'status': 'failed',
                'error': str(e),
                'sync_timestamp': datetime.now(timezone.utc).isoformat()
            }
    
    async def sync_legio_cognito(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Sync with Legio-Cognito scroll archival."""
        try:
            endpoint = self.endpoints.get('legio_cognito')
            
            # Create scroll summary
            scroll_data = {
                'type': 'mirror_watcher_sync',
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'analysis_summary': self.create_analysis_summary(analysis_results),
                'source': 'triune_sync_script'
            }
            
            headers = self.get_auth_headers('legio_cognito')
            
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
                        'response': result
                    }
                else:
                    error_text = await response.text()
                    return {
                        'status': 'failed',
                        'error': f'HTTP {response.status}: {error_text}'
                    }
        
        except Exception as e:
            logger.error(f"Legio-Cognito sync failed: {str(e)}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    async def sync_triumvirate_monitor(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Sync with Triumvirate Monitor dashboard."""
        try:
            endpoint = self.endpoints.get('triumvirate_monitor')
            
            # Create dashboard update
            dashboard_data = {
                'update_type': 'manual_sync',
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'analysis_summary': self.create_analysis_summary(analysis_results),
                'status': {
                    'last_sync': datetime.now(timezone.utc).isoformat(),
                    'sync_source': 'triune_sync_script'
                }
            }
            
            headers = self.get_auth_headers('triumvirate_monitor')
            
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
                        'response': result
                    }
                else:
                    error_text = await response.text()
                    return {
                        'status': 'failed',
                        'error': f'HTTP {response.status}: {error_text}'
                    }
        
        except Exception as e:
            logger.error(f"Triumvirate Monitor sync failed: {str(e)}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    async def sync_shadowscrolls(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Sync with ShadowScrolls attestation service."""
        try:
            endpoint = self.endpoints.get('shadowscrolls')
            
            # Create attestation data
            attestation_data = {
                'type': 'manual_sync_attestation',
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'analysis_hash': self.calculate_analysis_hash(analysis_results),
                'sync_metadata': {
                    'source': 'triune_sync_script',
                    'repositories_count': len(analysis_results.get('repositories', {})),
                    'analysis_timestamp': analysis_results.get('analysis', {}).get('timestamp')
                }
            }
            
            headers = self.get_auth_headers('shadowscrolls')
            
            async with self.session.post(
                f'{endpoint}/attestations',
                json=attestation_data,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                
                if response.status in [200, 201]:
                    result = await response.json()
                    return {
                        'status': 'success',
                        'attestation_id': result.get('id'),
                        'witness_hash': result.get('witness_hash'),
                        'response': result
                    }
                else:
                    error_text = await response.text()
                    return {
                        'status': 'failed',
                        'error': f'HTTP {response.status}: {error_text}'
                    }
        
        except Exception as e:
            logger.error(f"ShadowScrolls sync failed: {str(e)}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    async def sync_swarm_engine(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Sync with local Swarm Engine."""
        try:
            # Create swarm data directory
            swarm_data_dir = Path('./swarm_data')
            swarm_data_dir.mkdir(exist_ok=True)
            
            # Create sync payload
            sync_payload = {
                'sync_type': 'manual_triune_sync',
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'analysis_results': analysis_results,
                'sync_metadata': {
                    'source': 'triune_sync_script',
                    'repositories_analyzed': len(analysis_results.get('repositories', {})),
                    'success_rate': self.calculate_success_rate(analysis_results)
                }
            }
            
            # Save sync data
            timestamp = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
            sync_file = swarm_data_dir / f'manual_sync_{timestamp}.json'
            
            with open(sync_file, 'w') as f:
                json.dump(sync_payload, f, indent=2, default=str)
            
            # Update latest sync link
            latest_sync_link = swarm_data_dir / 'latest_manual_sync.json'
            if latest_sync_link.exists():
                latest_sync_link.unlink()
            latest_sync_link.symlink_to(sync_file.name)
            
            # Update swarm memory if exists
            await self.update_swarm_memory(analysis_results)
            
            return {
                'status': 'success',
                'sync_file': str(sync_file),
                'local_integration': True
            }
            
        except Exception as e:
            logger.error(f"Swarm Engine sync failed: {str(e)}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    async def update_swarm_memory(self, analysis_results: Dict[str, Any]) -> None:
        """Update local swarm memory with sync data."""
        try:
            memory_file = Path('./swarm_memory_log.json')
            
            # Load existing memory
            if memory_file.exists():
                with open(memory_file, 'r') as f:
                    memory_data = json.load(f)
            else:
                memory_data = {
                    'initialized': datetime.now(timezone.utc).isoformat(),
                    'entries': []
                }
            
            # Add sync entry
            sync_entry = {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'type': 'manual_sync',
                'summary': {
                    'repositories_synced': len(analysis_results.get('repositories', {})),
                    'sync_source': 'triune_sync_script',
                    'quality_score': analysis_results.get('metrics', {}).get('average_quality_score', 0)
                }
            }
            
            memory_data['entries'].append(sync_entry)
            memory_data['last_manual_sync'] = datetime.now(timezone.utc).isoformat()
            
            # Keep last 100 entries
            if len(memory_data['entries']) > 100:
                memory_data['entries'] = memory_data['entries'][-100:]
            
            # Save updated memory
            with open(memory_file, 'w') as f:
                json.dump(memory_data, f, indent=2, default=str)
            
        except Exception as e:
            logger.error(f"Failed to update swarm memory: {str(e)}")
    
    def create_analysis_summary(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Create a summary of analysis results for sync."""
        try:
            repositories = analysis_results.get('repositories', {})
            summary = analysis_results.get('summary', {})
            metrics = analysis_results.get('metrics', {})
            
            return {
                'total_repositories': summary.get('total_repositories', 0),
                'successful_analyses': summary.get('successful_analyses', 0),
                'failed_analyses': summary.get('failed_analyses', 0),
                'average_quality_score': metrics.get('average_quality_score', 0),
                'language_distribution': metrics.get('language_distribution', {}),
                'analysis_timestamp': summary.get('analysis_timestamp'),
                'sync_timestamp': datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            logger.error(f"Failed to create analysis summary: {str(e)}")
            return {'error': str(e)}
    
    def calculate_analysis_hash(self, analysis_results: Dict[str, Any]) -> str:
        """Calculate hash of analysis results."""
        try:
            import hashlib
            normalized = json.dumps(analysis_results, sort_keys=True, separators=(',', ':'))
            return hashlib.sha256(normalized.encode('utf-8')).hexdigest()
        except Exception as e:
            logger.error(f"Hash calculation failed: {str(e)}")
            return "hash_error"
    
    def calculate_success_rate(self, analysis_results: Dict[str, Any]) -> float:
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
    
    def get_auth_headers(self, service: str) -> Dict[str, str]:
        """Get authentication headers for a service."""
        headers = {'Content-Type': 'application/json'}
        
        if service == 'legio_cognito':
            api_key = os.environ.get('LEGIO_COGNITO_API_KEY')
            if api_key:
                headers['Authorization'] = f'Bearer {api_key}'
        
        elif service == 'triumvirate_monitor':
            api_key = os.environ.get('TRIUMVIRATE_MONITOR_API_KEY')
            if api_key:
                headers['Authorization'] = f'Bearer {api_key}'
        
        elif service == 'shadowscrolls':
            api_key = os.environ.get('SHADOWSCROLLS_API_KEY')
            if api_key:
                headers['Authorization'] = f'Bearer {api_key}'
        
        return headers
    
    async def health_check(self) -> Dict[str, Any]:
        """Check health of all configured services."""
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            health_results = {}
            
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
                            'http_status': response.status
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


def create_parser() -> argparse.ArgumentParser:
    """Create argument parser."""
    parser = argparse.ArgumentParser(
        description='Triune Sync - Ecosystem synchronization script'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Sync command
    sync_parser = subparsers.add_parser('sync', help='Sync latest analysis results')
    sync_parser.add_argument('--config', default='./config/triune_endpoints.json', help='Endpoints configuration file')
    
    # Health check command
    health_parser = subparsers.add_parser('health', help='Check service health')
    health_parser.add_argument('--config', default='./config/triune_endpoints.json', help='Endpoints configuration file')
    
    return parser


async def main():
    """Main entry point."""
    parser = create_parser()
    args = parser.parse_args()
    
    if args.command is None:
        parser.print_help()
        return
    
    async with TriuneSync(args.config) as sync_manager:
        try:
            if args.command == 'sync':
                print("🔄 Starting Triune ecosystem synchronization...")
                result = await sync_manager.sync_latest_analysis()
                
                if result.get('status') == 'completed':
                    print(f"✅ Synchronization completed successfully")
                    print(f"📄 Analysis file: {result['analysis_file']}")
                    print(f"⏰ Sync time: {result['sync_timestamp']}")
                    print()
                    
                    # Print service results
                    for service, service_result in result['services'].items():
                        status = service_result.get('status', 'unknown')
                        if status == 'success':
                            print(f"✅ {service}: Success")
                        elif status == 'error':
                            print(f"❌ {service}: Error - {service_result.get('error', 'Unknown')}")
                        else:
                            print(f"⚠️  {service}: {status}")
                else:
                    print(f"❌ Synchronization failed: {result.get('error', 'Unknown error')}")
            
            elif args.command == 'health':
                print("🔍 Checking Triune ecosystem service health...")
                result = await sync_manager.health_check()
                
                overall_status = result.get('overall_status', 'unknown')
                if overall_status == 'healthy':
                    print("✅ All services are healthy")
                elif overall_status == 'degraded':
                    print("⚠️  Some services have issues")
                else:
                    print("❌ Service health check failed")
                
                print()
                for service, service_health in result['services'].items():
                    status = service_health.get('status', 'unknown')
                    endpoint = service_health.get('endpoint', 'unknown')
                    
                    if status == 'healthy':
                        print(f"✅ {service}: Healthy ({endpoint})")
                    elif status == 'local':
                        print(f"🏠 {service}: Local integration")
                    elif status == 'not_configured':
                        print(f"⚙️  {service}: Not configured")
                    else:
                        error = service_health.get('error', 'Unknown error')
                        print(f"❌ {service}: {status} - {error}")
        
        except KeyboardInterrupt:
            print("\n⚠️  Operation cancelled by user")
        except Exception as e:
            print(f"❌ Fatal error: {str(e)}")
            logger.error(f"Fatal error in triune sync: {str(e)}")


if __name__ == '__main__':
    asyncio.run(main())