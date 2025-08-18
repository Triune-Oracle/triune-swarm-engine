#!/usr/bin/env python3
"""
Test suite for Triune ecosystem integration functionality.

Tests the integration with:
- Legio-Cognito scroll archival system
- Triumvirate Monitor dashboard
- Swarm Engine local integration
- Health monitoring and sync operations
"""

import pytest
import asyncio
import tempfile
import json
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock
import sys
import os

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from mirror_watcher_ai.triune_integration import TriuneEcosystemIntegration


class TestTriuneEcosystemIntegration:
    """Test cases for the TriuneEcosystemIntegration class."""
    
    @pytest.fixture
    def integration_config(self):
        """Provide basic integration configuration."""
        return {
            "legio_cognito_endpoint": "https://legio-cognito.test/api/v1",
            "triumvirate_monitor_endpoint": "https://monitor.test/api",
            "sync_interval": 300
        }
    
    @pytest.fixture
    def integration_service(self, integration_config):
        """Create TriuneEcosystemIntegration instance for testing."""
        return TriuneEcosystemIntegration(integration_config)
    
    def test_initialization(self, integration_service):
        """Test integration service initializes correctly."""
        assert integration_service.legio_cognito_endpoint == "https://legio-cognito.test/api/v1"
        assert integration_service.triumvirate_monitor_endpoint == "https://monitor.test/api"
        assert integration_service.sync_interval == 300
        assert "legio_cognito" in integration_service.integration_status
        assert "triumvirate_monitor" in integration_service.integration_status
        assert "swarm_engine" in integration_service.integration_status
    
    @pytest.mark.asyncio
    async def test_health_check_all_healthy(self, integration_service):
        """Test health check when all components are healthy."""
        with patch.object(integration_service, '_check_legio_cognito_health') as mock_legio, \
             patch.object(integration_service, '_check_triumvirate_monitor_health') as mock_monitor, \
             patch.object(integration_service, '_check_swarm_engine_health') as mock_swarm:
            
            mock_legio.return_value = {"status": "healthy"}
            mock_monitor.return_value = {"status": "healthy"}
            mock_swarm.return_value = {"status": "healthy"}
            
            health = await integration_service.health_check()
            
            assert health["overall_status"] == "healthy"
            assert health["components"]["legio_cognito"]["status"] == "healthy"
            assert health["components"]["triumvirate_monitor"]["status"] == "healthy"
            assert health["components"]["swarm_engine"]["status"] == "healthy"
            assert "performance_metrics" in health
    
    @pytest.mark.asyncio
    async def test_health_check_partial_failure(self, integration_service):
        """Test health check with some components failing."""
        with patch.object(integration_service, '_check_legio_cognito_health') as mock_legio, \
             patch.object(integration_service, '_check_triumvirate_monitor_health') as mock_monitor, \
             patch.object(integration_service, '_check_swarm_engine_health') as mock_swarm:
            
            mock_legio.return_value = {"status": "healthy"}
            mock_monitor.side_effect = Exception("Connection failed")
            mock_swarm.return_value = {"status": "healthy"}
            
            health = await integration_service.health_check()
            
            assert health["overall_status"] == "partial"
            assert health["components"]["legio_cognito"]["status"] == "healthy"
            assert health["components"]["triumvirate_monitor"]["status"] == "error"
            assert health["components"]["swarm_engine"]["status"] == "healthy"
    
    @pytest.mark.asyncio
    async def test_legio_cognito_health_check_success(self, integration_service):
        """Test successful Legio-Cognito health check."""
        with patch("aiohttp.ClientSession") as mock_session:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value={"service": "legio-cognito", "status": "ok"})
            mock_response.headers = {"X-Response-Time": "50ms"}
            mock_session.return_value.__aenter__.return_value.get.return_value.__aenter__.return_value = mock_response
            
            health = await integration_service._check_legio_cognito_health()
            
            assert health["status"] == "healthy"
            assert health["endpoint"] == "https://legio-cognito.test/api/v1"
            assert health["response_time"] == "50ms"
            assert "service_data" in health
    
    @pytest.mark.asyncio
    async def test_legio_cognito_health_check_not_configured(self):
        """Test Legio-Cognito health check when not configured."""
        config = {"legio_cognito_endpoint": ""}
        service = TriuneEcosystemIntegration(config)
        
        health = await service._check_legio_cognito_health()
        
        assert health["status"] == "not_configured"
        assert "not configured" in health["message"]
    
    @pytest.mark.asyncio
    async def test_triumvirate_monitor_health_check_success(self, integration_service):
        """Test successful Triumvirate Monitor health check."""
        with patch("aiohttp.ClientSession") as mock_session:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value={"dashboard": "online", "version": "1.0"})
            mock_response.headers = {"X-Response-Time": "25ms"}
            mock_session.return_value.__aenter__.return_value.get.return_value.__aenter__.return_value = mock_response
            
            health = await integration_service._check_triumvirate_monitor_health()
            
            assert health["status"] == "healthy"
            assert health["endpoint"] == "https://monitor.test/api"
            assert health["response_time"] == "25ms"
            assert "dashboard_data" in health
    
    @pytest.mark.asyncio
    async def test_swarm_engine_health_check(self, integration_service):
        """Test Swarm Engine health check."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Change to temp directory for testing
            original_cwd = os.getcwd()
            os.chdir(temp_dir)
            
            try:
                # Create mock swarm engine files
                Path("main.py").write_text("# Main swarm engine module")
                Path("storage.py").write_text("# Storage module")
                Path("memory_engine.js").write_text("// Memory engine")
                Path("task_listener.js").write_text("// Task listener")
                
                # Create scripts directory
                scripts_dir = Path("scripts")
                scripts_dir.mkdir()
                (scripts_dir / "setup-secrets.sh").write_text("#!/bin/bash")
                (scripts_dir / "validate-setup.py").write_text("# Validation script")
                
                health = await integration_service._check_swarm_engine_health()
                
                assert health["status"] in ["healthy", "partial"]
                assert "components" in health
                assert "python_integration" in health["components"]
                assert "shell_automation" in health["components"]
                assert "memory_engine" in health["components"]
                assert "task_listener" in health["components"]
                assert health["python_compatibility"] == "76.3%"
                assert health["shell_infrastructure"] == "10.1%"
                
            finally:
                os.chdir(original_cwd)
    
    def test_python_integration_check(self, integration_service):
        """Test Python integration check."""
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = os.getcwd()
            os.chdir(temp_dir)
            
            try:
                # Create Python files
                Path("main.py").write_text("print('main')")
                Path("storage.py").write_text("print('storage')")
                
                result = integration_service._check_python_integration()
                
                assert result["status"] == "healthy"
                assert result["python_files"]["main.py"] is True
                assert result["python_files"]["storage.py"] is True
                assert result["compatibility_score"] > 0.5
                
            finally:
                os.chdir(original_cwd)
    
    def test_shell_automation_check(self, integration_service):
        """Test shell automation check."""
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = os.getcwd()
            os.chdir(temp_dir)
            
            try:
                # Create scripts directory and files
                scripts_dir = Path("scripts")
                scripts_dir.mkdir()
                (scripts_dir / "setup-secrets.sh").write_text("#!/bin/bash")
                (scripts_dir / "test-integration.sh").write_text("#!/bin/bash")
                (scripts_dir / "validate-setup.py").write_text("#!/usr/bin/env python3")
                
                result = integration_service._check_shell_automation()
                
                assert result["status"] == "healthy"
                assert result["scripts_available"] == 3
                assert result["automation_ready"] is True
                
            finally:
                os.chdir(original_cwd)
    
    @pytest.mark.asyncio
    async def test_sync_results_success(self, integration_service):
        """Test successful result synchronization."""
        session_id = "test-sync-session"
        results = {
            "repositories": {
                "test-repo": {"status": "completed", "metrics": {"health_score": 0.8}}
            },
            "summary": {"successful": 1, "failed": 0, "total_repositories": 1}
        }
        
        with patch.object(integration_service, '_sync_to_legio_cognito') as mock_legio, \
             patch.object(integration_service, '_sync_to_triumvirate_monitor') as mock_monitor, \
             patch.object(integration_service, '_sync_to_swarm_engine') as mock_swarm:
            
            mock_legio.return_value = {"status": "success", "scroll_id": "scroll-123"}
            mock_monitor.return_value = {"status": "success", "update_id": "update-456"}
            mock_swarm.return_value = {"status": "success", "memory_log_updated": True}
            
            sync_result = await integration_service.sync_results(session_id, results)
            
            assert sync_result["session_id"] == session_id
            assert sync_result["sync_status"]["legio_cognito"]["status"] == "success"
            assert sync_result["sync_status"]["triumvirate_monitor"]["status"] == "success"
            assert sync_result["sync_status"]["swarm_engine"]["status"] == "success"
            assert len(sync_result["errors"]) == 0
    
    @pytest.mark.asyncio
    async def test_sync_to_legio_cognito_success(self, integration_service):
        """Test successful sync to Legio-Cognito."""
        session_id = "test-session"
        results = {"test": "data"}
        
        with patch("aiohttp.ClientSession") as mock_session:
            mock_response = AsyncMock()
            mock_response.status = 201
            mock_response.json = AsyncMock(return_value={"scroll_id": "scroll-789"})
            mock_session.return_value.__aenter__.return_value.post.return_value.__aenter__.return_value = mock_response
            
            result = await integration_service._sync_to_legio_cognito(session_id, results)
            
            assert result["status"] == "success"
            assert result["scroll_id"] == "scroll-789"
            assert result["endpoint"] == "https://legio-cognito.test/api/v1"
    
    @pytest.mark.asyncio
    async def test_sync_to_triumvirate_monitor_success(self, integration_service):
        """Test successful sync to Triumvirate Monitor."""
        session_id = "test-session"
        results = {
            "repositories": {"repo1": {"status": "completed"}},
            "summary": {"successful": 1, "failed": 0}
        }
        
        with patch("aiohttp.ClientSession") as mock_session:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value={"update_id": "update-123"})
            mock_session.return_value.__aenter__.return_value.post.return_value.__aenter__.return_value = mock_response
            
            result = await integration_service._sync_to_triumvirate_monitor(session_id, results)
            
            assert result["status"] == "success"
            assert result["update_id"] == "update-123"
            assert result["endpoint"] == "https://monitor.test/api"
    
    @pytest.mark.asyncio
    async def test_sync_to_swarm_engine_success(self, integration_service):
        """Test successful sync to Swarm Engine."""
        session_id = "test-session"
        results = {"repositories": {"repo1": {"status": "completed"}}}
        
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = os.getcwd()
            os.chdir(temp_dir)
            
            try:
                # Create initial memory log
                memory_log = [{"old": "entry"}]
                with open("swarm_memory_log.json", 'w') as f:
                    json.dump(memory_log, f)
                
                # Create agent state
                agent_state = {"status": "active"}
                with open("agent_state.json", 'w') as f:
                    json.dump(agent_state, f)
                
                result = await integration_service._sync_to_swarm_engine(session_id, results)
                
                assert result["status"] == "success"
                assert result["memory_log_updated"] is True
                assert result["agent_state_updated"] is True
                
                # Verify memory log was updated
                with open("swarm_memory_log.json", 'r') as f:
                    updated_log = json.load(f)
                assert len(updated_log) == 2  # Original + new entry
                assert updated_log[-1]["session_id"] == session_id
                
                # Verify agent state was updated
                with open("agent_state.json", 'r') as f:
                    updated_state = json.load(f)
                assert "last_mirror_analysis" in updated_state
                assert updated_state["last_mirror_analysis"]["session_id"] == session_id
                
            finally:
                os.chdir(original_cwd)
    
    def test_dashboard_summary_creation(self, integration_service):
        """Test dashboard summary creation."""
        results = {
            "repositories": {
                "repo1": {"metrics": {"repository_health_score": 0.8}},
                "repo2": {"metrics": {"repository_health_score": 0.6}}
            },
            "summary": {
                "successful": 2,
                "failed": 0,
                "total_analysis_time": 120.5
            }
        }
        
        summary = integration_service._create_dashboard_summary(results)
        
        assert summary["repositories_analyzed"] == 2
        assert summary["successful_analyses"] == 2
        assert summary["failed_analyses"] == 0
        assert summary["total_analysis_time"] == 120.5
        assert 0 <= summary["health_score"] <= 1
        assert "last_updated" in summary
    
    def test_metrics_extraction(self, integration_service):
        """Test metrics extraction for monitoring."""
        results = {
            "repositories": {
                "repo1": {
                    "metrics": {"repository_health_score": 0.8},
                    "analysis": {
                        "basic": {"file_count": 50},
                        "deep": {
                            "code_metrics": {"lines_of_code": 1000},
                            "security_scan": {"potential_secrets": ["secret1"]}
                        }
                    }
                },
                "repo2": {
                    "metrics": {"repository_health_score": 0.6},
                    "analysis": {
                        "basic": {"file_count": 30},
                        "deep": {
                            "code_metrics": {"lines_of_code": 500},
                            "security_scan": {"potential_secrets": []}
                        }
                    }
                }
            }
        }
        
        metrics = integration_service._extract_metrics(results)
        
        assert metrics["repository_count"] == 2
        assert metrics["average_health_score"] == 0.7  # (0.8 + 0.6) / 2
        assert metrics["total_files_analyzed"] == 80  # 50 + 30
        assert metrics["total_lines_of_code"] == 1500  # 1000 + 500
        assert metrics["security_issues"] == 1  # Only repo1 has secrets
        assert metrics["performance_score"] == 0.7  # Same as health score
    
    def test_alert_generation(self, integration_service):
        """Test alert generation from analysis results."""
        results = {
            "repositories": {
                "failed-repo": {"status": "failed"},
                "secure-repo": {
                    "status": "completed",
                    "analysis": {
                        "deep": {
                            "security_scan": {"potential_secrets": ["secret1", "secret2"]}
                        }
                    }
                },
                "unhealthy-repo": {
                    "status": "completed",
                    "metrics": {"repository_health_score": 0.3},
                    "analysis": {"deep": {"security_scan": {"potential_secrets": []}}}
                }
            }
        }
        
        alerts = integration_service._generate_alerts(results)
        
        # Should generate 3 alerts: failed analysis, security issues, low health
        assert len(alerts) == 3
        
        alert_types = [alert["type"] for alert in alerts]
        assert "error" in alert_types
        assert "security" in alert_types
        assert "health" in alert_types
        
        # Check specific alert details
        error_alert = next(alert for alert in alerts if alert["type"] == "error")
        assert error_alert["repository"] == "failed-repo"
        assert error_alert["severity"] == "high"
        
        security_alert = next(alert for alert in alerts if alert["type"] == "security")
        assert security_alert["repository"] == "secure-repo"
        assert security_alert["count"] == 2
        
        health_alert = next(alert for alert in alerts if alert["type"] == "health")
        assert health_alert["repository"] == "unhealthy-repo"
        assert health_alert["health_score"] == 0.3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])