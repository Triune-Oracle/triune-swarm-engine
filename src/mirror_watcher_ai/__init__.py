"""
MirrorWatcherAI - Complete Automation System for Triune Oracle Ecosystem

Provides comprehensive cloud-based execution with zero manual intervention,
integrating seamlessly with ShadowScrolls, MirrorLineage-Δ, and Triune components.

Version: 1.0.0
Author: Triune-Oracle
Target: First automated run at 06:00 UTC 2025-08-19
"""

__version__ = "1.0.0"
__author__ = "Triune-Oracle"

from .cli import main as cli_main, mirror_watcher_cli
from .analyzer import TriuneAnalyzer, MirrorAnalysisEngine
from .shadowscrolls import ShadowScrollsIntegration, ExternalAttestation
from .lineage import MirrorLineageDelta, ImmutableLogger
from .triune_integration import (
    LegioCognitoArchival, 
    TriumvirateMonitorSync, 
    SwarmEngineIntegration
)

__all__ = [
    "cli_main",
    "mirror_watcher_cli", 
    "TriuneAnalyzer",
    "MirrorAnalysisEngine",
    "ShadowScrollsIntegration",
    "ExternalAttestation",
    "MirrorLineageDelta", 
    "ImmutableLogger",
    "LegioCognitoArchival",
    "TriumvirateMonitorSync",
    "SwarmEngineIntegration"
]

# Module version info for compatibility checking
COMPATIBILITY_VERSION = "1.0"
REQUIRED_PYTHON = "3.9"
SWARM_ENGINE_COMPATIBILITY = "76.3%"
SHELL_INFRASTRUCTURE_USAGE = "10.1%"