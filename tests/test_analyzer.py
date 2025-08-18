#!/usr/bin/env python3
"""
Test suite for MirrorWatcherAI analyzer functionality.

Tests the core analysis engine including:
- Repository metadata fetching
- Basic and deep analysis
- Metrics calculation
- Error handling and recovery
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

from mirror_watcher_ai.analyzer import TriuneAnalyzer


class TestTriuneAnalyzer:
    """Test cases for the TriuneAnalyzer class."""
    
    @pytest.fixture
    def analyzer_config(self):
        """Provide basic analyzer configuration."""
        return {
            "timeout": 60,
            "concurrent_repos": 2,
            "output_format": "json"
        }
    
    @pytest.fixture
    def analyzer(self, analyzer_config):
        """Create TriuneAnalyzer instance for testing."""
        return TriuneAnalyzer(analyzer_config)
    
    def test_analyzer_initialization(self, analyzer):
        """Test analyzer initializes correctly."""
        assert analyzer.timeout == 60
        assert analyzer.concurrent_repos == 2
        assert analyzer.output_format == "json"
        assert analyzer.metrics["sessions"] == 0
    
    @pytest.mark.asyncio
    async def test_health_check_no_token(self, analyzer):
        """Test health check without GitHub token."""
        # Clear the token for this test
        analyzer.github_token = ""
        analyzer.github_headers = {}
        
        health = await analyzer.health_check()
        
        assert health["status"] == "healthy"
        assert health["github_api"] == "no_token"
        assert "metrics" in health
    
    @pytest.mark.asyncio
    async def test_health_check_with_token(self, analyzer):
        """Test health check with GitHub token."""
        # Mock the HTTP request
        analyzer.github_token = "test_token"
        analyzer.github_headers = {"Authorization": "token test_token"}
        
        with patch("aiohttp.ClientSession") as mock_session:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_session.return_value.__aenter__.return_value.get.return_value.__aenter__.return_value = mock_response
            
            health = await analyzer.health_check()
            
            assert health["status"] == "healthy"
            assert health["github_api"] == "connected"
    
    def test_basic_analysis_empty_repo(self, analyzer):
        """Test basic analysis on empty repository."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            
            # Run the analysis synchronously for testing
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                analysis = loop.run_until_complete(
                    analyzer._perform_basic_analysis(repo_path)
                )
                
                assert analysis["file_count"] == 0
                assert analysis["total_size"] == 0
                assert analysis["file_types"] == {}
                assert analysis["directory_structure"] == {}
                
            finally:
                loop.close()
    
    def test_basic_analysis_with_files(self, analyzer):
        """Test basic analysis with sample files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            
            # Create test files
            (repo_path / "README.md").write_text("# Test Repository")
            (repo_path / "main.py").write_text("print('Hello, World!')")
            (repo_path / "package.json").write_text('{"name": "test"}')
            
            # Create subdirectory
            (repo_path / "src").mkdir()
            (repo_path / "src" / "module.py").write_text("def test(): pass")
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                analysis = loop.run_until_complete(
                    analyzer._perform_basic_analysis(repo_path)
                )
                
                assert analysis["file_count"] == 4
                assert analysis["total_size"] > 0
                assert ".md" in analysis["file_types"]
                assert ".py" in analysis["file_types"]
                assert ".json" in analysis["file_types"]
                assert "README.md" in analysis["documentation_files"][0]
                assert "package.json" in analysis["config_files"][0]
                assert len(analysis["code_files"]) == 2
                
            finally:
                loop.close()
    
    def test_code_metrics_calculation(self, analyzer):
        """Test code metrics calculation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            
            # Create Python file with various constructs
            python_code = """# This is a comment
def hello_world():
    '''Function docstring'''
    print("Hello, World!")

class TestClass:
    def __init__(self):
        pass
    
    def method(self):
        return True

# Another comment
"""
            (repo_path / "test.py").write_text(python_code)
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                metrics = loop.run_until_complete(
                    analyzer._analyze_code_metrics(repo_path)
                )
                
                assert metrics["lines_of_code"] > 0
                assert metrics["lines_of_comments"] >= 2
                assert metrics["blank_lines"] > 0
                assert metrics["function_count"] >= 2  # hello_world and method
                assert metrics["class_count"] >= 1  # TestClass
                
            finally:
                loop.close()
    
    def test_security_scan_basic(self, analyzer):
        """Test basic security scanning."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            
            # Create file with potential secrets
            config_content = """
