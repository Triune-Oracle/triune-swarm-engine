# 📚 MirrorWatcherAI API Reference

## Overview

MirrorWatcherAI provides a comprehensive API for repository analysis, attestation, and ecosystem integration. This reference covers all available endpoints, classes, and methods.

## Table of Contents

- [CLI Interface](#cli-interface)
- [Core Classes](#core-classes)
- [Analysis API](#analysis-api)
- [ShadowScrolls API](#shadowscrolls-api)
- [Lineage API](#lineage-api)
- [Integration API](#integration-api)
- [Configuration API](#configuration-api)
- [Error Handling](#error-handling)
- [Examples](#examples)

## CLI Interface

### Main Commands

```bash
# Execute full analysis workflow
python -m src.mirror_watcher_ai.cli analyze [OPTIONS]

# Execute repository scanning
python -m src.mirror_watcher_ai.cli scan [OPTIONS]

# Create ShadowScrolls attestation
python -m src.mirror_watcher_ai.cli attest [OPTIONS]

# Synchronize Triune ecosystem
python -m src.mirror_watcher_ai.cli sync [OPTIONS]

# Perform system health check
python -m src.mirror_watcher_ai.cli health
```

### Command Options

#### `analyze` Command

```bash
python -m src.mirror_watcher_ai.cli analyze \
    --config CONFIG_FILE \
    --output OUTPUT_FILE
```

**Parameters:**
- `--config`: Path to configuration file (JSON)
- `--output`: Output file path for results

**Returns:** Comprehensive analysis results in JSON format

#### `scan` Command

```bash
python -m src.mirror_watcher_ai.cli scan \
    --repositories REPO1 REPO2 ... \
    --output OUTPUT_FILE
```

**Parameters:**
- `--repositories`: List of specific repositories to scan
- `--output`: Output file path for results

**Returns:** Repository scan results in JSON format

#### `attest` Command

```bash
python -m src.mirror_watcher_ai.cli attest \
    --data DATA_FILE \
    --output OUTPUT_FILE
```

**Parameters:**
- `--data`: JSON file with data to attest (required)
- `--output`: Output file path for attestation

**Returns:** ShadowScrolls attestation with verification data

#### `sync` Command

```bash
python -m src.mirror_watcher_ai.cli sync \
    --force
```

**Parameters:**
- `--force`: Force synchronization even if no new data

**Returns:** Ecosystem synchronization results

## Core Classes

### MirrorWatcherCLI

Main CLI interface class for async execution.

```python
class MirrorWatcherCLI:
    def __init__(self):
        """Initialize CLI with all components."""
        
    async def execute_full_analysis(self, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute complete mirror analysis workflow."""
        
    async def execute_repository_scan(self, repositories: Optional[List[str]] = None) -> Dict[str, Any]:
        """Execute targeted repository scanning."""
        
    async def create_shadowscrolls_report(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create standalone ShadowScrolls attestation report."""
        
    async def sync_triune_ecosystem(self, force: bool = False) -> Dict[str, Any]:
        """Synchronize with all Triune ecosystem services."""
        
    async def health_check(self) -> Dict[str, Any]:
        """Perform comprehensive health check."""
```

### TriuneAnalyzer

Core analysis engine for repository analysis.

```python
class TriuneAnalyzer:
    def __init__(self):
        """Initialize analyzer with GitHub API configuration."""
        
    async def analyze_all_repositories(self, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Analyze all Triune repositories comprehensively."""
        
    async def analyze_specific_repositories(self, repositories: List[str]) -> Dict[str, Any]:
        """Analyze specific repositories."""
        
    async def health_check(self) -> Dict[str, Any]:
        """Perform analyzer health check."""
```

### ShadowScrollsIntegration

External attestation and immutable logging integration.

```python
class ShadowScrollsIntegration:
    def __init__(self):
        """Initialize ShadowScrolls integration."""
        
    async def create_attestation(self, execution_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create comprehensive attestation scroll."""
        
    async def verify_attestation(self, attestation_file: str) -> Dict[str, Any]:
        """Verify the integrity of an existing attestation."""
        
    async def get_attestation_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get history of attestations."""
        
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check of ShadowScrolls integration."""
```

### MirrorLineageLogger

Immutable logging system with cryptographic verification.

```python
class MirrorLineageLogger:
    def __init__(self):
        """Initialize lineage logging system."""
        
    async def start_session(self, execution_id: str, execution_type: str = "analysis") -> Dict[str, Any]:
        """Start a new lineage tracking session."""
        
    async def log_phase(self, phase_name: str, phase_data: Dict[str, Any]) -> Dict[str, Any]:
        """Log completion of an execution phase."""
        
    async def finalize_session(self, final_report: Dict[str, Any]) -> Dict[str, Any]:
        """Finalize lineage session with comprehensive summary."""
        
    async def verify_lineage_integrity(self, session_id: str) -> Dict[str, Any]:
        """Verify the integrity of a lineage session."""
        
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check of lineage system."""
```

### TriuneEcosystemConnector

Integration with the complete Triune Oracle ecosystem.

```python
class TriuneEcosystemConnector:
    def __init__(self):
        """Initialize ecosystem connector."""
        
    async def sync_all_systems(self, analysis_results: Dict[str, Any], attestation: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Synchronize data with all Triune ecosystem services."""
        
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check of Triune ecosystem connections."""
```

## Analysis API

### Repository Analysis

#### analyze_all_repositories()

Analyzes all configured Triune repositories with comprehensive metrics.

**Parameters:**
```python
config: Optional[Dict[str, Any]] = None
```

**Configuration Options:**
```json
{
  "analysis_depth": "comprehensive",
  "security_scanning": {
    "enabled": true,
    "severity_threshold": "medium"
  },
  "performance_metrics": {
    "enabled": true,
    "collect_timing_data": true
  }
}
```

**Returns:**
```json
{
  "analysis_id": "full_20250818_060000",
  "timestamp": "2025-08-18T06:00:00Z",
  "repositories": {
    "triune-swarm-engine": {
      "repository": "triune-swarm-engine",
      "status": "completed",
      "repository_info": {
        "name": "triune-swarm-engine",
        "language": "Python",
        "size": 15000,
        "stargazers_count": 42
      },
      "commits_analysis": {
        "total_commits_analyzed": 100,
        "unique_authors": 3,
        "recent_activity": {
          "last_commit": "2025-08-18T20:00:00Z"
        }
      },
      "code_analysis": {
        "languages": {
          "Python": 45678,
          "JavaScript": 12345
        },
        "language_percentages": {
          "Python": 78.7,
          "JavaScript": 21.3
        }
      },
      "security_scan": {
        "security_advisories": 0,
        "security_score": 95
      },
      "performance_metrics": {
        "repository_size_kb": 15000,
        "clone_performance": {
          "estimated_clone_time_seconds": 15.0
        }
      },
      "health_score": 87
    }
  },
  "summary": {
    "total_repositories": 5,
    "successful_analyses": 5,
    "average_health_score": 82.4
  },
  "security_assessment": {
    "total_security_advisories": 1,
    "overall_security_status": "good"
  },
  "execution_time_seconds": 45.2
}
```

#### analyze_specific_repositories()

Analyzes specific repositories by name.

**Parameters:**
```python
repositories: List[str]  # List of repository names
```

**Example:**
```python
repositories = ["triune-swarm-engine", "legio-cognito"]
result = await analyzer.analyze_specific_repositories(repositories)
```

### Health Score Calculation

The health score is calculated based on multiple factors:

```python
def calculate_health_score(repo_info, commits_analysis, code_analysis, security_scan, performance_metrics, dependency_analysis):
    """
    Calculate repository health score (0-100).
    
    Factors:
    - Open issues count (weight: 10%)
    - Security score (weight: 30%)
    - Recent activity (weight: 25%)
    - Code quality indicators (weight: 20%)
    - Documentation presence (weight: 10%)
    - Community engagement (weight: 5%)
    """
    score = 100
    
    # Issue management
    open_issues = repo_info.get("open_issues_count", 0)
    if open_issues > 10:
        score -= 10
    
    # Security assessment
    security_score = security_scan.get("security_score", 100)
    if security_score < 80:
        score -= 15
    
    # Activity level
    has_recent_activity = commits_analysis.get("recent_activity", {}).get("last_commit")
    if not has_recent_activity:
        score -= 20
    
    # Positive indicators
    if security_scan.get("security_files_present", {}).get("SECURITY.md"):
        score += 5
    
    return max(0, min(100, score))
```

## ShadowScrolls API

### Attestation Creation

#### create_attestation()

Creates cryptographically verified attestation for analysis data.

**Parameters:**
```python
execution_id: str          # Unique execution identifier
data: Dict[str, Any]       # Analysis data to attest
```

**Returns:**
```json
{
  "scroll_id": "#001 – Mirror Analysis analysis_20250818_060000",
  "timestamp": "2025-08-18T06:00:00Z",
  "verification_hash": "sha256:a1b2c3d4...",
  "external_status": "success",
  "local_storage": ".shadowscrolls/attestations/analysis_20250818_060000.json",
  "attestation_summary": {
    "repositories_attested": 5,
    "verification_level": "cryptographic",
    "witness_count": 2
  }
}
```

### Verification Process

The attestation includes multiple verification layers:

1. **Data Integrity**: SHA-256 hash of canonical data representation
2. **Merkle Tree**: Hierarchical verification of repository data
3. **Lineage Chain**: Links to previous attestations
4. **External Witnesses**: GitHub Actions context and system environment
5. **Cryptographic Signature**: HMAC-SHA256 signature

#### Attestation Structure

```json
{
  "scroll_metadata": {
    "scroll_id": "#001 – Mirror Analysis analysis_20250818_060000",
    "timestamp": "2025-08-18T06:00:00Z",
    "system": "MirrorWatcherAI",
    "version": "1.0.0"
  },
  "verification": {
    "data_hash": "sha256:...",
    "algorithm": "SHA-256",
    "merkle_root": "sha256:...",
    "data_size_bytes": 12345
  },
  "lineage": {
    "execution_id": "analysis_20250818_060000",
    "chain_position": 42,
    "previous_attestations": [...],
    "lineage_hash": "sha256:...",
    "generation": "MirrorLineage-Δ"
  },
  "external_witnesses": [
    {
      "type": "github_actions",
      "execution_context": {
        "run_id": "123456789",
        "workflow": "🔍 MirrorWatcherAI Automation",
        "ref": "refs/heads/main"
      }
    }
  ],
  "signature": {
    "hash": "sha256:...",
    "signature": "hmac_sha256:...",
    "algorithm": "HMAC-SHA256",
    "timestamp": "2025-08-18T06:00:00Z"
  }
}
```

## Lineage API

### Session Management

#### start_session()

Initiates a new lineage tracking session.

**Parameters:**
```python
execution_id: str          # Unique execution identifier
execution_type: str        # Type of execution ("analysis", "scan", "sync")
```

**Returns:**
```json
{
  "session_id": "analysis_20250818_060000",
  "start_time": "2025-08-18T06:00:00Z",
  "execution_type": "analysis",
  "lineage_version": "MirrorLineage-Δ 1.0.0",
  "initial_state": {
    "timestamp": "2025-08-18T06:00:00Z",
    "system_info": {...},
    "environment": {...}
  }
}
```

#### log_phase()

Logs completion of an execution phase with integrity verification.

**Parameters:**
```python
phase_name: str           # Phase identifier
phase_data: Dict[str, Any] # Phase execution data
```

**Returns:**
```json
{
  "session_id": "analysis_20250818_060000",
  "phase_name": "repository_analysis",
  "start_time": "2025-08-18T06:00:00Z",
  "end_time": "2025-08-18T06:02:30Z",
  "duration_seconds": 150.0,
  "data_hash": "sha256:...",
  "verification": {
    "algorithm": "SHA-256",
    "integrity_verified": true
  }
}
```

### Database Schema

The lineage system uses SQLite with the following schema:

```sql
-- Sessions table
CREATE TABLE sessions (
    id TEXT PRIMARY KEY,
    start_time TEXT NOT NULL,
    end_time TEXT,
    status TEXT NOT NULL DEFAULT 'active',
    execution_type TEXT,
    metadata_json TEXT,
    verification_hash TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Phases table  
CREATE TABLE phases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    phase_name TEXT NOT NULL,
    start_time TEXT NOT NULL,
    end_time TEXT,
    status TEXT NOT NULL DEFAULT 'active',
    data_json TEXT,
    data_hash TEXT,
    error_message TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES sessions (id)
);

-- Events table
CREATE TABLE events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    phase_id INTEGER,
    event_type TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    message TEXT,
    data_json TEXT,
    severity TEXT NOT NULL DEFAULT 'info',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES sessions (id),
    FOREIGN KEY (phase_id) REFERENCES phases (id)
);
```

## Integration API

### Ecosystem Synchronization

#### sync_all_systems()

Synchronizes data with all Triune ecosystem services in parallel.

**Parameters:**
```python
analysis_results: Dict[str, Any]                    # Analysis results to sync
attestation: Optional[Dict[str, Any]] = None        # Optional attestation data
```

**Returns:**
```json
{
  "sync_id": "sync_20250818_060300",
  "timestamp": "2025-08-18T06:03:00Z",
  "systems": {
    "legio_cognito": {
      "status": "success",
      "scroll_id": "local_scroll_20250818_060300",
      "archive_file": ".shadowscrolls/legio_archive/sync_20250818_060300.json",
      "preservation_level": "local"
    },
    "triumvirate_monitor": {
      "status": "success",
      "dashboard_file": ".shadowscrolls/dashboard/current_status.json",
      "html_file": ".shadowscrolls/dashboard/dashboard.html",
      "alerts_generated": 1
    },
    "swarm_engine": {
      "status": "success",
      "files_updated": ["agent_state.json", "swarm_memory_log.json"],
      "integration_mode": "python_compatible"
    },
    "shell_automation": {
      "status": "success",
      "env_file": ".triune_sync_env",
      "infrastructure_utilization": "10.1%"
    }
  },
  "summary": {
    "successful_syncs": 4,
    "total_syncs": 4,
    "success_rate": 1.0,
    "overall_status": "success"
  },
  "execution_time_seconds": 5.2
}
```

### Service-Specific APIs

#### Legio-Cognito Integration

```python
async def sync_legio_cognito(data: Dict[str, Any]) -> Dict[str, Any]:
    """Archive analysis results to Legio-Cognito scroll system."""
    
    # Creates permanent archival scroll with:
    # - Immutable storage
    # - Search indexing
    # - Version control
    # - Metadata extraction
```

#### Triumvirate Monitor Integration

```python
async def sync_triumvirate_monitor(data: Dict[str, Any]) -> Dict[str, Any]:
    """Update Triumvirate Monitor dashboard with real-time metrics."""
    
    # Provides:
    # - Real-time dashboard updates
    # - Mobile alert notifications
    # - Performance metrics
    # - Status indicators
```

#### Swarm Engine Integration

```python
async def sync_swarm_engine(data: Dict[str, Any]) -> Dict[str, Any]:
    """Native Python integration with Swarm Engine."""
    
    # Features:
    # - 76.3% Python compatibility
    # - Shared memory updates
    # - Module synchronization
    # - Event streaming
```

## Configuration API

### Configuration Structure

```json
{
  "version": "1.0.0",
  "system_name": "MirrorWatcherAI",
  "execution_schedule": {
    "daily_run_time": "06:00",
    "timezone": "UTC",
    "enabled": true
  },
  "analysis_configuration": {
    "default_repositories": [...],
    "security_scanning": {...},
    "performance_metrics": {...}
  },
  "triune_integration": {
    "enabled": true,
    "systems": {...}
  }
}
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `REPO_SYNC_TOKEN` | GitHub Personal Access Token | Required |
| `SHADOWSCROLLS_ENDPOINT` | ShadowScrolls API endpoint | Required |
| `SHADOWSCROLLS_API_KEY` | ShadowScrolls API key | Required |
| `MIRROR_WATCHER_LOG_FILE` | Log file path | `mirror_watcher_ai.log` |
| `MIRROR_WATCHER_DEBUG` | Enable debug mode | `false` |

## Error Handling

### Exception Hierarchy

```python
class MirrorWatcherError(Exception):
    """Base exception for MirrorWatcher errors."""
    pass

class AnalysisError(MirrorWatcherError):
    """Errors during repository analysis."""
    pass

class AttestationError(MirrorWatcherError):
    """Errors during attestation creation."""
    pass

class IntegrationError(MirrorWatcherError):
    """Errors during ecosystem integration."""
    pass

class LineageError(MirrorWatcherError):
    """Errors in lineage tracking."""
    pass
```

### Error Response Format

```json
{
  "error": {
    "type": "AnalysisError",
    "message": "GitHub API rate limit exceeded",
    "code": "RATE_LIMIT_EXCEEDED",
    "timestamp": "2025-08-18T06:00:00Z",
    "context": {
      "repository": "triune-swarm-engine",
      "api_endpoint": "https://api.github.com/repos/...",
      "retry_after": 3600
    }
  }
}
```

### Retry Logic

```python
class RetryConfig:
    max_attempts: int = 3
    base_delay: float = 1.0
    exponential_backoff: bool = True
    max_delay: float = 30.0
    
async def with_retry(operation, config: RetryConfig):
    """Execute operation with retry logic."""
    for attempt in range(config.max_attempts):
        try:
            return await operation()
        except Exception as e:
            if attempt == config.max_attempts - 1:
                raise
            
            delay = config.base_delay * (2 ** attempt) if config.exponential_backoff else config.base_delay
            delay = min(delay, config.max_delay)
            await asyncio.sleep(delay)
```

## Examples

### Basic Analysis

```python
import asyncio
from src.mirror_watcher_ai import TriuneAnalyzer

async def basic_analysis():
    analyzer = TriuneAnalyzer()
    
    async with analyzer:
        # Analyze all repositories
        results = await analyzer.analyze_all_repositories()
        
        print(f"Analyzed {results['summary']['total_repositories']} repositories")
        print(f"Average health score: {results['summary']['average_health_score']}")
        
        return results

# Run analysis
results = asyncio.run(basic_analysis())
```

### Complete Workflow

```python
import asyncio
from src.mirror_watcher_ai import MirrorWatcherCLI

async def complete_workflow():
    cli = MirrorWatcherCLI()
    
    # Execute full analysis workflow
    analysis_results = await cli.execute_full_analysis()
    
    # Create attestation
    attestation = await cli.create_shadowscrolls_report(analysis_results)
    
    # Sync ecosystem
    sync_results = await cli.sync_triune_ecosystem()
    
    # Health check
    health_status = await cli.health_check()
    
    return {
        "analysis": analysis_results,
        "attestation": attestation,
        "sync": sync_results,
        "health": health_status
    }

# Run complete workflow
workflow_results = asyncio.run(complete_workflow())
```

### Custom Configuration

```python
async def custom_analysis():
    config = {
        "analysis_configuration": {
            "security_scanning": {
                "enabled": True,
                "severity_threshold": "high"
            },
            "performance_metrics": {
                "enabled": True,
                "detailed_timing": True
            }
        }
    }
    
    cli = MirrorWatcherCLI()
    results = await cli.execute_full_analysis(config)
    
    return results
```

### Error Handling Example

```python
import asyncio
from src.mirror_watcher_ai import MirrorWatcherCLI, AnalysisError

async def robust_analysis():
    cli = MirrorWatcherCLI()
    
    try:
        results = await cli.execute_full_analysis()
        return {"status": "success", "results": results}
        
    except AnalysisError as e:
        print(f"Analysis failed: {e}")
        return {"status": "analysis_failed", "error": str(e)}
        
    except Exception as e:
        print(f"Unexpected error: {e}")
        return {"status": "error", "error": str(e)}

# Robust execution
result = asyncio.run(robust_analysis())
```

## Rate Limits & Performance

### GitHub API Limits

- **Authenticated requests**: 5,000 per hour
- **Search API**: 30 requests per minute
- **Repository content**: 1,000 requests per hour

### Performance Benchmarks

| Operation | Typical Duration | Resource Usage |
|-----------|------------------|----------------|
| Full Analysis (5 repos) | 45-60 seconds | 200MB RAM |
| Single Repository Scan | 8-12 seconds | 50MB RAM |
| Attestation Creation | 2-3 seconds | 10MB RAM |
| Ecosystem Sync | 5-8 seconds | 30MB RAM |

### Optimization Guidelines

1. **Parallel Processing**: Use `asyncio.gather()` for concurrent operations
2. **Connection Pooling**: Reuse HTTP connections via `aiohttp.ClientSession`
3. **Caching**: Cache GitHub API responses for 30 minutes
4. **Rate Limiting**: Respect API limits with exponential backoff
5. **Memory Management**: Stream large responses instead of loading into memory

This API reference provides comprehensive documentation for all MirrorWatcherAI functionality, enabling developers to integrate and extend the system effectively.