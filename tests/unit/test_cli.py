"""
Unit tests for Mirror Watcher CLI module.
"""

import pytest
import json
import tempfile
import os
from unittest.mock import patch, MagicMock
from pathlib import Path

from mirror_watcher.cli import MirrorWatcherCLI, create_parser, main
from mirror_watcher.analysis_engine import AnalysisEngine
from mirror_watcher.validator import DataValidator
from mirror_watcher.report_generator import ShadowScrollsReporter


class TestMirrorWatcherCLI:
    """Test the main CLI class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.cli = MirrorWatcherCLI()
        self.sample_data = {
            "agents": {
                "Oracle": {"status": "operational", "response_time": 1.2},
                "Gemini": {"status": "operational", "response_time": 0.8}
            },
            "system": {"timestamp": "2024-01-15T14:30:00Z", "status": "operational"},
            "messages": [
                {
                    "timestamp": "2024-01-15T14:29:45Z",
                    "from_agent": "Oracle",
                    "to_agents": ["Gemini"],
                    "channel": "test",
                    "message": "Test message"
                }
            ]
        }
    
    def test_cli_initialization(self):
        """Test CLI initialization."""
        assert isinstance(self.cli.analysis_engine, AnalysisEngine)
        assert isinstance(self.cli.reporter, ShadowScrollsReporter)
        assert isinstance(self.cli.validator, DataValidator)
    
    def test_status_command(self):
        """Test status command."""
        result = self.cli.status()
        
        assert result["success"] is True
        assert "timestamp" in result
        assert result["system"] == "Mirror Watcher CLI"
        assert result["version"] == "1.0.0"
        assert "components" in result
        assert result["components"]["analysis_engine"] == "operational"
    
    def test_analyze_with_valid_data(self):
        """Test analyze command with valid data."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(self.sample_data, f)
            temp_file = f.name
        
        try:
            result = self.cli.analyze(temp_file)
            
            assert result["success"] is True
            assert "analysis" in result
            assert "timestamp" in result
            assert result["input_file"] == temp_file
        finally:
            os.unlink(temp_file)
    
    def test_analyze_with_missing_file(self):
        """Test analyze command with missing file."""
        result = self.cli.analyze("nonexistent_file.json")
        
        assert result["success"] is False
        assert "error" in result
        assert "not found" in result["error"]
    
    def test_validate_command(self):
        """Test validate command."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(self.sample_data, f)
            temp_file = f.name
        
        try:
            result = self.cli.validate(temp_file)
            
            assert result["success"] is True
            assert "validation" in result
            assert result["file"] == temp_file
        finally:
            os.unlink(temp_file)
    
    def test_validate_invalid_json(self):
        """Test validate command with invalid JSON."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("invalid json content")
            temp_file = f.name
        
        try:
            result = self.cli.validate(temp_file)
            
            assert result["success"] is False
            assert "Invalid JSON format" in result["error"]
        finally:
            os.unlink(temp_file)
    
    def test_report_generation(self):
        """Test report generation."""
        analysis_data = {
            "success": True,
            "analysis": {
                "confidence": 0.85,
                "patterns": ["Normal operation pattern"],
                "anomalies": [],
                "recommendations": ["Continue monitoring"]
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(analysis_data, f)
            analysis_file = f.name
        
        try:
            result = self.cli.report(analysis_file)
            
            assert result["success"] is True
            assert "report" in result
            assert result["format"] == "ShadowScrolls"
        finally:
            os.unlink(analysis_file)


class TestCLIArgumentParser:
    """Test CLI argument parsing."""
    
    def test_parser_creation(self):
        """Test parser creation."""
        parser = create_parser()
        assert parser is not None
        assert parser.description == "Mirror Watcher CLI - Triune Swarm Engine Monitor"
    
    def test_status_command_parsing(self):
        """Test status command parsing."""
        parser = create_parser()
        args = parser.parse_args(['status'])
        assert args.command == 'status'
    
    def test_analyze_command_parsing(self):
        """Test analyze command parsing."""
        parser = create_parser()
        args = parser.parse_args(['analyze', '--input', 'test.json'])
        assert args.command == 'analyze'
        assert args.input == 'test.json'
    
    def test_analyze_with_output_parsing(self):
        """Test analyze command with output parsing."""
        parser = create_parser()
        args = parser.parse_args(['analyze', '--input', 'test.json', '--output', 'out.json'])
        assert args.command == 'analyze'
        assert args.input == 'test.json'
        assert args.output == 'out.json'
    
    def test_validate_command_parsing(self):
        """Test validate command parsing."""
        parser = create_parser()
        args = parser.parse_args(['validate', '--input', 'test.json'])
        assert args.command == 'validate'
        assert args.input == 'test.json'
    
    def test_report_command_parsing(self):
        """Test report command parsing."""
        parser = create_parser()
        args = parser.parse_args(['report', '--input', 'analysis.json'])
        assert args.command == 'report'
        assert args.input == 'analysis.json'


class TestCLIMainFunction:
    """Test the main CLI function."""
    
    @patch('sys.argv')
    def test_main_status_command(self, mock_argv):
        """Test main function with status command."""
        mock_argv.__getitem__.side_effect = lambda x: ['mirror-watcher', 'status'][x]
        mock_argv.__len__.return_value = 2
        
        with patch('mirror_watcher.cli.create_parser') as mock_parser:
            mock_args = MagicMock()
            mock_args.command = 'status'
            mock_parser.return_value.parse_args.return_value = mock_args
            
            with patch('builtins.print') as mock_print:
                result = main()
                assert result == 0
                mock_print.assert_called()
    
    @patch('sys.argv')
    def test_main_no_command(self, mock_argv):
        """Test main function with no command."""
        mock_argv.__getitem__.side_effect = lambda x: ['mirror-watcher'][x]
        mock_argv.__len__.return_value = 1
        
        with patch('mirror_watcher.cli.create_parser') as mock_parser:
            mock_args = MagicMock()
            mock_args.command = None
            mock_parser.return_value.parse_args.return_value = mock_args
            
            result = main()
            assert result == 1
    
    def test_main_keyboard_interrupt(self):
        """Test main function with keyboard interrupt."""
        with patch('mirror_watcher.cli.create_parser') as mock_parser:
            mock_parser.return_value.parse_args.side_effect = KeyboardInterrupt()
            
            with patch('builtins.print') as mock_print:
                result = main()
                assert result == 1
                mock_print.assert_called_with("\nOperation cancelled by user")


class TestCLIErrorHandling:
    """Test CLI error handling scenarios."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.cli = MirrorWatcherCLI()
    
    def test_analyze_with_invalid_json_file(self):
        """Test analyze with invalid JSON file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("{ invalid json }")
            temp_file = f.name
        
        try:
            result = self.cli.analyze(temp_file)
            assert result["success"] is False
            assert "error" in result
        finally:
            os.unlink(temp_file)
    
    def test_report_with_missing_analysis_file(self):
        """Test report generation with missing analysis file."""
        result = self.cli.report("nonexistent_analysis.json")
        assert result["success"] is False
        assert "error" in result
    
    def test_analyze_with_validation_failure(self):
        """Test analyze with validation failure."""
        invalid_data = {"invalid": "structure"}
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(invalid_data, f)
            temp_file = f.name
        
        try:
            result = self.cli.analyze(temp_file)
            # The CLI should handle validation failures gracefully
            assert "success" in result
            if not result["success"]:
                assert "error" in result
        finally:
            os.unlink(temp_file)
    
    @patch('mirror_watcher.cli.MirrorWatcherCLI.status')
    def test_main_with_exception(self, mock_status):
        """Test main function handling unexpected exceptions."""
        mock_status.side_effect = Exception("Unexpected error")
        
        with patch('sys.argv', ['mirror-watcher', 'status']):
            with patch('builtins.print') as mock_print:
                result = main()
                assert result == 1
                mock_print.assert_called()


if __name__ == "__main__":
    pytest.main([__file__])