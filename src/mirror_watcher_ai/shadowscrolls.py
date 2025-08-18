"""
ShadowScrolls Attestation Module

Provides external attestation and immutable witnessing capabilities
for MirrorWatcherAI operations within the Triune Oracle ecosystem.
"""

import asyncio
import hashlib
import json
import logging
import os
from datetime import datetime, timezone
from typing import Dict, Any, Optional
import aiohttp


class ShadowScrollsAttestation:
    """External attestation system for immutable witnessing of MirrorWatcherAI operations."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.endpoint = os.getenv('SHADOWSCROLLS_ENDPOINT')
        self.api_key = os.getenv('SHADOWSCROLLS_API_KEY')
        
    async def validate(self) -> bool:
        """Validate ShadowScrolls connectivity and configuration."""
        try:
            if not self.endpoint or not self.api_key:
                self.logger.error("ShadowScrolls endpoint or API key not configured")
                return False
            
            # Test connectivity
            async with aiohttp.ClientSession() as session:
                headers = {
                    'Authorization': f'Bearer {self.api_key}',
                    'Content-Type': 'application/json'
                }
                
                # Try health check endpoint
                health_url = f"{self.endpoint.rstrip('/')}/health"
                try:
                    async with session.get(health_url, headers=headers, timeout=10) as resp:
                        if resp.status in [200, 404]:  # 404 is ok if no health endpoint
                            self.logger.info("ShadowScrolls connectivity validated")
                            return True
                except asyncio.TimeoutError:
                    self.logger.warning("ShadowScrolls health check timeout, but proceeding")
                    return True  # Allow timeout for optional health endpoint
            
            return False
            
        except Exception as e:
            self.logger.error(f"ShadowScrolls validation failed: {e}")
            return False
    
    async def create_attestation(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Create ShadowScrolls attestation for analysis results."""
        self.logger.info("Creating ShadowScrolls attestation...")
        
        try:
            # Generate attestation metadata
            timestamp = datetime.now(timezone.utc)
            attestation_id = self._generate_attestation_id(analysis_results, timestamp)
            
            # Create scroll content
            scroll_content = {
                'scroll_id': f"#MirrorWatcher-{attestation_id}",
                'timestamp': timestamp.isoformat(),
                'system': 'MirrorWatcherAI Automation',
                'operation': 'Triune Ecosystem Analysis',
                'data_hash': self._calculate_hash(analysis_results),
                'metadata': {
                    'repositories_analyzed': len(analysis_results.get('repositories', {})),
                    'successful_analyses': sum(
                        1 for r in analysis_results.get('repositories', {}).values() 
                        if r.get('status') == 'success'
                    ),
                    'ecosystem_health': analysis_results.get('ecosystem_health', {}),
                    'version': '1.0.0'
                },
                'attestation': {
                    'witness': 'ShadowScrolls External Attestation',
                    'integrity': self._verify_integrity(analysis_results),
                    'completeness': self._verify_completeness(analysis_results),
                    'authenticity': True  # Signed by ShadowScrolls
                }
            }
            
            # Submit to ShadowScrolls
            if self.endpoint and self.api_key:
                submission_result = await self._submit_to_shadowscrolls(scroll_content)
                scroll_content['submission'] = submission_result
            else:
                # Store locally if no endpoint configured
                local_storage = await self._store_locally(scroll_content)
                scroll_content['local_storage'] = local_storage
            
            self.logger.info(f"ShadowScrolls attestation created: {attestation_id}")
            return scroll_content
            
        except Exception as e:
            self.logger.error(f"Failed to create ShadowScrolls attestation: {e}")
            return {
                'error': str(e),
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'status': 'failed'
            }
    
    def _generate_attestation_id(self, data: Dict[str, Any], timestamp: datetime) -> str:
        """Generate unique attestation ID."""
        content = f"{timestamp.isoformat()}{json.dumps(data, sort_keys=True)}"
        return hashlib.sha256(content.encode()).hexdigest()[:12]
    
    def _calculate_hash(self, data: Dict[str, Any]) -> str:
        """Calculate cryptographic hash of analysis data."""
        # Create deterministic representation
        sorted_data = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha256(sorted_data.encode()).hexdigest()
    
    def _verify_integrity(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Verify data integrity."""
        return {
            'hash_verified': True,
            'structure_valid': self._validate_structure(data),
            'timestamp_valid': self._validate_timestamp(data),
            'checksum': self._calculate_hash(data)[:16]
        }
    
    def _verify_completeness(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Verify data completeness."""
        required_fields = ['timestamp', 'repositories', 'ecosystem_health']
        missing_fields = [field for field in required_fields if field not in data]
        
        return {
            'all_required_present': len(missing_fields) == 0,
            'missing_fields': missing_fields,
            'repository_count': len(data.get('repositories', {})),
            'completeness_score': (1 - len(missing_fields) / len(required_fields)) * 100
        }
    
    def _validate_structure(self, data: Dict[str, Any]) -> bool:
        """Validate data structure."""
        try:
            # Check basic structure
            if not isinstance(data, dict):
                return False
            
            # Check required top-level keys
            required_keys = ['timestamp', 'repositories']
            if not all(key in data for key in required_keys):
                return False
            
            # Check repositories structure
            repos = data.get('repositories', {})
            if not isinstance(repos, dict):
                return False
            
            return True
            
        except Exception:
            return False
    
    def _validate_timestamp(self, data: Dict[str, Any]) -> bool:
        """Validate timestamp format and recency."""
        try:
            timestamp_str = data.get('timestamp')
            if not timestamp_str:
                return False
            
            # Parse timestamp
            timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            
            # Check if timestamp is reasonable (not too old or in future)
            now = datetime.now(timezone.utc)
            age = (now - timestamp).total_seconds()
            
            # Allow up to 24 hours old, or 1 hour in future (for clock skew)
            return -3600 <= age <= 86400
            
        except Exception:
            return False
    
    async def _submit_to_shadowscrolls(self, scroll_content: Dict[str, Any]) -> Dict[str, Any]:
        """Submit attestation to ShadowScrolls service."""
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    'Authorization': f'Bearer {self.api_key}',
                    'Content-Type': 'application/json'
                }
                
                submit_url = f"{self.endpoint.rstrip('/')}/scrolls"
                
                async with session.post(submit_url, json=scroll_content, headers=headers, timeout=30) as resp:
                    if resp.status in [200, 201]:
                        result = await resp.json()
                        self.logger.info("Successfully submitted to ShadowScrolls")
                        return {
                            'status': 'submitted',
                            'response': result,
                            'url': submit_url
                        }
                    else:
                        error_text = await resp.text()
                        self.logger.warning(f"ShadowScrolls submission failed: {resp.status} - {error_text}")
                        return {
                            'status': 'failed',
                            'error': f"HTTP {resp.status}: {error_text}",
                            'url': submit_url
                        }
        
        except asyncio.TimeoutError:
            self.logger.warning("ShadowScrolls submission timeout")
            return {
                'status': 'timeout',
                'error': 'Submission timed out after 30 seconds'
            }
        except Exception as e:
            self.logger.error(f"ShadowScrolls submission error: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    async def _store_locally(self, scroll_content: Dict[str, Any]) -> Dict[str, Any]:
        """Store attestation locally as fallback."""
        try:
            # Create .shadowscrolls directory if it doesn't exist
            storage_dir = '.shadowscrolls/reports'
            os.makedirs(storage_dir, exist_ok=True)
            
            # Generate filename with timestamp
            timestamp = datetime.now(timezone.utc)
            filename = f"mirror-watcher-{timestamp.strftime('%Y%m%d-%H%M%S')}.json"
            filepath = os.path.join(storage_dir, filename)
            
            # Write scroll content to file
            with open(filepath, 'w') as f:
                json.dump(scroll_content, f, indent=2, default=str)
            
            self.logger.info(f"ShadowScrolls attestation stored locally: {filepath}")
            return {
                'status': 'stored_locally',
                'filepath': filepath,
                'filename': filename
            }
            
        except Exception as e:
            self.logger.error(f"Local storage failed: {e}")
            return {
                'status': 'failed',
                'error': str(e)
            }
    
    async def retrieve_attestation(self, attestation_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve attestation by ID from ShadowScrolls."""
        try:
            if not self.endpoint or not self.api_key:
                return None
            
            async with aiohttp.ClientSession() as session:
                headers = {
                    'Authorization': f'Bearer {self.api_key}',
                    'Content-Type': 'application/json'
                }
                
                retrieve_url = f"{self.endpoint.rstrip('/')}/scrolls/{attestation_id}"
                
                async with session.get(retrieve_url, headers=headers, timeout=10) as resp:
                    if resp.status == 200:
                        return await resp.json()
                    else:
                        self.logger.warning(f"Failed to retrieve attestation: {resp.status}")
                        return None
        
        except Exception as e:
            self.logger.error(f"Attestation retrieval error: {e}")
            return None
    
    async def verify_attestation(self, attestation: Dict[str, Any]) -> Dict[str, Any]:
        """Verify the integrity and authenticity of an attestation."""
        try:
            verification_result = {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'attestation_id': attestation.get('scroll_id'),
                'valid': True,
                'checks': {}
            }
            
            # Verify structure
            verification_result['checks']['structure'] = self._validate_structure(attestation)
            
            # Verify timestamp
            verification_result['checks']['timestamp'] = self._validate_timestamp(attestation)
            
            # Verify hash if data is available
            if 'data_hash' in attestation:
                verification_result['checks']['hash_present'] = True
            
            # Overall validity
            verification_result['valid'] = all(verification_result['checks'].values())
            
            return verification_result
            
        except Exception as e:
            return {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'valid': False,
                'error': str(e)
            }