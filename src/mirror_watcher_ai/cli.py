#!/usr/bin/env python3
"""
MirrorWatcherAI CLI Interface

Complete command-line interface for the MirrorWatcherAI automation system.
Provides async execution, comprehensive error handling, and integration with
the Triune ecosystem.

Usage:
    python -m mirror_watcher_ai [OPTIONS] COMMAND [ARGS]...
    
Commands:
    analyze    Run complete analysis of Triune repositories
    monitor    Start continuous monitoring mode
    attest     Create ShadowScrolls attestation
    sync       Synchronize with Triune ecosystem
    config     Manage configuration settings
    status     Check system status
"""

import asyncio
import sys
import json
import os
import logging
import argparse
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, Any, List
import traceback

from .analyzer import TriuneAnalyzer
from .shadowscrolls import ShadowScrollsAttestation
from .lineage import MirrorLineageDelta
from .triune_integration import TriuneEcosystemIntegration


class MirrorWatcherCLI:
    """Main CLI class for MirrorWatcherAI automation system."""
    
    def __init__(self):
        self.config_path = Path("config/mirror_watcher_config.json")
        self.config = self._load_config()
        self.logger = self._setup_logging()
        
        # Initialize core components
        self.analyzer = TriuneAnalyzer(self.config.get("analyzer", {}))
        self.shadowscrolls = ShadowScrollsAttestation(self.config.get("shadowscrolls", {}))
        self.lineage = MirrorLineageDelta(self.config.get("lineage", {}))
        self.triune = TriuneEcosystemIntegration(self.config.get("triune", {}))
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from JSON file."""
        if not self.config_path.exists():
            # Create default config
            default_config = {
                "analyzer": {
                    "timeout": 300,
                    "concurrent_repos": 3,
                    "output_format": "json"
                },
                "shadowscrolls": {
                    "endpoint": os.getenv("SHADOWSCROLLS_ENDPOINT", ""),
                    "api_key": os.getenv("SHADOWSCROLLS_API_KEY", ""),
                    "timeout": 30
                },
                "lineage": {
                    "crypto_enabled": True,
                    "signature_algorithm": "ed25519",
                    "storage_path": ".shadowscrolls/lineage"
                },
                "triune": {
                    "legio_cognito_endpoint": os.getenv("LEGIO_COGNITO_ENDPOINT", ""),
                    "triumvirate_monitor_endpoint": os.getenv("TRIUMVIRATE_MONITOR_ENDPOINT", ""),
                    "sync_interval": 300
                },
                "github": {
                    "token": os.getenv("REPO_SYNC_TOKEN", ""),
                    "repositories": [
                        "Triune-Oracle/triune-swarm-engine",
                        "Triune-Oracle/legio-cognito",
                        "Triune-Oracle/triumvirate-monitor"
                    ]
                }
            }
            
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump(default_config, f, indent=2)
            
            return default_config
        
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Failed to load config: {e}")
            return {}
    
    def _setup_logging(self) -> logging.Logger:
        """Setup structured logging."""
        logger = logging.getLogger("MirrorWatcherAI")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    async def analyze_command(self, args) -> int:
        """Run complete analysis of Triune repositories."""
        try:
            self.logger.info("🔍 Starting MirrorWatcherAI analysis...")
            
            # Create analysis session
            session_id = f"analysis-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}"
            
            # Initialize lineage tracking
            await self.lineage.start_session(session_id)
            
            # Run analysis
            results = await self.analyzer.analyze_repositories(
                repositories=self.config.get("github", {}).get("repositories", []),
                parallel=args.parallel,
                deep_scan=args.deep_scan
            )
            
            # Create ShadowScrolls attestation
            if args.attest:
                attestation = await self.shadowscrolls.create_attestation(
                    session_id=session_id,
                    results=results,
                    metadata={
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "system": "MirrorWatcherAI",
                        "version": "1.0.0"
                    }
                )
                self.logger.info(f"✅ ShadowScrolls attestation created: {attestation['scroll_id']}")
            
            # Sync with Triune ecosystem
            if args.sync:
                await self.triune.sync_results(session_id, results)
                self.logger.info("✅ Results synchronized with Triune ecosystem")
            
            # Finalize lineage
            await self.lineage.finalize_session(session_id, results)
            
            # Output results
            if args.output:
                output_path = Path(args.output)
                output_path.parent.mkdir(parents=True, exist_ok=True)
                with open(output_path, 'w') as f:
                    json.dump(results, f, indent=2)
                self.logger.info(f"📄 Results saved to {output_path}")
            
            self.logger.info("🎉 Analysis completed successfully")
            return 0
            
        except Exception as e:
            self.logger.error(f"❌ Analysis failed: {e}")
            if args.debug:
                traceback.print_exc()
            return 1
    
    async def monitor_command(self, args) -> int:
        """Start continuous monitoring mode."""
        try:
            self.logger.info("👁️ Starting continuous monitoring mode...")
            
            interval = args.interval or self.config.get("triune", {}).get("sync_interval", 300)
            
            while True:
                try:
                    # Run analysis
                    session_id = f"monitor-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}"
                    await self.lineage.start_session(session_id)
                    
                    results = await self.analyzer.analyze_repositories(
                        repositories=self.config.get("github", {}).get("repositories", []),
                        parallel=True,
                        deep_scan=False
                    )
                    
                    # Sync with ecosystem
                    await self.triune.sync_results(session_id, results)
                    await self.lineage.finalize_session(session_id, results)
                    
                    self.logger.info(f"✅ Monitoring cycle completed, sleeping for {interval}s...")
                    await asyncio.sleep(interval)
                    
                except KeyboardInterrupt:
                    self.logger.info("🛑 Monitoring stopped by user")
                    break
                except Exception as e:
                    self.logger.error(f"❌ Monitoring cycle failed: {e}")
                    await asyncio.sleep(60)  # Wait before retry
            
            return 0
            
        except Exception as e:
            self.logger.error(f"❌ Monitoring failed: {e}")
            return 1
    
    async def attest_command(self, args) -> int:
        """Create ShadowScrolls attestation."""
        try:
            self.logger.info("🔏 Creating ShadowScrolls attestation...")
            
            session_id = args.session_id or f"attest-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}"
            
            # Load data to attest
            data = {}
            if args.data_file:
                with open(args.data_file, 'r') as f:
                    data = json.load(f)
            
            attestation = await self.shadowscrolls.create_attestation(
                session_id=session_id,
                results=data,
                metadata={
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "system": "MirrorWatcherAI",
                    "version": "1.0.0",
                    "manual": True
                }
            )
            
            self.logger.info(f"✅ Attestation created: {attestation['scroll_id']}")
            
            if args.output:
                with open(args.output, 'w') as f:
                    json.dump(attestation, f, indent=2)
            
            return 0
            
        except Exception as e:
            self.logger.error(f"❌ Attestation failed: {e}")
            return 1
    
    async def sync_command(self, args) -> int:
        """Synchronize with Triune ecosystem."""
        try:
            self.logger.info("🔄 Synchronizing with Triune ecosystem...")
            
            # Test connectivity
            status = await self.triune.health_check()
            self.logger.info(f"🏥 Ecosystem health: {status}")
            
            # Perform sync
            session_id = args.session_id or f"sync-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}"
            
            if args.data_file:
                with open(args.data_file, 'r') as f:
                    data = json.load(f)
                await self.triune.sync_results(session_id, data)
            else:
                await self.triune.sync_status()
            
            self.logger.info("✅ Synchronization completed")
            return 0
            
        except Exception as e:
            self.logger.error(f"❌ Synchronization failed: {e}")
            return 1
    
    async def config_command(self, args) -> int:
        """Manage configuration settings."""
        try:
            if args.show:
                print(json.dumps(self.config, indent=2))
            elif args.set:
                key, value = args.set.split('=', 1)
                # Simple dot notation support
                keys = key.split('.')
                current = self.config
                for k in keys[:-1]:
                    if k not in current:
                        current[k] = {}
                    current = current[k]
                
                # Try to parse as JSON, fallback to string
                try:
                    parsed_value = json.loads(value)
                except:
                    parsed_value = value
                
                current[keys[-1]] = parsed_value
                
                # Save config
                with open(self.config_path, 'w') as f:
                    json.dump(self.config, f, indent=2)
                
                self.logger.info(f"✅ Configuration updated: {key} = {parsed_value}")
            
            return 0
            
        except Exception as e:
            self.logger.error(f"❌ Configuration operation failed: {e}")
            return 1
    
    async def status_command(self, args) -> int:
        """Check system status."""
        try:
            self.logger.info("📊 Checking MirrorWatcherAI system status...")
            
            status = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "version": "1.0.0",
                "components": {}
            }
            
            # Check analyzer
            try:
                await self.analyzer.health_check()
                status["components"]["analyzer"] = "healthy"
            except Exception as e:
                status["components"]["analyzer"] = f"error: {e}"
            
            # Check ShadowScrolls
            try:
                await self.shadowscrolls.health_check()
                status["components"]["shadowscrolls"] = "healthy"
            except Exception as e:
                status["components"]["shadowscrolls"] = f"error: {e}"
            
            # Check Triune integration
            try:
                triune_status = await self.triune.health_check()
                status["components"]["triune"] = triune_status
            except Exception as e:
                status["components"]["triune"] = f"error: {e}"
            
            # Check lineage
            try:
                await self.lineage.health_check()
                status["components"]["lineage"] = "healthy"
            except Exception as e:
                status["components"]["lineage"] = f"error: {e}"
            
            if args.json:
                print(json.dumps(status, indent=2))
            else:
                print(f"🕐 Status at {status['timestamp']}")
                print(f"📦 Version: {status['version']}")
                print("🔧 Components:")
                for component, state in status["components"].items():
                    icon = "✅" if state == "healthy" else "❌"
                    print(f"  {icon} {component}: {state}")
            
            # Return error code if any component is unhealthy
            unhealthy = [c for c, s in status["components"].items() if s != "healthy"]
            return 1 if unhealthy else 0
            
        except Exception as e:
            self.logger.error(f"❌ Status check failed: {e}")
            return 1


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser."""
    parser = argparse.ArgumentParser(
        description="MirrorWatcherAI Complete Automation System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m mirror_watcher_ai analyze --parallel --attest
  python -m mirror_watcher_ai monitor --interval 300
  python -m mirror_watcher_ai status --json
  python -m mirror_watcher_ai config --set analyzer.timeout=600
        """
    )
    
    parser.add_argument('--debug', action='store_true', help='Enable debug output')
    parser.add_argument('--config', type=str, help='Path to config file')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Run analysis of Triune repositories')
    analyze_parser.add_argument('--parallel', action='store_true', help='Run analysis in parallel')
    analyze_parser.add_argument('--deep-scan', action='store_true', help='Perform deep repository scan')
    analyze_parser.add_argument('--attest', action='store_true', help='Create ShadowScrolls attestation')
    analyze_parser.add_argument('--sync', action='store_true', help='Sync with Triune ecosystem')
    analyze_parser.add_argument('--output', type=str, help='Output file for results')
    
    # Monitor command
    monitor_parser = subparsers.add_parser('monitor', help='Start continuous monitoring')
    monitor_parser.add_argument('--interval', type=int, help='Monitoring interval in seconds')
    
    # Attest command
    attest_parser = subparsers.add_parser('attest', help='Create ShadowScrolls attestation')
    attest_parser.add_argument('--session-id', type=str, help='Session ID for attestation')
    attest_parser.add_argument('--data-file', type=str, help='Data file to attest')
    attest_parser.add_argument('--output', type=str, help='Output file for attestation')
    
    # Sync command
    sync_parser = subparsers.add_parser('sync', help='Synchronize with Triune ecosystem')
    sync_parser.add_argument('--session-id', type=str, help='Session ID for sync')
    sync_parser.add_argument('--data-file', type=str, help='Data file to sync')
    
    # Config command
    config_parser = subparsers.add_parser('config', help='Manage configuration')
    config_parser.add_argument('--show', action='store_true', help='Show current configuration')
    config_parser.add_argument('--set', type=str, help='Set configuration value (key=value)')
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Check system status')
    status_parser.add_argument('--json', action='store_true', help='Output status as JSON')
    
    return parser


async def main():
    """Main entry point for the CLI."""
    parser = create_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    cli = MirrorWatcherCLI()
    
    # Route to appropriate command
    command_map = {
        'analyze': cli.analyze_command,
        'monitor': cli.monitor_command,
        'attest': cli.attest_command,
        'sync': cli.sync_command,
        'config': cli.config_command,
        'status': cli.status_command
    }
    
    if args.command in command_map:
        return await command_map[args.command](args)
    else:
        print(f"Unknown command: {args.command}")
        return 1


def cli_main():
    """Entry point for setuptools console scripts."""
    try:
        return asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user")
        return 1
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(cli_main())