"""
Test suite for MirrorWatcherAI Analyzer

Comprehensive testing for the Triune analysis engine including
repository analysis, metrics calculation, and quality assessment.
"""

import pytest
import asyncio
import tempfile
from pathlib import Path
import json
import sys
import os

# Add src to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from mirror_watcher_ai.analyzer import TriuneAnalyzer, MirrorAnalysisEngine

class TestTriuneAnalyzer:
    """Test cases for the main Triune analyzer"""
    
    @pytest.fixture
    def analyzer(self):
        """Create analyzer instance for testing"""
        config = {
            'parallel_analysis': False,  # Use sequential for tests
            'max_workers': 1,
            'timeout_seconds': 30
        }
        return TriuneAnalyzer(config)
    
    @pytest.fixture
    def sample_repo(self):
        """Create a sample repository for testing"""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            
            # Create sample Python file
            (repo_path / "main.py").write_text("""
# Sample Python file
def hello_world():
    '''Print hello world'''
    print("Hello, World!")

class SampleClass:
    '''Sample class for testing'''
    def __init__(self):
        self.value = 42
    
    def get_value(self):
        return self.value

if __name__ == "__main__":
    hello_world()
""")
            
            # Create sample JavaScript file
            (repo_path / "app.js").write_text("""
// Sample JavaScript file
function helloWorld() {
    console.log("Hello, World!");
}

class SampleClass {
    constructor() {
        this.value = 42;
    }
    
    getValue() {
        return this.value;
    }
}

module.exports = { helloWorld, SampleClass };
""")
            
            # Create README
            (repo_path / "README.md").write_text("""
# Sample Repository

This is a sample repository for testing MirrorWatcherAI.

## Features

- Python code
- JavaScript code  
- Documentation
""")
            
            # Create package.json
            (repo_path / "package.json").write_text(json.dumps({
                "name": "sample-repo",
                "version": "1.0.0",
                "description": "Sample repository for testing"
            }))
            
            # Create .gitignore
            (repo_path / ".gitignore").write_text("""
node_modules/
*.pyc
__pycache__/
.env
""")
            
            yield repo_path
    
    @pytest.mark.asyncio
    async def test_analyze_local_repository(self, analyzer, sample_repo):
        """Test analysis of a local repository"""
        result = await analyzer.analyze_repository(str(sample_repo))
        
        # Check basic result structure
        assert "repository" in result
        assert "timestamp" in result
        assert "status" in result
        assert result["status"] == "completed"
        
        # Check analysis components
        assert "structure" in result
        assert "metrics" in result
        assert "quality" in result
        assert "security" in result
        assert "triune_integration" in result
    
    def test_analyze_structure(self, analyzer, sample_repo):
        """Test repository structure analysis"""
        structure = analyzer._analyze_structure(sample_repo)
        
        # Check structure analysis
        assert "total_files" in structure
        assert "total_directories" in structure
        assert "file_types" in structure
        assert "key_files" in structure
        
        # Verify detected files
        assert structure["total_files"] > 0
        assert ".py" in structure["file_types"]
        assert ".js" in structure["file_types"]
        assert "readme.md" in structure["key_files"]
        assert "package.json" in structure["key_files"]
    
    def test_analyze_metrics(self, analyzer, sample_repo):
        """Test code metrics analysis"""
        metrics = analyzer._analyze_metrics(sample_repo)
        
        # Check metrics structure
        assert "lines_of_code" in metrics
        assert "comment_lines" in metrics
        assert "functions" in metrics
        assert "classes" in metrics
        assert "language_breakdown" in metrics
        
        # Verify metrics values
        assert metrics["lines_of_code"] > 0
        assert metrics["functions"] >= 2  # hello_world and getValue
        assert metrics["classes"] >= 2   # SampleClass in both files
        assert "py" in metrics["language_breakdown"]
        assert "js" in metrics["language_breakdown"]
    
    def test_analyze_quality(self, analyzer, sample_repo):
        """Test code quality analysis"""
        quality = analyzer._analyze_quality(sample_repo)
        
        # Check quality metrics
        assert "documentation_score" in quality
        assert "test_coverage_estimated" in quality
        assert "configuration_quality" in quality
        assert "best_practices_score" in quality
        
        # Verify quality scores
        assert quality["documentation_score"] > 0  # Has README
        assert quality["configuration_quality"] > 0  # Has package.json and .gitignore
        assert quality["best_practices_score"] > 0  # Has .gitignore
    
    def test_analyze_security(self, analyzer, sample_repo):
        """Test security analysis"""
        security = analyzer._analyze_security(sample_repo)
        
        # Check security analysis
        assert "security_score" in security
        assert "vulnerabilities" in security
        assert "sensitive_files" in security
        assert "recommendations" in security
        
        # Verify security assessment
        assert isinstance(security["security_score"], (int, float))
        assert 0 <= security["security_score"] <= 100
        assert isinstance(security["sensitive_files"], list)
    
    def test_analyze_triune_integration(self, analyzer, sample_repo):
        """Test Triune ecosystem integration analysis"""
        integration = analyzer._analyze_triune_integration(sample_repo)
        
        # Check integration analysis
        assert "triune_compatibility" in integration
        assert "ecosystem_components" in integration
        assert "integration_score" in integration
        assert "mirror_watcher_ready" in integration
        
        # Verify integration assessment
        assert isinstance(integration["triune_compatibility"], (int, float))
        assert isinstance(integration["ecosystem_components"], list)
        assert isinstance(integration["mirror_watcher_ready"], bool)
    
    def test_file_metrics_analysis(self, analyzer):
        """Test individual file metrics analysis"""
        # Sample Python code lines
        python_lines = [
            "# This is a comment",
            "",
            "def sample_function():",
            "    '''Docstring here'''",
            "    return 42",
            "",
            "class SampleClass:",
            "    pass"
        ]
        
        patterns = {'comment': '#', 'multiline_start': '"""', 'multiline_end': '"""'}
        stats = analyzer._analyze_file_metrics(python_lines, patterns)
        
        # Verify metrics
        assert stats["comment_lines"] >= 1  # At least the # comment
        assert stats["blank_lines"] >= 2    # Empty lines
        assert stats["code_lines"] >= 4     # Actual code lines
        assert stats["functions"] >= 1      # sample_function
        assert stats["classes"] >= 1        # SampleClass

