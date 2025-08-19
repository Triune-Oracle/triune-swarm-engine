# Codex Post-Processing Scripts

This directory contains the essential post-processing scripts for MirrorWatcherAI integration with the Codex visualization system.

## Overview

The Codex system transforms MirrorWatcherAI analysis results into symbolic representations (glyphs) and creates constellation snapshots that visualize relationships between repositories in the Triune Oracle ecosystem.

## Components

### 1. Glyph Emission Processor (`processors/glyph_emitter.py`)

Transforms MirrorWatcherAI analysis results into standardized glyph events for visualization.

**Features:**
- Parses analysis results from MirrorWatcherAI output directory
- Transforms repository data into symbolic glyph representations
- Calculates glyph significance based on health, security, and activity metrics
- Appends new glyph events to `data/codexGlyphs.json` with timestamps and cryptographic signatures
- Comprehensive error handling and logging

**Glyph Types:**
- `stellar_convergence`: High-quality repositories (health ≥90%, security ≥95%)
- `harmonic_resonance`: Good repositories (health ≥80%)
- `temporal_flux`: Moderate repositories (health ≥60%)
- `shadow_anomaly`: Repositories with security issues (security <70%)
- `dimensional_drift`: Low-quality repositories

**Usage:**
```bash
# Process latest analysis
python scripts/processors/glyph_emitter.py

# Process specific file
python scripts/processors/glyph_emitter.py --file artifacts/analysis_20250118_060000.json

# Verbose output
python scripts/processors/glyph_emitter.py --verbose
```

### 2. Constellation Snapshot Generator (`generators/snapshot_creator.py`)

Creates timestamped constellation snapshots representing relationships between glyphs.

**Features:**
- Analyzes glyph relationships based on type similarity, language resonance, and temporal proximity
- Calculates 2D positions using force-directed layout algorithm
- Generates comprehensive constellation metrics (density, stability, type distribution)
- Updates `data/constellationSnapshots.json` with versioned snapshots
- Data integrity validation with cryptographic signatures
- Retention policy (keeps last 100 snapshots)

**Usage:**
```bash
# Generate constellation snapshot
python scripts/generators/snapshot_creator.py

# Validate data integrity
python scripts/generators/snapshot_creator.py --validate

# Verbose output
python scripts/generators/snapshot_creator.py --verbose
```

### 3. Dashboard Update Workflow (`.github/workflows/codex-dashboard-update.yml`)

GitHub Actions workflow that automatically processes MirrorWatcherAI results.

**Features:**
- Triggers after MirrorWatcherAI completion (06:00 UTC daily)
- Downloads and validates analysis artifacts
- Processes glyph emissions and generates constellation snapshots
- Updates dashboard data files and commits changes
- Comprehensive error handling and notifications
- Manual trigger support for testing

**Workflow Steps:**
1. Download MirrorWatcherAI artifacts
2. Validate analysis data integrity
3. Process glyph emissions
4. Generate constellation snapshot
5. Update dashboard components
6. Commit updated data files
7. Send notifications

## Data Files

### `data/codexGlyphs.json`
Contains all generated glyph events with:
- Unique identifiers and timestamps
- Repository metadata and analysis results
- Symbolic properties (type, significance, resonance)
- Cryptographic signatures for integrity verification

### `data/constellationSnapshots.json`
Contains constellation snapshots with:
- Node positions and properties
- Edge relationships and strengths
- Constellation metrics and metadata
- Versioning and integrity signatures

## Integration

The post-processing scripts integrate seamlessly with the existing MirrorWatcherAI workflow:

1. **MirrorWatcherAI** runs daily at 06:00 UTC via `.github/workflows/mirror-watcher-automation.yml`
2. **Codex Dashboard Update** triggers automatically after successful MirrorWatcherAI completion
3. **Analysis results** are transformed into glyphs and constellation snapshots
4. **Dashboard data** is updated and committed to the repository
5. **Notifications** are sent for success/failure status

## Error Handling

All scripts include comprehensive error handling:
- Input validation and sanitization
- Graceful degradation on partial failures
- Detailed logging with configurable verbosity
- Data integrity verification
- Recovery mechanisms for common issues

## Testing

Run the test suite to validate functionality:

```bash
# Run all Codex processor tests
python -m pytest tests/test_codex_processors.py -v

# Run specific test categories
python -m pytest tests/test_codex_processors.py::TestGlyphEmissionProcessor -v
python -m pytest tests/test_codex_processors.py::TestConstellationSnapshotGenerator -v
python -m pytest tests/test_codex_processors.py::TestIntegration -v
```

## Configuration

Scripts can be configured via command-line arguments:

- `--output-dir`: Directory containing MirrorWatcherAI analysis files (default: `artifacts`)
- `--data-dir`: Directory for Codex data files (default: `data`)
- `--verbose`: Enable verbose logging
- `--file`: Process specific analysis file
- `--validate`: Validate data integrity (snapshot generator only)

## Security

- All data files include cryptographic signatures for integrity verification
- Sensitive operations are logged for audit trails
- Input validation prevents injection attacks
- File permissions are properly managed

## Performance

- Scripts are optimized for processing large datasets
- Memory-efficient algorithms for relationship calculations
- Configurable retention policies to manage file sizes
- Incremental processing to avoid unnecessary work

## Monitoring

The workflow provides comprehensive monitoring:
- Processing status and metrics
- Data integrity validation results
- Performance timing information
- Error reporting and alerting
- Artifact retention and cleanup