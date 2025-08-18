#!/usr/bin/env python3
"""
MirrorWatcherAI CLI Interface
Complete CLI interface with async execution for automated mirror watching and analysis.
"""

import asyncio
import argparse
import sys
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Optional

from .analyzer import TriuneAnalyzer
from .shadowscrolls import ShadowScrollsClient
from .lineage import MirrorLineage
from .triune_integration import TriuneIntegrator


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('mirror_watcher.log')
    ]
)
logger = logging.getLogger(__name__)


class MirrorWatcherCLI:
    """Main CLI interface for MirrorWatcherAI automation system."""
    
    def __init__(self):
        self.analyzer = None
        self.shadowscrolls = None
        self.lineage = None
        self.integrator = None
        
    async def initialize_components(self, config: Dict[str, Any]) -> None:
        """Initialize all MirrorWatcherAI components asynchronously."""
        try:
            # Initialize core analyzer
            self.analyzer = TriuneAnalyzer(config.get('analysis', {}))
            
            # Initialize ShadowScrolls client
            shadowscrolls_config = config.get('shadowscrolls', {})
            self.shadowscrolls = ShadowScrollsClient(
                endpoint=shadowscrolls_config.get('endpoint'),
                api_key=shadowscrolls_config.get('api_key')
            )
            
            # Initialize lineage tracking
            self.lineage = MirrorLineage(config.get('lineage', {}))
            
            # Initialize Triune integration
            self.integrator = TriuneIntegrator(config.get('triune', {}))
            
            logger.info("All MirrorWatcherAI components initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize components: {str(e)}")
            raise
    
    async def run_analysis(self, targets: list, output_format: str = 'json') -> Dict[str, Any]:
        """Run comprehensive analysis on specified targets."""
        start_time = datetime.now(timezone.utc)
        
        try:
            logger.info(f"Starting analysis of {len(targets)} targets")
            
            # Run parallel analysis
            analysis_results = await self.analyzer.analyze_repositories(targets)
            
            # Create lineage entry
            lineage_entry = await self.lineage.create_entry(
                analysis_results, 
                start_time
            )
            
            # Submit to ShadowScrolls for attestation
            attestation_result = await self.shadowscrolls.submit_analysis(
                analysis_results, 
                lineage_entry
            )
            
            # Sync with Triune ecosystem
            integration_result = await self.integrator.sync_results(
                analysis_results,
                attestation_result
            )
            
            # Compile final results
            final_results = {
                'analysis': analysis_results,
                'lineage': lineage_entry,
                'attestation': attestation_result,
                'integration': integration_result,
                'execution_time': (datetime.now(timezone.utc) - start_time).total_seconds(),
                'timestamp': start_time.isoformat()
            }
            
            logger.info("Analysis completed successfully")
            return final_results
            
        except Exception as e:
            logger.error(f"Analysis failed: {str(e)}")
            raise
    
    async def automated_daily_run(self, config_path: str) -> Dict[str, Any]:
        """Execute the automated daily analysis run."""
        logger.info("Starting automated daily MirrorWatcher run")
        
        # Load configuration
        config = self.load_config(config_path)
        
        # Initialize components
        await self.initialize_components(config)
        
        # Get target repositories from config
        targets = config.get('targets', [])
        if not targets:
            # Default to Triune ecosystem repositories
            targets = [
                'Triune-Oracle/triune-swarm-engine',
                'Triune-Oracle/triune-memory-core',
                'Triune-Oracle/operation-mind-smog'
            ]
        
        # Run comprehensive analysis
        results = await self.run_analysis(targets, config.get('output_format', 'json'))
        
        # Save results
        await self.save_results(results, config.get('output_path', './results'))
        
        logger.info("Automated daily run completed successfully")
        return results
    
    def load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from file."""
        try:
            config_file = Path(config_path)
            if config_file.exists():
                with open(config_file, 'r') as f:
                    return json.load(f)
            else:
                logger.warning(f"Config file not found: {config_path}, using defaults")
                return self.get_default_config()
        except Exception as e:
            logger.error(f"Failed to load config: {str(e)}")
            return self.get_default_config()
    
    def get_default_config(self) -> Dict[str, Any]:
        """Get default configuration."""
        return {
            'analysis': {
                'depth': 'comprehensive',
                'include_dependencies': True,
                'security_scan': True,
                'performance_metrics': True
            },
            'shadowscrolls': {
                'endpoint': 'https://api.shadowscrolls.triune-oracle.com/v1',
                'api_key': None  # Will be loaded from environment
            },
            'lineage': {
                'encryption': True,
                'hash_algorithm': 'sha256',
                'compression': True
            },
            'triune': {
                'legio_cognito': True,
                'triumvirate_monitor': True,
                'auto_archive': True
            },
            'output_format': 'json',
            'output_path': './results'
        }
    
    async def save_results(self, results: Dict[str, Any], output_path: str) -> None:
        """Save analysis results to specified path."""
        try:
            output_dir = Path(output_path)
            output_dir.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
            filename = f"mirror_analysis_{timestamp}.json"
            
            output_file = output_dir / filename
            
            with open(output_file, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            
            logger.info(f"Results saved to: {output_file}")
            
        except Exception as e:
            logger.error(f"Failed to save results: {str(e)}")
            raise


def create_parser() -> argparse.ArgumentParser:
    """Create and configure argument parser."""
    parser = argparse.ArgumentParser(
        description='MirrorWatcherAI - Complete Automation System for Triune Projects',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Daily automation command
    daily_parser = subparsers.add_parser(
        'daily', 
        help='Run automated daily analysis'
    )
    daily_parser.add_argument(
        '--config', 
        default='./config/mirror_watcher_config.json',
        help='Configuration file path'
    )
    
    # Manual analysis command
    analyze_parser = subparsers.add_parser(
        'analyze', 
        help='Run manual analysis on specified repositories'
    )
    analyze_parser.add_argument(
        'repositories', 
        nargs='+',
        help='Repository paths to analyze (format: owner/repo)'
    )
    analyze_parser.add_argument(
        '--config', 
        default='./config/mirror_watcher_config.json',
        help='Configuration file path'
    )
    analyze_parser.add_argument(
        '--output', 
        default='./results',
        help='Output directory for results'
    )
    analyze_parser.add_argument(
        '--format', 
        choices=['json', 'yaml', 'csv'],
        default='json',
        help='Output format'
    )
    
    # Version command
    version_parser = subparsers.add_parser(
        'version', 
        help='Show version information'
    )
    
    return parser


async def main():
    """Main entry point for MirrorWatcherAI CLI."""
    parser = create_parser()
    args = parser.parse_args()
    
    if args.command is None:
        parser.print_help()
        sys.exit(1)
    
    cli = MirrorWatcherCLI()
    
    try:
        if args.command == 'version':
            from . import __version__
            print(f"MirrorWatcherAI v{__version__}")
            
        elif args.command == 'daily':
            results = await cli.automated_daily_run(args.config)
            print(f"Daily analysis completed. Results: {len(results)} items processed.")
            
        elif args.command == 'analyze':
            config = cli.load_config(args.config)
            await cli.initialize_components(config)
            
            results = await cli.run_analysis(args.repositories, args.format)
            await cli.save_results(results, args.output)
            
            print(f"Analysis completed for {len(args.repositories)} repositories.")
            print(f"Results saved to: {args.output}")
            
    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    asyncio.run(main())