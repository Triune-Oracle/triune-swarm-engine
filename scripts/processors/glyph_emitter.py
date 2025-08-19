#!/usr/bin/env python3
"""
Glyph Emission Processor
========================

Processes MirrorWatcherAI analysis results and transforms them into standardized 
glyph event format for the Codex visualization system.

This script:
- Parses MirrorWatcherAI analysis results from the output directory
- Transforms data into standardized glyph event format with required metadata
- Appends new entries to data/codexGlyphs.json with timestamps and signatures
- Includes comprehensive error handling and logging
"""

import json
import logging
import hashlib
import argparse
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional
import sys
import os

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class GlyphEmissionProcessor:
    """
    Processes MirrorWatcherAI analysis results into glyph events for Codex visualization.
    
    Transforms repository analysis data into symbolic glyph representations that
    capture the essence of code changes, security events, and ecosystem dynamics.
    """
    
    def __init__(self, output_dir: str = "artifacts", data_dir: str = "data"):
        self.output_dir = Path(output_dir)
        self.data_dir = Path(data_dir)
        self.codex_file = self.data_dir / "codexGlyphs.json"
        
        # Ensure directories exist
        self.data_dir.mkdir(exist_ok=True)
        
        # Initialize codex file if it doesn't exist
        if not self.codex_file.exists():
            self._initialize_codex_file()
    
    def _initialize_codex_file(self) -> None:
        """Initialize the codex glyphs file with proper structure."""
        initial_data = {
            "version": "1.0.0",
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "metadata": {
                "description": "Codex glyph events generated from MirrorWatcherAI analysis",
                "schema_version": "1.0",
                "source": "MirrorWatcherAI"
            },
            "glyphs": []
        }
        
        with open(self.codex_file, 'w') as f:
            json.dump(initial_data, f, indent=2)
        
        logger.info(f"Initialized codex file: {self.codex_file}")
    
    def _generate_glyph_signature(self, glyph_data: Dict[str, Any]) -> str:
        """Generate cryptographic signature for glyph integrity verification."""
        # Create deterministic string from glyph data
        signature_data = {
            "repository": glyph_data.get("repository"),
            "timestamp": glyph_data.get("timestamp"),
            "type": glyph_data.get("type"),
            "significance": glyph_data.get("significance")
        }
        
        data_string = json.dumps(signature_data, sort_keys=True)
        return hashlib.sha256(data_string.encode()).hexdigest()[:16]
    
    def _determine_glyph_type(self, analysis_data: Dict[str, Any]) -> str:
        """Determine glyph type based on analysis characteristics."""
        health_score = analysis_data.get("health_score", 0)
        security_score = analysis_data.get("security_scan", {}).get("security_score", 100)
        
        # Check security first for shadow anomaly
        if security_score < 70:
            return "shadow_anomaly"
        elif health_score >= 90 and security_score >= 95:
            return "stellar_convergence"
        elif health_score >= 80:
            return "harmonic_resonance"
        elif health_score >= 60:
            return "temporal_flux"
        else:
            return "dimensional_drift"
    
    def _calculate_significance(self, analysis_data: Dict[str, Any]) -> float:
        """Calculate glyph significance score (0.0-1.0)."""
        factors = []
        
        # Health score factor
        health_score = analysis_data.get("health_score", 0)
        factors.append(health_score / 100.0)
        
        # Security factor
        security_score = analysis_data.get("security_scan", {}).get("security_score", 100)
        factors.append(security_score / 100.0)
        
        # Activity factor (recent commits)
        commits_analysis = analysis_data.get("commits_analysis", {})
        recent_activity = commits_analysis.get("recent_activity", {})
        if recent_activity.get("last_commit"):
            factors.append(0.8)  # Active repository
        else:
            factors.append(0.2)  # Inactive repository
        
        # Repository size factor
        repo_info = analysis_data.get("repository_info", {})
        size_kb = analysis_data.get("performance_metrics", {}).get("repository_size_kb", 0)
        if size_kb > 50000:  # Large repository
            factors.append(0.9)
        elif size_kb > 10000:  # Medium repository
            factors.append(0.7)
        else:  # Small repository
            factors.append(0.5)
        
        return sum(factors) / len(factors) if factors else 0.5
    
    def _extract_glyph_properties(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract symbolic properties from analysis data."""
        properties = {}
        
        # Language resonance
        code_analysis = analysis_data.get("code_analysis", {})
        languages = code_analysis.get("languages", {})
        if languages:
            dominant_language = max(languages.items(), key=lambda x: x[1])[0]
            properties["dominant_resonance"] = dominant_language.lower()
            properties["language_diversity"] = len(languages)
        
        # Security aura
        security_scan = analysis_data.get("security_scan", {})
        properties["security_aura"] = security_scan.get("security_score", 100) / 100.0
        
        # Temporal signature
        commits_analysis = analysis_data.get("commits_analysis", {})
        properties["commit_frequency"] = commits_analysis.get("total_commits_analyzed", 0)
        properties["author_constellation"] = commits_analysis.get("unique_authors", 0)
        
        # Dimensional metrics
        performance = analysis_data.get("performance_metrics", {})
        properties["size_magnitude"] = performance.get("repository_size_kb", 0)
        
        return properties
    
    def _transform_analysis_to_glyph(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform MirrorWatcherAI analysis data into a glyph event."""
        timestamp = datetime.now(timezone.utc).isoformat()
        glyph_type = self._determine_glyph_type(analysis_data)
        significance = self._calculate_significance(analysis_data)
        properties = self._extract_glyph_properties(analysis_data)
        
        glyph = {
            "id": f"glyph_{analysis_data.get('repository', 'unknown')}_{int(datetime.now(timezone.utc).timestamp())}",
            "timestamp": timestamp,
            "repository": analysis_data.get("repository"),
            "type": glyph_type,
            "significance": round(significance, 3),
            "properties": properties,
            "source_analysis": {
                "analysis_timestamp": analysis_data.get("analysis_timestamp"),
                "health_score": analysis_data.get("health_score"),
                "status": analysis_data.get("status")
            },
            "metadata": {
                "processor_version": "1.0.0",
                "generated_at": timestamp
            }
        }
        
        # Add cryptographic signature
        glyph["signature"] = self._generate_glyph_signature(glyph)
        
        return glyph
    
    def process_analysis_file(self, analysis_file: Path) -> List[Dict[str, Any]]:
        """Process a single MirrorWatcherAI analysis file into glyph events."""
        try:
            logger.info(f"Processing analysis file: {analysis_file}")
            
            with open(analysis_file, 'r') as f:
                analysis_data = json.load(f)
            
            glyphs = []
            
            # Process individual repository analyses
            repositories = analysis_data.get("repositories", {})
            for repo_name, repo_analysis in repositories.items():
                if repo_analysis.get("status") == "completed":
                    glyph = self._transform_analysis_to_glyph(repo_analysis)
                    glyphs.append(glyph)
                    logger.info(f"Generated glyph for {repo_name}: {glyph['type']} (significance: {glyph['significance']})")
                else:
                    logger.warning(f"Skipping incomplete analysis for {repo_name}")
            
            return glyphs
            
        except Exception as e:
            logger.error(f"Error processing analysis file {analysis_file}: {str(e)}")
            return []
    
    def append_glyphs_to_codex(self, glyphs: List[Dict[str, Any]]) -> bool:
        """Append new glyph events to the codex file."""
        try:
            # Load existing codex data
            with open(self.codex_file, 'r') as f:
                codex_data = json.load(f)
            
            # Append new glyphs
            codex_data["glyphs"].extend(glyphs)
            codex_data["last_updated"] = datetime.now(timezone.utc).isoformat()
            
            # Update metadata
            codex_data["metadata"]["total_glyphs"] = len(codex_data["glyphs"])
            codex_data["metadata"]["last_emission_count"] = len(glyphs)
            
            # Write back to file
            with open(self.codex_file, 'w') as f:
                json.dump(codex_data, f, indent=2)
            
            logger.info(f"Appended {len(glyphs)} glyphs to codex. Total glyphs: {len(codex_data['glyphs'])}")
            return True
            
        except Exception as e:
            logger.error(f"Error appending glyphs to codex: {str(e)}")
            return False
    
    def process_latest_analysis(self) -> bool:
        """Find and process the latest MirrorWatcherAI analysis file."""
        try:
            # Find the most recent analysis file
            analysis_files = list(self.output_dir.glob("analysis_*.json"))
            if not analysis_files:
                logger.warning(f"No analysis files found in {self.output_dir}")
                return False
            
            latest_file = max(analysis_files, key=lambda x: x.stat().st_mtime)
            logger.info(f"Processing latest analysis file: {latest_file}")
            
            # Process the file
            glyphs = self.process_analysis_file(latest_file)
            
            if glyphs:
                return self.append_glyphs_to_codex(glyphs)
            else:
                logger.warning("No glyphs generated from analysis file")
                return False
                
        except Exception as e:
            logger.error(f"Error processing latest analysis: {str(e)}")
            return False
    
    def process_specific_file(self, file_path: str) -> bool:
        """Process a specific analysis file."""
        try:
            analysis_file = Path(file_path)
            if not analysis_file.exists():
                logger.error(f"Analysis file not found: {file_path}")
                return False
            
            glyphs = self.process_analysis_file(analysis_file)
            
            if glyphs:
                return self.append_glyphs_to_codex(glyphs)
            else:
                logger.warning("No glyphs generated from analysis file")
                return False
                
        except Exception as e:
            logger.error(f"Error processing specific file: {str(e)}")
            return False


def main():
    """Main entry point for the glyph emission processor."""
    parser = argparse.ArgumentParser(description="Process MirrorWatcherAI analysis into glyph events")
    parser.add_argument("--file", help="Specific analysis file to process")
    parser.add_argument("--output-dir", default="artifacts", help="Directory containing analysis files")
    parser.add_argument("--data-dir", default="data", help="Directory for codex data files")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Initialize processor
    processor = GlyphEmissionProcessor(args.output_dir, args.data_dir)
    
    # Process analysis
    if args.file:
        success = processor.process_specific_file(args.file)
    else:
        success = processor.process_latest_analysis()
    
    if success:
        logger.info("Glyph emission processing completed successfully")
        sys.exit(0)
    else:
        logger.error("Glyph emission processing failed")
        sys.exit(1)


if __name__ == "__main__":
    main()