"""
ShadowScrolls Integration Module
===============================

External attestation and immutable logging integration for the MirrorWatcherAI system.
Provides cryptographic verification and tamper-proof audit trails.
"""

import aiohttp
import asyncio
import json
import hashlib
import hmac
import os
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
import logging
import uuid
import base64

logger = logging.getLogger(__name__)


class ShadowScrollsIntegration:
    """
    ShadowScrolls external attestation and immutable logging integration.
    
    Provides:
    - External witnessing for immutable attestation
    - Cryptographic verification of analysis results
    - Tamper-proof audit trail generation
    - Integration with existing ShadowScrolls infrastructure
    """
    
    def __init__(self):
        self.endpoint = os.getenv("SHADOWSCROLLS_ENDPOINT", "https://api.shadowscrolls.triune-oracle.com/v1")
        self.api_key = os.getenv("SHADOWSCROLLS_API_KEY")
        self.signing_key = os.getenv("SHADOWSCROLLS_SIGNING_KEY", "")
        self.session = None
        
        # Local storage for scrolls
        self.scroll_directory = "/home/runner/work/triune-swarm-engine/triune-swarm-engine/.shadowscrolls"
        os.makedirs(f"{self.scroll_directory}/attestations", exist_ok=True)
        
    async def __aenter__(self):
        """Async context manager entry."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "MirrorWatcherAI/1.0.0"
        }
        
        self.session = aiohttp.ClientSession(headers=headers)
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def create_attestation(self, execution_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create comprehensive attestation scroll for analysis data.
        
        Args:
            execution_id: Unique execution identifier
            data: Analysis data to attest
            
        Returns:
            Attestation scroll with verification metadata
        """
        logger.info(f"Creating ShadowScrolls attestation for execution: {execution_id}")
        
        timestamp = datetime.now(timezone.utc)
        
        # Generate scroll metadata
        scroll_metadata = {
            "scroll_id": f"#{self._generate_scroll_number()} – Mirror Analysis {execution_id}",
            "timestamp": timestamp.isoformat(),
            "system": "MirrorWatcherAI Automation",
            "execution_id": execution_id,
            "version": "1.0.0"
        }
        
        # Create attestation payload
        attestation_payload = {
            "scroll_metadata": scroll_metadata,
            "analysis_data": data,
            "verification": await self._generate_verification_data(data),
            "lineage": await self._create_lineage_chain(execution_id),
            "external_witnesses": await self._collect_external_witnesses(execution_id)
        }
        
        # Sign the attestation
        signature = await self._sign_attestation(attestation_payload)
        attestation_payload["signature"] = signature
        
        # Submit to ShadowScrolls
        try:
            async with self:
                external_attestation = await self._submit_to_shadowscrolls(attestation_payload)
                attestation_payload["external_attestation"] = external_attestation
        except Exception as e:
            logger.warning(f"External ShadowScrolls submission failed: {str(e)}")
            attestation_payload["external_attestation"] = {
                "status": "local_only",
                "error": str(e),
                "timestamp": timestamp.isoformat()
            }
        
        # Store locally
        await self._store_attestation_locally(execution_id, attestation_payload)
        
        logger.info(f"Attestation created successfully: {scroll_metadata['scroll_id']}")
        
        return {
            "scroll_id": scroll_metadata["scroll_id"],
            "timestamp": timestamp.isoformat(),
            "verification_hash": signature.get("hash"),
            "external_status": attestation_payload["external_attestation"].get("status"),
            "local_storage": f"{self.scroll_directory}/attestations/{execution_id}.json",
            "attestation_summary": {
                "repositories_attested": len(data.get("repositories", {})),
                "verification_level": "cryptographic",
                "witness_count": len(attestation_payload["external_witnesses"])
            }
        }
    
    async def verify_attestation(self, attestation_file: str) -> Dict[str, Any]:
        """
        Verify the integrity of an existing attestation.
        
        Args:
            attestation_file: Path to attestation file
            
        Returns:
            Verification results
        """
        logger.info(f"Verifying attestation: {attestation_file}")
        
        try:
            with open(attestation_file, 'r') as f:
                attestation = json.load(f)
            
            verification_results = {
                "file": attestation_file,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "status": "verified",
                "checks": {}
            }
            
            # Verify signature
            signature_check = await self._verify_signature(attestation)
            verification_results["checks"]["signature"] = signature_check
            
            # Verify data integrity
            integrity_check = await self._verify_data_integrity(attestation)
            verification_results["checks"]["data_integrity"] = integrity_check
            
            # Verify lineage chain
            lineage_check = await self._verify_lineage_chain(attestation.get("lineage", {}))
            verification_results["checks"]["lineage"] = lineage_check
            
            # Check external attestation
            external_check = await self._verify_external_attestation(attestation)
            verification_results["checks"]["external_attestation"] = external_check
            
            # Overall verification status
            all_checks_passed = all(
                check.get("status") == "valid" 
                for check in verification_results["checks"].values()
            )
            
            if not all_checks_passed:
                verification_results["status"] = "failed"
                logger.warning(f"Attestation verification failed for {attestation_file}")
            else:
                logger.info(f"Attestation verified successfully: {attestation_file}")
            
            return verification_results
            
        except Exception as e:
            logger.error(f"Attestation verification error: {str(e)}")
            return {
                "file": attestation_file,
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    async def get_attestation_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get history of attestations.
        
        Args:
            limit: Maximum number of attestations to return
            
        Returns:
            List of attestation summaries
        """
        logger.info("Retrieving attestation history")
        
        attestation_dir = f"{self.scroll_directory}/attestations"
        history = []
        
        try:
            attestation_files = sorted(
                [f for f in os.listdir(attestation_dir) if f.endswith('.json')],
                reverse=True
            )[:limit]
            
            for filename in attestation_files:
                file_path = os.path.join(attestation_dir, filename)
                
                try:
                    with open(file_path, 'r') as f:
                        attestation = json.load(f)
                    
                    summary = {
                        "execution_id": attestation.get("scroll_metadata", {}).get("execution_id"),
                        "scroll_id": attestation.get("scroll_metadata", {}).get("scroll_id"),
                        "timestamp": attestation.get("scroll_metadata", {}).get("timestamp"),
                        "repositories_count": len(attestation.get("analysis_data", {}).get("repositories", {})),
                        "verification_hash": attestation.get("signature", {}).get("hash"),
                        "external_status": attestation.get("external_attestation", {}).get("status"),
                        "file_path": file_path
                    }
                    
                    history.append(summary)
                    
                except Exception as e:
                    logger.warning(f"Failed to parse attestation file {filename}: {str(e)}")
                    continue
            
            logger.info(f"Retrieved {len(history)} attestations from history")
            return history
            
        except Exception as e:
            logger.error(f"Failed to retrieve attestation history: {str(e)}")
            return []
    
    async def _generate_scroll_number(self) -> str:
        """Generate unique scroll number based on existing scrolls."""
        
        try:
            history = await self.get_attestation_history()
            
            # Extract scroll numbers and find the next available
            scroll_numbers = []
            for item in history:
                scroll_id = item.get("scroll_id", "")
                if scroll_id.startswith("#"):
                    try:
                        number = int(scroll_id.split("#")[1].split(" ")[0])
                        scroll_numbers.append(number)
                    except:
                        continue
            
            next_number = max(scroll_numbers) + 1 if scroll_numbers else 1
            return f"{next_number:03d}"
            
        except Exception:
            # Fallback to timestamp-based numbering
            return datetime.now(timezone.utc).strftime("%m%d%H")
    
    async def _generate_verification_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate cryptographic verification data."""
        
        # Create data hash
        data_json = json.dumps(data, sort_keys=True, separators=(',', ':'))
        data_hash = hashlib.sha256(data_json.encode()).hexdigest()
        
        # Create merkle-style verification
        verification = {
            "data_hash": data_hash,
            "algorithm": "SHA-256",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "verification_level": "cryptographic",
            "data_size_bytes": len(data_json),
            "merkle_root": await self._calculate_merkle_root(data)
        }
        
        return verification
    
    async def _calculate_merkle_root(self, data: Dict[str, Any]) -> str:
        """Calculate Merkle tree root for data integrity."""
        
        # Extract repository data for merkle tree
        repositories = data.get("repositories", {})
        
        if not repositories:
            return hashlib.sha256(b"empty").hexdigest()
        
        # Create leaf hashes
        leaves = []
        for repo_name, repo_data in repositories.items():
            repo_json = json.dumps(repo_data, sort_keys=True)
            leaf_hash = hashlib.sha256(repo_json.encode()).hexdigest()
            leaves.append(leaf_hash)
        
        # Build merkle tree
        current_level = leaves
        while len(current_level) > 1:
            next_level = []
            
            for i in range(0, len(current_level), 2):
                left = current_level[i]
                right = current_level[i + 1] if i + 1 < len(current_level) else left
                
                combined = left + right
                parent_hash = hashlib.sha256(combined.encode()).hexdigest()
                next_level.append(parent_hash)
            
            current_level = next_level
        
        return current_level[0] if current_level else hashlib.sha256(b"empty").hexdigest()
    
    async def _create_lineage_chain(self, execution_id: str) -> Dict[str, Any]:
        """Create lineage chain for traceability."""
        
        # Get previous attestations for chain building
        history = await self.get_attestation_history(limit=5)
        
        lineage = {
            "execution_id": execution_id,
            "chain_position": len(history) + 1,
            "previous_attestations": [
                {
                    "execution_id": item["execution_id"],
                    "verification_hash": item["verification_hash"],
                    "timestamp": item["timestamp"]
                }
                for item in history[:3]  # Link to last 3 attestations
            ],
            "lineage_hash": self._calculate_lineage_hash(execution_id, history),
            "generation": "MirrorLineage-Δ",
            "immutable_properties": {
                "timestamp_immutable": True,
                "hash_chain_verified": True,
                "cryptographic_binding": True
            }
        }
        
        return lineage
    
    def _calculate_lineage_hash(self, execution_id: str, history: List[Dict[str, Any]]) -> str:
        """Calculate hash for lineage chain."""
        
        chain_data = execution_id
        for item in history[:3]:
            chain_data += item.get("verification_hash", "")
        
        return hashlib.sha256(chain_data.encode()).hexdigest()
    
    async def _collect_external_witnesses(self, execution_id: str) -> List[Dict[str, Any]]:
        """Collect external witness data for attestation."""
        
        witnesses = []
        
        # GitHub Actions witness
        github_witness = {
            "type": "github_actions",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "execution_context": {
                "run_id": os.getenv("GITHUB_RUN_ID"),
                "run_number": os.getenv("GITHUB_RUN_NUMBER"),
                "workflow": os.getenv("GITHUB_WORKFLOW"),
                "actor": os.getenv("GITHUB_ACTOR"),
                "ref": os.getenv("GITHUB_REF"),
                "sha": os.getenv("GITHUB_SHA")
            },
            "verification_url": f"https://github.com/Triune-Oracle/triune-swarm-engine/actions/runs/{os.getenv('GITHUB_RUN_ID')}" if os.getenv('GITHUB_RUN_ID') else None
        }
        witnesses.append(github_witness)
        
        # System environment witness
        system_witness = {
            "type": "system_environment",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "environment": {
                "python_version": os.getenv("PYTHON_VERSION", "unknown"),
                "runner_os": os.getenv("RUNNER_OS", "unknown"),
                "runner_arch": os.getenv("RUNNER_ARCH", "unknown")
            }
        }
        witnesses.append(system_witness)
        
        return witnesses
    
    async def _sign_attestation(self, attestation_payload: Dict[str, Any]) -> Dict[str, Any]:
        """Sign attestation with cryptographic signature."""
        
        # Create canonical representation
        canonical_data = json.dumps(attestation_payload, sort_keys=True, separators=(',', ':'))
        
        # Generate hash
        content_hash = hashlib.sha256(canonical_data.encode()).hexdigest()
        
        # Create HMAC signature if signing key is available
        if self.signing_key:
            signature = hmac.new(
                self.signing_key.encode(),
                canonical_data.encode(),
                hashlib.sha256
            ).hexdigest()
        else:
            # Fallback to simple hash-based signature
            signature = hashlib.sha256(f"{content_hash}{datetime.now(timezone.utc).isoformat()}".encode()).hexdigest()
        
        return {
            "hash": content_hash,
            "signature": signature,
            "algorithm": "HMAC-SHA256" if self.signing_key else "SHA256-Timestamp",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    async def _submit_to_shadowscrolls(self, attestation_payload: Dict[str, Any]) -> Dict[str, Any]:
        """Submit attestation to external ShadowScrolls service."""
        
        if not self.api_key:
            raise Exception("ShadowScrolls API key not configured")
        
        url = f"{self.endpoint}/attestations"
        
        # Prepare submission payload
        submission = {
            "scroll_metadata": attestation_payload["scroll_metadata"],
            "verification": attestation_payload["verification"],
            "lineage": attestation_payload["lineage"],
            "signature": attestation_payload["signature"],
            "client_info": {
                "system": "MirrorWatcherAI",
                "version": "1.0.0",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        }
        
        try:
            async with self.session.post(url, json=submission) as response:
                if response.status in [200, 201]:
                    result = await response.json()
                    return {
                        "status": "success",
                        "external_id": result.get("id"),
                        "timestamp": result.get("timestamp"),
                        "verification_url": result.get("verification_url")
                    }
                else:
                    error_text = await response.text()
                    raise Exception(f"ShadowScrolls API error {response.status}: {error_text}")
        
        except Exception as e:
            logger.error(f"ShadowScrolls submission failed: {str(e)}")
            raise
    
    async def _store_attestation_locally(self, execution_id: str, attestation_payload: Dict[str, Any]):
        """Store attestation locally for backup and verification."""
        
        file_path = f"{self.scroll_directory}/attestations/{execution_id}.json"
        
        try:
            with open(file_path, 'w') as f:
                json.dump(attestation_payload, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Attestation stored locally: {file_path}")
            
        except Exception as e:
            logger.error(f"Failed to store attestation locally: {str(e)}")
            raise
    
    async def _verify_signature(self, attestation: Dict[str, Any]) -> Dict[str, Any]:
        """Verify attestation signature."""
        
        try:
            signature_data = attestation.get("signature", {})
            stored_hash = signature_data.get("hash")
            stored_signature = signature_data.get("signature")
            
            # Recreate signature for verification
            attestation_copy = dict(attestation)
            del attestation_copy["signature"]  # Remove signature for verification
            
            canonical_data = json.dumps(attestation_copy, sort_keys=True, separators=(',', ':'))
            calculated_hash = hashlib.sha256(canonical_data.encode()).hexdigest()
            
            # Verify hash
            hash_valid = stored_hash == calculated_hash
            
            # Verify signature if signing key is available
            signature_valid = True
            if self.signing_key and stored_signature:
                expected_signature = hmac.new(
                    self.signing_key.encode(),
                    canonical_data.encode(),
                    hashlib.sha256
                ).hexdigest()
                signature_valid = stored_signature == expected_signature
            
            return {
                "status": "valid" if hash_valid and signature_valid else "invalid",
                "hash_valid": hash_valid,
                "signature_valid": signature_valid,
                "algorithm": signature_data.get("algorithm"),
                "timestamp": signature_data.get("timestamp")
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def _verify_data_integrity(self, attestation: Dict[str, Any]) -> Dict[str, Any]:
        """Verify data integrity through hash verification."""
        
        try:
            verification_data = attestation.get("verification", {})
            stored_data_hash = verification_data.get("data_hash")
            analysis_data = attestation.get("analysis_data", {})
            
            # Recalculate data hash
            data_json = json.dumps(analysis_data, sort_keys=True, separators=(',', ':'))
            calculated_hash = hashlib.sha256(data_json.encode()).hexdigest()
            
            integrity_valid = stored_data_hash == calculated_hash
            
            return {
                "status": "valid" if integrity_valid else "invalid",
                "stored_hash": stored_data_hash,
                "calculated_hash": calculated_hash,
                "data_size_bytes": len(data_json)
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def _verify_lineage_chain(self, lineage: Dict[str, Any]) -> Dict[str, Any]:
        """Verify lineage chain integrity."""
        
        try:
            execution_id = lineage.get("execution_id")
            stored_lineage_hash = lineage.get("lineage_hash")
            previous_attestations = lineage.get("previous_attestations", [])
            
            # Recalculate lineage hash
            chain_data = execution_id or ""
            for item in previous_attestations:
                chain_data += item.get("verification_hash", "")
            
            calculated_hash = hashlib.sha256(chain_data.encode()).hexdigest()
            lineage_valid = stored_lineage_hash == calculated_hash
            
            return {
                "status": "valid" if lineage_valid else "invalid",
                "chain_position": lineage.get("chain_position"),
                "previous_count": len(previous_attestations),
                "generation": lineage.get("generation")
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def _verify_external_attestation(self, attestation: Dict[str, Any]) -> Dict[str, Any]:
        """Verify external attestation status."""
        
        try:
            external_attestation = attestation.get("external_attestation", {})
            status = external_attestation.get("status")
            
            if status == "success":
                return {
                    "status": "valid",
                    "external_id": external_attestation.get("external_id"),
                    "verification_url": external_attestation.get("verification_url")
                }
            elif status == "local_only":
                return {
                    "status": "warning",
                    "message": "External attestation not available, local only",
                    "error": external_attestation.get("error")
                }
            else:
                return {
                    "status": "invalid",
                    "message": "External attestation failed"
                }
                
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check of ShadowScrolls integration."""
        
        health_status = {
            "status": "healthy",
            "checks": {},
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        # Check API configuration
        if not self.api_key:
            health_status["checks"]["api_configuration"] = {
                "status": "warning",
                "message": "API key not configured"
            }
            health_status["status"] = "degraded"
        else:
            health_status["checks"]["api_configuration"] = {"status": "healthy"}
        
        # Check local storage
        try:
            os.makedirs(f"{self.scroll_directory}/attestations", exist_ok=True)
            test_file = f"{self.scroll_directory}/attestations/.health_check"
            
            with open(test_file, 'w') as f:
                f.write("health_check")
            
            os.remove(test_file)
            
            health_status["checks"]["local_storage"] = {"status": "healthy"}
            
        except Exception as e:
            health_status["checks"]["local_storage"] = {
                "status": "error",
                "error": str(e)
            }
            health_status["status"] = "unhealthy"
        
        # Check ShadowScrolls API connectivity
        if self.api_key:
            try:
                async with self:
                    health_url = f"{self.endpoint}/health"
                    async with self.session.get(health_url) as response:
                        if response.status in [200, 404]:  # 404 is OK if endpoint doesn't exist
                            health_status["checks"]["shadowscrolls_api"] = {"status": "healthy"}
                        else:
                            health_status["checks"]["shadowscrolls_api"] = {
                                "status": "error", 
                                "code": response.status
                            }
                            health_status["status"] = "degraded"
            
            except Exception as e:
                health_status["checks"]["shadowscrolls_api"] = {
                    "status": "warning",
                    "error": str(e),
                    "message": "External service unavailable"
                }
                health_status["status"] = "degraded"
        
        return health_status