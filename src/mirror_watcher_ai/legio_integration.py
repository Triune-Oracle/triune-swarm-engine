"""
Legio-Cognito Integration Module

Provides integration with the Legio-Cognito scroll archival system
for permanent storage and retrieval of MirrorWatcherAI results.
"""

import asyncio
import json
import logging
import os
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
import aiohttp
import hashlib


class LegioCognitoArchival:
    """Integration with Legio-Cognito scroll archival system."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.endpoint = os.getenv('LEGIO_COGNITO_ENDPOINT', 'https://api.legio-cognito.triune-oracle.com/v1')
        self.api_key = os.getenv('LEGIO_COGNITO_API_KEY')
        self.archive_enabled = bool(self.api_key)
        
    async def archive_results(self, analysis_results: Dict[str, Any], attestation: Dict[str, Any], lineage_record: Dict[str, Any]) -> Dict[str, Any]:
        """Archive MirrorWatcherAI results to Legio-Cognito."""
        self.logger.info("Archiving results to Legio-Cognito...")
        
        try:
            # Create comprehensive scroll package
            scroll_package = await self._create_scroll_package(analysis_results, attestation, lineage_record)
            
            # Archive to Legio-Cognito if enabled
            if self.archive_enabled:
                archive_result = await self._submit_to_legio(scroll_package)
            else:
                # Store locally as fallback
                archive_result = await self._store_locally(scroll_package)
            
            self.logger.info("Results archived successfully")
            return archive_result
            
        except Exception as e:
            self.logger.error(f"Failed to archive results: {e}")
            return {
                'status': 'failed',
                'error': str(e),
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
    
    async def _create_scroll_package(self, analysis_results: Dict[str, Any], attestation: Dict[str, Any], lineage_record: Dict[str, Any]) -> Dict[str, Any]:
        """Create comprehensive scroll package for archival."""
        timestamp = datetime.now(timezone.utc)
        
        scroll_package = {
            'scroll_metadata': {
                'type': 'MirrorWatcherAI_Results',
                'version': '1.0.0',
                'created_at': timestamp.isoformat(),
                'archive_id': self._generate_archive_id(analysis_results, timestamp),
                'classification': 'ecosystem_analysis',
                'retention': 'permanent',
                'access_level': 'triune_internal'
            },
            'content': {
                'analysis_results': analysis_results,
                'shadowscrolls_attestation': attestation,
                'lineage_record': lineage_record,
                'execution_summary': self._create_execution_summary(analysis_results, attestation, lineage_record)
            },
            'integrity': {
                'content_hash': self._calculate_content_hash(analysis_results, attestation, lineage_record),
                'package_hash': None,  # Will be calculated after complete package creation
                'verification': {
                    'attestation_verified': self._verify_attestation_integrity(attestation),
                    'lineage_verified': self._verify_lineage_integrity(lineage_record),
                    'analysis_verified': self._verify_analysis_integrity(analysis_results)
                }
            },
            'legio_metadata': {
                'scroll_classification': self._classify_scroll_importance(analysis_results),
                'indexing_tags': self._generate_indexing_tags(analysis_results),
                'search_keywords': self._generate_search_keywords(analysis_results),
                'related_scrolls': await self._find_related_scrolls(analysis_results)
            }
        }
        
        # Calculate final package hash
        scroll_package['integrity']['package_hash'] = self._calculate_package_hash(scroll_package)
        
        return scroll_package
    
    def _generate_archive_id(self, analysis_results: Dict[str, Any], timestamp: datetime) -> str:
        """Generate unique archive ID."""
        content = f"mirror_watcher_{timestamp.strftime('%Y%m%d_%H%M%S')}"
        repos_hash = hashlib.md5(str(sorted(analysis_results.get('repositories', {}).keys())).encode()).hexdigest()[:8]
        return f"{content}_{repos_hash}"
    
    def _create_execution_summary(self, analysis_results: Dict[str, Any], attestation: Dict[str, Any], lineage_record: Dict[str, Any]) -> Dict[str, Any]:
        """Create high-level execution summary."""
        repos = analysis_results.get('repositories', {})
        ecosystem_health = analysis_results.get('ecosystem_health', {})
        
        return {
            'execution_timestamp': analysis_results.get('timestamp'),
            'repositories_analyzed': len(repos),
            'successful_analyses': sum(1 for r in repos.values() if r.get('status') == 'success'),
            'failed_analyses': sum(1 for r in repos.values() if r.get('status') != 'success'),
            'ecosystem_health_score': ecosystem_health.get('average_compliance_score', 0),
            'ecosystem_status': ecosystem_health.get('ecosystem_status'),
            'attestation_id': attestation.get('scroll_id'),
            'lineage_execution_id': lineage_record.get('execution_id'),
            'changes_detected': len(lineage_record.get('deltas', {}).get('repository_changes', [])),
            'recommendations_count': len(analysis_results.get('recommendations', [])),
            'archive_classification': self._classify_execution_importance(analysis_results, ecosystem_health)
        }
    
    def _classify_execution_importance(self, analysis_results: Dict[str, Any], ecosystem_health: Dict[str, Any]) -> str:
        """Classify the importance of this execution for archival priority."""
        health_score = ecosystem_health.get('average_compliance_score', 0)
        recommendations_count = len(analysis_results.get('recommendations', []))
        
        if health_score < 50 or recommendations_count > 5:
            return 'critical'
        elif health_score < 70 or recommendations_count > 2:
            return 'important'
        else:
            return 'routine'
    
    def _calculate_content_hash(self, analysis_results: Dict[str, Any], attestation: Dict[str, Any], lineage_record: Dict[str, Any]) -> str:
        """Calculate hash of core content."""
        combined_content = {
            'analysis': analysis_results,
            'attestation': attestation,
            'lineage': lineage_record
        }
        content_str = json.dumps(combined_content, sort_keys=True, default=str)
        return hashlib.sha256(content_str.encode()).hexdigest()
    
    def _calculate_package_hash(self, scroll_package: Dict[str, Any]) -> str:
        """Calculate hash of complete package."""
        # Create copy without package_hash to avoid circular reference
        package_copy = scroll_package.copy()
        if 'integrity' in package_copy and 'package_hash' in package_copy['integrity']:
            package_copy['integrity'] = package_copy['integrity'].copy()
            del package_copy['integrity']['package_hash']
        
        package_str = json.dumps(package_copy, sort_keys=True, default=str)
        return hashlib.sha256(package_str.encode()).hexdigest()
    
    def _verify_attestation_integrity(self, attestation: Dict[str, Any]) -> bool:
        """Verify attestation integrity."""
        required_fields = ['scroll_id', 'timestamp', 'system']
        return all(field in attestation for field in required_fields)
    
    def _verify_lineage_integrity(self, lineage_record: Dict[str, Any]) -> bool:
        """Verify lineage record integrity."""
        required_fields = ['execution_id', 'timestamp', 'current_hash']
        return all(field in lineage_record for field in required_fields)
    
    def _verify_analysis_integrity(self, analysis_results: Dict[str, Any]) -> bool:
        """Verify analysis results integrity."""
        required_fields = ['timestamp', 'repositories', 'ecosystem_health']
        return all(field in analysis_results for field in required_fields)
    
    def _classify_scroll_importance(self, analysis_results: Dict[str, Any]) -> str:
        """Classify scroll importance for Legio-Cognito indexing."""
        ecosystem_health = analysis_results.get('ecosystem_health', {})
        health_score = ecosystem_health.get('average_compliance_score', 0)
        
        if health_score < 50:
            return 'high_priority'
        elif health_score < 80:
            return 'medium_priority'
        else:
            return 'standard'
    
    def _generate_indexing_tags(self, analysis_results: Dict[str, Any]) -> List[str]:
        """Generate tags for Legio-Cognito indexing."""
        tags = ['mirror_watcher', 'ecosystem_analysis', 'triune_oracle']
        
        # Add repository-specific tags
        repos = analysis_results.get('repositories', {})
        for repo_name in repos.keys():
            if 'swarm' in repo_name.lower():
                tags.append('swarm_engine')
            if 'legio' in repo_name.lower():
                tags.append('legio_cognito')
            if 'monitor' in repo_name.lower():
                tags.append('monitoring')
            if 'mobile' in repo_name.lower():
                tags.append('mobile')
        
        # Add health-based tags
        ecosystem_health = analysis_results.get('ecosystem_health', {})
        health_status = ecosystem_health.get('ecosystem_status')
        if health_status:
            tags.append(f'health_{health_status}')
        
        # Add recommendation-based tags
        recommendations = analysis_results.get('recommendations', [])
        if recommendations:
            tags.append('has_recommendations')
            for rec in recommendations:
                rec_type = rec.get('type')
                if rec_type:
                    tags.append(f'rec_{rec_type}')
        
        return list(set(tags))  # Remove duplicates
    
    def _generate_search_keywords(self, analysis_results: Dict[str, Any]) -> List[str]:
        """Generate search keywords for Legio-Cognito."""
        keywords = []
        
        # Repository names
        repos = analysis_results.get('repositories', {})
        for repo_name in repos.keys():
            keywords.extend(repo_name.split('/'))
            keywords.extend(repo_name.replace('-', ' ').replace('_', ' ').split())
        
        # Languages used
        for repo_data in repos.values():
            if repo_data.get('status') == 'success':
                languages = repo_data.get('languages', {})
                keywords.extend(languages.keys())
        
        # Ecosystem status
        ecosystem_health = analysis_results.get('ecosystem_health', {})
        if ecosystem_health.get('ecosystem_status'):
            keywords.append(ecosystem_health['ecosystem_status'])
        
        # Recommendation types
        recommendations = analysis_results.get('recommendations', [])
        for rec in recommendations:
            if rec.get('type'):
                keywords.append(rec['type'])
        
        return list(set(keyword.lower() for keyword in keywords if keyword))
    
    async def _find_related_scrolls(self, analysis_results: Dict[str, Any]) -> List[str]:
        """Find related scrolls in Legio-Cognito."""
        # This would query Legio-Cognito for related scrolls
        # For now, return empty list since we don't have the search API
        return []
    
    async def _submit_to_legio(self, scroll_package: Dict[str, Any]) -> Dict[str, Any]:
        """Submit scroll package to Legio-Cognito."""
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json',
                'X-Archive-Type': 'mirror_watcher_results'
            }
            
            archive_url = f"{self.endpoint.rstrip('/')}/scrolls/archive"
            
            async with aiohttp.ClientSession() as session:
                async with session.post(archive_url, json=scroll_package, headers=headers, timeout=60) as resp:
                    if resp.status in [200, 201]:
                        result = await resp.json()
                        self.logger.info("Successfully archived to Legio-Cognito")
                        return {
                            'status': 'archived',
                            'archive_id': scroll_package['scroll_metadata']['archive_id'],
                            'legio_response': result,
                            'archive_url': archive_url,
                            'timestamp': datetime.now(timezone.utc).isoformat()
                        }
                    else:
                        error_text = await resp.text()
                        self.logger.warning(f"Legio-Cognito archival failed: {resp.status} - {error_text}")
                        
                        # Store locally as fallback
                        local_result = await self._store_locally(scroll_package)
                        return {
                            'status': 'failed_archived_locally',
                            'error': f"HTTP {resp.status}: {error_text}",
                            'local_storage': local_result,
                            'timestamp': datetime.now(timezone.utc).isoformat()
                        }
        
        except asyncio.TimeoutError:
            self.logger.warning("Legio-Cognito archival timeout, storing locally")
            local_result = await self._store_locally(scroll_package)
            return {
                'status': 'timeout_archived_locally',
                'error': 'Archival timed out after 60 seconds',
                'local_storage': local_result,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            self.logger.error(f"Legio-Cognito archival error: {e}")
            local_result = await self._store_locally(scroll_package)
            return {
                'status': 'error_archived_locally',
                'error': str(e),
                'local_storage': local_result,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
    
    async def _store_locally(self, scroll_package: Dict[str, Any]) -> Dict[str, Any]:
        """Store scroll package locally as fallback."""
        try:
            # Create archive directory
            archive_dir = '.legio_cognito/archive'
            os.makedirs(archive_dir, exist_ok=True)
            
            # Generate filename
            archive_id = scroll_package['scroll_metadata']['archive_id']
            timestamp = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
            filename = f"{archive_id}_{timestamp}.json"
            filepath = os.path.join(archive_dir, filename)
            
            # Write scroll package to file
            with open(filepath, 'w') as f:
                json.dump(scroll_package, f, indent=2, default=str)
            
            self.logger.info(f"Scroll package stored locally: {filepath}")
            return {
                'status': 'stored_locally',
                'filepath': filepath,
                'archive_id': archive_id,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Local storage failed: {e}")
            return {
                'status': 'failed',
                'error': str(e),
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
    
    async def retrieve_scroll(self, archive_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve scroll from Legio-Cognito by archive ID."""
        try:
            if not self.archive_enabled:
                return await self._retrieve_locally(archive_id)
            
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            retrieve_url = f"{self.endpoint.rstrip('/')}/scrolls/{archive_id}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(retrieve_url, headers=headers, timeout=30) as resp:
                    if resp.status == 200:
                        return await resp.json()
                    elif resp.status == 404:
                        # Try local storage
                        return await self._retrieve_locally(archive_id)
                    else:
                        self.logger.warning(f"Failed to retrieve scroll: {resp.status}")
                        return None
        
        except Exception as e:
            self.logger.error(f"Scroll retrieval error: {e}")
            return await self._retrieve_locally(archive_id)
    
    async def _retrieve_locally(self, archive_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve scroll from local storage."""
        try:
            archive_dir = '.legio_cognito/archive'
            if not os.path.exists(archive_dir):
                return None
            
            # Look for files containing the archive_id
            for filename in os.listdir(archive_dir):
                if archive_id in filename and filename.endswith('.json'):
                    filepath = os.path.join(archive_dir, filename)
                    with open(filepath, 'r') as f:
                        return json.load(f)
            
            return None
            
        except Exception as e:
            self.logger.error(f"Local retrieval error: {e}")
            return None
    
    async def search_scrolls(self, query: str, tags: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Search scrolls in Legio-Cognito."""
        try:
            if not self.archive_enabled:
                return await self._search_locally(query, tags)
            
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            search_params = {'q': query}
            if tags:
                search_params['tags'] = ','.join(tags)
            
            search_url = f"{self.endpoint.rstrip('/')}/scrolls/search"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(search_url, headers=headers, params=search_params, timeout=30) as resp:
                    if resp.status == 200:
                        result = await resp.json()
                        return result.get('scrolls', [])
                    else:
                        self.logger.warning(f"Search failed: {resp.status}")
                        return []
        
        except Exception as e:
            self.logger.error(f"Search error: {e}")
            return await self._search_locally(query, tags)
    
    async def _search_locally(self, query: str, tags: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Search local scroll storage."""
        try:
            archive_dir = '.legio_cognito/archive'
            if not os.path.exists(archive_dir):
                return []
            
            results = []
            query_lower = query.lower()
            
            for filename in os.listdir(archive_dir):
                if filename.endswith('.json'):
                    filepath = os.path.join(archive_dir, filename)
                    try:
                        with open(filepath, 'r') as f:
                            scroll_data = json.load(f)
                        
                        # Simple text search in scroll content
                        scroll_text = json.dumps(scroll_data, default=str).lower()
                        if query_lower in scroll_text:
                            # Check tags if provided
                            if tags:
                                scroll_tags = scroll_data.get('legio_metadata', {}).get('indexing_tags', [])
                                if not any(tag in scroll_tags for tag in tags):
                                    continue
                            
                            results.append({
                                'archive_id': scroll_data.get('scroll_metadata', {}).get('archive_id'),
                                'timestamp': scroll_data.get('scroll_metadata', {}).get('created_at'),
                                'summary': scroll_data.get('content', {}).get('execution_summary', {}),
                                'local_file': filename
                            })
                    except Exception:
                        continue  # Skip corrupted files
            
            return results
            
        except Exception as e:
            self.logger.error(f"Local search error: {e}")
            return []