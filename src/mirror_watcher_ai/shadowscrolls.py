"""
ShadowScrolls Client - External attestation and immutable logging integration.
Provides cryptographic verification and external witnessing capabilities.
"""

import asyncio
import aiohttp
import hashlib
import json
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional
import os
import hmac
import base64

logger = logging.getLogger(__name__)


class ShadowScrollsClient:
    """Client for ShadowScrolls external attestation system."""
    
    def __init__(self, endpoint: Optional[str] = None, api_key: Optional[str] = None):
        self.endpoint = endpoint or os.environ.get('SHADOWSCROLLS_ENDPOINT')
        self.api_key = api_key or os.environ.get('SHADOWSCROLLS_API_KEY')
        self.session = None
        
        if not self.endpoint:
            logger.warning("ShadowScrolls endpoint not configured")
        if not self.api_key:
            logger.warning("ShadowScrolls API key not configured")
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def submit_analysis(self, analysis_results: Dict[str, Any], lineage_entry: Dict[str, Any]) -> Dict[str, Any]:
        """Submit analysis results for external attestation."""
        if not self.endpoint or not self.api_key:
            logger.warning("ShadowScrolls not configured, creating mock attestation")
            return self._create_mock_attestation(analysis_results, lineage_entry)
        
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            # Prepare submission payload
            submission = {
                'type': 'mirror_watcher_analysis',
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'analysis_hash': self._calculate_analysis_hash(analysis_results),
                'lineage_hash': lineage_entry.get('hash'),
                'metadata': {
                    'repositories_analyzed': len(analysis_results.get('repositories', {})),
                    'analysis_version': '1.0.0',
                    'submitter': 'MirrorWatcherAI'
                },
                'payload': {
                    'analysis_summary': self._create_analysis_summary(analysis_results),
                    'lineage_entry': lineage_entry
                }
            }
            
            # Sign the submission
            signature = self._sign_submission(submission)
            
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json',
                'X-Signature': signature
            }
            
            # Submit to ShadowScrolls
            async with self.session.post(
                f'{self.endpoint}/attestations',
                json=submission,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                
                if response.status == 200 or response.status == 201:
                    result = await response.json()
                    logger.info("Successfully submitted to ShadowScrolls")
                    
                    return {
                        'status': 'success',
                        'attestation_id': result.get('id'),
                        'witness_hash': result.get('witness_hash'),
                        'timestamp': result.get('timestamp'),
                        'verification_url': result.get('verification_url'),
                        'submission_hash': submission['analysis_hash']
                    }
                else:
                    error_text = await response.text()
                    logger.error(f"ShadowScrolls submission failed: {response.status} - {error_text}")
                    
                    return {
                        'status': 'failed',
                        'error': f'HTTP {response.status}: {error_text}',
                        'submission_hash': submission['analysis_hash']
                    }
        
        except asyncio.TimeoutError:
            logger.error("ShadowScrolls submission timeout")
            return {
                'status': 'timeout',
                'error': 'Request timeout after 30 seconds',
                'submission_hash': self._calculate_analysis_hash(analysis_results)
            }
        
        except Exception as e:
            logger.error(f"ShadowScrolls submission error: {str(e)}")
            return {
                'status': 'error',
                'error': str(e),
                'submission_hash': self._calculate_analysis_hash(analysis_results)
            }
    
    async def verify_attestation(self, attestation_id: str) -> Dict[str, Any]:
        """Verify an existing attestation."""
        if not self.endpoint or not self.api_key:
            logger.warning("ShadowScrolls not configured, cannot verify attestation")
            return {'status': 'not_configured'}
        
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            async with self.session.get(
                f'{self.endpoint}/attestations/{attestation_id}',
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=15)
            ) as response:
                
                if response.status == 200:
                    result = await response.json()
                    logger.info(f"Successfully verified attestation: {attestation_id}")
                    
                    return {
                        'status': 'verified',
                        'attestation': result,
                        'verification_timestamp': datetime.now(timezone.utc).isoformat()
                    }
                elif response.status == 404:
                    return {
                        'status': 'not_found',
                        'error': 'Attestation not found'
                    }
                else:
                    error_text = await response.text()
                    return {
                        'status': 'verification_failed',
                        'error': f'HTTP {response.status}: {error_text}'
                    }
        
        except Exception as e:
            logger.error(f"Attestation verification error: {str(e)}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    async def get_lineage_chain(self, lineage_hash: str) -> Dict[str, Any]:
        """Retrieve lineage chain for a given hash."""
        if not self.endpoint or not self.api_key:
            logger.warning("ShadowScrolls not configured, cannot retrieve lineage")
            return {'status': 'not_configured'}
        
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            async with self.session.get(
                f'{self.endpoint}/lineage/{lineage_hash}',
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=15)
            ) as response:
                
                if response.status == 200:
                    result = await response.json()
                    return {
                        'status': 'success',
                        'lineage_chain': result,
                        'retrieval_timestamp': datetime.now(timezone.utc).isoformat()
                    }
                else:
                    error_text = await response.text()
                    return {
                        'status': 'failed',
                        'error': f'HTTP {response.status}: {error_text}'
                    }
        
        except Exception as e:
            logger.error(f"Lineage retrieval error: {str(e)}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def _calculate_analysis_hash(self, analysis_results: Dict[str, Any]) -> str:
        """Calculate cryptographic hash of analysis results."""
        try:
            # Create normalized JSON string
            normalized = json.dumps(analysis_results, sort_keys=True, separators=(',', ':'))
            
            # Calculate SHA-256 hash
            hash_obj = hashlib.sha256(normalized.encode('utf-8'))
            return hash_obj.hexdigest()
        
        except Exception as e:
            logger.error(f"Hash calculation failed: {str(e)}")
            return hashlib.sha256(str(analysis_results).encode('utf-8')).hexdigest()
    
    def _sign_submission(self, submission: Dict[str, Any]) -> str:
        """Create HMAC signature for submission."""
        try:
            # Create canonical string representation
            canonical = json.dumps(submission, sort_keys=True, separators=(',', ':'))
            
            # Create HMAC signature
            signature = hmac.new(
                self.api_key.encode('utf-8'),
                canonical.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            
            return signature
        
        except Exception as e:
            logger.error(f"Signature creation failed: {str(e)}")
            return "signature_error"
    
    def _create_analysis_summary(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Create a summary of analysis results for attestation."""
        try:
            repositories = analysis_results.get('repositories', {})
            summary = analysis_results.get('summary', {})
            metrics = analysis_results.get('metrics', {})
            
            # Extract key metrics
            successful_repos = []
            failed_repos = []
            total_quality_score = 0
            
            for repo_name, repo_data in repositories.items():
                if repo_data.get('status') == 'completed':
                    successful_repos.append({
                        'repository': repo_name,
                        'quality_score': repo_data.get('quality_score', 0),
                        'language': repo_data.get('info', {}).get('language'),
                        'size': repo_data.get('structure', {}).get('total_size_bytes', 0)
                    })
                    total_quality_score += repo_data.get('quality_score', 0)
                else:
                    failed_repos.append({
                        'repository': repo_name,
                        'error': repo_data.get('error', 'Unknown error')
                    })
            
            avg_quality = total_quality_score / max(len(successful_repos), 1)
            
            return {
                'total_repositories': summary.get('total_repositories', 0),
                'successful_analyses': len(successful_repos),
                'failed_analyses': len(failed_repos),
                'average_quality_score': round(avg_quality, 2),
                'language_distribution': metrics.get('language_distribution', {}),
                'successful_repositories': successful_repos[:10],  # Limit for attestation
                'failed_repositories': failed_repos,
                'analysis_timestamp': summary.get('analysis_timestamp')
            }
        
        except Exception as e:
            logger.error(f"Analysis summary creation failed: {str(e)}")
            return {
                'error': 'Failed to create analysis summary',
                'raw_summary': str(analysis_results)[:1000]  # Truncated fallback
            }
    
    def _create_mock_attestation(self, analysis_results: Dict[str, Any], lineage_entry: Dict[str, Any]) -> Dict[str, Any]:
        """Create a mock attestation when ShadowScrolls is not available."""
        analysis_hash = self._calculate_analysis_hash(analysis_results)
        
        return {
            'status': 'mock_attestation',
            'attestation_id': f'mock_{analysis_hash[:16]}',
            'witness_hash': hashlib.sha256(f'mock_witness_{analysis_hash}'.encode()).hexdigest(),
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'verification_url': f'mock://verification/{analysis_hash}',
            'submission_hash': analysis_hash,
            'note': 'Mock attestation created - ShadowScrolls not configured'
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Check ShadowScrolls service health."""
        if not self.endpoint:
            return {
                'status': 'not_configured',
                'message': 'ShadowScrolls endpoint not configured'
            }
        
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            async with self.session.get(
                f'{self.endpoint}/health',
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                
                if response.status == 200:
                    return {
                        'status': 'healthy',
                        'endpoint': self.endpoint,
                        'response_time': response.headers.get('X-Response-Time'),
                        'timestamp': datetime.now(timezone.utc).isoformat()
                    }
                else:
                    return {
                        'status': 'unhealthy',
                        'endpoint': self.endpoint,
                        'http_status': response.status,
                        'timestamp': datetime.now(timezone.utc).isoformat()
                    }
        
        except Exception as e:
            return {
                'status': 'error',
                'endpoint': self.endpoint,
                'error': str(e),
                'timestamp': datetime.now(timezone.utc).isoformat()
            }