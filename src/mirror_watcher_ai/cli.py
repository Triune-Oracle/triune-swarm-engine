#!/usr/bin/env python3
"""
MirrorWatcherAI CLI Interface

Provides complete command-line interface for automated repository mirroring,
analysis, and integration with the Triune Oracle ecosystem.
"""

import argparse
import asyncio
import json
import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from .analyzer import TriuneAnalyzer
from .shadowscrolls import ShadowScrollsAttestation
from .lineage import MirrorLineage
from .legio_integration import LegioCognitoArchival
from .triune_monitor import TriuneMonitor


def setup_logging(debug: bool = False) -> None:
    """Setup logging configuration."""
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S UTC'
    )


async def run_analysis(config_path: Optional[str] = None, debug: bool = False) -> dict:
    """Run complete MirrorWatcherAI analysis."""
    logger = logging.getLogger(__name__)
    
    try:
        # Initialize components
        analyzer = TriuneAnalyzer(config_path)
        shadowscrolls = ShadowScrollsAttestation()
        lineage = MirrorLineage()
        legio = LegioCognitoArchival()
        monitor = TriuneMonitor()
        
        # Load configuration
        config = analyzer.load_config()
        logger.info(f"Loaded configuration from {config_path or 'default'}")
        
        # Run analysis
        logger.info("Starting Triune ecosystem analysis...")
        analysis_results = await analyzer.analyze_repositories(config.get('repositories', []))
        
        # Create ShadowScrolls attestation
        logger.info("Creating ShadowScrolls attestation...")
        attestation = await shadowscrolls.create_attestation(analysis_results)
        
        # Record lineage
        logger.info("Recording MirrorLineage-Δ trace...")
        lineage_record = await lineage.record_execution(analysis_results, attestation)
        
        # Archive to Legio-Cognito
        logger.info("Archiving to Legio-Cognito...")
        archive_result = await legio.archive_results(analysis_results, attestation, lineage_record)
        
        # Update Triune Monitor
        logger.info("Updating Triune Monitor...")
        monitor_result = await monitor.update_status(analysis_results, archive_result)
        
        # Compile final results
        final_results = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'analysis': analysis_results,
            'attestation': attestation,
            'lineage': lineage_record,
            'archive': archive_result,
            'monitor': monitor_result,
            'status': 'completed'
        }
        
        logger.info("MirrorWatcherAI analysis completed successfully")
        return final_results
        
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        if debug:
            logger.exception("Full traceback:")
        return {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'status': 'failed',
            'error': str(e)
        }


async def validate_setup() -> bool:
    """Validate MirrorWatcherAI setup and configuration."""
    logger = logging.getLogger(__name__)
    
    try:
        # Check environment variables
        required_vars = [
            'REPO_SYNC_TOKEN',
            'SHADOWSCROLLS_ENDPOINT',
            'SHADOWSCROLLS_API_KEY'
        ]
        
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        if missing_vars:
            logger.error(f"Missing environment variables: {', '.join(missing_vars)}")
            return False
        
        # Validate components
        analyzer = TriuneAnalyzer()
        if not await analyzer.validate():
            logger.error("TriuneAnalyzer validation failed")
            return False
            
        shadowscrolls = ShadowScrollsAttestation()
        if not await shadowscrolls.validate():
            logger.error("ShadowScrolls validation failed")
            return False
        
        logger.info("MirrorWatcherAI setup validation passed")
        return True
        
    except Exception as e:
        logger.error(f"Setup validation failed: {e}")
        return False


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="MirrorWatcherAI - Complete Automation System for Triune Ecosystem",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --analyze                    # Run complete analysis
  %(prog)s --validate                   # Validate setup
  %(prog)s --config config.json        # Use custom configuration
  %(prog)s --analyze --debug            # Run with debug logging
        """
    )
    
    parser.add_argument(
        '--analyze', 
        action='store_true',
        help='Run complete MirrorWatcherAI analysis'
    )
    
    parser.add_argument(
        '--validate',
        action='store_true', 
        help='Validate setup and configuration'
    )
    
    parser.add_argument(
        '--config',
        type=str,
        help='Path to configuration file'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        help='Output file for results (default: stdout)'
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug logging'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='MirrorWatcherAI 1.0.0'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.debug)
    logger = logging.getLogger(__name__)
    
    # Handle version and help
    if len(sys.argv) == 1:
        parser.print_help()
        return 0
    
    try:
        if args.validate:
            logger.info("Validating MirrorWatcherAI setup...")
            success = asyncio.run(validate_setup())
            return 0 if success else 1
            
        elif args.analyze:
            logger.info("Starting MirrorWatcherAI analysis...")
            results = asyncio.run(run_analysis(args.config, args.debug))
            
            # Output results
            output = json.dumps(results, indent=2)
            
            if args.output:
                with open(args.output, 'w') as f:
                    f.write(output)
                logger.info(f"Results written to {args.output}")
            else:
                print(output)
            
            return 0 if results.get('status') == 'completed' else 1
        
        else:
            parser.print_help()
            return 1
            
    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
        return 130
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        if args.debug:
            logger.exception("Full traceback:")
        return 1


if __name__ == "__main__":
    exit(main())