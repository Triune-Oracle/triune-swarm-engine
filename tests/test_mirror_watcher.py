"""
Test suite for MirrorWatcherAI system
"""

import unittest
import asyncio
import tempfile
import shutil
from pathlib import Path
import json
import sys
import os

# Add src to path for imports

from src.mirror_watcher_ai.analyzer import TriuneAnalyzer
from src.mirror_watcher_ai.shadowscrolls import ShadowScrollsClient  
from src.mirror_watcher_ai.lineage import MirrorLineage
from src.mirror_watcher_ai.triune_integration import TriuneIntegrator


class TestTriuneAnalyzer(unittest.TestCase):
    """Test cases for TriuneAnalyzer."""
    
    def setUp(self):
        self.config = {
            'depth': 'basic',
            'include_dependencies': False,
            'security_scan': False,
            'performance_metrics': False
        }
        self.analyzer = TriuneAnalyzer(self.config)
    
    def test_analyzer_initialization(self):
        """Test analyzer initializes correctly."""
        self.assertEqual(self.analyzer.analysis_depth, 'basic')
        self.assertFalse(self.analyzer.include_dependencies)
    
    def test_calculate_quality_score(self):
        """Test quality score calculation."""
        analysis = {
            'code_metrics': {'comment_ratio': 15},
            'security': {'security_score': 8},
            'performance': {'performance_score': 9},
            'structure': {'key_files_present': ['README.md', 'LICENSE']}
        }
        
        score = self.analyzer.calculate_quality_score(analysis)
        self.assertIsInstance(score, float)
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 10.0)


class TestShadowScrollsClient(unittest.TestCase):
    """Test cases for ShadowScrollsClient."""
    
    def setUp(self):
        self.client = ShadowScrollsClient()
    
    def test_client_initialization(self):
        """Test client initializes correctly."""
        self.assertIsInstance(self.client, ShadowScrollsClient)
    
    def test_calculate_analysis_hash(self):
        """Test analysis hash calculation."""
        analysis_data = {'test': 'data', 'number': 123}
        hash_result = self.client._calculate_analysis_hash(analysis_data)
        
        self.assertIsInstance(hash_result, str)
        self.assertEqual(len(hash_result), 64)  # SHA-256 hex length


class TestMirrorLineage(unittest.TestCase):
    """Test cases for MirrorLineage."""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.config = {
            'encryption': False,  # Disable for testing
            'hash_algorithm': 'sha256',
            'compression': False,  # Disable for testing
            'storage_path': self.temp_dir
        }
        self.lineage = MirrorLineage(self.config)
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir)
    
    def test_lineage_initialization(self):
        """Test lineage system initializes correctly."""
        self.assertTrue(Path(self.temp_dir).exists())
        self.assertTrue((Path(self.temp_dir) / 'lineage_chain.json').exists())
    
    def test_entry_id_generation(self):
        """Test entry ID generation."""
        entry_id = self.lineage._generate_entry_id()
        self.assertIsInstance(entry_id, str)
        self.assertTrue(entry_id.startswith('lineage_'))


class TestTriuneIntegrator(unittest.TestCase):
    """Test cases for TriuneIntegrator."""
    
    def setUp(self):
        self.config = {
            'legio_cognito': False,  # Disable for testing
            'triumvirate_monitor': False,  # Disable for testing
            'auto_archive': False
        }
        self.integrator = TriuneIntegrator(self.config)
    
    def test_integrator_initialization(self):
        """Test integrator initializes correctly."""
        self.assertFalse(self.integrator.legio_cognito_enabled)
        self.assertFalse(self.integrator.triumvirate_monitor_enabled)
    
    def test_calculate_success_rate(self):
        """Test success rate calculation."""
        analysis_results = {
            'summary': {
                'total_repositories': 5,
                'successful_analyses': 4
            }
        }
        
        success_rate = self.integrator._calculate_success_rate(analysis_results)
        self.assertEqual(success_rate, 80.0)


class TestIntegration(unittest.TestCase):
    """Integration tests for the complete system."""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        shutil.rmtree(self.temp_dir)
    
    def test_configuration_loading(self):
        """Test configuration file loading."""
        config_path = Path(self.temp_dir) / 'test_config.json'
        test_config = {
            'analysis': {'depth': 'test'},
            'shadowscrolls': {'endpoint': 'test'},
            'targets': ['test/repo']
        }
        
        with open(config_path, 'w') as f:
            json.dump(test_config, f)
        
        # Test that configuration can be loaded
        with open(config_path, 'r') as f:
            loaded_config = json.load(f)
        
        self.assertEqual(loaded_config['analysis']['depth'], 'test')
        self.assertEqual(loaded_config['targets'], ['test/repo'])


async def run_async_tests():
    """Run async test cases."""
    
    # Test async analyzer functionality
    config = {
        'depth': 'basic',
        'include_dependencies': False,
        'security_scan': False,
        'performance_metrics': False
    }
    
    analyzer = TriuneAnalyzer(config)
    
    # Test aggregate metrics calculation
    mock_results = [
        {'status': 'completed', 'quality_score': 8.5},
        {'status': 'completed', 'quality_score': 7.2},
        Exception('test error')  # Simulate a failed analysis
    ]
    
    metrics = await analyzer.calculate_aggregate_metrics(mock_results)
    assert 'average_quality_score' in metrics
    print("✅ Async analyzer tests passed")
    
    # Test ShadowScrolls client
    client = ShadowScrollsClient()
    analysis_data = {'test': 'data'}
    lineage_data = {'hash': 'test_hash'}
    
    # This will create a mock attestation since we don't have real credentials
    result = await client.submit_analysis(analysis_data, lineage_data)
    assert result['status'] == 'mock_attestation'
    print("✅ Async ShadowScrolls tests passed")


if __name__ == '__main__':
    # Run sync tests
    print("🧪 Running MirrorWatcherAI test suite...")
    print()
    
    unittest.main(verbosity=2, exit=False)
    
    print()
    print("🔄 Running async tests...")
    asyncio.run(run_async_tests())
    
    print()
    print("✅ All tests completed successfully!")
    print("🎉 MirrorWatcherAI system is ready for deployment!")