API_KEY = "secret_key_123"
password = "my_password"
token = "abc123def456"
"""
            (repo_path / "config.py").write_text(config_content)
            
            # Create suspicious file
            (repo_path / "private.key").write_text("-----BEGIN PRIVATE KEY-----")
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                security = loop.run_until_complete(
                    analyzer._perform_security_scan(repo_path)
                )
                
                assert len(security["suspicious_files"]) >= 1
                assert "private.key" in security["suspicious_files"][0]
                assert len(security["potential_secrets"]) > 0
                
            finally:
                loop.close()
    
    def test_dependency_analysis_python(self, analyzer):
        """Test dependency analysis for Python projects."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            
            # Create requirements.txt
            requirements = """requests==2.28.1
pytest>=7.0.0
black
# This is a comment
"""
            (repo_path / "requirements.txt").write_text(requirements)
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                deps = loop.run_until_complete(
                    analyzer._analyze_dependencies(repo_path)
                )
                
                assert "pip" in deps["package_managers"]
                assert "requirements.txt" in deps["dependency_files"]
                assert deps["total_dependencies"] == 3  # Excluding comment
                
            finally:
                loop.close()
    
    def test_dependency_analysis_nodejs(self, analyzer):
        """Test dependency analysis for Node.js projects."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            
            # Create package.json
            package_json = {
                "name": "test-project",
                "dependencies": {
                    "express": "^4.18.0",
                    "lodash": "^4.17.21"
                },
                "devDependencies": {
                    "jest": "^28.0.0"
                }
            }
            (repo_path / "package.json").write_text(json.dumps(package_json, indent=2))
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                deps = loop.run_until_complete(
                    analyzer._analyze_dependencies(repo_path)
                )
                
                assert "npm" in deps["package_managers"]
                assert "package.json" in deps["dependency_files"]
                assert deps["total_dependencies"] == 3  # 2 deps + 1 devDep
                
            finally:
                loop.close()
    
    def test_quality_metrics_calculation(self, analyzer):
        """Test quality metrics calculation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            
            # Create various file types
            (repo_path / "README.md").write_text("Documentation")
            (repo_path / "test_main.py").write_text("def test(): pass")
            (repo_path / "config.json").write_text('{"setting": "value"}')
            (repo_path / "main.py").write_text("def main(): pass")
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                quality = loop.run_until_complete(
                    analyzer._calculate_quality_metrics(repo_path)
                )
                
                assert 0 <= quality["documentation_coverage"] <= 1
                assert 0 <= quality["test_coverage_estimate"] <= 1
                assert 0 <= quality["configuration_completeness"] <= 1
                
                # Should have some test coverage due to test_main.py
                assert quality["test_coverage_estimate"] > 0
                
            finally:
                loop.close()
    
    @pytest.mark.asyncio
    async def test_repository_metrics_calculation(self, analyzer):
        """Test comprehensive repository metrics calculation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            
            # Create sample files
            (repo_path / "README.md").write_text("# Test Project")
            (repo_path / "main.py").write_text("def main(): pass")
            
            # Mock metadata
            metadata = {
                "description": "Test repository",
                "stargazers_count": 5,
                "open_issues_count": 2,
                "pushed_at": "2024-01-01T12:00:00Z"
            }
            
            # Mock analysis
            analysis = {
                "file_count": 10,
                "documentation_files": ["README.md"],
                "config_files": ["package.json"],
                "code_files": ["main.py", "utils.py"]
            }
            
            metrics = await analyzer._calculate_repository_metrics(
                repo_path, metadata, analysis
            )
            
            assert 0 <= metrics["repository_health_score"] <= 1
            assert 0 <= metrics["activity_score"] <= 1
            assert 0 <= metrics["code_quality_score"] <= 1
            assert 0 <= metrics["maintainability_score"] <= 1
            assert "timestamps" in metrics


if __name__ == "__main__":
    pytest.main([__file__, "-v"])