class TestMirrorAnalysisEngine:
    """Test cases for the advanced analysis engine"""
    
    @pytest.fixture
    def analysis_engine(self):
        """Create analysis engine for testing"""
        config = {
            'parallel_analysis': False,
            'timeout_seconds': 30
        }
        return MirrorAnalysisEngine(config)
    
    @pytest.mark.asyncio
    async def test_analyze_multiple_repositories(self, analysis_engine, sample_repo):
        """Test analysis of multiple repositories"""
        # For testing, use the same sample repo twice
        repositories = [str(sample_repo), str(sample_repo)]
        
        result = await analysis_engine.analyze_multiple_repositories(repositories)
        
        # Check result structure
        assert "repositories" in result
        assert "comparative_analysis" in result
        assert "recommendations" in result
        
        # Verify repository results
        assert len(result["repositories"]) == 2
        for repo_result in result["repositories"].values():
            assert "status" in repo_result
    
    def test_generate_comparative_analysis(self, analysis_engine):
        """Test comparative analysis generation"""
        # Sample repository results
        repo_results = {
            "repo1": {
                "metrics": {
                    "lines_of_code": 100,
                    "functions": 5,
                    "classes": 2
                },
                "quality": {
                    "documentation_score": 80
                }
            },
            "repo2": {
                "metrics": {
                    "lines_of_code": 200,
                    "functions": 10,
                    "classes": 4
                },
                "quality": {
                    "documentation_score": 60
                }
            }
        }
        
        comparative = analysis_engine._generate_comparative_analysis(repo_results)
        
        # Check comparative analysis
        assert "total_repositories" in comparative
        assert "average_metrics" in comparative
        assert comparative["total_repositories"] == 2
        
        # Verify averages if calculated
        if "avg_lines_of_code" in comparative["average_metrics"]:
            assert comparative["average_metrics"]["avg_lines_of_code"] == 150

class TestAnalyzerIntegration:
    """Integration tests for the analyzer system"""
    
    @pytest.mark.asyncio
    async def test_end_to_end_analysis(self):
        """Test complete end-to-end analysis flow"""
        # Create analyzer
        analyzer = TriuneAnalyzer({
            'parallel_analysis': False,
            'timeout_seconds': 60
        })
        
        # Create temporary repository
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            
            # Create a more comprehensive test repository
            (repo_path / "src").mkdir()
            (repo_path / "tests").mkdir()
            (repo_path / "docs").mkdir()
            
            # Add source files
            (repo_path / "src" / "main.py").write_text("""
import os
import sys

def main():
    '''Main function'''
    print("Hello from main!")
    
def process_data(data):
    '''Process data function'''
    if not data:
        return None
    return [x * 2 for x in data]

class DataProcessor:
    '''Data processing class'''
    def __init__(self):
        self.count = 0
    
    def process(self, item):
        self.count += 1
        return item.upper()

if __name__ == "__main__":
    main()
""")
            
            # Add test files
            (repo_path / "tests" / "test_main.py").write_text("""
import unittest
from src.main import process_data, DataProcessor

class TestMain(unittest.TestCase):
    def test_process_data(self):
        result = process_data([1, 2, 3])
        self.assertEqual(result, [2, 4, 6])
    
    def test_data_processor(self):
        processor = DataProcessor()
        result = processor.process("hello")
        self.assertEqual(result, "HELLO")

if __name__ == "__main__":
    unittest.main()
""")
            
            # Add documentation
            (repo_path / "docs" / "README.md").write_text("""
# Test Project

This is a comprehensive test project.

## Features
- Data processing
- Unit tests
- Documentation
""")
            
            # Add configuration files
            (repo_path / "requirements.txt").write_text("pytest\nrequests\n")
            (repo_path / ".gitignore").write_text("*.pyc\n__pycache__/\n")
            
            # Run analysis
            result = await analyzer.analyze_repository(str(repo_path))
            
            # Comprehensive verification
            assert result["status"] == "completed"
            assert "execution_time_seconds" in result
            
            # Check structure analysis
            structure = result["structure"]
            assert structure["total_files"] >= 5
            assert structure["total_directories"] >= 3
            assert ".py" in structure["file_types"]
            
            # Check metrics
            metrics = result["metrics"]
            assert metrics["lines_of_code"] > 20
            assert metrics["functions"] >= 3
            assert metrics["classes"] >= 2
            
            # Check quality scores
            quality = result["quality"]
            assert quality["documentation_score"] > 0
            assert quality["test_coverage_estimated"] > 0  # Has test files
            assert quality["configuration_quality"] > 0  # Has requirements.txt
            
            # Check security analysis
            security = result["security"]
            assert "security_score" in security
            assert isinstance(security["security_score"], (int, float))
            
            # Check Triune integration
            integration = result["triune_integration"]
            assert "triune_compatibility" in integration
            assert "integration_score" in integration

if __name__ == "__main__":
    # Run tests if executed directly
    pytest.main([__file__, "-v"])