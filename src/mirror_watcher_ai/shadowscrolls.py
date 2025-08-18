"""
ShadowScrolls Integration Module

Provides external attestation and witnessing for MirrorWatcherAI automation system.
Integrates with ShadowScrolls API for immutable attestation and cryptographic verification.
"""

import asyncio
import json
import logging
import hashlib
import hmac
import time
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Union
import os
import aiohttp
import base64

logger = logging.getLogger(__name__)

class ShadowScrollsIntegration:
    """Integration with ShadowScrolls external attestation system"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.endpoint = self._get_endpoint()
        self.api_key = self._get_api_key()
        self.attestation_enabled = self.config.get('attestation_enabled', True)
        self.timeout = self.config.get('timeout', 30)
        
    def _get_endpoint(self) -> Optional[str]:
        """Get ShadowScrolls API endpoint from config or environment"""
        endpoint = self.config.get('endpoint')
        if not endpoint:
            endpoint = os.getenv('SHADOWSCROLLS_ENDPOINT')
        
        if not endpoint:
            logger.warning("ShadowScrolls endpoint not configured")
            
        return endpoint
    
    def _get_api_key(self) -> Optional[str]:
        """Get ShadowScrolls API key from config or environment"""
        api_key = self.config.get('api_key')
        if not api_key:
            api_key = os.getenv('SHADOWSCROLLS_API_KEY')
        
        if not api_key:
            logger.warning("ShadowScrolls API key not configured")
            
        return api_key
    
    async def create_attestation(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create an external attestation for the provided data"""
        try:
            if not self.attestation_enabled:
                logger.info("ShadowScrolls attestation disabled, skipping")
                return {"status": "disabled", "message": "Attestation disabled in configuration"}
            
            if not self.endpoint or not self.api_key:
                logger.warning("ShadowScrolls not configured, skipping attestation")
                return {"status": "not_configured", "message": "ShadowScrolls credentials not available"}
            
            logger.info("Creating ShadowScrolls attestation")
            
            # Prepare attestation payload
            attestation_payload = self._prepare_attestation_payload(data)
            
            # Create cryptographic proof
            proof = self._create_cryptographic_proof(attestation_payload)
            attestation_payload["cryptographic_proof"] = proof
            
            # Submit to ShadowScrolls
            attestation_result = await self._submit_attestation(attestation_payload)
            
            logger.info(f"ShadowScrolls attestation created: {attestation_result.get('attestation_id', 'unknown')}")
            return attestation_result
            
        except Exception as e:
            logger.error(f"Failed to create ShadowScrolls attestation: {e}")
            return {
                "status": "error",
                "message": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    def _prepare_attestation_payload(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare data for ShadowScrolls attestation"""
        # Create a standardized payload structure
        payload = {
            "attestation_type": "mirror_watcher_analysis",
            "version": "1.0.0",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source": "triune-swarm-engine/mirror-watcher-ai",
            "data_hash": self._calculate_data_hash(data),
            "metadata": {
                "session_id": data.get("session_id"),
                "repository_count": len(data.get("repositories", {})),
                "analysis_summary": data.get("summary", {}),
                "execution_environment": {
                    "system": "github_actions",
                    "runner": "ubuntu-latest",
                    "python_version": "3.11"
                }
            },
            "attestation_content": {
                "analysis_results": data,
                "validation_rules": {
                    "min_repositories": 1,
                    "required_fields": ["session_id", "timestamp", "repositories"],
                    "max_execution_time": 3600
                }
            }
        }
        
        return payload
    
    def _calculate_data_hash(self, data: Dict[str, Any]) -> str:
        """Calculate SHA-256 hash of the data for integrity verification"""
        # Create deterministic JSON representation
        json_str = json.dumps(data, sort_keys=True, separators=(',', ':'))
        hash_obj = hashlib.sha256(json_str.encode('utf-8'))
        return hash_obj.hexdigest()
    
    def _create_cryptographic_proof(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Create cryptographic proof for the attestation"""
        try:
            # Create timestamp proof
            timestamp = int(time.time())
            
            # Create payload hash
            payload_json = json.dumps(payload, sort_keys=True, separators=(',', ':'))
            payload_hash = hashlib.sha256(payload_json.encode('utf-8')).hexdigest()
            
            # Create HMAC signature if API key is available
            signature = None
            if self.api_key:
                signature_data = f"{timestamp}:{payload_hash}".encode('utf-8')
                signature = hmac.new(
                    self.api_key.encode('utf-8'),
                    signature_data,
                    hashlib.sha256
                ).hexdigest()
            
            proof = {
                "timestamp": timestamp,
                "payload_hash": payload_hash,
                "signature": signature,
                "algorithm": "HMAC-SHA256",
                "proof_version": "1.0"
            }
            
            return proof
            
        except Exception as e:
            logger.error(f"Failed to create cryptographic proof: {e}")
            return {
                "error": str(e),
                "timestamp": int(time.time()),
                "proof_version": "1.0"
            }
    
    async def _submit_attestation(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Submit attestation to ShadowScrolls API"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "User-Agent": "MirrorWatcherAI/1.0.0 TriuneSwarmEngine"
            }
            
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
                url = f"{self.endpoint.rstrip('/')}/attestations"
                
                async with session.post(url, json=payload, headers=headers) as response:
                    if response.status == 200 or response.status == 201:
                        result = await response.json()
                        return {
                            "status": "success",
                            "attestation_id": result.get("id"),
                            "attestation_url": result.get("url"),
                            "witness_nodes": result.get("witness_nodes", []),
                            "verification_hash": result.get("verification_hash"),
                            "timestamp": datetime.now(timezone.utc).isoformat()
                        }
                    else:
                        error_text = await response.text()
                        raise Exception(f"ShadowScrolls API returned {response.status}: {error_text}")
                        
        except asyncio.TimeoutError:
            raise Exception(f"ShadowScrolls API request timed out after {self.timeout} seconds")
        except aiohttp.ClientError as e:
            raise Exception(f"HTTP client error: {e}")
        except Exception as e:
            raise Exception(f"Failed to submit attestation: {e}")
    
    async def verify_attestation(self, attestation_id: str) -> Dict[str, Any]:
        """Verify an existing attestation"""
        try:
            if not self.endpoint or not self.api_key:
                return {"status": "not_configured", "message": "ShadowScrolls credentials not available"}
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "User-Agent": "MirrorWatcherAI/1.0.0 TriuneSwarmEngine"
            }
            
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
                url = f"{self.endpoint.rstrip('/')}/attestations/{attestation_id}"
                
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            "status": "verified",
                            "attestation": result,
                            "verification_timestamp": datetime.now(timezone.utc).isoformat()
                        }
                    else:
                        error_text = await response.text()
                        return {
                            "status": "verification_failed",
                            "error": f"API returned {response.status}: {error_text}"
                        }
                        
        except Exception as e:
            logger.error(f"Failed to verify attestation {attestation_id}: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def list_attestations(self, limit: int = 10) -> Dict[str, Any]:
        """List recent attestations"""
        try:
            if not self.endpoint or not self.api_key:
                return {"status": "not_configured", "message": "ShadowScrolls credentials not available"}
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "User-Agent": "MirrorWatcherAI/1.0.0 TriuneSwarmEngine"
            }
            
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
                url = f"{self.endpoint.rstrip('/')}/attestations?limit={limit}"
                
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            "status": "success",
                            "attestations": result.get("attestations", []),
                            "total": result.get("total", 0),
                            "retrieved_at": datetime.now(timezone.utc).isoformat()
                        }
                    else:
                        error_text = await response.text()
                        return {
                            "status": "error",
                            "error": f"API returned {response.status}: {error_text}"
                        }
                        
        except Exception as e:
            logger.error(f"Failed to list attestations: {e}")
            return {
                "status": "error",
                "error": str(e)
            }

