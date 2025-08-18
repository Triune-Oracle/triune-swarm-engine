#!/usr/bin/env python3
"""
Test suite for ShadowScrolls attestation functionality.

Tests the external attestation system including:
- Attestation creation and storage
- Cryptographic verification
- Local backup and recovery
- Health checks and validation
"""

import pytest
import asyncio
import tempfile
import json
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock
import sys
import os
from datetime import datetime, timezone

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from mirror_watcher_ai.shadowscrolls import ShadowScrollsAttestation


class TestShadowScrollsAttestation:
    """Test cases for the ShadowScrollsAttestation class."""
    
    @pytest.fixture
    def attestation_config(self):
        """Provide basic attestation configuration."""
        return {
            "endpoint": "https://api.shadowscrolls.test/v1",
            "api_key": "test_api_key_123",
            "timeout": 30
        }
    
    @pytest.fixture
    def attestation_service(self, attestation_config):
        """Create ShadowScrollsAttestation instance for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Override storage path to use temp directory
            attestation_config["storage_path"] = temp_dir
            service = ShadowScrollsAttestation(attestation_config)
            service.storage_path = Path(temp_dir) / ".shadowscrolls" / "attestations"
            service.storage_path.mkdir(parents=True, exist_ok=True)
            yield service
    
    def test_initialization(self, attestation_service):
        """Test ShadowScrolls service initializes correctly."""
        assert attestation_service.endpoint == "https://api.shadowscrolls.test/v1"
        assert attestation_service.api_key == "test_api_key_123"
        assert attestation_service.timeout == 30
        assert attestation_service.storage_path.exists()
        assert attestation_service.attestation_counter >= 0
    
    @pytest.mark.asyncio
    async def test_health_check_success(self, attestation_service):
        """Test successful health check."""
        with patch("aiohttp.ClientSession") as mock_session:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.headers = {"X-Response-Time": "123ms"}
            mock_session.return_value.__aenter__.return_value.get.return_value.__aenter__.return_value = mock_response
            
            health = await attestation_service.health_check()
            
            assert health["status"] == "healthy"
            assert health["endpoint"] == "https://api.shadowscrolls.test/v1"
            assert health["response_time"] == "123ms"
    
    @pytest.mark.asyncio
    async def test_health_check_failure(self, attestation_service):
        """Test health check failure."""
        with patch("aiohttp.ClientSession") as mock_session:
            mock_response = AsyncMock()
            mock_response.status = 500
            mock_session.return_value.__aenter__.return_value.get.return_value.__aenter__.return_value = mock_response
            
            with pytest.raises(Exception) as exc_info:
                await attestation_service.health_check()
            
            assert "Health check failed" in str(exc_info.value)
    
    def test_attestation_data_creation(self, attestation_service):
        """Test creation of attestation data structure."""
        session_id = "test-session-123"
        results = {"test": "data", "count": 42}
        metadata = {"custom": "metadata"}
        scroll_number = "001"
        
        attestation_data = attestation_service._create_attestation_data(
            session_id, results, metadata, scroll_number
        )
        
        assert attestation_data["scroll_metadata"]["session_id"] == session_id
        assert attestation_data["scroll_metadata"]["scroll_number"] == scroll_number
        assert attestation_data["session_data"]["analysis_results"] == results
        assert attestation_data["verification"]["hash_algorithm"] == "sha256"
        assert attestation_data["verification"]["signature_algorithm"] == "hmac-sha256"
        assert len(attestation_data["verification"]["content_hash"]) == 64  # SHA256 hex length
        assert "mirrorlineage_delta" in attestation_data
    
    def test_merkle_root_calculation(self, attestation_service):
        """Test Merkle root calculation."""
        # Test with simple data
        simple_data = {"key": "value"}
        merkle_root = attestation_service._calculate_merkle_root(simple_data)
        assert len(merkle_root) == 64  # SHA256 hex length
        
        # Test with complex nested data
        complex_data = {
            "level1": {
                "level2": {
                    "value": "test"
                },
                "array": [1, 2, 3]
            }
        }
        complex_merkle_root = attestation_service._calculate_merkle_root(complex_data)
        assert len(complex_merkle_root) == 64
        
        # Same data should produce same root
        merkle_root2 = attestation_service._calculate_merkle_root(simple_data)
        assert merkle_root == merkle_root2
        
        # Different data should produce different root
        assert merkle_root != complex_merkle_root
    
    def test_traceability_chain_creation(self, attestation_service):
        """Test MirrorLineage-Δ traceability chain creation."""
        session_id = "test-session-456"
        
        chain = attestation_service._create_traceability_chain(session_id)
        
        assert chain["chain_id"] == f"mirrorlineage-{session_id}"
        assert chain["node_type"] == "attestation"
        assert chain["parent_nodes"] == []
        assert chain["child_nodes"] == []
        assert chain["metadata"]["created_by"] == "MirrorWatcherAI"
        assert chain["metadata"]["chain_version"] == "delta-1.0"
        assert chain["metadata"]["immutability_level"] == "cryptographic"
    
    @pytest.mark.asyncio
    async def test_create_attestation_api_success(self, attestation_service):
        """Test successful attestation creation with API submission."""
        session_id = "test-session-789"
        results = {"repositories": {"test-repo": {"status": "completed"}}}
        metadata = {"test": True}
        
        # Mock successful API response
        with patch("aiohttp.ClientSession") as mock_session:
            mock_response = AsyncMock()
            mock_response.status = 201
            mock_response.json = AsyncMock(return_value={"id": "scroll-123", "status": "created"})
            mock_session.return_value.__aenter__.return_value.post.return_value.__aenter__.return_value = mock_response
            
            attestation = await attestation_service.create_attestation(
                session_id, results, metadata
            )
            
            assert attestation["session_id"] == session_id
            assert "scroll_id" in attestation
            assert "scroll_number" in attestation
            assert "verification_hash" in attestation
            assert "local_storage" in attestation
            assert attestation["api_response"]["status"] == "submitted"
    
    @pytest.mark.asyncio
    async def test_create_attestation_api_failure(self, attestation_service):
        """Test attestation creation with API failure (should still store locally)."""
        session_id = "test-session-fail"
        results = {"test": "data"}
        
        # Mock API failure
        with patch("aiohttp.ClientSession") as mock_session:
            mock_session.return_value.__aenter__.return_value.post.side_effect = Exception("API Error")
            
            attestation = await attestation_service.create_attestation(
                session_id, results
            )
            
            assert attestation["session_id"] == session_id
            assert attestation["api_response"]["status"] == "api_failed"
            assert "local_storage" in attestation
            
            # Verify local storage exists
            local_path = Path(attestation["local_storage"])
            assert local_path.exists()
    
    @pytest.mark.asyncio
    async def test_verify_attestation_valid(self, attestation_service):
        """Test verification of a valid attestation."""
        # Create a test attestation file
        attestation_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "scroll_metadata": {
                "scroll_id": "#001 – Test Attestation",
                "session_id": "test-session"
            },
            "session_data": {
                "analysis_results": {"test": "data"}
            },
            "verification": {
                "content_hash": "test_hash",
                "hash_algorithm": "sha256"
            },
            "mirrorlineage_delta": {
                "enabled": True
            }
        }
        
        # Calculate correct hash
        import hashlib
        content_json = json.dumps({"test": "data"}, sort_keys=True, separators=(',', ':'))
        correct_hash = hashlib.sha256(content_json.encode()).hexdigest()
        attestation_data["verification"]["content_hash"] = correct_hash
        
        # Save to file
        test_file = attestation_service.storage_path / "test-attestation.json"
        with open(test_file, 'w') as f:
            json.dump(attestation_data, f)
        
        verification = await attestation_service.verify_attestation(test_file)
        
        assert verification["overall_status"] in ["valid", "warning"]  # Warning if no signature
        assert verification["checks"]["file_integrity"]["status"] == "valid"
        assert verification["checks"]["content_hash"]["status"] == "valid"
    
    @pytest.mark.asyncio
    async def test_verify_attestation_invalid_hash(self, attestation_service):
        """Test verification of attestation with invalid hash."""
        attestation_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "scroll_metadata": {"scroll_id": "#001", "session_id": "test"},
            "session_data": {"analysis_results": {"test": "data"}},
            "verification": {
                "content_hash": "invalid_hash_12345",
                "hash_algorithm": "sha256"
            },
            "mirrorlineage_delta": {"enabled": True}
        }
        
        test_file = attestation_service.storage_path / "invalid-attestation.json"
        with open(test_file, 'w') as f:
            json.dump(attestation_data, f)
        
        verification = await attestation_service.verify_attestation(test_file)
        
        assert verification["overall_status"] == "invalid"
        assert verification["checks"]["content_hash"]["status"] == "invalid"
    
    @pytest.mark.asyncio
    async def test_list_attestations(self, attestation_service):
        """Test listing stored attestations."""
        # Create test attestation files
        for i in range(3):
            attestation_data = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "scroll_metadata": {
                    "scroll_id": f"#00{i+1}",
                    "session_id": f"test-session-{i}"
                },
                "api_submission": {"status": "success"}
            }
            
            test_file = attestation_service.storage_path / f"attestation-00{i+1}-test.json"
            with open(test_file, 'w') as f:
                json.dump(attestation_data, f)
        
        attestations = await attestation_service.list_attestations()
        
        assert len(attestations) == 3
        
        for attestation in attestations:
            assert "file_path" in attestation
            assert "scroll_id" in attestation
            assert "session_id" in attestation
            assert "timestamp" in attestation
            assert "file_size" in attestation
            assert "api_status" in attestation
    
    def test_counter_persistence(self, attestation_service):
        """Test that the attestation counter persists across instances."""
        # Set a specific counter value
        original_counter = 42
        attestation_service.attestation_counter = original_counter
        attestation_service._save_counter()
        
        # Create new instance with same storage path
        new_config = {
            "endpoint": "https://test.com",
            "api_key": "test",
            "timeout": 30
        }
        
        new_service = ShadowScrollsAttestation(new_config)
        new_service.storage_path = attestation_service.storage_path
        new_counter = new_service._load_counter()
        
        assert new_counter == original_counter
    
    def test_previous_hash_chaining(self, attestation_service):
        """Test that attestations properly chain to previous hashes."""
        # Create first attestation file
        first_hash = "first_attestation_hash_123"
        first_attestation = {
            "verification": {"content_hash": first_hash}
        }
        
        first_file = attestation_service.storage_path / "attestation-001-first.json"
        with open(first_file, 'w') as f:
            json.dump(first_attestation, f)
        
        # Get previous hash - should return the first hash
        previous_hash = attestation_service._get_previous_hash()
        assert previous_hash == first_hash
        
        # Test with no files (should return genesis)
        # Remove the file temporarily
        first_file.unlink()
        genesis_hash = attestation_service._get_previous_hash()
        assert genesis_hash == "genesis"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])