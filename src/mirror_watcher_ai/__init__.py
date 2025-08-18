"""
MirrorWatcherAI - Complete Automation System for Triune Projects
Provides comprehensive cloud-based execution with zero manual intervention.
"""

__version__ = "1.0.0"
__author__ = "Triune-Oracle"

from .cli import main as cli_main
from .analyzer import TriuneAnalyzer
from .shadowscrolls import ShadowScrollsClient
from .lineage import MirrorLineage
from .triune_integration import TriuneIntegrator

__all__ = [
    "cli_main", 
    "TriuneAnalyzer", 
    "ShadowScrollsClient", 
    "MirrorLineage", 
    "TriuneIntegrator"
]