class ExternalAttestation:
    """Enhanced external attestation with multiple witness nodes"""
    
    def __init__(self, shadowscrolls: ShadowScrollsIntegration):
        self.shadowscrolls = shadowscrolls
        
    async def create_multi_witness_attestation(self, data: Dict[str, Any], witness_count: int = 3) -> Dict[str, Any]:
        """Create attestation with multiple witness nodes for enhanced security"""
        try:
            logger.info(f"Creating multi-witness attestation with {witness_count} witnesses")
            
            # Create primary attestation
            primary_attestation = await self.shadowscrolls.create_attestation(data)
            
            if primary_attestation.get("status") != "success":
                return primary_attestation
            
            # Create additional witness attestations
            witness_attestations = []
            for i in range(witness_count - 1):
                try:
                    # Add witness metadata
                    witness_data = data.copy()
                    witness_data["witness_node"] = i + 2
                    witness_data["primary_attestation"] = primary_attestation.get("attestation_id")
                    
                    witness_result = await self.shadowscrolls.create_attestation(witness_data)
                    witness_attestations.append(witness_result)
                    
                except Exception as e:
                    logger.warning(f"Failed to create witness attestation {i + 2}: {e}")
                    witness_attestations.append({"status": "failed", "error": str(e)})
            
            return {
                "status": "success",
                "primary_attestation": primary_attestation,
                "witness_attestations": witness_attestations,
                "total_witnesses": witness_count,
                "successful_witnesses": sum(1 for w in witness_attestations if w.get("status") == "success") + 1,
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to create multi-witness attestation: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def verify_multi_witness_attestation(self, primary_attestation_id: str) -> Dict[str, Any]:
        """Verify multi-witness attestation integrity"""
        try:
            # Verify primary attestation
            primary_verification = await self.shadowscrolls.verify_attestation(primary_attestation_id)
            
            if primary_verification.get("status") != "verified":
                return primary_verification
            
            # Extract witness attestation IDs
            primary_data = primary_verification.get("attestation", {})
            witness_nodes = primary_data.get("witness_nodes", [])
            
            # Verify each witness
            witness_verifications = []
            for witness_id in witness_nodes:
                verification = await self.shadowscrolls.verify_attestation(witness_id)
                witness_verifications.append(verification)
            
            successful_verifications = sum(1 for v in witness_verifications if v.get("status") == "verified")
            
            return {
                "status": "verified" if successful_verifications > len(witness_nodes) / 2 else "partial_verification",
                "primary_verification": primary_verification,
                "witness_verifications": witness_verifications,
                "consensus": {
                    "total_witnesses": len(witness_nodes) + 1,
                    "successful_verifications": successful_verifications + 1,
                    "consensus_threshold": (len(witness_nodes) + 1) / 2,
                    "consensus_achieved": successful_verifications + 1 > (len(witness_nodes) + 1) / 2
                },
                "verified_at": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to verify multi-witness attestation: {e}")
            return {
                "status": "error",
                "error": str(e)
            }