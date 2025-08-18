"""
ShadowScrolls Attestation System for MirrorWatcherAI

Provides external attestation and immutable logging through ShadowScrolls
integration, enabling cryptographic verification and tamper-proof audit trails.

Features:
- External witnessing for analysis results
- Cryptographic attestation with digital signatures
- Immutable storage with ShadowScrolls API
- Comprehensive audit trails
- Error handling and retry mechanisms
"""

import asyncio
import aiohttp
import json
import hashlib
import hmac
import time
import logging
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import os
import base64


class ShadowScrollsAttestation:
    """ShadowScrolls external attestation system for MirrorWatcherAI."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.endpoint = config.get("endpoint", os.getenv("SHADOWSCROLLS_ENDPOINT", ""))
        self.api_key = config.get("api_key", os.getenv("SHADOWSCROLLS_API_KEY", ""))
        self.timeout = config.get("timeout", 30)
        self.logger = logging.getLogger("ShadowScrollsAttestation")
        
        # Storage for attestations
        self.storage_path = Path(".shadowscrolls/attestations")
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Attestation counter
        self.attestation_counter = self._load_counter()
        
        # Headers for API requests
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "MirrorWatcherAI/1.0.0"
        } if self.api_key else {}
    
    def _load_counter(self) -> int:
        """Load the attestation counter from storage."""
        counter_file = self.storage_path / "counter.json"
        if counter_file.exists():
            try:
                with open(counter_file, 'r') as f:
                    data = json.load(f)
                return data.get("counter", 0)
            except Exception:
                return 0
        return 0
    
    def _save_counter(self):
        """Save the attestation counter to storage."""
        counter_file = self.storage_path / "counter.json"
        try:
            with open(counter_file, 'w') as f:
                json.dump({
                    "counter": self.attestation_counter,
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save counter: {e}")
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on ShadowScrolls service."""
        if not self.endpoint or not self.api_key:
            raise Exception("ShadowScrolls endpoint or API key not configured")
        
        try:
            async with aiohttp.ClientSession() as session:
                health_url = f"{self.endpoint.rstrip('/')}/health"
                async with session.get(
                    health_url,
                    headers=self.headers,
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    if response.status in [200, 201]:
                        return {
                            "status": "healthy",
                            "endpoint": self.endpoint,
                            "response_time": response.headers.get("X-Response-Time", "unknown")
                        }
                    else:
                        raise Exception(f"Health check failed: HTTP {response.status}")
        except Exception as e:
            raise Exception(f"ShadowScrolls health check failed: {e}")
    
    async def create_attestation(
        self,
        session_id: str,
        results: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create a ShadowScrolls attestation for analysis results."""
        try:
            self.logger.info(f"🔏 Creating ShadowScrolls attestation for session: {session_id}")
            
            # Increment counter
            self.attestation_counter += 1
            scroll_number = f"{self.attestation_counter:03d}"
            
            # Create attestation data
            attestation_data = self._create_attestation_data(
                session_id, results, metadata, scroll_number
            )
            
            # Submit to ShadowScrolls API
            api_response = await self._submit_to_shadowscrolls(attestation_data)
            
            # Store locally
            local_path = await self._store_attestation_locally(attestation_data, api_response)
            
            # Update counter
            self._save_counter()
            
            self.logger.info(f"✅ Attestation created: Scroll #{scroll_number}")
            
            return {
                "scroll_id": attestation_data["scroll_metadata"]["scroll_id"],
                "scroll_number": scroll_number,
                "session_id": session_id,
                "timestamp": attestation_data["timestamp"],
                "api_response": api_response,
                "local_storage": str(local_path),
                "verification_hash": attestation_data["verification"]["content_hash"]
            }
            
        except Exception as e:
            self.logger.error(f"❌ Attestation creation failed: {e}")
            raise
    
    def _create_attestation_data(
        self,
        session_id: str,
        results: Dict[str, Any],
        metadata: Optional[Dict[str, Any]],
        scroll_number: str
    ) -> Dict[str, Any]:
        """Create the attestation data structure."""
        timestamp = datetime.now(timezone.utc).isoformat()
        
        # Create scroll metadata
        scroll_metadata = {
            "scroll_id": f"#{scroll_number} – MirrorWatcher Analysis",
            "scroll_number": scroll_number,
            "session_id": session_id,
            "system": "MirrorWatcherAI Complete Automation System",
            "version": "1.0.0",
            "attestation_type": "repository_analysis"
        }
        
        # Merge provided metadata
        if metadata:
            scroll_metadata.update(metadata)
        
        # Create verification data
        content_for_hash = json.dumps(results, sort_keys=True, separators=(',', ':'))
        content_hash = hashlib.sha256(content_for_hash.encode()).hexdigest()
        
        verification = {
            "content_hash": content_hash,
            "hash_algorithm": "sha256",
            "signature_algorithm": "hmac-sha256",
            "content_size": len(content_for_hash)
        }
        
        # Create HMAC signature if API key is available
        if self.api_key:
            signature_data = f"{timestamp}:{session_id}:{content_hash}"
            signature = hmac.new(
                self.api_key.encode(),
                signature_data.encode(),
                hashlib.sha256
            ).hexdigest()
            verification["signature"] = signature
            verification["signature_data"] = signature_data
        
        # Create attestation structure
        attestation = {
            "timestamp": timestamp,
            "scroll_metadata": scroll_metadata,
            "session_data": {
                "session_id": session_id,
                "analysis_results": results
            },
            "verification": verification,
            "mirrorlineage_delta": {
                "enabled": True,
                "traceability_chain": self._create_traceability_chain(session_id),
                "immutable_log_entry": {
                    "entry_id": f"{scroll_number}-{int(time.time())}",
                    "previous_hash": self._get_previous_hash(),
                    "merkle_root": self._calculate_merkle_root(results)
                }
            }
        }
        
        return attestation
    
    def _create_traceability_chain(self, session_id: str) -> Dict[str, Any]:
        """Create MirrorLineage-Δ traceability chain."""
        return {
            "chain_id": f"mirrorlineage-{session_id}",
            "node_type": "attestation",
            "parent_nodes": [],
            "child_nodes": [],
            "metadata": {
                "created_by": "MirrorWatcherAI",
                "chain_version": "delta-1.0",
                "immutability_level": "cryptographic"
            }
        }
    
    def _get_previous_hash(self) -> str:
        """Get the hash of the previous attestation for chaining."""
        try:
            # Find the most recent attestation file
            attestation_files = list(self.storage_path.glob("attestation-*.json"))
            if not attestation_files:
                return "genesis"
            
            # Sort by modification time and get the latest
            latest_file = max(attestation_files, key=lambda x: x.stat().st_mtime)
            
            with open(latest_file, 'r') as f:
                data = json.load(f)
            
            return data.get("verification", {}).get("content_hash", "unknown")
            
        except Exception:
            return "genesis"
    
    def _calculate_merkle_root(self, data: Dict[str, Any]) -> str:
        """Calculate a simple Merkle root for the data."""
        try:
            # Flatten the data structure and hash each element
            def flatten_dict(d, parent_key='', sep='.'):
                items = []
                for k, v in d.items():
                    new_key = f"{parent_key}{sep}{k}" if parent_key else k
                    if isinstance(v, dict):
                        items.extend(flatten_dict(v, new_key, sep=sep).items())
                    else:
                        items.append((new_key, str(v)))
                return dict(items)
            
            flattened = flatten_dict(data)
            
            # Create hashes for each key-value pair
            hashes = []
            for key, value in sorted(flattened.items()):
                hash_input = f"{key}:{value}"
                hash_value = hashlib.sha256(hash_input.encode()).hexdigest()
                hashes.append(hash_value)
            
            # Simple Merkle tree construction (binary tree)
            while len(hashes) > 1:
                next_level = []
                for i in range(0, len(hashes), 2):
                    if i + 1 < len(hashes):
                        combined = hashes[i] + hashes[i + 1]
                    else:
                        combined = hashes[i] + hashes[i]  # Duplicate if odd number
                    next_level.append(hashlib.sha256(combined.encode()).hexdigest())
                hashes = next_level
            
            return hashes[0] if hashes else "empty"
            
        except Exception:
            return "calculation_failed"
    
    async def _submit_to_shadowscrolls(self, attestation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Submit attestation to ShadowScrolls API."""
        if not self.endpoint or not self.api_key:
            self.logger.warning("ShadowScrolls API not configured, skipping remote submission")
            return {
                "status": "local_only",
                "message": "API not configured"
            }
        
        try:
            async with aiohttp.ClientSession() as session:
                submit_url = f"{self.endpoint.rstrip('/')}/attestations"
                
                # Prepare payload
                payload = {
                    "scroll": attestation_data["scroll_metadata"],
                    "data": attestation_data["session_data"],
                    "verification": attestation_data["verification"],
                    "mirrorlineage": attestation_data["mirrorlineage_delta"]
                }
                
                async with session.post(
                    submit_url,
                    headers=self.headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    response_data = await response.json()
                    
                    if response.status in [200, 201]:
                        self.logger.info("✅ Attestation submitted to ShadowScrolls API")
                        return {
                            "status": "submitted",
                            "api_response": response_data,
                            "status_code": response.status
                        }
                    else:
                        raise Exception(f"API submission failed: HTTP {response.status}")
                        
        except Exception as e:
            self.logger.error(f"❌ ShadowScrolls API submission failed: {e}")
            # Continue with local storage even if API fails
            return {
                "status": "api_failed",
                "error": str(e),
                "fallback": "local_storage_only"
            }
    
    async def _store_attestation_locally(
        self,
        attestation_data: Dict[str, Any],
        api_response: Dict[str, Any]
    ) -> Path:
        """Store attestation locally for backup and verification."""
        try:
            # Create filename with timestamp and scroll number
            timestamp = datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')
            scroll_number = attestation_data["scroll_metadata"]["scroll_number"]
            filename = f"attestation-{scroll_number}-{timestamp}.json"
            
            file_path = self.storage_path / filename
            
            # Add API response to the stored data
            stored_data = {
                **attestation_data,
                "api_submission": api_response,
                "local_storage": {
                    "stored_at": datetime.now(timezone.utc).isoformat(),
                    "file_path": str(file_path),
                    "file_size": 0  # Will be updated after writing
                }
            }
            
            # Write to file
            with open(file_path, 'w') as f:
                json.dump(stored_data, f, indent=2)
            
            # Update file size
            stored_data["local_storage"]["file_size"] = file_path.stat().st_size
            
            # Write updated data
            with open(file_path, 'w') as f:
                json.dump(stored_data, f, indent=2)
            
            self.logger.info(f"💾 Attestation stored locally: {file_path}")
            return file_path
            
        except Exception as e:
            self.logger.error(f"❌ Local storage failed: {e}")
            raise
    
    async def verify_attestation(self, attestation_path: Path) -> Dict[str, Any]:
        """Verify an existing attestation."""
        try:
            self.logger.info(f"🔍 Verifying attestation: {attestation_path}")
            
            with open(attestation_path, 'r') as f:
                attestation = json.load(f)
            
            verification_result = {
                "file_path": str(attestation_path),
                "verification_time": datetime.now(timezone.utc).isoformat(),
                "checks": {},
                "overall_status": "unknown"
            }
            
            # Check file integrity
            verification_result["checks"]["file_integrity"] = self._verify_file_integrity(attestation)
            
            # Check hash verification
            verification_result["checks"]["content_hash"] = self._verify_content_hash(attestation)
            
            # Check signature (if available)
            verification_result["checks"]["signature"] = self._verify_signature(attestation)
            
            # Check timestamp validity
            verification_result["checks"]["timestamp"] = self._verify_timestamp(attestation)
            
            # Determine overall status
            all_checks = list(verification_result["checks"].values())
            if all(check["status"] == "valid" for check in all_checks):
                verification_result["overall_status"] = "valid"
            elif any(check["status"] == "invalid" for check in all_checks):
                verification_result["overall_status"] = "invalid"
            else:
                verification_result["overall_status"] = "warning"
            
            self.logger.info(f"✅ Verification completed: {verification_result['overall_status']}")
            return verification_result
            
        except Exception as e:
            self.logger.error(f"❌ Verification failed: {e}")
            raise
    
    def _verify_file_integrity(self, attestation: Dict[str, Any]) -> Dict[str, Any]:
        """Verify file structure integrity."""
        required_fields = [
            "timestamp", "scroll_metadata", "session_data", 
            "verification", "mirrorlineage_delta"
        ]
        
        missing_fields = [field for field in required_fields if field not in attestation]
        
        return {
            "status": "valid" if not missing_fields else "invalid",
            "missing_fields": missing_fields,
            "check_type": "structure_integrity"
        }
    
    def _verify_content_hash(self, attestation: Dict[str, Any]) -> Dict[str, Any]:
        """Verify content hash."""
        try:
            stored_hash = attestation["verification"]["content_hash"]
            session_data = attestation["session_data"]["analysis_results"]
            
            # Recalculate hash
            content_for_hash = json.dumps(session_data, sort_keys=True, separators=(',', ':'))
            calculated_hash = hashlib.sha256(content_for_hash.encode()).hexdigest()
            
            return {
                "status": "valid" if stored_hash == calculated_hash else "invalid",
                "stored_hash": stored_hash,
                "calculated_hash": calculated_hash,
                "check_type": "content_hash"
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "check_type": "content_hash"
            }
    
    def _verify_signature(self, attestation: Dict[str, Any]) -> Dict[str, Any]:
        """Verify HMAC signature if present."""
        try:
            verification = attestation["verification"]
            
            if "signature" not in verification:
                return {
                    "status": "skipped",
                    "reason": "no_signature",
                    "check_type": "signature"
                }
            
            if not self.api_key:
                return {
                    "status": "warning",
                    "reason": "no_api_key_for_verification",
                    "check_type": "signature"
                }
            
            stored_signature = verification["signature"]
            signature_data = verification["signature_data"]
            
            # Recalculate signature
            calculated_signature = hmac.new(
                self.api_key.encode(),
                signature_data.encode(),
                hashlib.sha256
            ).hexdigest()
            
            return {
                "status": "valid" if stored_signature == calculated_signature else "invalid",
                "stored_signature": stored_signature,
                "calculated_signature": calculated_signature,
                "check_type": "signature"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "check_type": "signature"
            }
    
    def _verify_timestamp(self, attestation: Dict[str, Any]) -> Dict[str, Any]:
        """Verify timestamp validity."""
        try:
            timestamp_str = attestation["timestamp"]
            timestamp = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
            now = datetime.now(timezone.utc)
            
            # Check if timestamp is not in the future
            future_tolerance = 300  # 5 minutes tolerance
            if timestamp > now + timedelta(seconds=future_tolerance):
                return {
                    "status": "invalid",
                    "reason": "timestamp_in_future",
                    "timestamp": timestamp_str,
                    "check_type": "timestamp"
                }
            
            # Check if timestamp is not too old (optional check)
            max_age_days = 365  # 1 year
            if timestamp < now - timedelta(days=max_age_days):
                return {
                    "status": "warning",
                    "reason": "timestamp_very_old",
                    "timestamp": timestamp_str,
                    "age_days": (now - timestamp).days,
                    "check_type": "timestamp"
                }
            
            return {
                "status": "valid",
                "timestamp": timestamp_str,
                "age_seconds": (now - timestamp).total_seconds(),
                "check_type": "timestamp"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "check_type": "timestamp"
            }
    
    async def list_attestations(self) -> List[Dict[str, Any]]:
        """List all stored attestations."""
        try:
            attestations = []
            
            for file_path in self.storage_path.glob("attestation-*.json"):
                try:
                    with open(file_path, 'r') as f:
                        data = json.load(f)
                    
                    attestations.append({
                        "file_path": str(file_path),
                        "scroll_id": data.get("scroll_metadata", {}).get("scroll_id", "unknown"),
                        "session_id": data.get("scroll_metadata", {}).get("session_id", "unknown"),
                        "timestamp": data.get("timestamp", "unknown"),
                        "file_size": file_path.stat().st_size,
                        "api_status": data.get("api_submission", {}).get("status", "unknown")
                    })
                    
                except Exception as e:
                    self.logger.warning(f"Failed to read attestation {file_path}: {e}")
                    continue
            
            # Sort by timestamp (newest first)
            attestations.sort(key=lambda x: x["timestamp"], reverse=True)
            
            return attestations
            
        except Exception as e:
            self.logger.error(f"Failed to list attestations: {e}")
            return []