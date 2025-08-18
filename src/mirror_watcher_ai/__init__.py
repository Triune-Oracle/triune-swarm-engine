"""
MirrorWatcherAI - Complete Automation System for Triune Oracle Ecosystem

A comprehensive system providing complete cloud-based execution with zero manual 
intervention, integrating seamlessly with the Triune ecosystem.

Key Features:
- Complete CLI interface with async execution
- ShadowScrolls external attestation
- MirrorLineage-Δ immutable logging with cryptographic verification
- Comprehensive error handling and recovery mechanisms
- Triune ecosystem integration (Legio-Cognito, Triumvirate Monitor, Swarm Engine)

Version: 1.0.0
Author: Triune-Oracle
Target: First automated run at 06:00 UTC on 2025-08-19
"""

__version__ = "1.0.0"
__author__ = "Triune-Oracle"
__title__ = "MirrorWatcherAI Complete Automation System"

from .cli import main as cli_main
from .analyzer import TriuneAnalyzer
from .shadowscrolls import ShadowScrollsAttestation
from .lineage import MirrorLineageDelta
from .triune_integration import TriuneEcosystemIntegration

__all__ = [
    "cli_main",
    "TriuneAnalyzer", 
    "ShadowScrollsAttestation",
    "MirrorLineageDelta",
    "TriuneEcosystemIntegration"
]