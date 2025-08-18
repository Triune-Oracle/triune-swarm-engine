"""
MirrorWatcherAI CLI Interface
============================

Complete CLI interface with async execution for the MirrorWatcherAI system.
Provides comprehensive command-line access to all automation features.
"""

import asyncio
import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging

from .analyzer import TriuneAnalyzer
from .shadowscrolls import ShadowScrollsIntegration
from .lineage import MirrorLineageLogger
from .triune_integration import TriuneEcosystemConnector

logger = logging.getLogger(__name__)


class MirrorWatcherCLI:
    """
    Async CLI interface for MirrorWatcherAI automation system.
    
    Provides comprehensive command-line access with async execution patterns
    optimized for cloud-based GitHub Actions execution.
    """
    
    def __init__(self):
        self.analyzer = TriuneAnalyzer()
        self.shadowscrolls = ShadowScrollsIntegration()
        self.lineage_logger = MirrorLineageLogger()
        self.triune_connector = TriuneEcosystemConnector()
        self.start_time = datetime.now(timezone.utc)
        
    async def execute_full_analysis(self, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute complete mirror analysis workflow with all integrations.
        
        Args:
            config: Optional configuration dictionary
            
        Returns:
            Dict containing analysis results and execution metadata
        """
        logger.info("Starting comprehensive mirror analysis workflow")
        execution_id = f"analysis_{self.start_time.strftime('%Y%m%d_%H%M%S')}"
        
        try:
            # Initialize lineage tracking
            await self.lineage_logger.start_session(execution_id)
            
            # Step 1: Repository Analysis
            logger.info("Phase 1: Executing repository analysis")
            analysis_results = await self.analyzer.analyze_all_repositories(config)
            await self.lineage_logger.log_phase("repository_analysis", analysis_results)
            
            # Step 2: ShadowScrolls Attestation
            logger.info("Phase 2: Creating ShadowScrolls attestation")
            attestation = await self.shadowscrolls.create_attestation(
                execution_id, analysis_results
            )
            await self.lineage_logger.log_phase("shadowscrolls_attestation", attestation)
            
            # Step 3: Triune Ecosystem Integration
            logger.info("Phase 3: Synchronizing with Triune ecosystem")
            integration_results = await self.triune_connector.sync_all_systems(
                analysis_results, attestation
            )
            await self.lineage_logger.log_phase("triune_integration", integration_results)
            
            # Step 4: Finalize and generate report
            logger.info("Phase 4: Finalizing execution and generating report")
            final_report = await self._generate_final_report(
                execution_id, analysis_results, attestation, integration_results
            )
            
            await self.lineage_logger.finalize_session(final_report)
            
            logger.info(f"Analysis workflow completed successfully: {execution_id}")
            return final_report
            
        except Exception as e:
            logger.error(f"Analysis workflow failed: {str(e)}")
            await self.lineage_logger.log_error(execution_id, str(e))
            raise
    
    async def execute_repository_scan(self, repositories: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Execute targeted repository scanning.
        
        Args:
            repositories: Optional list of specific repositories to analyze
            
        Returns:
            Dict containing scan results
        """
        logger.info("Executing repository scan")
        
        if repositories:
            logger.info(f"Scanning specific repositories: {repositories}")
            results = await self.analyzer.analyze_specific_repositories(repositories)
        else:
            logger.info("Scanning all Triune repositories")
            results = await self.analyzer.analyze_all_repositories()
            
        # Log to lineage system
        scan_id = f"scan_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"
        await self.lineage_logger.log_scan_results(scan_id, results)
        
        return {
            "scan_id": scan_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "repositories_scanned": len(results.get("repositories", [])),
            "results": results
        }
    
    async def create_shadowscrolls_report(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create standalone ShadowScrolls attestation report.
        
        Args:
            data: Data to attest
            
        Returns:
            Attestation report
        """
        logger.info("Creating ShadowScrolls attestation report")
        
        report_id = f"manual_report_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"
        attestation = await self.shadowscrolls.create_attestation(report_id, data)
        
        logger.info(f"ShadowScrolls report created: {report_id}")
        return attestation
    
    async def sync_triune_ecosystem(self, force: bool = False) -> Dict[str, Any]:
        """
        Synchronize with all Triune ecosystem services.
        
        Args:
            force: Force synchronization even if no new data
            
        Returns:
            Synchronization results
        """
        logger.info("Synchronizing Triune ecosystem")
        
        # Get latest data if not forcing
        if not force:
            latest_data = await self.lineage_logger.get_latest_session_data()
            if not latest_data:
                logger.warning("No recent data found for synchronization")
                return {"status": "no_data", "message": "No recent data available"}
        else:
            latest_data = {"force_sync": True}
        
        sync_results = await self.triune_connector.sync_all_systems(latest_data)
        
        logger.info("Triune ecosystem synchronization completed")
        return sync_results
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform comprehensive health check of all system components.
        
        Returns:
            Health status report
        """
        logger.info("Performing system health check")
        
        health_status = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "overall_status": "healthy",
            "components": {}
        }
        
        # Check analyzer
        try:
            analyzer_health = await self.analyzer.health_check()
            health_status["components"]["analyzer"] = analyzer_health
        except Exception as e:
            health_status["components"]["analyzer"] = {"status": "error", "error": str(e)}
            health_status["overall_status"] = "degraded"
        
        # Check ShadowScrolls
        try:
            shadowscrolls_health = await self.shadowscrolls.health_check()
            health_status["components"]["shadowscrolls"] = shadowscrolls_health
        except Exception as e:
            health_status["components"]["shadowscrolls"] = {"status": "error", "error": str(e)}
            health_status["overall_status"] = "degraded"
        
        # Check Triune connector
        try:
            triune_health = await self.triune_connector.health_check()
            health_status["components"]["triune_connector"] = triune_health
        except Exception as e:
            health_status["components"]["triune_connector"] = {"status": "error", "error": str(e)}
            health_status["overall_status"] = "degraded"
        
        # Check lineage logger
        try:
            lineage_health = await self.lineage_logger.health_check()
            health_status["components"]["lineage_logger"] = lineage_health
        except Exception as e:
            health_status["components"]["lineage_logger"] = {"status": "error", "error": str(e)}
            health_status["overall_status"] = "degraded"
        
        logger.info(f"Health check completed: {health_status['overall_status']}")
        return health_status
    
    async def _generate_final_report(
        self, 
        execution_id: str, 
        analysis_results: Dict[str, Any],
        attestation: Dict[str, Any],
        integration_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate comprehensive final execution report."""
        
        end_time = datetime.now(timezone.utc)
        execution_duration = (end_time - self.start_time).total_seconds()
        
        return {
            "execution_id": execution_id,
            "start_time": self.start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "execution_duration_seconds": execution_duration,
            "status": "completed",
            "analysis_summary": {
                "repositories_analyzed": len(analysis_results.get("repositories", [])),
                "total_commits": analysis_results.get("total_commits", 0),
                "security_issues": analysis_results.get("security_issues", 0),
                "performance_metrics": analysis_results.get("performance_metrics", {})
            },
            "attestation_summary": {
                "scroll_id": attestation.get("scroll_id"),
                "verification_hash": attestation.get("verification_hash"),
                "timestamp": attestation.get("timestamp")
            },
            "integration_summary": {
                "legio_cognito_sync": integration_results.get("legio_cognito", {}).get("status"),
                "triumvirate_monitor_sync": integration_results.get("triumvirate_monitor", {}).get("status"),
                "swarm_engine_sync": integration_results.get("swarm_engine", {}).get("status")
            },
            "artifacts": {
                "analysis_report": f"analysis_{execution_id}.json",
                "attestation_scroll": f"scroll_{execution_id}.json",
                "lineage_log": f"lineage_{execution_id}.json"
            }
        }


async def main():
    """Main CLI entry point with async execution."""
    
    parser = argparse.ArgumentParser(
        description="MirrorWatcherAI - Complete Automation System for Triune Oracle",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Full analysis command
    analysis_parser = subparsers.add_parser("analyze", help="Execute full mirror analysis workflow")
    analysis_parser.add_argument("--config", type=str, help="Configuration file path")
    analysis_parser.add_argument("--output", type=str, help="Output file path")
    
    # Repository scan command
    scan_parser = subparsers.add_parser("scan", help="Execute repository scanning")
    scan_parser.add_argument("--repositories", nargs="+", help="Specific repositories to scan")
    scan_parser.add_argument("--output", type=str, help="Output file path")
    
    # ShadowScrolls command
    scroll_parser = subparsers.add_parser("attest", help="Create ShadowScrolls attestation")
    scroll_parser.add_argument("--data", type=str, required=True, help="JSON data file to attest")
    scroll_parser.add_argument("--output", type=str, help="Output file path")
    
    # Sync command
    sync_parser = subparsers.add_parser("sync", help="Synchronize Triune ecosystem")
    sync_parser.add_argument("--force", action="store_true", help="Force synchronization")
    
    # Health check command
    subparsers.add_parser("health", help="Perform system health check")
    
    # Parse arguments
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Initialize CLI
    cli = MirrorWatcherCLI()
    
    try:
        # Execute command
        if args.command == "analyze":
            config = None
            if args.config:
                with open(args.config, 'r') as f:
                    config = json.load(f)
            
            result = await cli.execute_full_analysis(config)
            
            if args.output:
                with open(args.output, 'w') as f:
                    json.dump(result, f, indent=2)
            else:
                print(json.dumps(result, indent=2))
        
        elif args.command == "scan":
            result = await cli.execute_repository_scan(args.repositories)
            
            if args.output:
                with open(args.output, 'w') as f:
                    json.dump(result, f, indent=2)
            else:
                print(json.dumps(result, indent=2))
        
        elif args.command == "attest":
            with open(args.data, 'r') as f:
                data = json.load(f)
            
            result = await cli.create_shadowscrolls_report(data)
            
            if args.output:
                with open(args.output, 'w') as f:
                    json.dump(result, f, indent=2)
            else:
                print(json.dumps(result, indent=2))
        
        elif args.command == "sync":
            result = await cli.sync_triune_ecosystem(args.force)
            print(json.dumps(result, indent=2))
        
        elif args.command == "health":
            result = await cli.health_check()
            print(json.dumps(result, indent=2))
            
            # Exit with error code if not healthy
            if result["overall_status"] != "healthy":
                sys.exit(1)
    
    except Exception as e:
        logger.error(f"CLI execution failed: {str(e)}")
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())