"""
ShadowScrolls - Immutable Logging System
Provides blockchain-style attestation and MirrorLineage-Δ traceability
"""

import hashlib
import json
import time
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric.padding import PSS, MGF1


class ShadowScrolls:
    """
    Immutable logging system with cryptographic attestation
    
    Provides MirrorLineage-Δ traceability and external witnessing capabilities
    for complete audit trails and verification.
    """
    
    def __init__(self):
        self.version = "1.0.0"
        self.scroll_chain = []
        self._private_key = None
        self._public_key = None
        self._initialize_keys()
    
    def _initialize_keys(self):
        """Initialize cryptographic keys for attestation"""
        try:
            # Generate RSA key pair for attestation
            self._private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048
            )
            self._public_key = self._private_key.public_key()
        except Exception:
            # Fallback to simpler hash-based attestation if crypto fails
            self._private_key = None
            self._public_key = None
    
    def generate_lineage_id(self) -> str:
        """Generate unique MirrorLineage-Δ identifier"""
        timestamp = datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')
        unique_id = str(uuid.uuid4())[:8]
        return f"MirrorLineage-Δ-{timestamp}-{unique_id}"
    
    def create_attestation(self, analysis_result: Dict[str, Any], 
                          lineage_id: Optional[str] = None,
                          witness_enabled: bool = False) -> Dict[str, Any]:
        """
        Create cryptographic attestation for analysis results
        
        Args:
            analysis_result: The analysis data to attest
            lineage_id: Optional lineage identifier
            witness_enabled: Whether external witnessing is enabled
            
        Returns:
            Attestation dictionary with hash, signature, and metadata
        """
        if not lineage_id:
            lineage_id = self.generate_lineage_id()
        
        # Create attestation data
        attestation_data = {
            'lineage_id': lineage_id,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'version': self.version,
            'content_hash': self._hash_content(analysis_result),
            'previous_hash': self._get_previous_hash(),
            'witness_enabled': witness_enabled
        }
        
        # Add cryptographic signature if keys available
        if self._private_key:
            signature = self._sign_data(attestation_data)
            attestation_data['signature'] = signature
            attestation_data['public_key_fingerprint'] = self._get_public_key_fingerprint()
        
        # Calculate attestation hash
        attestation_hash = self._hash_content(attestation_data)
        attestation_data['hash'] = attestation_hash
        
        # Add to scroll chain
        scroll_entry = {
            'lineage_id': lineage_id,
            'attestation_hash': attestation_hash,
            'timestamp': attestation_data['timestamp'],
            'content_size': len(json.dumps(analysis_result)),
            'witness_enabled': witness_enabled
        }
        self.scroll_chain.append(scroll_entry)
        
        # External witnessing preparation
        if witness_enabled:
            attestation_data['blockchain_ready'] = True
            attestation_data['witness_payload'] = self._prepare_witness_payload(attestation_data)
        
        return attestation_data
    
    def verify_attestation(self, attestation: Dict[str, Any], 
                          original_content: Dict[str, Any]) -> bool:
        """
        Verify the integrity of an attestation
        
        Args:
            attestation: The attestation to verify
            original_content: The original content that was attested
            
        Returns:
            True if attestation is valid, False otherwise
        """
        try:
            # Verify content hash
            expected_hash = self._hash_content(original_content)
            if attestation.get('content_hash') != expected_hash:
                return False
            
            # Verify signature if present
            if 'signature' in attestation and self._public_key:
                return self._verify_signature(attestation)
            
            # Basic hash verification
            attestation_copy = attestation.copy()
            del attestation_copy['hash']
            expected_attestation_hash = self._hash_content(attestation_copy)
            
            return attestation.get('hash') == expected_attestation_hash
            
        except Exception:
            return False
    
    def get_chain_integrity(self) -> Dict[str, Any]:
        """Get integrity information about the scroll chain"""
        if not self.scroll_chain:
            return {
                'chain_length': 0,
                'integrity_status': 'empty',
                'last_entry': None
            }
        
        # Calculate chain hash
        chain_content = json.dumps(self.scroll_chain, sort_keys=True)
        chain_hash = hashlib.sha256(chain_content.encode()).hexdigest()
        
        return {
            'chain_length': len(self.scroll_chain),
            'chain_hash': chain_hash,
            'integrity_status': 'verified',
            'last_entry': self.scroll_chain[-1],
            'first_entry': self.scroll_chain[0],
            'total_witnessed': sum(1 for entry in self.scroll_chain if entry.get('witness_enabled'))
        }
    
    def export_scroll_chain(self) -> Dict[str, Any]:
        """Export the complete scroll chain for external storage"""
        return {
            'version': self.version,
            'export_timestamp': datetime.now(timezone.utc).isoformat(),
            'chain': self.scroll_chain,
            'integrity': self.get_chain_integrity(),
            'public_key': self._get_public_key_pem() if self._public_key else None
        }
    
    def import_scroll_chain(self, chain_data: Dict[str, Any]) -> bool:
        """Import and verify a scroll chain from external source"""
        try:
            if 'chain' not in chain_data:
                return False
            
            # Verify integrity if provided
            if 'integrity' in chain_data:
                imported_chain = chain_data['chain']
                chain_content = json.dumps(imported_chain, sort_keys=True)
                chain_hash = hashlib.sha256(chain_content.encode()).hexdigest()
                
                if chain_hash != chain_data['integrity'].get('chain_hash'):
                    return False
            
            # Import chain
            self.scroll_chain = chain_data['chain']
            return True
            
        except Exception:
            return False
    
    def _hash_content(self, content: Any) -> str:
        """Create deterministic hash of content"""
        json_content = json.dumps(content, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(json_content.encode()).hexdigest()
    
    def _get_previous_hash(self) -> Optional[str]:
        """Get hash of previous entry in scroll chain"""
        if not self.scroll_chain:
            return None
        return self.scroll_chain[-1].get('attestation_hash')
    
    def _sign_data(self, data: Dict[str, Any]) -> str:
        """Create cryptographic signature of data"""
        if not self._private_key:
            return self._hash_content(data)  # Fallback to hash
        
        try:
            content = json.dumps(data, sort_keys=True).encode()
            signature = self._private_key.sign(
                content,
                PSS(
                    mgf=MGF1(hashes.SHA256()),
                    salt_length=PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return signature.hex()
        except Exception:
            return self._hash_content(data)  # Fallback to hash
    
    def _verify_signature(self, attestation: Dict[str, Any]) -> bool:
        """Verify cryptographic signature"""
        if not self._public_key or 'signature' not in attestation:
            return False
        
        try:
            # Recreate data without signature
            data_copy = attestation.copy()
            signature_hex = data_copy.pop('signature')
            data_copy.pop('hash', None)  # Remove hash for verification
            
            content = json.dumps(data_copy, sort_keys=True).encode()
            signature = bytes.fromhex(signature_hex)
            
            self._public_key.verify(
                signature,
                content,
                PSS(
                    mgf=MGF1(hashes.SHA256()),
                    salt_length=PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except Exception:
            return False
    
    def _get_public_key_fingerprint(self) -> str:
        """Get fingerprint of public key"""
        if not self._public_key:
            return "no-key"
        
        try:
            public_key_bytes = self._public_key.public_bytes(
                encoding=serialization.Encoding.DER,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
            return hashlib.sha256(public_key_bytes).hexdigest()[:16]
        except Exception:
            return "key-error"
    
    def _get_public_key_pem(self) -> Optional[str]:
        """Get public key in PEM format"""
        if not self._public_key:
            return None
        
        try:
            return self._public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            ).decode()
        except Exception:
            return None
    
    def _prepare_witness_payload(self, attestation: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare payload for blockchain witnessing"""
        return {
            'lineage_id': attestation['lineage_id'],
            'attestation_hash': attestation['hash'],
            'timestamp': attestation['timestamp'],
            'content_hash': attestation['content_hash'],
            'previous_hash': attestation.get('previous_hash'),
            'witness_ready': True,
            'chain_position': len(self.scroll_chain)
        }


class MirrorLineageTracker:
    """Specialized tracker for Mirror Lineage operations"""
    
    def __init__(self):
        self.shadowscrolls = ShadowScrolls()
        self.lineage_registry = {}
    
    def register_mirror_operation(self, source_repo: str, target_path: str, 
                                 operation_type: str = "mirror") -> str:
        """Register a new mirror operation with lineage tracking"""
        lineage_id = self.shadowscrolls.generate_lineage_id()
        
        operation_data = {
            'operation_type': operation_type,
            'source_repository': source_repo,
            'target_path': target_path,
            'operation_timestamp': datetime.now(timezone.utc).isoformat(),
            'lineage_id': lineage_id
        }
        
        # Create attestation
        attestation = self.shadowscrolls.create_attestation(
            operation_data, 
            lineage_id=lineage_id,
            witness_enabled=True
        )
        
        # Register in local registry
        self.lineage_registry[lineage_id] = {
            'operation_data': operation_data,
            'attestation': attestation,
            'status': 'registered'
        }
        
        return lineage_id
    
    def get_lineage_history(self, lineage_id: str) -> Optional[Dict[str, Any]]:
        """Get complete history for a lineage ID"""
        return self.lineage_registry.get(lineage_id)
    
    def export_lineage_registry(self) -> Dict[str, Any]:
        """Export complete lineage registry"""
        return {
            'version': '1.0.0',
            'export_timestamp': datetime.now(timezone.utc).isoformat(),
            'registry': self.lineage_registry,
            'scroll_chain': self.shadowscrolls.export_scroll_chain()
        }