"""
CLI module for Mirror Watcher.

Provides command-line interface for monitoring and analyzing Triune Swarm Engine.
"""

import argparse
import json
import sys
from datetime import datetime
from typing import Dict, Any, List
from pathlib import Path

from .analysis_engine import AnalysisEngine
from .report_generator import ShadowScrollsReporter
from .validator import DataValidator


class MirrorWatcherCLI:
    """Main CLI class for Mirror Watcher commands."""
    
    def __init__(self):
        self.analysis_engine = AnalysisEngine()
        self.reporter = ShadowScrollsReporter()
        self.validator = DataValidator()
    
    def analyze(self, input_file: str, output_format: str = "json") -> Dict[str, Any]:
        """Analyze input data and return results."""
        try:
            # Validate input file
            if not Path(input_file).exists():
                raise FileNotFoundError(f"Input file not found: {input_file}")
            
            # Load and validate data
            with open(input_file, 'r') as f:
                data = json.load(f)
            
            validation_result = self.validator.validate_input(data)
            if not validation_result["valid"]:
                return {
                    "success": False,
                    "error": "Input validation failed",
                    "details": validation_result["errors"]
                }
            
            # Perform analysis
            analysis_result = self.analysis_engine.analyze(data)
            
            # Convert AnalysisResult to dict for JSON serialization
            analysis_dict = self.analysis_engine.to_dict(analysis_result)
            
            result = {
                "success": True,
                "timestamp": datetime.now().isoformat(),
                "input_file": input_file,
                "analysis": analysis_dict,
                "format": output_format
            }
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def status(self) -> Dict[str, Any]:
        """Get system status."""
        return {
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "system": "Mirror Watcher CLI",
            "version": "1.0.0",
            "components": {
                "analysis_engine": "operational",
                "reporter": "operational",
                "validator": "operational"
            },
            "uptime": "system_initialized"
        }
    
    def validate(self, input_file: str) -> Dict[str, Any]:
        """Validate input data format and structure."""
        try:
            if not Path(input_file).exists():
                return {
                    "success": False,
                    "error": f"File not found: {input_file}"
                }
            
            with open(input_file, 'r') as f:
                data = json.load(f)
            
            result = self.validator.validate_input(data)
            return {
                "success": True,
                "timestamp": datetime.now().isoformat(),
                "file": input_file,
                "validation": result
            }
            
        except json.JSONDecodeError as e:
            return {
                "success": False,
                "error": f"Invalid JSON format: {str(e)}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def report(self, analysis_file: str, output_file: str = None) -> Dict[str, Any]:
        """Generate ShadowScrolls format report."""
        try:
            with open(analysis_file, 'r') as f:
                analysis_data = json.load(f)
            
            report = self.reporter.generate_report(analysis_data)
            
            if output_file:
                with open(output_file, 'w') as f:
                    json.dump(report, f, indent=2)
                
                return {
                    "success": True,
                    "timestamp": datetime.now().isoformat(),
                    "report_file": output_file,
                    "format": "ShadowScrolls"
                }
            else:
                return {
                    "success": True,
                    "timestamp": datetime.now().isoformat(),
                    "report": report,
                    "format": "ShadowScrolls"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


def create_parser() -> argparse.ArgumentParser:
    """Create command line argument parser."""
    parser = argparse.ArgumentParser(
        description="Mirror Watcher CLI - Triune Swarm Engine Monitor",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  mirror-watcher status
  mirror-watcher analyze --input data.json --output analysis.json
  mirror-watcher validate --input data.json
  mirror-watcher report --input analysis.json --output report.json
        """)
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Show system status')
    
    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Analyze input data')
    analyze_parser.add_argument('--input', '-i', required=True, help='Input JSON file')
    analyze_parser.add_argument('--output', '-o', help='Output file (default: stdout)')
    analyze_parser.add_argument('--format', choices=['json', 'yaml'], default='json', help='Output format')
    
    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Validate input data')
    validate_parser.add_argument('--input', '-i', required=True, help='Input JSON file')
    
    # Report command
    report_parser = subparsers.add_parser('report', help='Generate ShadowScrolls report')
    report_parser.add_argument('--input', '-i', required=True, help='Analysis JSON file')
    report_parser.add_argument('--output', '-o', help='Output report file (default: stdout)')
    
    return parser


def main():
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    cli = MirrorWatcherCLI()
    
    try:
        if args.command == 'status':
            result = cli.status()
        
        elif args.command == 'analyze':
            result = cli.analyze(args.input, args.format)
            if args.output:
                with open(args.output, 'w') as f:
                    json.dump(result, f, indent=2)
                print(f"Analysis saved to {args.output}")
                return 0
        
        elif args.command == 'validate':
            result = cli.validate(args.input)
        
        elif args.command == 'report':
            result = cli.report(args.input, args.output)
            if not args.output:
                # Print report to stdout if no output file specified
                if result.get("success") and "report" in result:
                    print(json.dumps(result["report"], indent=2))
                    return 0
        
        else:
            print(f"Unknown command: {args.command}")
            return 1
        
        # Print result
        print(json.dumps(result, indent=2))
        return 0 if result.get("success", False) else 1
        
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        return 1
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())