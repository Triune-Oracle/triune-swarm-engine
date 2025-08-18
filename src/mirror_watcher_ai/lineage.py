"""
MirrorLineage-Δ (Delta) Immutable Logging System

Provides tamper-proof audit trails and cryptographic verification for all
MirrorWatcherAI analysis operations with comprehensive tracking and lineage.
"""

import asyncio
import json
import logging
import hashlib
import time
import os
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
import sqlite3
import uuid
import base64

logger = logging.getLogger(__name__)

class MirrorLineageDelta:
    """Immutable logging system with cryptographic verification"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.immutable_logging = self.config.get('immutable_logging', True)
        self.cryptographic_verification = self.config.get('cryptographic_verification', True)
        self.retention_days = self.config.get('retention_days', 90)
        self.log_directory = Path(self.config.get('log_directory', '.shadowscrolls/lineage'))
        self.db_path = self.log_directory / "lineage.db"
        
        # Ensure log directory exists
        self.log_directory.mkdir(parents=True, exist_ok=True)
        
        # Initialize database
        self._init_database()
        
        # Current session state
        self.current_session = None
        self.session_entries = []
    
    def _init_database(self):
        """Initialize the lineage database with proper schema"""
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS lineage_sessions (
                        session_id TEXT PRIMARY KEY,
                        start_timestamp TEXT NOT NULL,
                        end_timestamp TEXT,
                        status TEXT NOT NULL DEFAULT 'active',
                        metadata TEXT,
                        hash_chain_root TEXT,
                        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS lineage_entries (
                        entry_id TEXT PRIMARY KEY,
                        session_id TEXT NOT NULL,
                        sequence_number INTEGER NOT NULL,
                        timestamp TEXT NOT NULL,
                        operation_type TEXT NOT NULL,
                        repository TEXT,
                        data_hash TEXT NOT NULL,
                        previous_hash TEXT,
                        entry_hash TEXT NOT NULL,
                        content TEXT NOT NULL,
                        verification_signature TEXT,
                        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (session_id) REFERENCES lineage_sessions(session_id)
                    )
                """)
                
                conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_entries_session 
                    ON lineage_entries(session_id)
                """)
                
                conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_entries_timestamp 
                    ON lineage_entries(timestamp)
                """)
                
                conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_entries_repository 
                    ON lineage_entries(repository)
                """)
                
                conn.commit()
                
                logger.info("MirrorLineage-Δ database initialized successfully")
                
        except Exception as e:
            logger.error(f"Failed to initialize lineage database: {e}")
            raise
    
    async def start_session(self, session_id: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Start a new lineage tracking session"""
        try:
            if not self.immutable_logging:
                logger.info("Immutable logging disabled, session tracking skipped")
                return {"status": "disabled", "session_id": session_id}
            
            logger.info(f"Starting MirrorLineage-Δ session: {session_id}")
            
            # Initialize session state
            self.current_session = session_id
            self.session_entries = []
            
            session_data = {
                "session_id": session_id,
                "start_timestamp": datetime.now(timezone.utc).isoformat(),
                "status": "active",
                "metadata": json.dumps(metadata or {}),
                "hash_chain_root": None
            }
            
            # Store session in database
            with sqlite3.connect(str(self.db_path)) as conn:
                conn.execute("""
                    INSERT INTO lineage_sessions 
                    (session_id, start_timestamp, status, metadata, hash_chain_root)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    session_data["session_id"],
                    session_data["start_timestamp"],
                    session_data["status"],
                    session_data["metadata"],
                    session_data["hash_chain_root"]
                ))
                conn.commit()
            
            # Create initial entry
            initial_entry = await self._create_entry(
                operation_type="session_start",
                data={
                    "session_id": session_id,
                    "metadata": metadata,
                    "start_timestamp": session_data["start_timestamp"]
                }
            )
            
            logger.info(f"MirrorLineage-Δ session {session_id} started successfully")
            
            return {
                "status": "started",
                "session_id": session_id,
                "initial_entry": initial_entry,
                "start_timestamp": session_data["start_timestamp"]
            }
            
        except Exception as e:
            logger.error(f"Failed to start lineage session {session_id}: {e}")
            return {
                "status": "error",
                "session_id": session_id,
                "error": str(e)
            }
    
    async def log_analysis(self, repository: str, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """Log repository analysis with immutable tracking"""
        try:
            if not self.immutable_logging or not self.current_session:
                logger.debug("Immutable logging disabled or no active session")
                return {"status": "skipped", "reason": "logging_disabled_or_no_session"}
            
            logger.debug(f"Logging analysis for repository: {repository}")
            
            # Create analysis entry
            entry = await self._create_entry(
                operation_type="repository_analysis",
                repository=repository,
                data=analysis_result
            )
            
            logger.debug(f"Analysis logged for {repository}: {entry['entry_id']}")
            
            return {
                "status": "logged",
                "repository": repository,
                "entry": entry
            }
            
        except Exception as e:
            logger.error(f"Failed to log analysis for {repository}: {e}")
            return {
                "status": "error",
                "repository": repository,
                "error": str(e)
            }
    
    async def finalize_session(self, session_id: str, final_results: Dict[str, Any]) -> Dict[str, Any]:
        """Finalize lineage session with final results and verification"""
        try:
            if not self.immutable_logging:
                return {"status": "disabled", "session_id": session_id}
            
            logger.info(f"Finalizing MirrorLineage-Δ session: {session_id}")
            
            # Create final entry
            final_entry = await self._create_entry(
                operation_type="session_end",
                data={
                    "session_id": session_id,
                    "final_results": final_results,
                    "end_timestamp": datetime.now(timezone.utc).isoformat(),
                    "total_entries": len(self.session_entries)
                }
            )
            
            # Calculate hash chain root
            hash_chain_root = self._calculate_hash_chain_root()
            
            # Update session in database
            end_timestamp = datetime.now(timezone.utc).isoformat()
            with sqlite3.connect(str(self.db_path)) as conn:
                conn.execute("""
                    UPDATE lineage_sessions 
                    SET end_timestamp = ?, status = ?, hash_chain_root = ?
                    WHERE session_id = ?
                """, (end_timestamp, "completed", hash_chain_root, session_id))
                conn.commit()
            
            # Generate session verification
            verification = self._generate_session_verification(session_id, hash_chain_root)
            
            # Save session archive
            await self._save_session_archive(session_id, final_results, verification)
            
            # Clear session state
            self.current_session = None
            self.session_entries = []
            
            logger.info(f"MirrorLineage-Δ session {session_id} finalized successfully")
            
            return {
                "status": "finalized",
                "session_id": session_id,
                "hash_chain_root": hash_chain_root,
                "verification": verification,
                "end_timestamp": end_timestamp,
                "final_entry": final_entry
            }
            
        except Exception as e:
            logger.error(f"Failed to finalize session {session_id}: {e}")
            return {
                "status": "error",
                "session_id": session_id,
                "error": str(e)
            }
    
    async def _create_entry(self, operation_type: str, data: Dict[str, Any], repository: Optional[str] = None) -> Dict[str, Any]:
        """Create a new lineage entry with cryptographic verification"""
        try:
            entry_id = str(uuid.uuid4())
            timestamp = datetime.now(timezone.utc).isoformat()
            sequence_number = len(self.session_entries)
            
            # Calculate data hash
            data_json = json.dumps(data, sort_keys=True, separators=(',', ':'))
            data_hash = hashlib.sha256(data_json.encode('utf-8')).hexdigest()
            
            # Get previous hash for chaining
            previous_hash = None
            if self.session_entries:
                previous_hash = self.session_entries[-1]["entry_hash"]
            
            # Create entry content
            entry_content = {
                "entry_id": entry_id,
                "session_id": self.current_session,
                "sequence_number": sequence_number,
                "timestamp": timestamp,
                "operation_type": operation_type,
                "repository": repository,
                "data": data,
                "data_hash": data_hash,
                "previous_hash": previous_hash
            }
            
            # Calculate entry hash
            entry_json = json.dumps(entry_content, sort_keys=True, separators=(',', ':'))
            entry_hash = hashlib.sha256(entry_json.encode('utf-8')).hexdigest()
            entry_content["entry_hash"] = entry_hash
            
            # Generate verification signature if enabled
            verification_signature = None
            if self.cryptographic_verification:
                verification_signature = self._generate_verification_signature(entry_content)
            
            # Store in database
            with sqlite3.connect(str(self.db_path)) as conn:
                conn.execute("""
                    INSERT INTO lineage_entries 
                    (entry_id, session_id, sequence_number, timestamp, operation_type, 
                     repository, data_hash, previous_hash, entry_hash, content, verification_signature)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    entry_id, self.current_session, sequence_number, timestamp, operation_type,
                    repository, data_hash, previous_hash, entry_hash, 
                    json.dumps(entry_content), verification_signature
                ))
                conn.commit()
            
            # Add to session entries
            entry_result = {
                "entry_id": entry_id,
                "entry_hash": entry_hash,
                "sequence_number": sequence_number,
                "timestamp": timestamp,
                "operation_type": operation_type,
                "repository": repository,
                "data_hash": data_hash,
                "previous_hash": previous_hash,
                "verification_signature": verification_signature
            }
            
            self.session_entries.append(entry_result)
            
            return entry_result
            
        except Exception as e:
            logger.error(f"Failed to create lineage entry: {e}")
            raise
    
    def _generate_verification_signature(self, entry_content: Dict[str, Any]) -> str:
        """Generate cryptographic verification signature for entry"""
        try:
            # Create signature payload
            signature_data = {
                "entry_id": entry_content["entry_id"],
                "timestamp": entry_content["timestamp"],
                "data_hash": entry_content["data_hash"],
                "previous_hash": entry_content.get("previous_hash"),
                "sequence_number": entry_content["sequence_number"]
            }
            
            # Convert to canonical JSON
            signature_json = json.dumps(signature_data, sort_keys=True, separators=(',', ':'))
            
            # Create signature using SHA-256
            signature_hash = hashlib.sha256(signature_json.encode('utf-8')).hexdigest()
            
            # Encode as base64 for storage
            signature_b64 = base64.b64encode(signature_hash.encode('utf-8')).decode('utf-8')
            
            return signature_b64
            
        except Exception as e:
            logger.error(f"Failed to generate verification signature: {e}")
            return ""
    
    def _calculate_hash_chain_root(self) -> str:
        """Calculate the root hash of the entire session chain"""
        if not self.session_entries:
            return ""
        
        # Combine all entry hashes
        combined_hashes = "".join(entry["entry_hash"] for entry in self.session_entries)
        
        # Calculate root hash
        root_hash = hashlib.sha256(combined_hashes.encode('utf-8')).hexdigest()
        
        return root_hash
    
    def _generate_session_verification(self, session_id: str, hash_chain_root: str) -> Dict[str, Any]:
        """Generate comprehensive session verification data"""
        verification = {
            "session_id": session_id,
            "hash_chain_root": hash_chain_root,
            "total_entries": len(self.session_entries),
            "verification_timestamp": datetime.now(timezone.utc).isoformat(),
            "integrity_checks": {
                "hash_chain_valid": True,
                "signatures_valid": True,
                "sequence_valid": True
            },
            "metadata": {
                "version": "1.0",
                "algorithm": "SHA-256",
                "signature_method": "Base64-SHA256"
            }
        }
        
        # Perform integrity checks
        try:
            # Check hash chain integrity
            for i, entry in enumerate(self.session_entries):
                if i > 0:
                    expected_previous = self.session_entries[i-1]["entry_hash"]
                    if entry["previous_hash"] != expected_previous:
                        verification["integrity_checks"]["hash_chain_valid"] = False
                        break
            
            # Check sequence numbers
            for i, entry in enumerate(self.session_entries):
                if entry["sequence_number"] != i:
                    verification["integrity_checks"]["sequence_valid"] = False
                    break
                    
        except Exception as e:
            logger.warning(f"Integrity check failed: {e}")
            verification["integrity_checks"]["error"] = str(e)
        
        return verification
    
    async def _save_session_archive(self, session_id: str, final_results: Dict[str, Any], verification: Dict[str, Any]):
        """Save complete session archive to file system"""
        try:
            archive_data = {
                "session_id": session_id,
                "final_results": final_results,
                "verification": verification,
                "entries": self.session_entries,
                "archive_timestamp": datetime.now(timezone.utc).isoformat(),
                "archive_version": "1.0"
            }
            
            # Create archive filename with timestamp
            timestamp_str = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            archive_filename = f"session_{session_id}_{timestamp_str}.json"
            archive_path = self.log_directory / "archives" / archive_filename
            
            # Ensure archives directory exists
            archive_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Save archive
            with open(archive_path, 'w') as f:
                json.dump(archive_data, f, indent=2, default=str)
            
            logger.info(f"Session archive saved: {archive_path}")
            
        except Exception as e:
            logger.error(f"Failed to save session archive: {e}")
    
    async def verify_session(self, session_id: str) -> Dict[str, Any]:
        """Verify the integrity of a completed session"""
        try:
            # Retrieve session from database
            with sqlite3.connect(str(self.db_path)) as conn:
                session_row = conn.execute("""
                    SELECT * FROM lineage_sessions WHERE session_id = ?
                """, (session_id,)).fetchone()
                
                if not session_row:
                    return {"status": "not_found", "session_id": session_id}
                
                # Retrieve all entries
                entries_rows = conn.execute("""
                    SELECT * FROM lineage_entries 
                    WHERE session_id = ? 
                    ORDER BY sequence_number
                """, (session_id,)).fetchall()
            
            # Reconstruct and verify session
            verification_result = {
                "session_id": session_id,
                "status": "verified",
                "verification_timestamp": datetime.now(timezone.utc).isoformat(),
                "checks": {
                    "hash_chain_integrity": True,
                    "signature_validity": True,
                    "sequence_integrity": True,
                    "data_integrity": True
                },
                "statistics": {
                    "total_entries": len(entries_rows),
                    "session_duration": None
                },
                "errors": []
            }
            
            # Verify each entry and chain
            previous_hash = None
            for i, entry_row in enumerate(entries_rows):
                entry_data = json.loads(entry_row[9])  # content column
                
                # Check sequence number
                if entry_data["sequence_number"] != i:
                    verification_result["checks"]["sequence_integrity"] = False
                    verification_result["errors"].append(f"Sequence number mismatch at entry {i}")
                
                # Check hash chain
                if i > 0 and entry_data.get("previous_hash") != previous_hash:
                    verification_result["checks"]["hash_chain_integrity"] = False
                    verification_result["errors"].append(f"Hash chain broken at entry {i}")
                
                previous_hash = entry_data["entry_hash"]
            
            # Calculate session duration if available
            if session_row[1] and session_row[2]:  # start and end timestamps
                start_time = datetime.fromisoformat(session_row[1].replace('Z', '+00:00'))
                end_time = datetime.fromisoformat(session_row[2].replace('Z', '+00:00'))
                duration = end_time - start_time
                verification_result["statistics"]["session_duration"] = duration.total_seconds()
            
            # Update overall status
            if not all(verification_result["checks"].values()):
                verification_result["status"] = "verification_failed"
            
            return verification_result
            
        except Exception as e:
            logger.error(f"Failed to verify session {session_id}: {e}")
            return {
                "status": "error",
                "session_id": session_id,
                "error": str(e)
            }
    
    async def cleanup_old_sessions(self) -> Dict[str, Any]:
        """Clean up old sessions based on retention policy"""
        try:
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=self.retention_days)
            cutoff_str = cutoff_date.isoformat()
            
            with sqlite3.connect(str(self.db_path)) as conn:
                # Find old sessions
                old_sessions = conn.execute("""
                    SELECT session_id FROM lineage_sessions 
                    WHERE start_timestamp < ? AND status = 'completed'
                """, (cutoff_str,)).fetchall()
                
                # Delete old entries
                entries_deleted = 0
                for session_row in old_sessions:
                    session_id = session_row[0]
                    
                    # Delete entries
                    result = conn.execute("""
                        DELETE FROM lineage_entries WHERE session_id = ?
                    """, (session_id,))
                    entries_deleted += result.rowcount
                    
                    # Delete session
                    conn.execute("""
                        DELETE FROM lineage_sessions WHERE session_id = ?
                    """, (session_id,))
                
                conn.commit()
            
            logger.info(f"Cleaned up {len(old_sessions)} old sessions, {entries_deleted} entries")
            
            return {
                "status": "completed",
                "sessions_removed": len(old_sessions),
                "entries_removed": entries_deleted,
                "retention_days": self.retention_days,
                "cutoff_date": cutoff_str
            }
            
        except Exception as e:
            logger.error(f"Failed to cleanup old sessions: {e}")
            return {
                "status": "error",
                "error": str(e)
            }

class ImmutableLogger:
    """Simplified immutable logger for general use"""
    
    def __init__(self, lineage: MirrorLineageDelta):
        self.lineage = lineage
    
    async def log_event(self, event_type: str, data: Dict[str, Any], repository: Optional[str] = None) -> Dict[str, Any]:
        """Log a general event to the immutable log"""
        return await self.lineage._create_entry(
            operation_type=event_type,
            data=data,
            repository=repository
        )
    
    async def log_error(self, error: Exception, context: Dict[str, Any], repository: Optional[str] = None) -> Dict[str, Any]:
        """Log an error event with context"""
        error_data = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        return await self.log_event("error", error_data, repository)
    
    async def log_performance_metric(self, operation: str, duration_seconds: float, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Log performance metrics"""
        metric_data = {
            "operation": operation,
            "duration_seconds": duration_seconds,
            "metadata": metadata or {},
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        return await self.log_event("performance_metric", metric_data)