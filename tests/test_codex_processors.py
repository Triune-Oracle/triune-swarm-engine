#!/usr/bin/env python3
"""
Test suite for Codex post-processing scripts
============================================

Tests for glyph emission processor and constellation snapshot generator.
"""

import asyncio
import os
import sys
import json
import tempfile
import unittest
from pathlib import Path
import shutil

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from scripts.processors.glyph_emitter import GlyphEmissionProcessor
    from scripts.generators.snapshot_creator import ConstellationSnapshotGenerator
except ImportError as e:
    print(f"Import error: {e}")
    print("Scripts may not be in the expected location")
    sys.exit(1)


class TestGlyphEmissionProcessor(unittest.TestCase):
    """Test glyph emission processor functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.output_dir = Path(self.temp_dir) / "artifacts"
        self.data_dir = Path(self.temp_dir) / "data"
        self.output_dir.mkdir(exist_ok=True)
        self.data_dir.mkdir(exist_ok=True)
        
        # Create sample analysis data
        self.sample_analysis = {
            "execution_id": "test_analysis",
            "timestamp": "2025-01-18T06:00:00Z",
            "repositories": {
                "test-repo": {
                    "repository": "test-repo",
                    "analysis_timestamp": "2025-01-18T06:00:00Z",
                    "status": "completed",
                    "repository_info": {
                        "name": "test-repo",
                        "stargazers_count": 10,
                        "open_issues_count": 2
                    },
                    "commits_analysis": {
                        "total_commits_analyzed": 50,
                        "unique_authors": 2,
                        "recent_activity": {
                            "last_commit": "2025-01-18T05:30:00Z"
                        }
                    },
                    "code_analysis": {
                        "languages": {"Python": 1000, "JavaScript": 500}
                    },
                    "security_scan": {
                        "security_score": 85,
                        "security_advisories": 0
                    },
                    "performance_metrics": {
                        "repository_size_kb": 5000
                    },
                    "health_score": 80
                }
            }
        }
        
        # Save sample analysis file
        self.analysis_file = self.output_dir / "analysis_test.json"
        with open(self.analysis_file, 'w') as f:
            json.dump(self.sample_analysis, f)
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)
    
    def test_processor_initialization(self):
        """Test processor initialization."""
        processor = GlyphEmissionProcessor(str(self.output_dir), str(self.data_dir))
        self.assertTrue(processor.codex_file.exists())
        
        # Check initial codex structure
        with open(processor.codex_file, 'r') as f:
            data = json.load(f)
        
        self.assertIn("version", data)
        self.assertIn("glyphs", data)
        self.assertEqual(len(data["glyphs"]), 0)
    
    def test_glyph_type_determination(self):
        """Test glyph type determination logic."""
        processor = GlyphEmissionProcessor(str(self.output_dir), str(self.data_dir))
        
        # Test stellar convergence (high health + security)
        high_quality = {"health_score": 95, "security_scan": {"security_score": 98}}
        self.assertEqual(processor._determine_glyph_type(high_quality), "stellar_convergence")
        
        # Test harmonic resonance (good health)
        good_quality = {"health_score": 85, "security_scan": {"security_score": 90}}
        self.assertEqual(processor._determine_glyph_type(good_quality), "harmonic_resonance")
        
        # Test shadow anomaly (poor security)
        poor_security = {"health_score": 70, "security_scan": {"security_score": 60}}
        self.assertEqual(processor._determine_glyph_type(poor_security), "shadow_anomaly")
    
    def test_significance_calculation(self):
        """Test significance score calculation."""
        processor = GlyphEmissionProcessor(str(self.output_dir), str(self.data_dir))
        
        analysis_data = self.sample_analysis["repositories"]["test-repo"]
        significance = processor._calculate_significance(analysis_data)
        
        self.assertIsInstance(significance, float)
        self.assertGreaterEqual(significance, 0.0)
        self.assertLessEqual(significance, 1.0)
    
    def test_glyph_transformation(self):
        """Test transformation of analysis data to glyph."""
        processor = GlyphEmissionProcessor(str(self.output_dir), str(self.data_dir))
        
        analysis_data = self.sample_analysis["repositories"]["test-repo"]
        glyph = processor._transform_analysis_to_glyph(analysis_data)
        
        # Verify glyph structure
        required_fields = ["id", "timestamp", "repository", "type", "significance", 
                          "properties", "source_analysis", "metadata", "signature"]
        for field in required_fields:
            self.assertIn(field, glyph)
        
        self.assertEqual(glyph["repository"], "test-repo")
        self.assertIn("python", glyph["properties"].get("dominant_resonance", ""))
    
    def test_process_analysis_file(self):
        """Test processing of analysis file."""
        processor = GlyphEmissionProcessor(str(self.output_dir), str(self.data_dir))
        
        glyphs = processor.process_analysis_file(self.analysis_file)
        
        self.assertEqual(len(glyphs), 1)
        self.assertEqual(glyphs[0]["repository"], "test-repo")
    
    def test_append_glyphs_to_codex(self):
        """Test appending glyphs to codex file."""
        processor = GlyphEmissionProcessor(str(self.output_dir), str(self.data_dir))
        
        # Process analysis and append glyphs
        glyphs = processor.process_analysis_file(self.analysis_file)
        success = processor.append_glyphs_to_codex(glyphs)
        
        self.assertTrue(success)
        
        # Verify codex was updated
        with open(processor.codex_file, 'r') as f:
            data = json.load(f)
        
        self.assertEqual(len(data["glyphs"]), 1)
        self.assertEqual(data["metadata"]["total_glyphs"], 1)


class TestConstellationSnapshotGenerator(unittest.TestCase):
    """Test constellation snapshot generator functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.data_dir = Path(self.temp_dir) / "data"
        self.data_dir.mkdir(exist_ok=True)
        
        # Create sample glyph data
        sample_glyphs = {
            "version": "1.0.0",
            "last_updated": "2025-01-18T06:00:00Z",
            "metadata": {"schema_version": "1.0"},
            "glyphs": [
                {
                    "id": "glyph_repo1_1",
                    "timestamp": "2025-01-18T06:00:00Z",
                    "repository": "repo1",
                    "type": "stellar_convergence",
                    "significance": 0.9,
                    "properties": {
                        "dominant_resonance": "python",
                        "security_aura": 0.95
                    }
                },
                {
                    "id": "glyph_repo2_2",
                    "timestamp": "2025-01-18T06:01:00Z",
                    "repository": "repo2",
                    "type": "harmonic_resonance",
                    "significance": 0.8,
                    "properties": {
                        "dominant_resonance": "python",
                        "security_aura": 0.85
                    }
                },
                {
                    "id": "glyph_repo3_3",
                    "timestamp": "2025-01-18T06:02:00Z",
                    "repository": "repo3",
                    "type": "temporal_flux",
                    "significance": 0.7,
                    "properties": {
                        "dominant_resonance": "javascript",
                        "security_aura": 0.75
                    }
                }
            ]
        }
        
        # Save sample glyph data
        codex_file = self.data_dir / "codexGlyphs.json"
        with open(codex_file, 'w') as f:
            json.dump(sample_glyphs, f)
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)
    
    def test_generator_initialization(self):
        """Test generator initialization."""
        generator = ConstellationSnapshotGenerator(str(self.data_dir))
        self.assertTrue(generator.constellation_file.exists())
        
        # Check initial constellation structure
        with open(generator.constellation_file, 'r') as f:
            data = json.load(f)
        
        self.assertIn("version", data)
        self.assertIn("snapshots", data)
        self.assertEqual(len(data["snapshots"]), 0)
    
    def test_load_glyphs(self):
        """Test loading glyph data."""
        generator = ConstellationSnapshotGenerator(str(self.data_dir))
        glyphs = generator._load_glyphs()
        
        self.assertEqual(len(glyphs), 3)
        self.assertEqual(glyphs[0]["repository"], "repo1")
    
    def test_relationship_calculation(self):
        """Test glyph relationship calculation."""
        generator = ConstellationSnapshotGenerator(str(self.data_dir))
        glyphs = generator._load_glyphs()
        relationships = generator._calculate_glyph_relationships(glyphs)
        
        self.assertIsInstance(relationships, dict)
        # Should have relationships between different repositories
        self.assertGreater(len(relationships), 0)
    
    def test_position_calculation(self):
        """Test glyph position calculation."""
        generator = ConstellationSnapshotGenerator(str(self.data_dir))
        glyphs = generator._load_glyphs()
        relationships = generator._calculate_glyph_relationships(glyphs)
        positions = generator._calculate_glyph_positions(glyphs, relationships)
        
        self.assertEqual(len(positions), 3)
        for repo, pos in positions.items():
            self.assertEqual(len(pos), 2)  # x, y coordinates
            self.assertIsInstance(pos[0], float)
            self.assertIsInstance(pos[1], float)
    
    def test_constellation_metrics(self):
        """Test constellation metrics calculation."""
        generator = ConstellationSnapshotGenerator(str(self.data_dir))
        glyphs = generator._load_glyphs()
        relationships = generator._calculate_glyph_relationships(glyphs)
        positions = generator._calculate_glyph_positions(glyphs, relationships)
        metrics = generator._calculate_constellation_metrics(glyphs, relationships, positions)
        
        self.assertIn("total_glyphs", metrics)
        self.assertIn("total_relationships", metrics)
        self.assertIn("average_significance", metrics)
        self.assertIn("stability_index", metrics)
        
        self.assertEqual(metrics["total_glyphs"], 3)
    
    def test_snapshot_generation(self):
        """Test constellation snapshot generation."""
        generator = ConstellationSnapshotGenerator(str(self.data_dir))
        snapshot = generator.generate_constellation_snapshot()
        
        self.assertIsNotNone(snapshot)
        
        # Verify snapshot structure
        required_fields = ["id", "timestamp", "version", "nodes", "edges", 
                          "metrics", "metadata", "signature"]
        for field in required_fields:
            self.assertIn(field, snapshot)
        
        self.assertEqual(len(snapshot["nodes"]), 3)
        self.assertGreaterEqual(len(snapshot["edges"]), 0)
    
    def test_snapshot_saving(self):
        """Test saving constellation snapshot."""
        generator = ConstellationSnapshotGenerator(str(self.data_dir))
        snapshot = generator.generate_constellation_snapshot()
        success = generator.save_constellation_snapshot(snapshot)
        
        self.assertTrue(success)
        
        # Verify snapshot was saved
        with open(generator.constellation_file, 'r') as f:
            data = json.load(f)
        
        self.assertEqual(len(data["snapshots"]), 1)
        self.assertEqual(data["metadata"]["total_snapshots"], 1)
    
    def test_data_integrity_validation(self):
        """Test data integrity validation."""
        generator = ConstellationSnapshotGenerator(str(self.data_dir))
        
        # Generate and save a snapshot
        snapshot = generator.generate_constellation_snapshot()
        generator.save_constellation_snapshot(snapshot)
        
        # Validate integrity
        integrity_ok = generator.validate_data_integrity()
        self.assertTrue(integrity_ok)


