#!/usr/bin/env python3
"""
Basic test suite for MirrorWatcherAI components
==============================================

Simple tests to validate core functionality without external dependencies.
"""

import asyncio
import os
import sys
import json
import tempfile
import unittest
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from src.mirror_watcher_ai import MirrorWatcherCLI, TriuneAnalyzer
    from src.mirror_watcher_ai.shadowscrolls import ShadowScrollsIntegration
    from src.mirror_watcher_ai.lineage import MirrorLineageLogger
    from src.mirror_watcher_ai.triune_integration import TriuneEcosystemConnector
except ImportError as e:
    print(f"Import error: {e}")
    print("Please install required dependencies: pip install aiohttp aiosqlite")
    sys.exit(1)


class TestMirrorWatcherCore(unittest.IsolatedAsyncioTestCase):
    """Test core MirrorWatcher functionality."""
    
    async def test_module_imports(self):
        """Test that all modules can be imported successfully."""
        # All imports should work without error
        self.assertIsNotNone(MirrorWatcherCLI)
        self.assertIsNotNone(TriuneAnalyzer)
        self.assertIsNotNone(ShadowScrollsIntegration)
        self.assertIsNotNone(MirrorLineageLogger)
        self.assertIsNotNone(TriuneEcosystemConnector)
    
    async def test_cli_initialization(self):
        """Test CLI initialization."""
        cli = MirrorWatcherCLI()
        self.assertIsNotNone(cli.analyzer)
        self.assertIsNotNone(cli.shadowscrolls)
        self.assertIsNotNone(cli.lineage_logger)
        self.assertIsNotNone(cli.triune_connector)
    
    async def test_health_check(self):
        """Test system health check."""
        cli = MirrorWatcherCLI()
        health_result = await cli.health_check()
        
        # Should return valid health check structure
        self.assertIn("timestamp", health_result)
        self.assertIn("overall_status", health_result)
        self.assertIn("components", health_result)
        
        # Should have all components
        components = health_result["components"]
        expected_components = ["analyzer", "shadowscrolls", "triune_connector", "lineage_logger"]
        
        for component in expected_components:
            self.assertIn(component, components)


class TestShadowScrollsIntegration(unittest.IsolatedAsyncioTestCase):
    """Test ShadowScrolls integration functionality."""
    
    async def test_shadowscrolls_initialization(self):
        """Test ShadowScrolls integration initialization."""
        shadowscrolls = ShadowScrollsIntegration()
        self.assertIsNotNone(shadowscrolls.endpoint)
        self.assertIsNotNone(shadowscrolls.scroll_directory)
    
    async def test_generate_verification_data(self):
        """Test verification data generation."""
        shadowscrolls = ShadowScrollsIntegration()
        
        test_data = {
            "test": "data",
            "repositories": {
                "test-repo": {"status": "completed"}
            }
        }
        
        verification = await shadowscrolls._generate_verification_data(test_data)
        
        self.assertIn("data_hash", verification)
        self.assertIn("algorithm", verification)
        self.assertIn("timestamp", verification)
        self.assertIn("merkle_root", verification)
        self.assertEqual(verification["algorithm"], "SHA-256")
    
    async def test_merkle_root_calculation(self):
        """Test Merkle tree root calculation."""
        shadowscrolls = ShadowScrollsIntegration()
        
        test_data = {
            "repositories": {
                "repo1": {"status": "completed"},
                "repo2": {"status": "completed"}
            }
        }
        
        merkle_root = await shadowscrolls._calculate_merkle_root(test_data)
        self.assertIsInstance(merkle_root, str)
        self.assertEqual(len(merkle_root), 64)  # SHA-256 hex string


