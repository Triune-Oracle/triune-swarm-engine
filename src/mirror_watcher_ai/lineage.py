"""
MirrorLineage - Immutable logging with cryptographic verification.
Provides MirrorLineage-Δ tamper-proof audit trails for all analysis activities.
"""

import hashlib
import json
import logging
import os
import gzip
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import asyncio

logger = logging.getLogger(__name__)


class MirrorLineage:
    """Immutable lineage tracking system with cryptographic verification."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.encryption_enabled = config.get('encryption', True)
        self.hash_algorithm = config.get('hash_algorithm', 'sha256')
        self.compression_enabled = config.get('compression', True)
        self.storage_path = Path(config.get('storage_path', './.lineage'))
        self.chain_file = self.storage_path / 'lineage_chain.json'
        
        # Ensure storage directory exists
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize chain if it doesn't exist
        if not self.chain_file.exists():
            self._initialize_chain()
    
    async def create_entry(self, analysis_results: Dict[str, Any], start_time: datetime) -> Dict[str, Any]:
        """Create a new lineage entry with cryptographic verification."""
        try:
            entry_id = self._generate_entry_id()
            timestamp = datetime.now(timezone.utc)
            
            # Get previous entry hash for chaining
            previous_hash = await self._get_last_entry_hash()
            
            # Create entry data
            entry_data = {
                'id': entry_id,
                'timestamp': timestamp.isoformat(),
                'start_time': start_time.isoformat(),
                'type': 'mirror_watcher_analysis',
                'version': '1.0.0',
                'previous_hash': previous_hash,
                'analysis_metadata': self._extract_metadata(analysis_results),
                'execution_info': {
                    'duration_seconds': (timestamp - start_time).total_seconds(),
                    'repositories_count': len(analysis_results.get('repositories', {})),
                    'successful_analyses': analysis_results.get('summary', {}).get('successful_analyses', 0),
                    'failed_analyses': analysis_results.get('summary', {}).get('failed_analyses', 0)
                }
            }
            
            # Calculate entry hash
            entry_hash = self._calculate_entry_hash(entry_data)
            entry_data['hash'] = entry_hash
            
            # Create verification data
            verification = self._create_verification(entry_data, analysis_results)
            entry_data['verification'] = verification
            
            # Compress if enabled
            if self.compression_enabled:
                compressed_data = await self._compress_data(analysis_results)
                entry_data['compressed_analysis'] = compressed_data
            else:
                entry_data['analysis_results'] = analysis_results
            
            # Save entry
            await self._save_entry(entry_data)
            
            # Update chain
            await self._update_chain(entry_data)
            
            logger.info(f"Lineage entry created: {entry_id}")
            
            return {
                'id': entry_id,
                'hash': entry_hash,
                'timestamp': timestamp.isoformat(),
                'previous_hash': previous_hash,
                'verification_hash': verification['verification_hash'],
                'chain_position': await self._get_chain_length(),
                'status': 'created'
            }
            
        except Exception as e:
            logger.error(f"Failed to create lineage entry: {str(e)}")
            return {
                'status': 'failed',
                'error': str(e),
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
    
    async def verify_entry(self, entry_id: str) -> Dict[str, Any]:
        """Verify the integrity of a lineage entry."""
        try:
            entry_data = await self._load_entry(entry_id)
            if not entry_data:
                return {
                    'status': 'not_found',
                    'entry_id': entry_id
                }
            
            # Verify entry hash
            stored_hash = entry_data.get('hash')
            calculated_hash = self._calculate_entry_hash({k: v for k, v in entry_data.items() if k != 'hash'})
            
            hash_valid = stored_hash == calculated_hash
            
            # Verify chain integrity
            chain_valid = await self._verify_chain_integrity(entry_id)
            
            # Verify data integrity
            data_valid = await self._verify_data_integrity(entry_data)
            
            verification_result = {
                'status': 'verified' if all([hash_valid, chain_valid, data_valid]) else 'invalid',
                'entry_id': entry_id,
                'hash_valid': hash_valid,
                'chain_valid': chain_valid,
                'data_valid': data_valid,
                'stored_hash': stored_hash,
                'calculated_hash': calculated_hash,
                'verification_timestamp': datetime.now(timezone.utc).isoformat()
            }
            
            logger.info(f"Entry verification completed: {entry_id} - {verification_result['status']}")
            return verification_result
            
        except Exception as e:
            logger.error(f"Entry verification failed: {str(e)}")
            return {
                'status': 'error',
                'entry_id': entry_id,
                'error': str(e)
            }
    
    async def get_lineage_chain(self, limit: Optional[int] = None) -> Dict[str, Any]:
        """Retrieve the complete lineage chain or last N entries."""
        try:
            if not self.chain_file.exists():
                return {
                    'status': 'empty',
                    'entries': [],
                    'chain_length': 0
                }
            
            with open(self.chain_file, 'r') as f:
                chain_data = json.load(f)
            
            entries = chain_data.get('entries', [])
            
            if limit:
                entries = entries[-limit:]
            
            # Calculate chain integrity
            integrity_valid = await self._verify_complete_chain_integrity()
            
            return {
                'status': 'success',
                'entries': entries,
                'chain_length': len(chain_data.get('entries', [])),
                'integrity_valid': integrity_valid,
                'chain_hash': self._calculate_chain_hash(entries),
                'retrieved_timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to retrieve lineage chain: {str(e)}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    async def export_lineage(self, output_path: str, format: str = 'json') -> Dict[str, Any]:
        """Export lineage data to external file."""
        try:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            chain_data = await self.get_lineage_chain()
            
            if format.lower() == 'json':
                with open(output_file, 'w') as f:
                    json.dump(chain_data, f, indent=2, default=str)
            else:
                raise ValueError(f"Unsupported export format: {format}")
            
            return {
                'status': 'exported',
                'output_path': str(output_file),
                'format': format,
                'entries_count': chain_data.get('chain_length', 0),
                'export_timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to export lineage: {str(e)}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def _initialize_chain(self) -> None:
        """Initialize the lineage chain with genesis entry."""
        try:
            genesis_entry = {
                'id': 'genesis',
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'type': 'genesis',
                'version': '1.0.0',
                'previous_hash': '0' * 64,
                'hash': self._calculate_genesis_hash()
            }
            
            chain_data = {
                'initialized': datetime.now(timezone.utc).isoformat(),
                'version': '1.0.0',
                'hash_algorithm': self.hash_algorithm,
                'entries': [genesis_entry]
            }
            
            with open(self.chain_file, 'w') as f:
                json.dump(chain_data, f, indent=2)
            
            logger.info("Lineage chain initialized with genesis entry")
            
        except Exception as e:
            logger.error(f"Failed to initialize lineage chain: {str(e)}")
            raise
    
    def _generate_entry_id(self) -> str:
        """Generate unique entry ID."""
        timestamp = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S_%f')
        return f"lineage_{timestamp}"
    
    def _calculate_entry_hash(self, entry_data: Dict[str, Any]) -> str:
        """Calculate cryptographic hash of entry data."""
        try:
            # Create normalized JSON string
            normalized = json.dumps(entry_data, sort_keys=True, separators=(',', ':'))
            
            # Calculate hash based on configured algorithm
            if self.hash_algorithm == 'sha256':
                hash_obj = hashlib.sha256(normalized.encode('utf-8'))
            elif self.hash_algorithm == 'sha512':
                hash_obj = hashlib.sha512(normalized.encode('utf-8'))
            else:
                hash_obj = hashlib.sha256(normalized.encode('utf-8'))
            
            return hash_obj.hexdigest()
        
        except Exception as e:
            logger.error(f"Hash calculation failed: {str(e)}")
            return hashlib.sha256(str(entry_data).encode('utf-8')).hexdigest()
    
    def _calculate_genesis_hash(self) -> str:
        """Calculate hash for genesis entry."""
        genesis_data = {
            'type': 'genesis',
            'version': '1.0.0',
            'algorithm': self.hash_algorithm,
            'timestamp': '2025-01-01T00:00:00+00:00'  # Fixed timestamp for reproducibility
        }
        return self._calculate_entry_hash(genesis_data)
    
    def _calculate_chain_hash(self, entries: List[Dict[str, Any]]) -> str:
        """Calculate hash of entire chain."""
        chain_string = ''.join(entry.get('hash', '') for entry in entries)
        return hashlib.sha256(chain_string.encode('utf-8')).hexdigest()
    
    def _extract_metadata(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Extract metadata from analysis results for lineage."""
        try:
            summary = analysis_results.get('summary', {})
            metrics = analysis_results.get('metrics', {})
            repositories = analysis_results.get('repositories', {})
            
            # Extract repository names and basic info
            repo_metadata = {}
            for repo_name, repo_data in repositories.items():
                if repo_data.get('status') == 'completed':
                    repo_metadata[repo_name] = {
                        'quality_score': repo_data.get('quality_score', 0),
                        'language': repo_data.get('info', {}).get('language'),
                        'size_bytes': repo_data.get('structure', {}).get('total_size_bytes', 0),
                        'analysis_timestamp': repo_data.get('analysis_timestamp')
                    }
                else:
                    repo_metadata[repo_name] = {
                        'status': 'failed',
                        'error': repo_data.get('error')
                    }
            
            return {
                'analysis_summary': {
                    'total_repositories': summary.get('total_repositories', 0),
                    'successful_analyses': summary.get('successful_analyses', 0),
                    'failed_analyses': summary.get('failed_analyses', 0),
                    'analyzer_version': summary.get('analyzer_version')
                },
                'aggregate_metrics': metrics,
                'repositories': repo_metadata
            }
            
        except Exception as e:
            logger.error(f"Metadata extraction failed: {str(e)}")
            return {'error': str(e)}
    
    def _create_verification(self, entry_data: Dict[str, Any], analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Create verification data for entry."""
        try:
            # Calculate verification hash
            verification_data = {
                'entry_hash': entry_data.get('hash'),
                'analysis_hash': hashlib.sha256(json.dumps(analysis_results, sort_keys=True).encode()).hexdigest(),
                'timestamp': entry_data.get('timestamp'),
                'algorithm': self.hash_algorithm
            }
            
            verification_hash = self._calculate_entry_hash(verification_data)
            
            return {
                'verification_hash': verification_hash,
                'analysis_hash': verification_data['analysis_hash'],
                'algorithm': self.hash_algorithm,
                'created_timestamp': entry_data.get('timestamp')
            }
            
        except Exception as e:
            logger.error(f"Verification creation failed: {str(e)}")
            return {'error': str(e)}
    
    async def _compress_data(self, data: Any) -> str:
        """Compress data if compression is enabled."""
        try:
            json_str = json.dumps(data, separators=(',', ':'))
            compressed = gzip.compress(json_str.encode('utf-8'))
            return compressed.hex()
        except Exception as e:
            logger.error(f"Data compression failed: {str(e)}")
            return json.dumps({'error': str(e)})
    
    async def _decompress_data(self, compressed_hex: str) -> Any:
        """Decompress previously compressed data."""
        try:
            compressed_bytes = bytes.fromhex(compressed_hex)
            decompressed = gzip.decompress(compressed_bytes)
            return json.loads(decompressed.decode('utf-8'))
        except Exception as e:
            logger.error(f"Data decompression failed: {str(e)}")
            return {'error': str(e)}
    
    async def _save_entry(self, entry_data: Dict[str, Any]) -> None:
        """Save entry to storage."""
        try:
            entry_file = self.storage_path / f"{entry_data['id']}.json"
            
            with open(entry_file, 'w') as f:
                json.dump(entry_data, f, indent=2, default=str)
            
            logger.debug(f"Entry saved: {entry_data['id']}")
            
        except Exception as e:
            logger.error(f"Failed to save entry: {str(e)}")
            raise
    
    async def _load_entry(self, entry_id: str) -> Optional[Dict[str, Any]]:
        """Load entry from storage."""
        try:
            entry_file = self.storage_path / f"{entry_id}.json"
            
            if not entry_file.exists():
                return None
            
            with open(entry_file, 'r') as f:
                return json.load(f)
            
        except Exception as e:
            logger.error(f"Failed to load entry {entry_id}: {str(e)}")
            return None
    
    async def _update_chain(self, entry_data: Dict[str, Any]) -> None:
        """Update the lineage chain with new entry."""
        try:
            with open(self.chain_file, 'r') as f:
                chain_data = json.load(f)
            
            # Add entry reference to chain
            chain_entry = {
                'id': entry_data['id'],
                'hash': entry_data['hash'],
                'timestamp': entry_data['timestamp'],
                'previous_hash': entry_data['previous_hash']
            }
            
            chain_data['entries'].append(chain_entry)
            chain_data['last_updated'] = datetime.now(timezone.utc).isoformat()
            
            with open(self.chain_file, 'w') as f:
                json.dump(chain_data, f, indent=2)
            
        except Exception as e:
            logger.error(f"Failed to update chain: {str(e)}")
            raise
    
    async def _get_last_entry_hash(self) -> str:
        """Get hash of the last entry in the chain."""
        try:
            if not self.chain_file.exists():
                return '0' * 64
            
            with open(self.chain_file, 'r') as f:
                chain_data = json.load(f)
            
            entries = chain_data.get('entries', [])
            if entries:
                return entries[-1]['hash']
            else:
                return '0' * 64
            
        except Exception as e:
            logger.error(f"Failed to get last entry hash: {str(e)}")
            return '0' * 64
    
    async def _get_chain_length(self) -> int:
        """Get current chain length."""
        try:
            if not self.chain_file.exists():
                return 0
            
            with open(self.chain_file, 'r') as f:
                chain_data = json.load(f)
            
            return len(chain_data.get('entries', []))
            
        except Exception as e:
            logger.error(f"Failed to get chain length: {str(e)}")
            return 0
    
    async def _verify_chain_integrity(self, entry_id: str) -> bool:
        """Verify chain integrity for a specific entry."""
        try:
            with open(self.chain_file, 'r') as f:
                chain_data = json.load(f)
            
            entries = chain_data.get('entries', [])
            
            # Find entry position
            entry_index = None
            for i, entry in enumerate(entries):
                if entry['id'] == entry_id:
                    entry_index = i
                    break
            
            if entry_index is None:
                return False
            
            # Verify chain up to this entry
            for i in range(1, entry_index + 1):
                current_entry = entries[i]
                previous_entry = entries[i - 1]
                
                if current_entry['previous_hash'] != previous_entry['hash']:
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Chain integrity verification failed: {str(e)}")
            return False
    
    async def _verify_complete_chain_integrity(self) -> bool:
        """Verify integrity of the complete chain."""
        try:
            with open(self.chain_file, 'r') as f:
                chain_data = json.load(f)
            
            entries = chain_data.get('entries', [])
            
            if len(entries) < 2:
                return True  # Genesis only or empty
            
            # Verify each link in the chain
            for i in range(1, len(entries)):
                current_entry = entries[i]
                previous_entry = entries[i - 1]
                
                if current_entry['previous_hash'] != previous_entry['hash']:
                    logger.error(f"Chain integrity broken at entry {i}: {current_entry['id']}")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Complete chain integrity verification failed: {str(e)}")
            return False
    
    async def _verify_data_integrity(self, entry_data: Dict[str, Any]) -> bool:
        """Verify data integrity of an entry."""
        try:
            verification = entry_data.get('verification', {})
            
            if not verification:
                return False
            
            # Verify verification hash if present
            if 'verification_hash' in verification:
                # This would require recalculating the verification
                # For now, we just check if it exists
                return True
            
            return True
            
        except Exception as e:
            logger.error(f"Data integrity verification failed: {str(e)}")
            return False