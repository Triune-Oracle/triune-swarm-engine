#!/usr/bin/env python3
"""
MirrorWatcherAI CLI Interface

Complete command-line interface with async execution capabilities,
providing zero manual intervention automation for the Triune ecosystem.

Features:
- Async/await execution patterns
- Comprehensive error handling and recovery
- Integration with ShadowScrolls external attestation
- MirrorLineage-Δ immutable logging
- Configurable analysis parameters and output formats
"""

import asyncio
import argparse
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any
import traceback

from .analyzer import TriuneAnalyzer, MirrorAnalysisEngine
from .shadowscrolls import ShadowScrollsIntegration
from .lineage import MirrorLineageDelta
from .triune_integration import (
    LegioCognitoArchival,
    TriumvirateMonitorSync, 
    SwarmEngineIntegration
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S UTC'
)
logger = logging.getLogger(__name__)

class MirrorWatcherCLI:
    """Main CLI interface for MirrorWatcherAI automation system"""
    
    def __init__(self):
        self.analyzer = None
        self.shadowscrolls = None
        self.lineage = None
        self.legio_cognito = None
        self.triumvirate_monitor = None
        self.swarm_engine = None
        self.config = {}
        
    async def initialize_components(self, config_path: Optional[str] = None):
        """Initialize all system components asynchronously"""
        try:
            # Load configuration
            if config_path:
                config_file = Path(config_path)
            else:
                config_file = Path("config/mirror_watcher_config.json")
                
            if config_file.exists():
                with open(config_file, 'r') as f:
                    self.config = json.load(f)
            else:
                logger.warning(f"Config file {config_file} not found, using defaults")
                self.config = self._get_default_config()
            
            # Initialize core components
            self.analyzer = TriuneAnalyzer(self.config.get('analyzer', {}))
            self.shadowscrolls = ShadowScrollsIntegration(self.config.get('shadowscrolls', {}))
            self.lineage = MirrorLineageDelta(self.config.get('lineage', {}))
            
            # Initialize Triune ecosystem integrations
            self.legio_cognito = LegioCognitoArchival(self.config.get('legio_cognito', {}))
            self.triumvirate_monitor = TriumvirateMonitorSync(self.config.get('triumvirate_monitor', {}))
            self.swarm_engine = SwarmEngineIntegration(self.config.get('swarm_engine', {}))
            
            logger.info("All MirrorWatcherAI components initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize components: {e}")
            logger.debug(traceback.format_exc())
            raise
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration when config file is not available"""
        return {
            "analyzer": {
                "parallel_analysis": True,
                "max_workers": 4,
                "timeout_seconds": 300
            },
            "shadowscrolls": {
                "endpoint": None,  # Will be loaded from environment
                "api_key": None,   # Will be loaded from environment
                "attestation_enabled": True
            },
            "lineage": {
                "immutable_logging": True,
                "cryptographic_verification": True,
                "retention_days": 90
            },
            "legio_cognito": {
                "auto_archival": True,
                "scroll_format": "json"
            },
            "triumvirate_monitor": {
                "real_time_sync": True,
                "mobile_dashboard": True
            },
            "swarm_engine": {
                "native_integration": True,
                "compatibility_mode": "76.3%"
            }
        }
    
    async def analyze_repositories(self, repositories: List[str], output_format: str = "json") -> Dict[str, Any]:
        """Perform comprehensive analysis across multiple repositories"""
        try:
            logger.info(f"Starting analysis of {len(repositories)} repositories")
            
            # Create analysis session
            session_id = f"mirror_session_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"
            
            # Initialize MirrorLineage-Δ for this session
            await self.lineage.start_session(session_id)
            
            results = {
                "session_id": session_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "repositories": {},
                "summary": {},
                "attestations": []
            }
            
            # Analyze each repository
            for repo in repositories:
                logger.info(f"Analyzing repository: {repo}")
                
                try:
                    # Perform analysis
                    analysis_result = await self.analyzer.analyze_repository(repo)
                    
                    # Log to MirrorLineage-Δ
                    await self.lineage.log_analysis(repo, analysis_result)
                    
                    # Store result
                    results["repositories"][repo] = analysis_result
                    
                    # Archive to Legio-Cognito
                    if self.legio_cognito:
                        await self.legio_cognito.archive_analysis(repo, analysis_result)
                    
                    # Sync with Triumvirate Monitor
                    if self.triumvirate_monitor:
                        await self.triumvirate_monitor.update_status(repo, "completed")
                    
                    logger.info(f"Successfully analyzed repository: {repo}")
                    
                except Exception as e:
                    logger.error(f"Failed to analyze repository {repo}: {e}")
                    results["repositories"][repo] = {
                        "error": str(e),
                        "status": "failed"
                    }
                    
                    # Update monitor with failure
                    if self.triumvirate_monitor:
                        await self.triumvirate_monitor.update_status(repo, "failed", str(e))
            
            # Generate summary
            successful = sum(1 for r in results["repositories"].values() if "error" not in r)
            failed = len(repositories) - successful
            
            results["summary"] = {
                "total_repositories": len(repositories),
                "successful_analyses": successful,
                "failed_analyses": failed,
                "success_rate": successful / len(repositories) if repositories else 0
            }
            
            # Create ShadowScrolls attestation
            if self.shadowscrolls:
                attestation = await self.shadowscrolls.create_attestation(results)
                results["attestations"].append(attestation)
            
            # Finalize MirrorLineage-Δ session
            await self.lineage.finalize_session(session_id, results)
            
            logger.info(f"Analysis session {session_id} completed successfully")
            return results
            
        except Exception as e:
            logger.error(f"Analysis session failed: {e}")
            logger.debug(traceback.format_exc())
            raise
    
    async def run_automated_cycle(self):
        """Run the complete automated analysis cycle"""
        try:
            logger.info("Starting automated MirrorWatcherAI cycle")
            
            # Get repositories from Swarm Engine integration
            repositories = await self.swarm_engine.get_target_repositories()
            
            if not repositories:
                logger.warning("No repositories found for analysis")
                return
            
            # Perform analysis
            results = await self.analyze_repositories(repositories)
            
            # Generate output artifacts
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            output_file = f"mirror_analysis_{timestamp}.json"
            
            with open(output_file, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            
            logger.info(f"Analysis results saved to {output_file}")
            
            # Final status update
            if self.triumvirate_monitor:
                await self.triumvirate_monitor.update_dashboard({
                    "last_run": datetime.now(timezone.utc).isoformat(),
                    "status": "completed",
                    "results_file": output_file,
                    "summary": results["summary"]
                })
            
            logger.info("Automated cycle completed successfully")
            return results
            
        except Exception as e:
            logger.error(f"Automated cycle failed: {e}")
            
            # Update monitor with failure
            if self.triumvirate_monitor:
                await self.triumvirate_monitor.update_dashboard({
                    "last_run": datetime.now(timezone.utc).isoformat(),
                    "status": "failed",
                    "error": str(e)
                })
            
            raise

def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser for the CLI"""
    parser = argparse.ArgumentParser(
        description="MirrorWatcherAI - Complete Automation System for Triune Oracle Ecosystem",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "--config", "-c",
        type=str,
        help="Path to configuration file (default: config/mirror_watcher_config.json)"
    )
    
    parser.add_argument(
        "--repositories", "-r",
        nargs="+",
        help="List of repositories to analyze"
    )
    
    parser.add_argument(
        "--output-format", "-f",
        choices=["json", "yaml", "csv"],
        default="json",
        help="Output format for results (default: json)"
    )
    
    parser.add_argument(
        "--automated",
        action="store_true",
        help="Run automated cycle using Swarm Engine integration"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    
    return parser

async def mirror_watcher_cli(args: Optional[List[str]] = None) -> int:
    """Main CLI entry point with async support"""
    try:
        # Parse arguments
        parser = create_parser()
        parsed_args = parser.parse_args(args)
        
        # Configure logging level
        if parsed_args.debug:
            logging.getLogger().setLevel(logging.DEBUG)
        elif parsed_args.verbose:
            logging.getLogger().setLevel(logging.INFO)
        
        logger.info("MirrorWatcherAI CLI starting")
        
        # Initialize CLI instance
        cli = MirrorWatcherCLI()
        await cli.initialize_components(parsed_args.config)
        
        # Execute based on mode
        if parsed_args.automated:
            # Run automated cycle
            results = await cli.run_automated_cycle()
        elif parsed_args.repositories:
            # Analyze specific repositories
            results = await cli.analyze_repositories(
                parsed_args.repositories,
                parsed_args.output_format
            )
            
            # Output results
            if parsed_args.output_format == "json":
                print(json.dumps(results, indent=2, default=str))
            else:
                logger.info("Non-JSON output formats not yet implemented")
                print(json.dumps(results, indent=2, default=str))
        else:
            parser.print_help()
            return 1
        
        logger.info("MirrorWatcherAI CLI completed successfully")
        return 0
        
    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
        return 130
    except Exception as e:
        logger.error(f"CLI execution failed: {e}")
        logger.debug(traceback.format_exc())
        return 1

def main() -> int:
    """Synchronous entry point that runs the async CLI"""
    try:
        return asyncio.run(mirror_watcher_cli())
    except KeyboardInterrupt:
        return 130
    except Exception as e:
        logger.error(f"Failed to start CLI: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())