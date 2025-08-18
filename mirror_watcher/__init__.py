"""
Mirror Watcher CLI - A comprehensive monitoring and analysis tool for the Triune Swarm Engine.

This module provides CLI commands for monitoring, analyzing, and validating 
the Triune Swarm Engine system components and workflows.
"""

__version__ = "1.0.0"
__author__ = "Triune Oracle"
__description__ = "Mirror Watcher CLI for Triune Swarm Engine"

from .cli import main as cli_main
from .analysis_engine import AnalysisEngine
from .report_generator import ShadowScrollsReporter

__all__ = [
    "cli_main",
    "AnalysisEngine", 
    "ShadowScrollsReporter"
]