"""
MirrorLineage-Δ Traceability Module

Provides comprehensive audit trail and cryptographic integrity logging
for MirrorWatcherAI operations with delta-based change tracking.
"""

import asyncio
import hashlib
import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional
import uuid


class MirrorLineage:
    """MirrorLineage-Δ system for comprehensive audit trail and change tracking."""
    
    def __init__(self, lineage_dir: str = ".mirror_lineage"):
        self.logger = logging.getLogger(__name__)
        self.lineage_dir = Path(lineage_dir)
        self.lineage_dir.mkdir(exist_ok=True)
        
        # Initialize lineage tracking
        self.chain_file = self.lineage_dir / "lineage_chain.json"
        self.deltas_dir = self.lineage_dir / "deltas"
        self.deltas_dir.mkdir(exist_ok=True)
        
    async def record_execution(self, analysis_results: Dict[str, Any], attestation: Dict[str, Any]) -> Dict[str, Any]:
        """Record execution in MirrorLineage-Δ chain with delta tracking."""
        self.logger.info("Recording execution in MirrorLineage-Δ...")
        
        try:
            timestamp = datetime.now(timezone.utc)
            execution_id = str(uuid.uuid4())
            
            # Load previous state for delta calculation
            previous_state = await self._load_previous_state()
            
            # Calculate deltas
            deltas = await self._calculate_deltas(previous_state, analysis_results)
            
            # Create lineage record
            lineage_record = {
                'execution_id': execution_id,
                'timestamp': timestamp.isoformat(),
                'version': '1.0.0',
                'operation': 'mirror_watcher_analysis',
                'previous_hash': previous_state.get('hash') if previous_state else None,
                'current_hash': self._calculate_hash(analysis_results),
                'attestation_reference': {
                    'scroll_id': attestation.get('scroll_id'),
                    'attestation_hash': self._calculate_hash(attestation),
                    'timestamp': attestation.get('timestamp')
                },
                'deltas': deltas,
                'metadata': {
                    'repositories_count': len(analysis_results.get('repositories', {})),
                    'successful_analyses': sum(
                        1 for r in analysis_results.get('repositories', {}).values() 
                        if r.get('status') == 'success'
                    ),
                    'ecosystem_health_score': analysis_results.get('ecosystem_health', {}).get('average_compliance_score', 0),
                    'changes_detected': len(deltas.get('repository_changes', [])),
                    'execution_duration': deltas.get('execution_metadata', {}).get('duration')
                },
                'integrity': {
                    'chain_validated': await self._validate_chain_integrity(),
                    'hash_chain': self._create_hash_chain(previous_state, analysis_results),
                    'signatures': await self._create_signatures(analysis_results, attestation)
                }
            }
            
            # Store lineage record
            await self._store_lineage_record(lineage_record)
            
            # Update lineage chain
            await self._update_lineage_chain(lineage_record)
            
            # Store current state for next delta calculation
            await self._store_current_state(analysis_results, lineage_record)
            
            self.logger.info(f"MirrorLineage-Δ record created: {execution_id}")
            return lineage_record
            
        except Exception as e:
            self.logger.error(f"Failed to record execution in MirrorLineage-Δ: {e}")
            return {
                'error': str(e),
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'status': 'failed'
            }
    
    async def _load_previous_state(self) -> Optional[Dict[str, Any]]:
        """Load previous execution state for delta calculation."""
        try:
            state_file = self.lineage_dir / "current_state.json"
            if state_file.exists():
                with open(state_file, 'r') as f:
                    return json.load(f)
            return None
        except Exception as e:
            self.logger.warning(f"Failed to load previous state: {e}")
            return None
    
    async def _calculate_deltas(self, previous_state: Optional[Dict[str, Any]], current_results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate deltas between previous and current execution."""
        if not previous_state:
            return {
                'type': 'initial_execution',
                'repository_changes': [],
                'new_repositories': list(current_results.get('repositories', {}).keys()),
                'execution_metadata': {
                    'duration': None,  # First execution
                    'change_summary': 'Initial MirrorWatcherAI execution'
                }
            }
        
        deltas = {
            'type': 'delta_execution',
            'repository_changes': [],
            'new_repositories': [],
            'removed_repositories': [],
            'modified_repositories': [],
            'execution_metadata': {}
        }
        
        previous_repos = previous_state.get('analysis_results', {}).get('repositories', {})
        current_repos = current_results.get('repositories', {})
        
        # Find new repositories
        previous_repo_names = set(previous_repos.keys())
        current_repo_names = set(current_repos.keys())
        
        deltas['new_repositories'] = list(current_repo_names - previous_repo_names)
        deltas['removed_repositories'] = list(previous_repo_names - current_repo_names)
        
        # Find modified repositories
        for repo_name in current_repo_names.intersection(previous_repo_names):
            previous_repo = previous_repos.get(repo_name, {})
            current_repo = current_repos.get(repo_name, {})
            
            repo_changes = self._compare_repository_states(previous_repo, current_repo)
            if repo_changes['has_changes']:
                deltas['repository_changes'].append({
                    'repository': repo_name,
                    'changes': repo_changes
                })
                deltas['modified_repositories'].append(repo_name)
        
        # Calculate execution metadata
        previous_timestamp = previous_state.get('timestamp')
        current_timestamp = current_results.get('timestamp')
        
        if previous_timestamp and current_timestamp:
            try:
                prev_dt = datetime.fromisoformat(previous_timestamp.replace('Z', '+00:00'))
                curr_dt = datetime.fromisoformat(current_timestamp.replace('Z', '+00:00'))
                duration = (curr_dt - prev_dt).total_seconds()
                deltas['execution_metadata']['duration'] = duration
            except Exception:
                deltas['execution_metadata']['duration'] = None
        
        # Create change summary
        change_count = len(deltas['repository_changes'])
        new_count = len(deltas['new_repositories'])
        removed_count = len(deltas['removed_repositories'])
        
        deltas['execution_metadata']['change_summary'] = (
            f"{change_count} repositories modified, "
            f"{new_count} added, {removed_count} removed"
        )
        
        return deltas
    
    def _compare_repository_states(self, previous: Dict[str, Any], current: Dict[str, Any]) -> Dict[str, Any]:
        """Compare two repository states to detect changes."""
        changes = {
            'has_changes': False,
            'field_changes': [],
            'metric_changes': {},
            'structure_changes': []
        }
        
        # Fields to monitor for changes
        monitored_fields = [
            'stars', 'forks', 'issues', 'updated_at', 'size', 
            'commits', 'workflows'
        ]
        
        for field in monitored_fields:
            prev_value = previous.get(field)
            curr_value = current.get(field)
            
            if prev_value != curr_value:
                changes['has_changes'] = True
                changes['field_changes'].append({
                    'field': field,
                    'previous': prev_value,
                    'current': curr_value,
                    'change_type': self._classify_change(prev_value, curr_value)
                })
        
        # Compare metrics
        prev_metrics = previous.get('metrics', {})
        curr_metrics = current.get('metrics', {})
        
        for metric, curr_value in curr_metrics.items():
            prev_value = prev_metrics.get(metric)
            if prev_value != curr_value:
                changes['has_changes'] = True
                changes['metric_changes'][metric] = {
                    'previous': prev_value,
                    'current': curr_value,
                    'delta': curr_value - prev_value if isinstance(curr_value, (int, float)) and isinstance(prev_value, (int, float)) else None
                }
        
        # Compare structure
        prev_structure = previous.get('structure', {})
        curr_structure = current.get('structure', {})
        
        structure_fields = ['files', 'directories', 'triune_patterns']
        for field in structure_fields:
            if prev_structure.get(field) != curr_structure.get(field):
                changes['has_changes'] = True
                changes['structure_changes'].append({
                    'field': field,
                    'change_detected': True
                })
        
        return changes
    
    def _classify_change(self, previous, current) -> str:
        """Classify the type of change between two values."""
        if previous is None and current is not None:
            return 'addition'
        elif previous is not None and current is None:
            return 'removal'
        elif isinstance(previous, (int, float)) and isinstance(current, (int, float)):
            if current > previous:
                return 'increase'
            elif current < previous:
                return 'decrease'
            else:
                return 'no_change'
        else:
            return 'modification'
    
    def _calculate_hash(self, data: Dict[str, Any]) -> str:
        """Calculate cryptographic hash of data."""
        sorted_data = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha256(sorted_data.encode()).hexdigest()
    
    def _create_hash_chain(self, previous_state: Optional[Dict[str, Any]], current_results: Dict[str, Any]) -> str:
        """Create hash chain linking previous and current executions."""
        previous_hash = previous_state.get('hash', '') if previous_state else ''
        current_hash = self._calculate_hash(current_results)
        
        chain_content = f"{previous_hash}{current_hash}"
        return hashlib.sha256(chain_content.encode()).hexdigest()
    
    async def _create_signatures(self, analysis_results: Dict[str, Any], attestation: Dict[str, Any]) -> Dict[str, str]:
        """Create cryptographic signatures for integrity verification."""
        return {
            'analysis_signature': self._calculate_hash(analysis_results)[:32],
            'attestation_signature': self._calculate_hash(attestation)[:32],
            'combined_signature': self._calculate_hash({
                'analysis': analysis_results,
                'attestation': attestation
            })[:32]
        }
    
    async def _validate_chain_integrity(self) -> bool:
        """Validate the integrity of the lineage chain."""
        try:
            if not self.chain_file.exists():
                return True  # Empty chain is valid
            
            with open(self.chain_file, 'r') as f:
                chain_data = json.load(f)
            
            records = chain_data.get('records', [])
            if len(records) <= 1:
                return True  # Single or empty record is valid
            
            # Validate chain links
            for i in range(1, len(records)):
                current_record = records[i]
                previous_record = records[i-1]
                
                expected_previous_hash = previous_record.get('current_hash')
                actual_previous_hash = current_record.get('previous_hash')
                
                if expected_previous_hash != actual_previous_hash:
                    self.logger.error(f"Chain integrity violation at record {i}")
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Chain validation error: {e}")
            return False
    
    async def _store_lineage_record(self, record: Dict[str, Any]) -> None:
        """Store individual lineage record."""
        try:
            record_file = self.deltas_dir / f"{record['execution_id']}.json"
            with open(record_file, 'w') as f:
                json.dump(record, f, indent=2, default=str)
                
        except Exception as e:
            self.logger.error(f"Failed to store lineage record: {e}")
            raise
    
    async def _update_lineage_chain(self, record: Dict[str, Any]) -> None:
        """Update the main lineage chain."""
        try:
            # Load existing chain
            chain_data = {'records': [], 'metadata': {}}
            if self.chain_file.exists():
                with open(self.chain_file, 'r') as f:
                    chain_data = json.load(f)
            
            # Add new record
            chain_data['records'].append({
                'execution_id': record['execution_id'],
                'timestamp': record['timestamp'],
                'current_hash': record['current_hash'],
                'previous_hash': record['previous_hash'],
                'attestation_reference': record['attestation_reference']
            })
            
            # Update metadata
            chain_data['metadata'] = {
                'last_updated': datetime.now(timezone.utc).isoformat(),
                'total_executions': len(chain_data['records']),
                'chain_integrity': await self._validate_chain_integrity()
            }
            
            # Save updated chain
            with open(self.chain_file, 'w') as f:
                json.dump(chain_data, f, indent=2, default=str)
                
        except Exception as e:
            self.logger.error(f"Failed to update lineage chain: {e}")
            raise
    
    async def _store_current_state(self, analysis_results: Dict[str, Any], lineage_record: Dict[str, Any]) -> None:
        """Store current state for next delta calculation."""
        try:
            state_data = {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'hash': lineage_record['current_hash'],
                'execution_id': lineage_record['execution_id'],
                'analysis_results': analysis_results
            }
            
            state_file = self.lineage_dir / "current_state.json"
            with open(state_file, 'w') as f:
                json.dump(state_data, f, indent=2, default=str)
                
        except Exception as e:
            self.logger.error(f"Failed to store current state: {e}")
            raise
    
    async def get_lineage_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Retrieve lineage history."""
        try:
            if not self.chain_file.exists():
                return []
            
            with open(self.chain_file, 'r') as f:
                chain_data = json.load(f)
            
            records = chain_data.get('records', [])
            
            # Sort by timestamp (newest first)
            records.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
            
            if limit:
                records = records[:limit]
            
            return records
            
        except Exception as e:
            self.logger.error(f"Failed to retrieve lineage history: {e}")
            return []
    
    async def get_deltas_for_execution(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """Get delta information for specific execution."""
        try:
            record_file = self.deltas_dir / f"{execution_id}.json"
            if record_file.exists():
                with open(record_file, 'r') as f:
                    record = json.load(f)
                return record.get('deltas')
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to retrieve deltas for execution {execution_id}: {e}")
            return None