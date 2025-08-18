"""
Mirror Watcher - CLI Mirroring & Analysis for Triune Projects
Automates mirroring, CLI execution, and ShadowScrolls logging
"""

__version__ = "0.1.0"
__author__ = "Triune-Oracle"

from .cli import main as cli_main
from .analyzer import TriuneAnalyzer

__all__ = ["cli_main", "TriuneAnalyzer"]
