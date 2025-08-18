"""
MirrorWatcherAI - Complete Automation System for Triune Ecosystem

This module provides comprehensive automation for repository mirroring,
analysis, and integration with the Triune Oracle ecosystem including
ShadowScrolls attestation, MirrorLineage-Δ traceability, and Legio-Cognito archival.
"""

__version__ = "1.0.0"
__author__ = "Triune-Oracle"

from .cli import main as cli_main
from .analyzer import TriuneAnalyzer
from .shadowscrolls import ShadowScrollsAttestation
from .lineage import MirrorLineage
from .legio_integration import LegioCognitoArchival
from .triune_monitor import TriuneMonitor

__all__ = [
    "cli_main",
    "TriuneAnalyzer", 
    "ShadowScrollsAttestation",
    "MirrorLineage",
    "LegioCognitoArchival",
    "TriuneMonitor"
]