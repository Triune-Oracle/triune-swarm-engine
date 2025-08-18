# 📚 MirrorWatcherAI API Documentation

Complete API reference for the MirrorWatcherAI Complete Automation System.

## Table of Contents

1. [CLI Interface](#cli-interface)
2. [Python API](#python-api)
3. [Configuration API](#configuration-api)
4. [Integration APIs](#integration-apis)
5. [Error Handling](#error-handling)
6. [Examples](#examples)

## CLI Interface

### Main Commands

#### `analyze` - Repository Analysis
Perform comprehensive analysis of Triune repositories.

```bash
python -m src.mirror_watcher_ai.cli analyze [OPTIONS]
```

**Options:**
- `--parallel` - Run analysis in parallel (default: sequential)
- `--deep-scan` - Perform deep repository scanning
- `--attest` - Create ShadowScrolls attestation
- `--sync` - Sync with Triune ecosystem
- `--output PATH` - Output file for results (JSON format)

**Examples:**
```bash
# Standard analysis with attestation
python -m src.mirror_watcher_ai.cli analyze --parallel --attest

# Deep scan with ecosystem sync
python -m src.mirror_watcher_ai.cli analyze --deep-scan --sync --output results.json

# Quick analysis for testing
python -m src.mirror_watcher_ai.cli analyze --output /tmp/test-results.json
```

#### `monitor` - Continuous Monitoring
Start continuous monitoring mode for real-time analysis.

```bash
python -m src.mirror_watcher_ai.cli monitor [OPTIONS]
```

**Options:**
- `--interval SECONDS` - Monitoring interval (default: 300)

**Examples:**
```bash
# Start monitoring with 5-minute intervals
python -m src.mirror_watcher_ai.cli monitor --interval 300

# Fast monitoring for development
python -m src.mirror_watcher_ai.cli monitor --interval 60
```

#### `status` - System Status
Check the health and status of all system components.

```bash
python -m src.mirror_watcher_ai.cli status [OPTIONS]
```

**Options:**
- `--json` - Output status in JSON format

**Examples:**
```bash
# Human-readable status
python -m src.mirror_watcher_ai.cli status

# JSON output for automation
python -m src.mirror_watcher_ai.cli status --json
```

#### `config` - Configuration Management
Manage system configuration settings.

```bash
python -m src.mirror_watcher_ai.cli config [OPTIONS]
```

**Options:**
- `--show` - Display current configuration
- `--set KEY=VALUE` - Set configuration value

**Examples:**
```bash
# Show current configuration
python -m src.mirror_watcher_ai.cli config --show

# Update timeout setting
python -m src.mirror_watcher_ai.cli config --set analyzer.timeout=600

# Enable deep scanning by default
python -m src.mirror_watcher_ai.cli config --set analyzer.enable_deep_scan=true
```

#### `attest` - Manual Attestation
Create ShadowScrolls attestation for specific data.

```bash
python -m src.mirror_watcher_ai.cli attest [OPTIONS]
```

**Options:**
- `--session-id ID` - Session ID for attestation
- `--data-file PATH` - Data file to attest
- `--output PATH` - Output file for attestation

#### `sync` - Ecosystem Synchronization
Manually synchronize with Triune ecosystem components.

```bash
python -m src.mirror_watcher_ai.cli sync [OPTIONS]
```

**Options:**
- `--session-id ID` - Session ID for sync operation
- `--data-file PATH` - Data file to synchronize

### Global Options

- `--debug` - Enable debug output for troubleshooting
- `--config PATH` - Custom configuration file path

## Python API

### Core Classes

#### `TriuneAnalyzer`
Main analysis engine for repository scanning and metrics collection.

```python
from mirror_watcher_ai.analyzer import TriuneAnalyzer

# Initialize analyzer
config = {
    "timeout": 300,
    "concurrent_repos": 3,
    "output_format": "json"
}
analyzer = TriuneAnalyzer(config)

# Perform analysis
repositories = [
    "Triune-Oracle/triune-swarm-engine",
    "Triune-Oracle/legio-cognito"
]

results = await analyzer.analyze_repositories(
    repositories=repositories,
    parallel=True,
    deep_scan=False
)
```

**Methods:**

##### `analyze_repositories(repositories, parallel=True, deep_scan=False)`
Analyze multiple repositories with optional parallel execution.

**Parameters:**
- `repositories` (List[str]): List of repository names in "owner/repo" format
- `parallel` (bool): Enable parallel processing
- `deep_scan` (bool): Perform comprehensive deep scanning

**Returns:**
```python
{
    "session_id": "analysis-20250819-060000",
    "timestamp": "2025-08-19T06:00:00Z",
    "repositories": {
        "triune-swarm-engine": {
            "status": "completed",
            "metadata": {...},
            "analysis": {...},
            "metrics": {...}
        }
    },
    "summary": {
        "total_repositories": 2,
        "successful": 2,
        "failed": 0,
        "total_analysis_time": 45.7
    }
}
```

##### `health_check()`
Perform health check on analyzer components.

**Returns:**
```python
{
    "status": "healthy",
    "github_api": "connected",
    "metrics": {
        "sessions": 5,
        "repositories_analyzed": 15,
        "total_analysis_time": 234.5
    }
}
```

#### `ShadowScrollsAttestation`
External attestation system for cryptographic verification.

```python
from mirror_watcher_ai.shadowscrolls import ShadowScrollsAttestation

# Initialize attestation service
config = {
    "endpoint": "https://api.shadowscrolls.com/v1",
    "api_key": "ss_live_your_key_here",
    "timeout": 30
}
attestation = ShadowScrollsAttestation(config)

# Create attestation
result = await attestation.create_attestation(
    session_id="analysis-session",
    results=analysis_results,
    metadata={"system": "MirrorWatcherAI"}
)
```

**Methods:**

##### `create_attestation(session_id, results, metadata=None)`
Create external attestation for analysis results.

**Parameters:**
- `session_id` (str): Unique session identifier
- `results` (Dict): Analysis results to attest
- `metadata` (Dict, optional): Additional metadata

**Returns:**
```python
{
    "scroll_id": "#001 – MirrorWatcher Analysis",
    "session_id": "analysis-session",
    "verification_hash": "sha256_hash",
    "api_response": {"status": "submitted"},
    "local_storage": "/path/to/attestation.json"
}
```

##### `verify_attestation(attestation_path)`
Verify existing attestation integrity.

**Parameters:**
- `attestation_path` (Path): Path to attestation file

**Returns:**
```python
{
    "overall_status": "valid",
    "checks": {
        "file_integrity": {"status": "valid"},
        "content_hash": {"status": "valid"},
        "signature": {"status": "valid"},
        "timestamp": {"status": "valid"}
    }
}
```

#### `MirrorLineageDelta`
Immutable logging system with cryptographic chaining.

```python
from mirror_watcher_ai.lineage import MirrorLineageDelta

# Initialize lineage system
config = {
    "crypto_enabled": True,
    "signature_algorithm": "ed25519",
    "storage_path": ".shadowscrolls/lineage"
}
lineage = MirrorLineageDelta(config)

# Session management
await lineage.start_session("analysis-session")
await lineage.add_entry(
    session_id="analysis-session",
    entry_type="repository_analysis",
    content={"repository": "triune-swarm-engine", "status": "completed"},
    metadata={"source": "MirrorWatcherAI"}
)
await lineage.finalize_session("analysis-session", final_results)
```

**Methods:**

##### `start_session(session_id, metadata=None)`
Start new lineage tracking session.

##### `add_entry(session_id, entry_type, content, metadata=None)`
Add entry to active session with cryptographic verification.

##### `finalize_session(session_id, final_results=None)`
Finalize session and create immutable record.

##### `verify_session(session_id)`
Verify integrity of complete session chain.

#### `TriuneEcosystemIntegration`
Integration with Triune Oracle ecosystem services.

```python
from mirror_watcher_ai.triune_integration import TriuneEcosystemIntegration

# Initialize integration
config = {
    "legio_cognito_endpoint": "https://legio-cognito.com/api/v1",
    "triumvirate_monitor_endpoint": "https://monitor.com/api",
    "sync_interval": 300
}
integration = TriuneEcosystemIntegration(config)

# Sync results
await integration.sync_results("session-id", analysis_results)
```

**Methods:**

##### `health_check()`
Check health of all ecosystem components.

##### `sync_results(session_id, results)`
Synchronize analysis results with ecosystem services.

##### `sync_status()`
Sync current system status with monitoring dashboard.

## Configuration API

### Configuration Structure

```json
{
  "analyzer": {
    "timeout": 300,
    "concurrent_repos": 3,
    "output_format": "json",
    "retry_attempts": 3
  },
  "shadowscrolls": {
    "timeout": 30,
    "enable_external_attestation": true,
    "local_storage_enabled": true
  },
  "lineage": {
    "crypto_enabled": true,
    "signature_algorithm": "ed25519",
    "storage_path": ".shadowscrolls/lineage"
  },
  "triune": {
    "sync_interval": 300,
    "enable_legio_cognito_sync": true,
    "enable_triumvirate_monitor_sync": true
  },
  "github": {
    "repositories": [
      "Triune-Oracle/triune-swarm-engine"
    ],
    "api_timeout": 30,
    "concurrent_repos": 3
  }
}
```

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `REPO_SYNC_TOKEN` | Yes | GitHub API token with repo, workflow, read:org scopes |
| `SHADOWSCROLLS_ENDPOINT` | No | ShadowScrolls API endpoint URL |
| `SHADOWSCROLLS_API_KEY` | No | ShadowScrolls API authentication key |
| `LEGIO_COGNITO_ENDPOINT` | No | Legio-Cognito API endpoint URL |
| `TRIUMVIRATE_MONITOR_ENDPOINT` | No | Triumvirate Monitor API endpoint URL |
| `TRIUNE_API_KEY` | No | General Triune ecosystem API key |

## Integration APIs

### GitHub Actions Integration

#### Workflow Inputs
```yaml
inputs:
  analysis_mode:
    description: 'Analysis mode'
    required: false
    default: 'standard'
    type: choice
    options: [standard, deep_scan, monitor_only]
  
  create_attestation:
    description: 'Create ShadowScrolls attestation'
    required: false
    default: true
    type: boolean
  
  sync_ecosystem:
    description: 'Sync with Triune ecosystem'
    required: false
    default: true
    type: boolean
```

#### Artifacts
- **Name**: `mirror-watcher-analysis-{run_number}`
- **Contents**: Analysis results, attestations, execution reports
- **Retention**: 90 days
- **Compression**: Level 6

### REST API Endpoints (Ecosystem Integration)

#### ShadowScrolls API
```
POST /attestations
Content-Type: application/json
Authorization: Bearer {api_key}

{
  "scroll": {...},
  "data": {...},
  "verification": {...}
}
```

#### Legio-Cognito API
```
POST /scrolls
Content-Type: application/json
Authorization: Bearer {api_key}

{
  "scroll_type": "mirror_watcher_analysis",
  "session_id": "...",
  "analysis_results": {...}
}
```

#### Triumvirate Monitor API
```
POST /api/updates
Content-Type: application/json
Authorization: Bearer {api_key}

{
  "event_type": "mirror_watcher_update",
  "session_id": "...",
  "status": "completed",
  "summary": {...}
}
```

## Error Handling

### Exception Types

#### `MirrorWatcherError`
Base exception for all MirrorWatcherAI errors.

#### `AnalysisError`
Repository analysis failures.

#### `AttestationError`
ShadowScrolls attestation failures.

#### `IntegrationError`
Triune ecosystem integration failures.

#### `ConfigurationError`
Configuration validation errors.

### Error Response Format

```python
{
    "error": {
        "type": "AnalysisError",
        "message": "Repository analysis failed",
        "details": {
            "repository": "owner/repo",
            "stage": "metadata_fetch",
            "http_status": 404
        },
        "timestamp": "2025-08-19T06:00:00Z",
        "session_id": "analysis-session"
    }
}
```

### Retry Logic

```python
# Exponential backoff configuration
retry_config = {
    "attempts": 3,
    "backoff_strategy": "exponential",
    "base_delay": 30,  # seconds
    "max_delay": 300   # seconds
}
```

## Examples

### Complete Analysis Workflow

```python
import asyncio
from mirror_watcher_ai import (
    TriuneAnalyzer,
    ShadowScrollsAttestation,
    MirrorLineageDelta,
    TriuneEcosystemIntegration
)

async def run_complete_analysis():
    # Initialize components
    analyzer = TriuneAnalyzer(analyzer_config)
    attestation = ShadowScrollsAttestation(shadowscrolls_config)
    lineage = MirrorLineageDelta(lineage_config)
    integration = TriuneEcosystemIntegration(triune_config)
    
    session_id = "manual-analysis-session"
    
    try:
        # Start lineage tracking
        await lineage.start_session(session_id)
        
        # Perform analysis
        results = await analyzer.analyze_repositories(
            repositories=["Triune-Oracle/triune-swarm-engine"],
            parallel=True,
            deep_scan=False
        )
        
        # Create attestation
        attestation_result = await attestation.create_attestation(
            session_id=session_id,
            results=results,
            metadata={"manual": True}
        )
        
        # Sync with ecosystem
        sync_result = await integration.sync_results(session_id, results)
        
        # Finalize lineage
        final_summary = await lineage.finalize_session(session_id, results)
        
        print(f"Analysis completed: {session_id}")
        print(f"Attestation: {attestation_result['scroll_id']}")
        print(f"Sync status: {sync_result['sync_status']}")
        
    except Exception as e:
        print(f"Analysis failed: {e}")
        raise

# Run the analysis
asyncio.run(run_complete_analysis())
```

### Configuration Management

```python
from mirror_watcher_ai.cli import MirrorWatcherCLI

# Initialize CLI
cli = MirrorWatcherCLI()

# Update configuration
cli.config["analyzer"]["timeout"] = 600
cli.config["github"]["concurrent_repos"] = 5

# Save configuration
with open("config/mirror_watcher_config.json", 'w') as f:
    json.dump(cli.config, f, indent=2)
```

### Health Monitoring

```python
async def monitor_system_health():
    components = [
        TriuneAnalyzer(config),
        ShadowScrollsAttestation(config),
        MirrorLineageDelta(config),
        TriuneEcosystemIntegration(config)
    ]
    
    for component in components:
        try:
            health = await component.health_check()
            print(f"{component.__class__.__name__}: {health['status']}")
        except Exception as e:
            print(f"{component.__class__.__name__}: ERROR - {e}")

asyncio.run(monitor_system_health())
```

---

**📚 API Status**: Complete and operational  
**🔗 Integration**: Full ecosystem connectivity  
**🛡️ Security**: Cryptographic verification enabled  
**📊 Monitoring**: Real-time health tracking active