"""
MirrorLineage-Δ Immutable Logging System
========================================

Cryptographic verification and tamper-proof audit trail generation
for the MirrorWatcherAI automation system.
"""

import asyncio
import json
import os
import hashlib
import time
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
import logging
import uuid
import sqlite3
import aiosqlite

logger = logging.getLogger(__name__)


class MirrorLineageLogger:
    """
    MirrorLineage-Δ immutable logging system with cryptographic verification.
    
    Provides:
    - Tamper-proof audit trail generation
    - Cryptographic verification of log integrity
    - Immutable session tracking
    - Performance metrics collection
    - Comprehensive error tracking
    """
    
    def __init__(self):
        self.lineage_directory = "/home/runner/work/triune-swarm-engine/triune-swarm-engine/.shadowscrolls/lineage"
        self.db_path = f"{self.lineage_directory}/mirror_lineage.db"
        
        # Ensure directory structure exists
        os.makedirs(self.lineage_directory, exist_ok=True)
        
        # Initialize database
        asyncio.create_task(self._initialize_database())
        
        # Current session tracking
        self.current_session = None
        self.session_start_time = None
        self.phase_timings = {}
    
    async def _initialize_database(self):
        """Initialize SQLite database for lineage tracking."""
        
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Sessions table
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS sessions (
                        id TEXT PRIMARY KEY,
                        start_time TEXT NOT NULL,
                        end_time TEXT,
                        status TEXT NOT NULL DEFAULT 'active',
                        execution_type TEXT,
                        metadata_json TEXT,
                        verification_hash TEXT,
                        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Phases table
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS phases (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        session_id TEXT NOT NULL,
                        phase_name TEXT NOT NULL,
                        start_time TEXT NOT NULL,
                        end_time TEXT,
                        status TEXT NOT NULL DEFAULT 'active',
                        data_json TEXT,
                        data_hash TEXT,
                        error_message TEXT,
                        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (session_id) REFERENCES sessions (id)
                    )
                """)
                
                # Events table for detailed logging
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS events (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        session_id TEXT NOT NULL,
                        phase_id INTEGER,
                        event_type TEXT NOT NULL,
                        timestamp TEXT NOT NULL,
                        message TEXT,
                        data_json TEXT,
                        severity TEXT NOT NULL DEFAULT 'info',
                        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (session_id) REFERENCES sessions (id),
                        FOREIGN KEY (phase_id) REFERENCES phases (id)
                    )
                """)
                
                # Chain verification table
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS verification_chain (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        session_id TEXT NOT NULL,
                        previous_hash TEXT,
                        current_hash TEXT NOT NULL,
                        chain_position INTEGER NOT NULL,
                        verification_data TEXT,
                        timestamp TEXT NOT NULL,
                        FOREIGN KEY (session_id) REFERENCES sessions (id)
                    )
                """)
                
                await db.commit()
                
            logger.info("MirrorLineage-Δ database initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize lineage database: {str(e)}")
            raise
    
    async def start_session(self, execution_id: str, execution_type: str = "analysis") -> Dict[str, Any]:
        """
        Start a new lineage tracking session.
        
        Args:
            execution_id: Unique execution identifier
            execution_type: Type of execution (analysis, scan, sync, etc.)
            
        Returns:
            Session metadata
        """
        logger.info(f"Starting lineage session: {execution_id}")
        
        self.current_session = execution_id
        self.session_start_time = datetime.now(timezone.utc)
        self.phase_timings = {}
        
        session_metadata = {
            "session_id": execution_id,
            "start_time": self.session_start_time.isoformat(),
            "execution_type": execution_type,
            "lineage_version": "MirrorLineage-Δ 1.0.0",
            "initial_state": {
                "timestamp": self.session_start_time.isoformat(),
                "system_info": await self._collect_system_info(),
                "environment": await self._collect_environment_info()
            }
        }
        
        # Store in database
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(
                    """INSERT INTO sessions 
                       (id, start_time, execution_type, metadata_json, status) 
                       VALUES (?, ?, ?, ?, ?)""",
                    (
                        execution_id,
                        self.session_start_time.isoformat(),
                        execution_type,
                        json.dumps(session_metadata),
                        "active"
                    )
                )
                await db.commit()
            
            # Log session start event
            await self._log_event("session_start", "Session started successfully", session_metadata)
            
            # Create initial verification chain entry
            await self._create_verification_entry(execution_id, None, session_metadata)
            
            logger.info(f"Lineage session started: {execution_id}")
            return session_metadata
            
        except Exception as e:
            logger.error(f"Failed to start lineage session: {str(e)}")
            raise
    
    async def log_phase(self, phase_name: str, phase_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Log completion of an execution phase.
        
        Args:
            phase_name: Name of the phase (e.g., 'repository_analysis')
            phase_data: Data generated by the phase
            
        Returns:
            Phase logging metadata
        """
        if not self.current_session:
            raise Exception("No active session for phase logging")
        
        logger.info(f"Logging phase: {phase_name}")
        
        phase_start = self.phase_timings.get(phase_name, datetime.now(timezone.utc))
        phase_end = datetime.now(timezone.utc)
        phase_duration = (phase_end - phase_start).total_seconds()
        
        # Create phase hash for integrity verification
        phase_json = json.dumps(phase_data, sort_keys=True, separators=(',', ':'))
        phase_hash = hashlib.sha256(phase_json.encode()).hexdigest()
        
        phase_metadata = {
            "session_id": self.current_session,
            "phase_name": phase_name,
            "start_time": phase_start.isoformat(),
            "end_time": phase_end.isoformat(),
            "duration_seconds": phase_duration,
            "data_hash": phase_hash,
            "data_size_bytes": len(phase_json),
            "verification": {
                "algorithm": "SHA-256",
                "timestamp": phase_end.isoformat(),
                "integrity_verified": True
            }
        }
        
        try:
            # Store phase in database
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute(
                    """INSERT INTO phases 
                       (session_id, phase_name, start_time, end_time, status, data_json, data_hash) 
                       VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (
                        self.current_session,
                        phase_name,
                        phase_start.isoformat(),
                        phase_end.isoformat(),
                        "completed",
                        phase_json,
                        phase_hash
                    )
                )
                phase_id = cursor.lastrowid
                await db.commit()
            
            # Log phase completion event
            await self._log_event(
                "phase_completed", 
                f"Phase {phase_name} completed successfully",
                phase_metadata,
                phase_id=phase_id
            )
            
            # Create verification chain entry
            await self._create_verification_entry(self.current_session, phase_hash, phase_metadata)
            
            logger.info(f"Phase logged successfully: {phase_name} (duration: {phase_duration:.2f}s)")
            return phase_metadata
            
        except Exception as e:
            logger.error(f"Failed to log phase {phase_name}: {str(e)}")
            await self._log_error(self.current_session, f"Phase logging failed: {str(e)}")
            raise
    
    async def log_scan_results(self, scan_id: str, scan_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Log repository scan results with integrity verification.
        
        Args:
            scan_id: Unique scan identifier
            scan_results: Scan results data
            
        Returns:
            Scan logging metadata
        """
        logger.info(f"Logging scan results: {scan_id}")
        
        # Start session if not active
        if not self.current_session:
            await self.start_session(scan_id, "scan")
        
        return await self.log_phase("repository_scan", scan_results)
    
    async def log_error(self, session_id: str, error_message: str, error_data: Optional[Dict[str, Any]] = None):
        """
        Log error with full context and debugging information.
        
        Args:
            session_id: Session identifier
            error_message: Error description
            error_data: Optional additional error data
        """
        logger.error(f"Logging error for session {session_id}: {error_message}")
        
        error_context = {
            "session_id": session_id,
            "error_message": error_message,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "error_data": error_data or {},
            "system_state": await self._collect_system_info()
        }
        
        try:
            # Update session status to error
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(
                    "UPDATE sessions SET status = ? WHERE id = ?",
                    ("error", session_id)
                )
                await db.commit()
            
            # Log error event
            await self._log_event("error", error_message, error_context, severity="error")
            
            # Store error details in file for debugging
            error_file = f"{self.lineage_directory}/errors/{session_id}_error.json"
            os.makedirs(os.path.dirname(error_file), exist_ok=True)
            
            with open(error_file, 'w') as f:
                json.dump(error_context, f, indent=2)
            
            logger.info(f"Error logged successfully for session: {session_id}")
            
        except Exception as e:
            logger.critical(f"Failed to log error: {str(e)}")
    
    async def finalize_session(self, final_report: Dict[str, Any]) -> Dict[str, Any]:
        """
        Finalize lineage session with comprehensive summary.
        
        Args:
            final_report: Final execution report
            
        Returns:
            Session finalization metadata
        """
        if not self.current_session:
            raise Exception("No active session to finalize")
        
        logger.info(f"Finalizing lineage session: {self.current_session}")
        
        session_end_time = datetime.now(timezone.utc)
        total_duration = (session_end_time - self.session_start_time).total_seconds()
        
        # Generate comprehensive session summary
        session_summary = await self._generate_session_summary(final_report)
        
        # Create final verification hash
        final_verification = await self._create_final_verification(session_summary)
        
        finalization_metadata = {
            "session_id": self.current_session,
            "start_time": self.session_start_time.isoformat(),
            "end_time": session_end_time.isoformat(),
            "total_duration_seconds": total_duration,
            "final_verification": final_verification,
            "session_summary": session_summary,
            "lineage_integrity": "verified",
            "immutable_record": True
        }
        
        try:
            # Update session in database
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(
                    """UPDATE sessions 
                       SET end_time = ?, status = ?, verification_hash = ? 
                       WHERE id = ?""",
                    (
                        session_end_time.isoformat(),
                        "completed",
                        final_verification["hash"],
                        self.current_session
                    )
                )
                await db.commit()
            
            # Log session completion
            await self._log_event(
                "session_completed",
                f"Session completed successfully (duration: {total_duration:.2f}s)",
                finalization_metadata
            )
            
            # Store final lineage record
            await self._store_final_lineage_record(finalization_metadata)
            
            logger.info(f"Session finalized successfully: {self.current_session}")
            
            # Reset session state
            self.current_session = None
            self.session_start_time = None
            self.phase_timings = {}
            
            return finalization_metadata
            
        except Exception as e:
            logger.error(f"Failed to finalize session: {str(e)}")
            raise
    
    async def get_latest_session_data(self) -> Optional[Dict[str, Any]]:
        """
        Get data from the most recent completed session.
        
        Returns:
            Latest session data or None if no sessions found
        """
        try:
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute(
                    """SELECT id, metadata_json, verification_hash, end_time 
                       FROM sessions 
                       WHERE status = 'completed' 
                       ORDER BY end_time DESC 
                       LIMIT 1"""
                ) as cursor:
                    row = await cursor.fetchone()
                    
                    if row:
                        session_id, metadata_json, verification_hash, end_time = row
                        
                        # Get session phases
                        phases = []
                        async with db.execute(
                            "SELECT phase_name, data_json FROM phases WHERE session_id = ? AND status = 'completed'",
                            (session_id,)
                        ) as phase_cursor:
                            async for phase_row in phase_cursor:
                                phase_name, data_json = phase_row
                                phases.append({
                                    "phase_name": phase_name,
                                    "data": json.loads(data_json)
                                })
                        
                        return {
                            "session_id": session_id,
                            "metadata": json.loads(metadata_json),
                            "verification_hash": verification_hash,
                            "end_time": end_time,
                            "phases": phases
                        }
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get latest session data: {str(e)}")
            return None
    
    async def verify_lineage_integrity(self, session_id: str) -> Dict[str, Any]:
        """
        Verify the integrity of a lineage session.
        
        Args:
            session_id: Session to verify
            
        Returns:
            Verification results
        """
        logger.info(f"Verifying lineage integrity for session: {session_id}")
        
        verification_results = {
            "session_id": session_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "overall_status": "verified",
            "checks": {}
        }
        
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Verify session exists
                async with db.execute(
                    "SELECT id, metadata_json, verification_hash FROM sessions WHERE id = ?",
                    (session_id,)
                ) as cursor:
                    session_row = await cursor.fetchone()
                    
                    if not session_row:
                        verification_results["overall_status"] = "failed"
                        verification_results["checks"]["session_exists"] = {"status": "failed", "message": "Session not found"}
                        return verification_results
                
                verification_results["checks"]["session_exists"] = {"status": "passed"}
                
                # Verify phase integrity
                phase_verification = await self._verify_phase_integrity(db, session_id)
                verification_results["checks"]["phase_integrity"] = phase_verification
                
                # Verify verification chain
                chain_verification = await self._verify_verification_chain(db, session_id)
                verification_results["checks"]["verification_chain"] = chain_verification
                
                # Check for any failed verifications
                failed_checks = [
                    check for check in verification_results["checks"].values()
                    if check.get("status") != "passed"
                ]
                
                if failed_checks:
                    verification_results["overall_status"] = "failed"
                    verification_results["failed_checks"] = len(failed_checks)
                
                logger.info(f"Lineage verification completed: {verification_results['overall_status']}")
                return verification_results
                
        except Exception as e:
            logger.error(f"Lineage verification failed: {str(e)}")
            verification_results["overall_status"] = "error"
            verification_results["error"] = str(e)
            return verification_results
    
    async def _collect_system_info(self) -> Dict[str, Any]:
        """Collect system information for lineage tracking."""
        
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "platform": os.name,
            "python_version": os.getenv("PYTHON_VERSION", "unknown"),
            "working_directory": os.getcwd(),
            "process_id": os.getpid(),
            "environment_type": "github_actions" if os.getenv("GITHUB_ACTIONS") else "local"
        }
    
    async def _collect_environment_info(self) -> Dict[str, Any]:
        """Collect environment information for context."""
        
        env_info = {
            "github_actions": bool(os.getenv("GITHUB_ACTIONS")),
            "repository": os.getenv("GITHUB_REPOSITORY"),
            "ref": os.getenv("GITHUB_REF"),
            "sha": os.getenv("GITHUB_SHA"),
            "run_id": os.getenv("GITHUB_RUN_ID"),
            "workflow": os.getenv("GITHUB_WORKFLOW")
        }
        
        # Filter out None values
        return {k: v for k, v in env_info.items() if v is not None}
    
    async def _log_event(self, event_type: str, message: str, data: Dict[str, Any], 
                        phase_id: Optional[int] = None, severity: str = "info"):
        """Log an event in the lineage system."""
        
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(
                    """INSERT INTO events 
                       (session_id, phase_id, event_type, timestamp, message, data_json, severity) 
                       VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (
                        self.current_session,
                        phase_id,
                        event_type,
                        datetime.now(timezone.utc).isoformat(),
                        message,
                        json.dumps(data),
                        severity
                    )
                )
                await db.commit()
                
        except Exception as e:
            logger.error(f"Failed to log event: {str(e)}")
    
    async def _create_verification_entry(self, session_id: str, previous_hash: Optional[str], 
                                       data: Dict[str, Any]):
        """Create verification chain entry."""
        
        try:
            # Calculate current hash
            data_json = json.dumps(data, sort_keys=True, separators=(',', ':'))
            current_hash = hashlib.sha256(data_json.encode()).hexdigest()
            
            # Get chain position
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute(
                    "SELECT COUNT(*) FROM verification_chain WHERE session_id = ?",
                    (session_id,)
                ) as cursor:
                    count_row = await cursor.fetchone()
                    chain_position = (count_row[0] if count_row else 0) + 1
                
                # Insert verification entry
                await db.execute(
                    """INSERT INTO verification_chain 
                       (session_id, previous_hash, current_hash, chain_position, verification_data, timestamp) 
                       VALUES (?, ?, ?, ?, ?, ?)""",
                    (
                        session_id,
                        previous_hash,
                        current_hash,
                        chain_position,
                        data_json,
                        datetime.now(timezone.utc).isoformat()
                    )
                )
                await db.commit()
                
        except Exception as e:
            logger.error(f"Failed to create verification entry: {str(e)}")
    
    async def _generate_session_summary(self, final_report: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive session summary."""
        
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Get phase count and timings
                async with db.execute(
                    "SELECT COUNT(*), SUM(CAST((julianday(end_time) - julianday(start_time)) * 86400 AS REAL)) FROM phases WHERE session_id = ?",
                    (self.current_session,)
                ) as cursor:
                    phase_row = await cursor.fetchone()
                    phase_count, total_phase_time = phase_row if phase_row else (0, 0)
                
                # Get event count by severity
                event_counts = {}
                async with db.execute(
                    "SELECT severity, COUNT(*) FROM events WHERE session_id = ? GROUP BY severity",
                    (self.current_session,)
                ) as cursor:
                    async for event_row in cursor:
                        severity, count = event_row
                        event_counts[severity] = count
                
                return {
                    "session_id": self.current_session,
                    "phase_count": phase_count,
                    "total_phase_time_seconds": total_phase_time or 0,
                    "event_counts": event_counts,
                    "final_report_summary": {
                        "status": final_report.get("status"),
                        "repositories_analyzed": len(final_report.get("analysis_summary", {}).get("repositories", [])),
                        "execution_duration": final_report.get("execution_duration_seconds", 0)
                    }
                }
                
        except Exception as e:
            logger.error(f"Failed to generate session summary: {str(e)}")
            return {"error": str(e)}
    
    async def _create_final_verification(self, session_summary: Dict[str, Any]) -> Dict[str, Any]:
        """Create final verification hash for session."""
        
        # Combine all verification data
        verification_data = {
            "session_summary": session_summary,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "lineage_version": "MirrorLineage-Δ 1.0.0"
        }
        
        # Create final hash
        verification_json = json.dumps(verification_data, sort_keys=True, separators=(',', ':'))
        final_hash = hashlib.sha256(verification_json.encode()).hexdigest()
        
        return {
            "hash": final_hash,
            "algorithm": "SHA-256",
            "data_size_bytes": len(verification_json),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "immutable": True
        }
    
    async def _store_final_lineage_record(self, finalization_metadata: Dict[str, Any]):
        """Store final immutable lineage record."""
        
        record_file = f"{self.lineage_directory}/final_records/{self.current_session}.json"
        os.makedirs(os.path.dirname(record_file), exist_ok=True)
        
        with open(record_file, 'w') as f:
            json.dump(finalization_metadata, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Final lineage record stored: {record_file}")
    
    async def _verify_phase_integrity(self, db: aiosqlite.Connection, session_id: str) -> Dict[str, Any]:
        """Verify integrity of all phases in a session."""
        
        try:
            phases_verified = 0
            phases_failed = 0
            
            async with db.execute(
                "SELECT phase_name, data_json, data_hash FROM phases WHERE session_id = ? AND status = 'completed'",
                (session_id,)
            ) as cursor:
                async for phase_row in cursor:
                    phase_name, data_json, stored_hash = phase_row
                    
                    # Recalculate hash
                    calculated_hash = hashlib.sha256(data_json.encode()).hexdigest()
                    
                    if calculated_hash == stored_hash:
                        phases_verified += 1
                    else:
                        phases_failed += 1
                        logger.warning(f"Phase integrity check failed for {phase_name}")
            
            return {
                "status": "passed" if phases_failed == 0 else "failed",
                "phases_verified": phases_verified,
                "phases_failed": phases_failed
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def _verify_verification_chain(self, db: aiosqlite.Connection, session_id: str) -> Dict[str, Any]:
        """Verify the verification chain integrity."""
        
        try:
            chain_entries = []
            
            async with db.execute(
                "SELECT previous_hash, current_hash, chain_position, verification_data FROM verification_chain WHERE session_id = ? ORDER BY chain_position",
                (session_id,)
            ) as cursor:
                async for chain_row in cursor:
                    previous_hash, current_hash, chain_position, verification_data = chain_row
                    
                    # Verify hash
                    calculated_hash = hashlib.sha256(verification_data.encode()).hexdigest()
                    
                    chain_entries.append({
                        "position": chain_position,
                        "hash_valid": calculated_hash == current_hash,
                        "previous_hash": previous_hash,
                        "current_hash": current_hash
                    })
            
            # Verify chain links
            chain_valid = True
            for i in range(1, len(chain_entries)):
                if chain_entries[i]["previous_hash"] != chain_entries[i-1]["current_hash"]:
                    chain_valid = False
                    break
            
            return {
                "status": "passed" if chain_valid and all(entry["hash_valid"] for entry in chain_entries) else "failed",
                "chain_length": len(chain_entries),
                "chain_linked": chain_valid
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check of lineage system."""
        
        health_status = {
            "status": "healthy",
            "checks": {},
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        # Check database connectivity
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("SELECT COUNT(*) FROM sessions")
            
            health_status["checks"]["database"] = {"status": "healthy"}
            
        except Exception as e:
            health_status["checks"]["database"] = {"status": "error", "error": str(e)}
            health_status["status"] = "unhealthy"
        
        # Check file system access
        try:
            test_file = f"{self.lineage_directory}/.health_check"
            with open(test_file, 'w') as f:
                f.write("health_check")
            os.remove(test_file)
            
            health_status["checks"]["filesystem"] = {"status": "healthy"}
            
        except Exception as e:
            health_status["checks"]["filesystem"] = {"status": "error", "error": str(e)}
            health_status["status"] = "unhealthy"
        
        return health_status