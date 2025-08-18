"""
MirrorWatcherAI - Complete Automation System for Triune Oracle
===============================================================

A comprehensive automation system that integrates seamlessly with the Triune ecosystem,
providing complete cloud-based execution with zero manual intervention.

Features:
- Async CLI interface with comprehensive analysis capabilities
- ShadowScrolls external attestation and immutable logging
- MirrorLineage-Δ cryptographic verification system
- Triune ecosystem integration (Legio-Cognito, Triumvirate Monitor, Swarm Engine)
- Automated GitHub Actions workflow with daily execution
- Error recovery mechanisms and comprehensive monitoring

Usage:
    from mirror_watcher_ai import MirrorWatcherCLI, TriuneAnalyzer
    
    # CLI execution
    await MirrorWatcherCLI().execute_analysis()
    
    # Direct analyzer usage
    analyzer = TriuneAnalyzer()
    results = await analyzer.analyze_repositories()

Version: 1.0.0
Author: Triune-Oracle
License: MIT
"""

__version__ = "1.0.0"
__author__ = "Triune-Oracle"
__license__ = "MIT"
__description__ = "Complete automation system for Triune Oracle mirror watching and analysis"

# Core imports
from .cli import MirrorWatcherCLI
from .analyzer import TriuneAnalyzer
from .shadowscrolls import ShadowScrollsIntegration
from .lineage import MirrorLineageLogger
from .triune_integration import TriuneEcosystemConnector

# Public API
__all__ = [
    "MirrorWatcherCLI",
    "TriuneAnalyzer", 
    "ShadowScrollsIntegration",
    "MirrorLineageLogger",
    "TriuneEcosystemConnector",
]

# Module configuration
import logging
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('mirror_watcher_ai.log') if os.getenv('MIRROR_WATCHER_LOG_FILE') else logging.NullHandler()
    ]
)

logger = logging.getLogger(__name__)
logger.info(f"MirrorWatcherAI v{__version__} initialized")