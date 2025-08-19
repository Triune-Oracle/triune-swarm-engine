#!/usr/bin/env python3
"""
Constellation Snapshot Generator
================================

Creates timestamped constellation snapshots that represent relationships between 
glyphs in the Codex visualization system.

This script:
- Creates timestamped constellation snapshots representing glyph relationships
- Calculates glyph positions based on their relationships and significance
- Updates data/constellationSnapshots.json with new snapshot data
- Includes versioning and data integrity validation
"""

import json
import logging
import hashlib
import argparse
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import sys

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ConstellationSnapshotGenerator:
    """
    Generates constellation snapshots representing relationships between glyphs.
    
    Creates geometric representations of glyph interconnections, calculating
    positions, strengths, and temporal dynamics of the Codex ecosystem.
    """
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.codex_file = self.data_dir / "codexGlyphs.json"
        self.constellation_file = self.data_dir / "constellationSnapshots.json"
        
        # Ensure directories exist
        self.data_dir.mkdir(exist_ok=True)
        
        # Initialize constellation file if it doesn't exist
        if not self.constellation_file.exists():
            self._initialize_constellation_file()
    
    def _initialize_constellation_file(self) -> None:
        """Initialize the constellation snapshots file with proper structure."""
        initial_data = {
            "version": "1.0.0",
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "metadata": {
                "description": "Constellation snapshots representing glyph relationships",
                "schema_version": "1.0",
                "source": "MirrorWatcherAI"
            },
            "snapshots": []
        }
        
        with open(self.constellation_file, 'w') as f:
            json.dump(initial_data, f, indent=2)
        
        logger.info(f"Initialized constellation file: {self.constellation_file}")
    
    def _load_glyphs(self) -> List[Dict[str, Any]]:
        """Load glyph data from the codex file."""
        try:
            if not self.codex_file.exists():
                logger.warning(f"Codex file not found: {self.codex_file}")
                return []
            
            with open(self.codex_file, 'r') as f:
                codex_data = json.load(f)
            
            return codex_data.get("glyphs", [])
            
        except Exception as e:
            logger.error(f"Error loading glyphs: {str(e)}")
            return []
    
    def _calculate_glyph_relationships(self, glyphs: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate relationship strengths between glyphs."""
        relationships = {}
        
        for i, glyph1 in enumerate(glyphs):
            for j, glyph2 in enumerate(glyphs[i+1:], i+1):
                repo1 = glyph1.get("repository", "")
                repo2 = glyph2.get("repository", "")
                
                # Skip self-relationships
                if repo1 == repo2:
                    continue
                
                strength = self._calculate_relationship_strength(glyph1, glyph2)
                if strength > 0.1:  # Only include meaningful relationships
                    key = f"{repo1}:{repo2}" if repo1 < repo2 else f"{repo2}:{repo1}"
                    relationships[key] = strength
        
        return relationships
    
    def _calculate_relationship_strength(self, glyph1: Dict[str, Any], glyph2: Dict[str, Any]) -> float:
        """Calculate the relationship strength between two glyphs."""
        factors = []
        
        # Type similarity
        type1 = glyph1.get("type", "")
        type2 = glyph2.get("type", "")
        if type1 == type2:
            factors.append(0.8)
        elif self._are_compatible_types(type1, type2):
            factors.append(0.5)
        else:
            factors.append(0.1)
        
        # Significance correlation
        sig1 = glyph1.get("significance", 0)
        sig2 = glyph2.get("significance", 0)
        sig_diff = abs(sig1 - sig2)
        sig_factor = 1.0 - sig_diff  # Closer significance = stronger relationship
        factors.append(max(0, sig_factor))
        
        # Language resonance
        props1 = glyph1.get("properties", {})
        props2 = glyph2.get("properties", {})
        lang1 = props1.get("dominant_resonance", "")
        lang2 = props2.get("dominant_resonance", "")
        if lang1 and lang2:
            if lang1 == lang2:
                factors.append(0.7)
            else:
                factors.append(0.2)
        
        # Temporal proximity
        time1 = glyph1.get("timestamp", "")
        time2 = glyph2.get("timestamp", "")
        if time1 and time2:
            try:
                dt1 = datetime.fromisoformat(time1.replace('Z', '+00:00'))
                dt2 = datetime.fromisoformat(time2.replace('Z', '+00:00'))
                time_diff = abs((dt1 - dt2).total_seconds())
                # Stronger relationship for glyphs created within 24 hours
                if time_diff < 86400:  # 24 hours
                    factors.append(0.9)
                elif time_diff < 604800:  # 1 week
                    factors.append(0.6)
                else:
                    factors.append(0.2)
            except:
                factors.append(0.3)
        
        return sum(factors) / len(factors) if factors else 0.0
    
    def _are_compatible_types(self, type1: str, type2: str) -> bool:
        """Check if two glyph types are compatible/related."""
        compatible_pairs = {
            ("stellar_convergence", "harmonic_resonance"),
            ("harmonic_resonance", "temporal_flux"),
            ("shadow_anomaly", "dimensional_drift"),
        }
        
        pair = (type1, type2) if type1 < type2 else (type2, type1)
        return pair in compatible_pairs
    
    def _calculate_glyph_positions(self, glyphs: List[Dict[str, Any]], 
                                 relationships: Dict[str, float]) -> Dict[str, Tuple[float, float]]:
        """Calculate 2D positions for glyphs in the constellation."""
        positions = {}
        
        if not glyphs:
            return positions
        
        # Use force-directed layout algorithm
        repos = [g.get("repository", "") for g in glyphs]
        n = len(repos)
        
        # Initialize positions in a circle
        for i, repo in enumerate(repos):
            angle = 2 * math.pi * i / n
            radius = 100  # Base radius
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            positions[repo] = (x, y)
        
        # Apply force-directed iterations
        for iteration in range(50):  # 50 iterations for stability
            forces = {repo: (0.0, 0.0) for repo in repos}
            
            # Repulsive forces between all nodes
            for i, repo1 in enumerate(repos):
                for j, repo2 in enumerate(repos[i+1:], i+1):
                    x1, y1 = positions[repo1]
                    x2, y2 = positions[repo2]
                    
                    dx = x2 - x1
                    dy = y2 - y1
                    distance = math.sqrt(dx*dx + dy*dy)
                    
                    if distance > 0:
                        repulsion = 1000 / (distance * distance)  # Coulomb-like repulsion
                        fx = -repulsion * dx / distance
                        fy = -repulsion * dy / distance
                        
                        forces[repo1] = (forces[repo1][0] + fx, forces[repo1][1] + fy)
                        forces[repo2] = (forces[repo2][0] - fx, forces[repo2][1] - fy)
            
            # Attractive forces based on relationships
            for rel_key, strength in relationships.items():
                repo1, repo2 = rel_key.split(":")
                if repo1 in positions and repo2 in positions:
                    x1, y1 = positions[repo1]
                    x2, y2 = positions[repo2]
                    
                    dx = x2 - x1
                    dy = y2 - y1
                    distance = math.sqrt(dx*dx + dy*dy)
                    
                    if distance > 0:
                        attraction = strength * distance * 0.1  # Spring-like attraction
                        fx = attraction * dx / distance
                        fy = attraction * dy / distance
                        
                        forces[repo1] = (forces[repo1][0] + fx, forces[repo1][1] + fy)
                        forces[repo2] = (forces[repo2][0] - fx, forces[repo2][1] - fy)
            
            # Update positions
            for repo in repos:
                fx, fy = forces[repo]
                x, y = positions[repo]
                
                # Apply damping and update
                damping = 0.8
                positions[repo] = (x + fx * damping * 0.01, y + fy * damping * 0.01)
        
        return positions
    
    def _calculate_constellation_metrics(self, glyphs: List[Dict[str, Any]], 
                                       relationships: Dict[str, float], 
                                       positions: Dict[str, Tuple[float, float]]) -> Dict[str, Any]:
        """Calculate overall constellation metrics."""
        if not glyphs:
            return {}
        
        # Basic metrics
        total_glyphs = len(glyphs)
        total_relationships = len(relationships)
        avg_significance = sum(g.get("significance", 0) for g in glyphs) / total_glyphs
        
        # Type distribution
        type_counts = {}
        for glyph in glyphs:
            glyph_type = glyph.get("type", "unknown")
            type_counts[glyph_type] = type_counts.get(glyph_type, 0) + 1
        
        # Constellation density
        avg_relationship_strength = sum(relationships.values()) / len(relationships) if relationships else 0
        
        # Stability metric (based on position spread)
        if positions:
            x_coords = [pos[0] for pos in positions.values()]
            y_coords = [pos[1] for pos in positions.values()]
            x_spread = max(x_coords) - min(x_coords) if x_coords else 0
            y_spread = max(y_coords) - min(y_coords) if y_coords else 0
            stability = 1.0 / (1.0 + (x_spread + y_spread) / 1000)  # Normalized stability
        else:
            stability = 0.0
        
        return {
            "total_glyphs": total_glyphs,
            "total_relationships": total_relationships,
            "average_significance": round(avg_significance, 3),
            "type_distribution": type_counts,
            "constellation_density": round(avg_relationship_strength, 3),
            "stability_index": round(stability, 3)
        }
    
    def _generate_snapshot_signature(self, snapshot: Dict[str, Any]) -> str:
        """Generate cryptographic signature for snapshot integrity verification."""
        signature_data = {
            "timestamp": snapshot.get("timestamp"),
            "glyph_count": len(snapshot.get("nodes", [])),
            "relationship_count": len(snapshot.get("edges", [])),
            "metrics": snapshot.get("metrics", {})
        }
        
        data_string = json.dumps(signature_data, sort_keys=True)
        return hashlib.sha256(data_string.encode()).hexdigest()[:16]
    
    def generate_constellation_snapshot(self) -> Optional[Dict[str, Any]]:
        """Generate a new constellation snapshot from current glyph data."""
        try:
            logger.info("Generating constellation snapshot")
            
            # Load current glyphs
            glyphs = self._load_glyphs()
            if not glyphs:
                logger.warning("No glyphs found for constellation generation")
                return None
            
            # Calculate relationships
            relationships = self._calculate_glyph_relationships(glyphs)
            logger.info(f"Calculated {len(relationships)} glyph relationships")
            
            # Calculate positions
            positions = self._calculate_glyph_positions(glyphs, relationships)
            logger.info(f"Calculated positions for {len(positions)} glyphs")
            
            # Calculate metrics
            metrics = self._calculate_constellation_metrics(glyphs, relationships, positions)
            
            # Create snapshot
            timestamp = datetime.now(timezone.utc).isoformat()
            snapshot = {
                "id": f"constellation_{int(datetime.now(timezone.utc).timestamp())}",
                "timestamp": timestamp,
                "version": "1.0.0",
                "nodes": [
                    {
                        "id": glyph.get("repository"),
                        "type": glyph.get("type"),
                        "significance": glyph.get("significance"),
                        "position": {
                            "x": positions.get(glyph.get("repository"), (0, 0))[0],
                            "y": positions.get(glyph.get("repository"), (0, 0))[1]
                        },
                        "properties": glyph.get("properties", {}),
                        "glyph_id": glyph.get("id")
                    }
                    for glyph in glyphs
                ],
                "edges": [
                    {
                        "source": rel_key.split(":")[0],
                        "target": rel_key.split(":")[1],
                        "strength": strength,
                        "type": "relationship"
                    }
                    for rel_key, strength in relationships.items()
                ],
                "metrics": metrics,
                "metadata": {
                    "generator_version": "1.0.0",
                    "generated_at": timestamp,
                    "source_glyphs": len(glyphs)
                }
            }
            
            # Add signature
            snapshot["signature"] = self._generate_snapshot_signature(snapshot)
            
            logger.info(f"Generated constellation snapshot with {len(snapshot['nodes'])} nodes and {len(snapshot['edges'])} edges")
            return snapshot
            
        except Exception as e:
            logger.error(f"Error generating constellation snapshot: {str(e)}")
            return None
    
    def save_constellation_snapshot(self, snapshot: Dict[str, Any]) -> bool:
        """Save constellation snapshot to the snapshots file."""
        try:
            # Load existing data
            with open(self.constellation_file, 'r') as f:
                constellation_data = json.load(f)
            
            # Append new snapshot
            constellation_data["snapshots"].append(snapshot)
            constellation_data["last_updated"] = datetime.now(timezone.utc).isoformat()
            
            # Update metadata
            constellation_data["metadata"]["total_snapshots"] = len(constellation_data["snapshots"])
            constellation_data["metadata"]["latest_snapshot_id"] = snapshot.get("id")
            
            # Implement retention policy (keep last 100 snapshots)
            if len(constellation_data["snapshots"]) > 100:
                constellation_data["snapshots"] = constellation_data["snapshots"][-100:]
                logger.info("Applied retention policy: kept last 100 snapshots")
            
            # Write back to file
            with open(self.constellation_file, 'w') as f:
                json.dump(constellation_data, f, indent=2)
            
            logger.info(f"Saved constellation snapshot: {snapshot.get('id')}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving constellation snapshot: {str(e)}")
            return False
    
    def validate_data_integrity(self) -> bool:
        """Validate data integrity of existing snapshots."""
        try:
            with open(self.constellation_file, 'r') as f:
                constellation_data = json.load(f)
            
            snapshots = constellation_data.get("snapshots", [])
            valid_count = 0
            
            for snapshot in snapshots:
                expected_signature = self._generate_snapshot_signature(snapshot)
                actual_signature = snapshot.get("signature", "")
                
                if expected_signature == actual_signature:
                    valid_count += 1
                else:
                    logger.warning(f"Integrity check failed for snapshot: {snapshot.get('id')}")
            
            logger.info(f"Data integrity validation: {valid_count}/{len(snapshots)} snapshots valid")
            return valid_count == len(snapshots)
            
        except Exception as e:
            logger.error(f"Error validating data integrity: {str(e)}")
            return False
    
    def generate_and_save_snapshot(self) -> bool:
        """Generate and save a new constellation snapshot."""
        snapshot = self.generate_constellation_snapshot()
        if snapshot:
            return self.save_constellation_snapshot(snapshot)
        return False


def main():
    """Main entry point for the constellation snapshot generator."""
    parser = argparse.ArgumentParser(description="Generate constellation snapshots from glyph data")
    parser.add_argument("--data-dir", default="data", help="Directory for codex data files")
    parser.add_argument("--validate", action="store_true", help="Validate data integrity")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Initialize generator
    generator = ConstellationSnapshotGenerator(args.data_dir)
    
    # Validate if requested
    if args.validate:
        integrity_ok = generator.validate_data_integrity()
        if not integrity_ok:
            logger.error("Data integrity validation failed")
            sys.exit(1)
    
    # Generate snapshot
    success = generator.generate_and_save_snapshot()
    
    if success:
        logger.info("Constellation snapshot generation completed successfully")
        sys.exit(0)
    else:
        logger.error("Constellation snapshot generation failed")
        sys.exit(1)


if __name__ == "__main__":
    main()