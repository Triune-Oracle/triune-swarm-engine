"""
MirrorLineage-Δ Immutable Logging System

Provides cryptographic verification and tamper-proof audit trails for the
MirrorWatcherAI automation system. Implements the MirrorLineage-Δ protocol
for immutable logging with cryptographic integrity verification.

Features:
- Immutable log entries with cryptographic chaining
- Session-based tracking and lifecycle management
- Merkle tree construction for data integrity
- Digital signatures and hash verification
- Comprehensive audit trails
- Recovery and validation mechanisms
"""

import asyncio
import json
import hashlib
import time
import logging
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import os
import sqlite3
import threading
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64


class MirrorLineageDelta:
    """MirrorLineage-Δ immutable logging system with cryptographic verification."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.crypto_enabled = config.get("crypto_enabled", True)
        self.signature_algorithm = config.get("signature_algorithm", "ed25519")
        self.storage_path = Path(config.get("storage_path", ".shadowscrolls/lineage"))
        self.logger = logging.getLogger("MirrorLineageDelta")
        
        # Initialize storage
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.db_path = self.storage_path / "lineage.db"
        self.keys_path = self.storage_path / "keys"
        self.keys_path.mkdir(exist_ok=True)
        
        # Initialize database
        self.db_lock = threading.Lock()
        self._init_database()
        
        # Initialize cryptography
        if self.crypto_enabled:
            self.private_key, self.public_key = self._load_or_generate_keys()
        else:
            self.private_key = None
            self.public_key = None
        
        # Session tracking
        self.active_sessions = {}
    
    def _init_database(self):
        """Initialize SQLite database for lineage tracking."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS lineage_sessions (
                        session_id TEXT PRIMARY KEY,
                        started_at TEXT NOT NULL,
                        finished_at TEXT,
                        status TEXT NOT NULL DEFAULT 'active',
                        metadata TEXT,
                        entry_count INTEGER DEFAULT 0,
                        last_hash TEXT,
                        signature TEXT
                    )
                ''')
                
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS lineage_entries (
                        entry_id TEXT PRIMARY KEY,
                        session_id TEXT NOT NULL,
                        sequence_number INTEGER NOT NULL,
                        timestamp TEXT NOT NULL,
                        entry_type TEXT NOT NULL,
                        content_hash TEXT NOT NULL,
                        previous_hash TEXT NOT NULL,
                        merkle_root TEXT NOT NULL,
                        signature TEXT,
                        content TEXT NOT NULL,
                        metadata TEXT,
                        FOREIGN KEY (session_id) REFERENCES lineage_sessions (session_id)
                    )
                ''')
                
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS lineage_chain (
                        chain_id TEXT PRIMARY KEY,
                        genesis_hash TEXT NOT NULL,
                        current_hash TEXT NOT NULL,
                        entry_count INTEGER DEFAULT 0,
                        created_at TEXT NOT NULL,
                        updated_at TEXT NOT NULL
                    )
                ''')
                
                conn.commit()
                self.logger.info("✅ MirrorLineage-Δ database initialized")
                
        except Exception as e:
            self.logger.error(f"❌ Database initialization failed: {e}")
            raise
    
    def _load_or_generate_keys(self) -> Tuple[ed25519.Ed25519PrivateKey, ed25519.Ed25519PublicKey]:
        """Load existing keys or generate new ones for signing."""
        private_key_path = self.keys_path / "private_key.pem"
        public_key_path = self.keys_path / "public_key.pem"
        
        try:
            if private_key_path.exists() and public_key_path.exists():
                # Load existing keys
                with open(private_key_path, 'rb') as f:
                    private_key = serialization.load_pem_private_key(f.read(), password=None)
                
                with open(public_key_path, 'rb') as f:
                    public_key = serialization.load_pem_public_key(f.read())
                
                self.logger.info("🔑 Loaded existing Ed25519 keys")
                return private_key, public_key
            
        except Exception as e:
            self.logger.warning(f"Failed to load existing keys: {e}")
        
        # Generate new keys
        try:
            private_key = ed25519.Ed25519PrivateKey.generate()
            public_key = private_key.public_key()
            
            # Save keys
            with open(private_key_path, 'wb') as f:
                f.write(private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                ))
            
            with open(public_key_path, 'wb') as f:
                f.write(public_key.public_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo
                ))
            
            # Set appropriate permissions
            os.chmod(private_key_path, 0o600)
            os.chmod(public_key_path, 0o644)
            
            self.logger.info("🔑 Generated new Ed25519 keys")
            return private_key, public_key
            
        except Exception as e:
            self.logger.error(f"❌ Key generation failed: {e}")
            raise
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on the lineage system."""
        try:
            # Check database connectivity
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("SELECT COUNT(*) FROM lineage_sessions")
                session_count = cursor.fetchone()[0]
                
                cursor = conn.execute("SELECT COUNT(*) FROM lineage_entries")
                entry_count = cursor.fetchone()[0]
            
            # Check cryptographic system
            crypto_status = "enabled" if self.crypto_enabled else "disabled"
            if self.crypto_enabled and self.private_key and self.public_key:
                # Test signing capability
                test_data = b"health_check_test"
                signature = self.private_key.sign(test_data)
                
                # Test verification
                try:
                    self.public_key.verify(signature, test_data)
                    crypto_status = "fully_functional"
                except:
                    crypto_status = "signing_error"
            
            return {
                "status": "healthy",
                "database": {
                    "path": str(self.db_path),
                    "sessions": session_count,
                    "entries": entry_count
                },
                "cryptography": {
                    "status": crypto_status,
                    "algorithm": self.signature_algorithm,
                    "keys_available": bool(self.private_key and self.public_key)
                },
                "storage": {
                    "path": str(self.storage_path),
                    "writable": os.access(self.storage_path, os.W_OK)
                }
            }
            
        except Exception as e:
            raise Exception(f"Health check failed: {e}")
    
    async def start_session(self, session_id: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Start a new lineage tracking session."""
        try:
            self.logger.info(f"🆔 Starting lineage session: {session_id}")
            
            timestamp = datetime.now(timezone.utc).isoformat()
            
            # Initialize session tracking
            session_data = {
                "session_id": session_id,
                "started_at": timestamp,
                "status": "active",
                "entries": [],
                "current_sequence": 0,
                "last_hash": "genesis",
                "metadata": metadata or {}
            }
            
            self.active_sessions[session_id] = session_data
            
            # Store in database
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT INTO lineage_sessions 
                    (session_id, started_at, status, metadata, last_hash)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    session_id,
                    timestamp,
                    "active",
                    json.dumps(metadata or {}),
                    "genesis"
                ))
                conn.commit()
            
            # Create genesis entry
            genesis_entry = await self._create_entry(
                session_id=session_id,
                entry_type="genesis",
                content={"action": "session_start", "timestamp": timestamp},
                metadata={"genesis": True}
            )
            
            self.logger.info(f"✅ Session started: {session_id}")
            
            return {
                "session_id": session_id,
                "started_at": timestamp,
                "genesis_entry": genesis_entry,
                "status": "active"
            }
            
        except Exception as e:
            self.logger.error(f"❌ Session start failed: {e}")
            raise
    
    async def add_entry(
        self,
        session_id: str,
        entry_type: str,
        content: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Add an entry to an active session."""
        if session_id not in self.active_sessions:
            raise Exception(f"Session not active: {session_id}")
        
        return await self._create_entry(session_id, entry_type, content, metadata)
    
    async def _create_entry(
        self,
        session_id: str,
        entry_type: str,
        content: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create a new lineage entry with cryptographic verification."""
        try:
            timestamp = datetime.now(timezone.utc).isoformat()
            
            # Get session data
            session_data = self.active_sessions.get(session_id)
            if not session_data:
                raise Exception(f"Session not found: {session_id}")
            
            # Generate entry ID and sequence
            sequence_number = session_data["current_sequence"] + 1
            entry_id = f"{session_id}-{sequence_number:04d}-{int(time.time())}"
            
            # Calculate content hash
            content_json = json.dumps(content, sort_keys=True, separators=(',', ':'))
            content_hash = hashlib.sha256(content_json.encode()).hexdigest()
            
            # Get previous hash
            previous_hash = session_data["last_hash"]
            
            # Calculate Merkle root
            merkle_root = self._calculate_merkle_root(content, metadata or {})
            
            # Create entry data for signing
            entry_data = {
                "entry_id": entry_id,
                "session_id": session_id,
                "sequence_number": sequence_number,
                "timestamp": timestamp,
                "entry_type": entry_type,
                "content_hash": content_hash,
                "previous_hash": previous_hash,
                "merkle_root": merkle_root,
                "content": content,
                "metadata": metadata or {}
            }
            
            # Create signature
            signature = None
            if self.crypto_enabled and self.private_key:
                signature_data = self._create_signature_data(entry_data)
                signature_bytes = self.private_key.sign(signature_data.encode())
                signature = base64.b64encode(signature_bytes).decode()
                entry_data["signature"] = signature
            
            # Calculate chain hash for next entry
            chain_data = f"{entry_id}:{content_hash}:{merkle_root}:{timestamp}"
            chain_hash = hashlib.sha256(chain_data.encode()).hexdigest()
            
            # Store in database
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT INTO lineage_entries 
                    (entry_id, session_id, sequence_number, timestamp, entry_type,
                     content_hash, previous_hash, merkle_root, signature, content, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    entry_id, session_id, sequence_number, timestamp, entry_type,
                    content_hash, previous_hash, merkle_root, signature,
                    json.dumps(content), json.dumps(metadata or {})
                ))
                
                # Update session
                conn.execute('''
                    UPDATE lineage_sessions 
                    SET entry_count = entry_count + 1, last_hash = ?
                    WHERE session_id = ?
                ''', (chain_hash, session_id))
                
                conn.commit()
            
            # Update session tracking
            session_data["current_sequence"] = sequence_number
            session_data["last_hash"] = chain_hash
            session_data["entries"].append(entry_data)
            
            self.logger.debug(f"📝 Entry created: {entry_id}")
            
            return entry_data
            
        except Exception as e:
            self.logger.error(f"❌ Entry creation failed: {e}")
            raise
    
    def _create_signature_data(self, entry_data: Dict[str, Any]) -> str:
        """Create canonical data for signing."""
        # Create a deterministic string representation for signing
        signature_fields = [
            "entry_id", "session_id", "sequence_number", "timestamp",
            "entry_type", "content_hash", "previous_hash", "merkle_root"
        ]
        
        signature_data = ":".join(str(entry_data.get(field, "")) for field in signature_fields)
        return signature_data
    
    def _calculate_merkle_root(self, content: Dict[str, Any], metadata: Dict[str, Any]) -> str:
        """Calculate Merkle root for content and metadata."""
        try:
            # Combine content and metadata
            combined_data = {"content": content, "metadata": metadata}
            
            # Flatten the data structure
            def flatten_dict(d, parent_key='', sep='.'):
                items = []
                for k, v in d.items():
                    new_key = f"{parent_key}{sep}{k}" if parent_key else k
                    if isinstance(v, dict):
                        items.extend(flatten_dict(v, new_key, sep=sep).items())
                    elif isinstance(v, list):
                        for i, item in enumerate(v):
                            if isinstance(item, dict):
                                items.extend(flatten_dict(item, f"{new_key}[{i}]", sep=sep).items())
                            else:
                                items.append((f"{new_key}[{i}]", str(item)))
                    else:
                        items.append((new_key, str(v)))
                return dict(items)
            
            flattened = flatten_dict(combined_data)
            
            # Create leaf hashes
            leaves = []
            for key, value in sorted(flattened.items()):
                leaf_data = f"{key}={value}"
                leaf_hash = hashlib.sha256(leaf_data.encode()).hexdigest()
                leaves.append(leaf_hash)
            
            # Build Merkle tree
            if not leaves:
                return hashlib.sha256(b"empty").hexdigest()
            
            current_level = leaves
            while len(current_level) > 1:
                next_level = []
                for i in range(0, len(current_level), 2):
                    if i + 1 < len(current_level):
                        combined = current_level[i] + current_level[i + 1]
                    else:
                        combined = current_level[i] + current_level[i]  # Duplicate if odd
                    
                    next_hash = hashlib.sha256(combined.encode()).hexdigest()
                    next_level.append(next_hash)
                
                current_level = next_level
            
            return current_level[0]
            
        except Exception as e:
            self.logger.warning(f"Merkle root calculation failed: {e}")
            return hashlib.sha256(json.dumps(combined_data, sort_keys=True).encode()).hexdigest()
    
    async def finalize_session(
        self,
        session_id: str,
        final_results: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Finalize a lineage session and create final attestation."""
        try:
            self.logger.info(f"🔒 Finalizing lineage session: {session_id}")
            
            if session_id not in self.active_sessions:
                raise Exception(f"Session not active: {session_id}")
            
            session_data = self.active_sessions[session_id]
            timestamp = datetime.now(timezone.utc).isoformat()
            
            # Create finalization entry
            finalization_content = {
                "action": "session_finalize",
                "timestamp": timestamp,
                "entry_count": session_data["current_sequence"],
                "final_results": final_results or {}
            }
            
            finalization_entry = await self._create_entry(
                session_id=session_id,
                entry_type="finalization",
                content=finalization_content,
                metadata={"finalization": True, "immutable": True}
            )
            
            # Create session signature if crypto enabled
            session_signature = None
            if self.crypto_enabled and self.private_key:
                session_summary = {
                    "session_id": session_id,
                    "entry_count": session_data["current_sequence"],
                    "first_hash": "genesis",
                    "last_hash": session_data["last_hash"],
                    "finalized_at": timestamp
                }
                
                summary_data = json.dumps(session_summary, sort_keys=True)
                signature_bytes = self.private_key.sign(summary_data.encode())
                session_signature = base64.b64encode(signature_bytes).decode()
            
            # Update database
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    UPDATE lineage_sessions 
                    SET finished_at = ?, status = ?, signature = ?
                    WHERE session_id = ?
                ''', (timestamp, "finalized", session_signature, session_id))
                conn.commit()
            
            # Remove from active sessions
            finalized_session = self.active_sessions.pop(session_id)
            
            # Create final summary
            summary = {
                "session_id": session_id,
                "started_at": finalized_session["started_at"],
                "finalized_at": timestamp,
                "total_entries": session_data["current_sequence"],
                "final_hash": session_data["last_hash"],
                "finalization_entry": finalization_entry,
                "session_signature": session_signature,
                "immutable": True
            }
            
            self.logger.info(f"✅ Session finalized: {session_id}")
            
            return summary
            
        except Exception as e:
            self.logger.error(f"❌ Session finalization failed: {e}")
            raise
    
    async def verify_session(self, session_id: str) -> Dict[str, Any]:
        """Verify the integrity of a complete session."""
        try:
            self.logger.info(f"🔍 Verifying session: {session_id}")
            
            verification_result = {
                "session_id": session_id,
                "verification_time": datetime.now(timezone.utc).isoformat(),
                "status": "unknown",
                "checks": {},
                "errors": []
            }
            
            with sqlite3.connect(self.db_path) as conn:
                # Get session info
                cursor = conn.execute('''
                    SELECT started_at, finished_at, status, metadata, entry_count, signature
                    FROM lineage_sessions WHERE session_id = ?
                ''', (session_id,))
                
                session_row = cursor.fetchone()
                if not session_row:
                    verification_result["status"] = "not_found"
                    verification_result["errors"].append("Session not found in database")
                    return verification_result
                
                # Get all entries
                cursor = conn.execute('''
                    SELECT entry_id, sequence_number, timestamp, entry_type, content_hash,
                           previous_hash, merkle_root, signature, content, metadata
                    FROM lineage_entries 
                    WHERE session_id = ? 
                    ORDER BY sequence_number
                ''', (session_id,))
                
                entries = cursor.fetchall()
            
            # Verify entry chain
            verification_result["checks"]["chain_integrity"] = self._verify_chain_integrity(entries)
            
            # Verify signatures
            verification_result["checks"]["signatures"] = self._verify_entry_signatures(entries)
            
            # Verify content hashes
            verification_result["checks"]["content_hashes"] = self._verify_content_hashes(entries)
            
            # Verify Merkle roots
            verification_result["checks"]["merkle_roots"] = self._verify_merkle_roots(entries)
            
            # Determine overall status
            all_checks = [check["valid"] for check in verification_result["checks"].values()]
            
            if all(all_checks):
                verification_result["status"] = "valid"
            elif any(all_checks):
                verification_result["status"] = "partial"
            else:
                verification_result["status"] = "invalid"
            
            self.logger.info(f"✅ Verification completed: {verification_result['status']}")
            
            return verification_result
            
        except Exception as e:
            self.logger.error(f"❌ Session verification failed: {e}")
            raise
    
    def _verify_chain_integrity(self, entries: List[Tuple]) -> Dict[str, Any]:
        """Verify the integrity of the entry chain."""
        try:
            if not entries:
                return {"valid": False, "error": "No entries found"}
            
            previous_hash = "genesis"
            valid_chain = True
            errors = []
            
            for entry in entries:
                entry_id, seq_num, timestamp, entry_type, content_hash, prev_hash, merkle_root, signature, content, metadata = entry
                
                if prev_hash != previous_hash:
                    valid_chain = False
                    errors.append(f"Chain break at entry {entry_id}: expected {previous_hash}, got {prev_hash}")
                
                # Calculate expected next hash
                chain_data = f"{entry_id}:{content_hash}:{merkle_root}:{timestamp}"
                next_hash = hashlib.sha256(chain_data.encode()).hexdigest()
                previous_hash = next_hash
            
            return {
                "valid": valid_chain,
                "total_entries": len(entries),
                "errors": errors
            }
            
        except Exception as e:
            return {"valid": False, "error": str(e)}
    
    def _verify_entry_signatures(self, entries: List[Tuple]) -> Dict[str, Any]:
        """Verify digital signatures of entries."""
        if not self.crypto_enabled or not self.public_key:
            return {"valid": True, "skipped": "Crypto not enabled or no public key"}
        
        try:
            valid_signatures = 0
            total_signatures = 0
            errors = []
            
            for entry in entries:
                entry_id, seq_num, timestamp, entry_type, content_hash, prev_hash, merkle_root, signature, content, metadata = entry
                
                if not signature:
                    continue
                
                total_signatures += 1
                
                # Reconstruct signature data
                entry_data = {
                    "entry_id": entry_id,
                    "session_id": entry_id.split('-')[0],  # Extract from entry_id
                    "sequence_number": seq_num,
                    "timestamp": timestamp,
                    "entry_type": entry_type,
                    "content_hash": content_hash,
                    "previous_hash": prev_hash,
                    "merkle_root": merkle_root
                }
                
                signature_data = self._create_signature_data(entry_data)
                
                try:
                    signature_bytes = base64.b64decode(signature)
                    self.public_key.verify(signature_bytes, signature_data.encode())
                    valid_signatures += 1
                except Exception as e:
                    errors.append(f"Invalid signature for entry {entry_id}: {e}")
            
            return {
                "valid": valid_signatures == total_signatures if total_signatures > 0 else True,
                "valid_signatures": valid_signatures,
                "total_signatures": total_signatures,
                "errors": errors
            }
            
        except Exception as e:
            return {"valid": False, "error": str(e)}
    
    def _verify_content_hashes(self, entries: List[Tuple]) -> Dict[str, Any]:
        """Verify content hashes of entries."""
        try:
            valid_hashes = 0
            total_entries = len(entries)
            errors = []
            
            for entry in entries:
                entry_id, seq_num, timestamp, entry_type, content_hash, prev_hash, merkle_root, signature, content, metadata = entry
                
                # Recalculate content hash
                try:
                    content_data = json.loads(content)
                    content_json = json.dumps(content_data, sort_keys=True, separators=(',', ':'))
                    calculated_hash = hashlib.sha256(content_json.encode()).hexdigest()
                    
                    if calculated_hash == content_hash:
                        valid_hashes += 1
                    else:
                        errors.append(f"Hash mismatch for entry {entry_id}")
                        
                except Exception as e:
                    errors.append(f"Hash calculation failed for entry {entry_id}: {e}")
            
            return {
                "valid": valid_hashes == total_entries,
                "valid_hashes": valid_hashes,
                "total_entries": total_entries,
                "errors": errors
            }
            
        except Exception as e:
            return {"valid": False, "error": str(e)}
    
    def _verify_merkle_roots(self, entries: List[Tuple]) -> Dict[str, Any]:
        """Verify Merkle roots of entries."""
        try:
            valid_roots = 0
            total_entries = len(entries)
            errors = []
            
            for entry in entries:
                entry_id, seq_num, timestamp, entry_type, content_hash, prev_hash, stored_merkle_root, signature, content, metadata = entry
                
                try:
                    content_data = json.loads(content)
                    metadata_data = json.loads(metadata) if metadata else {}
                    
                    calculated_merkle_root = self._calculate_merkle_root(content_data, metadata_data)
                    
                    if calculated_merkle_root == stored_merkle_root:
                        valid_roots += 1
                    else:
                        errors.append(f"Merkle root mismatch for entry {entry_id}")
                        
                except Exception as e:
                    errors.append(f"Merkle root calculation failed for entry {entry_id}: {e}")
            
            return {
                "valid": valid_roots == total_entries,
                "valid_roots": valid_roots,
                "total_entries": total_entries,
                "errors": errors
            }
            
        except Exception as e:
            return {"valid": False, "error": str(e)}
    
    async def get_session_summary(self, session_id: str) -> Dict[str, Any]:
        """Get a summary of a lineage session."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Get session info
                cursor = conn.execute('''
                    SELECT started_at, finished_at, status, metadata, entry_count, signature
                    FROM lineage_sessions WHERE session_id = ?
                ''', (session_id,))
                
                session_row = cursor.fetchone()
                if not session_row:
                    raise Exception(f"Session not found: {session_id}")
                
                started_at, finished_at, status, metadata, entry_count, signature = session_row
                
                # Get entry summary
                cursor = conn.execute('''
                    SELECT entry_type, COUNT(*) as count
                    FROM lineage_entries 
                    WHERE session_id = ?
                    GROUP BY entry_type
                ''', (session_id,))
                
                entry_types = dict(cursor.fetchall())
                
                return {
                    "session_id": session_id,
                    "started_at": started_at,
                    "finished_at": finished_at,
                    "status": status,
                    "metadata": json.loads(metadata) if metadata else {},
                    "entry_count": entry_count,
                    "entry_types": entry_types,
                    "has_signature": bool(signature),
                    "is_finalized": status == "finalized"
                }
                
        except Exception as e:
            self.logger.error(f"Failed to get session summary: {e}")
            raise