class TestLineageLogger(unittest.IsolatedAsyncioTestCase):
    """Test lineage logging functionality."""
    
    async def test_lineage_initialization(self):
        """Test lineage logger initialization."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create temporary lineage logger
            lineage_logger = MirrorLineageLogger()
            lineage_logger.lineage_directory = temp_dir
            lineage_logger.db_path = os.path.join(temp_dir, "test_lineage.db")
            
            # Initialize database
            await lineage_logger._initialize_database()
            
            # Verify database file was created
            self.assertTrue(os.path.exists(lineage_logger.db_path))
    
    async def test_session_workflow(self):
        """Test complete session workflow."""
        with tempfile.TemporaryDirectory() as temp_dir:
            lineage_logger = MirrorLineageLogger()
            lineage_logger.lineage_directory = temp_dir
            lineage_logger.db_path = os.path.join(temp_dir, "test_lineage.db")
            
            await lineage_logger._initialize_database()
            
            # Start session
            session_data = await lineage_logger.start_session("test_session", "test")
            self.assertEqual(session_data["session_id"], "test_session")
            self.assertEqual(session_data["execution_type"], "test")
            
            # Log phase
            phase_data = await lineage_logger.log_phase("test_phase", {"test": "data"})
            self.assertEqual(phase_data["phase_name"], "test_phase")
            self.assertIn("data_hash", phase_data)
            
            # Finalize session
            final_report = {"status": "completed"}
            finalization = await lineage_logger.finalize_session(final_report)
            self.assertEqual(finalization["session_id"], "test_session")
            self.assertIn("final_verification", finalization)


class TestTriuneIntegration(unittest.IsolatedAsyncioTestCase):
    """Test Triune ecosystem integration."""
    
    async def test_connector_initialization(self):
        """Test Triune connector initialization."""
        connector = TriuneEcosystemConnector()
        self.assertIsNotNone(connector.endpoints)
        self.assertIsNotNone(connector.auth_tokens)
        self.assertIsNotNone(connector.config)
    
    async def test_configuration_loading(self):
        """Test configuration loading."""
        connector = TriuneEcosystemConnector()
        config = connector._load_configuration()
        
        # Should have basic configuration structure
        self.assertIsInstance(config, dict)
        self.assertIn("ecosystem_version", config)
    
    async def test_health_check(self):
        """Test Triune connector health check."""
        connector = TriuneEcosystemConnector()
        health_result = await connector.health_check()
        
        self.assertIn("status", health_result)
        self.assertIn("checks", health_result)
        self.assertIn("timestamp", health_result)


class TestAnalyzer(unittest.IsolatedAsyncioTestCase):
    """Test analyzer functionality (without external API calls)."""
    
    async def test_analyzer_initialization(self):
        """Test analyzer initialization."""
        analyzer = TriuneAnalyzer()
        self.assertIsNotNone(analyzer.github_api_base)
        self.assertIsNotNone(analyzer.triune_repositories)
        self.assertIsInstance(analyzer.triune_repositories, list)
    
    async def test_health_scoring(self):
        """Test health score calculation logic."""
        analyzer = TriuneAnalyzer()
        
        # Mock data for health score calculation
        repo_info = {"open_issues_count": 5}
        commits_analysis = {"recent_activity": {"last_commit": "2025-08-18T20:00:00Z"}}
        code_analysis = {"languages": {"Python": 1000}}
        security_scan = {"security_score": 90, "security_files_present": {"SECURITY.md": True}}
        performance_metrics = {"repository_size_kb": 1000}
        dependency_analysis = {"ecosystems_found": ["python"]}
        
        score = await analyzer._calculate_health_score(
            repo_info, commits_analysis, code_analysis,
            security_scan, performance_metrics, dependency_analysis
        )
        
        self.assertIsInstance(score, int)
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 100)
    
    async def test_utility_functions(self):
        """Test utility functions."""
        analyzer = TriuneAnalyzer()
        
        # Test conventional commit detection
        self.assertTrue(analyzer._is_conventional_commit("feat: add new feature"))
        self.assertTrue(analyzer._is_conventional_commit("fix: resolve bug"))
        self.assertFalse(analyzer._is_conventional_commit("random commit message"))
        
        # Test repo size categorization
        self.assertEqual(analyzer._categorize_repo_size(500), "small")
        self.assertEqual(analyzer._categorize_repo_size(5000), "medium")
        self.assertEqual(analyzer._categorize_repo_size(50000), "large")


def run_tests():
    """Run all tests and return results."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test cases
    test_classes = [
        TestMirrorWatcherCore,
        TestShadowScrollsIntegration,
        TestLineageLogger,
        TestTriuneIntegration,
        TestAnalyzer
    ]
    
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result


async def integration_test():
    """Run basic integration test."""
    print("\n🧪 Running integration test...")
    
    try:
        # Test CLI health check
        cli = MirrorWatcherCLI()
        health_result = await cli.health_check()
        
        print(f"✅ Health check completed")
        print(f"   Overall status: {health_result['overall_status']}")
        print(f"   Components checked: {len(health_result['components'])}")
        
        # Test ShadowScrolls verification
        shadowscrolls = ShadowScrollsIntegration()
        test_data = {"test": "integration"}
        verification = await shadowscrolls._generate_verification_data(test_data)
        
        print(f"✅ ShadowScrolls verification generated")
        print(f"   Algorithm: {verification['algorithm']}")
        print(f"   Hash length: {len(verification['data_hash'])}")
        
        # Test lineage logging
        with tempfile.TemporaryDirectory() as temp_dir:
            lineage_logger = MirrorLineageLogger()
            lineage_logger.lineage_directory = temp_dir
            lineage_logger.db_path = os.path.join(temp_dir, "test.db")
            
            await lineage_logger._initialize_database()
            await lineage_logger.start_session("integration_test", "test")
            
            print(f"✅ Lineage logging initialized")
            print(f"   Database created: {os.path.exists(lineage_logger.db_path)}")
        
        print("\n🎉 Integration test completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Integration test failed: {str(e)}")
        return False


def main():
    """Main test runner."""
    print("🔍 MirrorWatcherAI Test Suite")
    print("=" * 50)
    
    # Run unit tests
    print("\n📋 Running unit tests...")
    test_result = run_tests()
    
    # Run integration test
    integration_success = asyncio.run(integration_test())
    
    # Summary
    print("\n📊 Test Summary")
    print("-" * 30)
    print(f"Unit tests run: {test_result.testsRun}")
    print(f"Failures: {len(test_result.failures)}")
    print(f"Errors: {len(test_result.errors)}")
    print(f"Integration test: {'✅ PASSED' if integration_success else '❌ FAILED'}")
    
    # Overall result
    overall_success = (
        test_result.wasSuccessful() and 
        integration_success
    )
    
    print(f"\n🎯 Overall Result: {'✅ ALL TESTS PASSED' if overall_success else '❌ SOME TESTS FAILED'}")
    
    # Exit with appropriate code
    sys.exit(0 if overall_success else 1)


if __name__ == "__main__":
    main()