class TestIntegration(unittest.TestCase):
    """Test integration between glyph processor and snapshot generator."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.output_dir = Path(self.temp_dir) / "artifacts"
        self.data_dir = Path(self.temp_dir) / "data"
        self.output_dir.mkdir(exist_ok=True)
        self.data_dir.mkdir(exist_ok=True)
        
        # Create sample analysis data with multiple repositories
        self.sample_analysis = {
            "execution_id": "test_integration",
            "repositories": {
                "repo1": {
                    "repository": "repo1",
                    "status": "completed",
                    "health_score": 90,
                    "security_scan": {"security_score": 95},
                    "code_analysis": {"languages": {"Python": 1000}},
                    "commits_analysis": {"total_commits_analyzed": 100, "unique_authors": 3},
                    "performance_metrics": {"repository_size_kb": 10000}
                },
                "repo2": {
                    "repository": "repo2",
                    "status": "completed",
                    "health_score": 85,
                    "security_scan": {"security_score": 88},
                    "code_analysis": {"languages": {"JavaScript": 800}},
                    "commits_analysis": {"total_commits_analyzed": 75, "unique_authors": 2},
                    "performance_metrics": {"repository_size_kb": 8000}
                }
            }
        }
        
        # Save analysis file
        self.analysis_file = self.output_dir / "analysis_integration.json"
        with open(self.analysis_file, 'w') as f:
            json.dump(self.sample_analysis, f)
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)
    
    def test_full_processing_pipeline(self):
        """Test complete processing pipeline from analysis to constellation."""
        # Step 1: Process glyphs
        processor = GlyphEmissionProcessor(str(self.output_dir), str(self.data_dir))
        success = processor.process_specific_file(str(self.analysis_file))
        self.assertTrue(success)
        
        # Verify glyphs were created
        with open(processor.codex_file, 'r') as f:
            glyph_data = json.load(f)
        self.assertEqual(len(glyph_data["glyphs"]), 2)
        
        # Step 2: Generate constellation snapshot
        generator = ConstellationSnapshotGenerator(str(self.data_dir))
        success = generator.generate_and_save_snapshot()
        self.assertTrue(success)
        
        # Verify snapshot was created
        with open(generator.constellation_file, 'r') as f:
            constellation_data = json.load(f)
        self.assertEqual(len(constellation_data["snapshots"]), 1)
        
        # Verify snapshot contains correct data
        snapshot = constellation_data["snapshots"][0]
        self.assertEqual(len(snapshot["nodes"]), 2)
        self.assertEqual(snapshot["metadata"]["source_glyphs"], 2)


if __name__ == "__main__":
    unittest.main()