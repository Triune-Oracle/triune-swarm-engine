# MirrorWatcherAI API Documentation

> **Complete API reference for the MirrorWatcherAI automation system.**

## 📋 Overview

MirrorWatcherAI provides both programmatic Python APIs and RESTful interfaces for integration with the Triune Oracle ecosystem. This documentation covers all available APIs, data structures, and integration patterns.

## 🐍 Python API

### Core Classes

#### `TriuneAnalyzer`

The main analysis engine for repository monitoring and ecosystem health assessment.

```python
from src.mirror_watcher_ai.analyzer import TriuneAnalyzer

# Initialize analyzer
analyzer = TriuneAnalyzer(config_path="config/mirror_watcher/default.json")

# Load configuration
config = analyzer.load_config()

# Validate setup
is_valid = await analyzer.validate()

# Analyze repositories
results = await analyzer.analyze_repositories([
    "Triune-Oracle/triune-swarm-engine",
    "Triune-Oracle/Legio-Cognito"
])
```

**Methods:**

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `load_config()` | `None` | `Dict[str, Any]` | Load configuration from file or defaults |
| `validate()` | `None` | `bool` | Validate analyzer setup and connectivity |
| `analyze_repositories(repos)` | `List[str]` | `Dict[str, Any]` | Analyze list of repositories |

#### `ShadowScrollsAttestation`

External attestation system for immutable witnessing.

```python
from src.mirror_watcher_ai.shadowscrolls import ShadowScrollsAttestation

# Initialize attestation
shadowscrolls = ShadowScrollsAttestation()

# Validate setup
is_valid = await shadowscrolls.validate()

# Create attestation
attestation = await shadowscrolls.create_attestation(analysis_results)

# Verify attestation
verification = await shadowscrolls.verify_attestation(attestation)

# Retrieve attestation
retrieved = await shadowscrolls.retrieve_attestation(attestation_id)
```

**Methods:**

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `validate()` | `None` | `bool` | Validate ShadowScrolls connectivity |
| `create_attestation(data)` | `Dict[str, Any]` | `Dict[str, Any]` | Create attestation for data |
| `verify_attestation(attestation)` | `Dict[str, Any]` | `Dict[str, Any]` | Verify attestation integrity |
| `retrieve_attestation(id)` | `str` | `Optional[Dict[str, Any]]` | Retrieve attestation by ID |

#### `MirrorLineage`

Audit trail system with delta-based change tracking.

```python
from src.mirror_watcher_ai.lineage import MirrorLineage

# Initialize lineage
lineage = MirrorLineage()

# Record execution
lineage_record = await lineage.record_execution(analysis_results, attestation)

# Get history
history = await lineage.get_lineage_history(limit=10)

# Get deltas for execution
deltas = await lineage.get_deltas_for_execution(execution_id)
```

**Methods:**

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `record_execution(results, attestation)` | `Dict[str, Any], Dict[str, Any]` | `Dict[str, Any]` | Record execution with deltas |
| `get_lineage_history(limit)` | `Optional[int]` | `List[Dict[str, Any]]` | Get execution history |
| `get_deltas_for_execution(id)` | `str` | `Optional[Dict[str, Any]]` | Get delta info for execution |

#### `LegioCognitoArchival`

Integration with Legio-Cognito scroll archival system.

```python
from src.mirror_watcher_ai.legio_integration import LegioCognitoArchival

# Initialize archival
legio = LegioCognitoArchival()

# Archive results
archive_result = await legio.archive_results(analysis_results, attestation, lineage_record)

# Retrieve scroll
scroll = await legio.retrieve_scroll(archive_id)

# Search scrolls
results = await legio.search_scrolls("ecosystem analysis", tags=["mirror_watcher"])
```

**Methods:**

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `archive_results(results, attestation, lineage)` | `Dict, Dict, Dict` | `Dict[str, Any]` | Archive complete result set |
| `retrieve_scroll(id)` | `str` | `Optional[Dict[str, Any]]` | Retrieve archived scroll |
| `search_scrolls(query, tags)` | `str, Optional[List[str]]` | `List[Dict[str, Any]]` | Search archived scrolls |

#### `TriuneMonitor`

Integration with TtriumvirateMonitor-Mobile system.

```python
from src.mirror_watcher_ai.triune_monitor import TriuneMonitor

# Initialize monitor
monitor = TriuneMonitor()

# Update status
monitor_result = await monitor.update_status(analysis_results, archive_result)

# Send alert
alert_result = await monitor.send_alert("workflow_failure", "Analysis failed", "high")

# Get current status
status = await monitor.get_current_status()
```

**Methods:**

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `update_status(results, archive)` | `Dict[str, Any], Dict[str, Any]` | `Dict[str, Any]` | Update system status |
| `send_alert(type, message, priority)` | `str, str, str` | `Dict[str, Any]` | Send alert notification |
| `get_current_status()` | `None` | `Optional[Dict[str, Any]]` | Get current status |

## 🔌 CLI API

### Command Line Interface

The CLI provides direct access to all MirrorWatcherAI functionality.

```bash
# Show help
python3 -m src.mirror_watcher_ai.cli --help

# Validate setup
python3 -m src.mirror_watcher_ai.cli --validate

# Run analysis
python3 -m src.mirror_watcher_ai.cli --analyze

# Use custom config
python3 -m src.mirror_watcher_ai.cli --analyze --config custom.json

# Enable debug mode
python3 -m src.mirror_watcher_ai.cli --analyze --debug

# Save output to file
python3 -m src.mirror_watcher_ai.cli --analyze --output results.json
```

**Options:**

| Option | Description | Required | Default |
|--------|-------------|----------|---------|
| `--analyze` | Run complete analysis | No | - |
| `--validate` | Validate setup | No | - |
| `--config CONFIG` | Configuration file path | No | default.json |
| `--output OUTPUT` | Output file path | No | stdout |
| `--debug` | Enable debug logging | No | False |
| `--version` | Show version | No | - |
| `--help` | Show help | No | - |

## 📊 Data Structures

### Analysis Results

```json
{
  "timestamp": "2025-08-18T19:00:00Z",
  "repositories": {
    "Triune-Oracle/triune-swarm-engine": {
      "status": "success",
      "name": "triune-swarm-engine",
      "description": "Core swarm automation engine",
      "language": "Python",
      "languages": {"Python": 12345, "JavaScript": 5678},
      "size": 1024,
      "stars": 42,
      "forks": 7,
      "issues": 3,
      "commits": 156,
      "workflows": 2,
      "triune_compliance": {
        "score": 85.5,
        "status": "compliant",
        "checks": {
          "has_documentation": true,
          "has_automation": true,
          "triune_integration": true
        }
      }
    }
  },
  "ecosystem_health": {
    "total_repositories": 4,
    "analyzed_successfully": 4,
    "analysis_success_rate": 100.0,
    "average_compliance_score": 82.3,
    "active_repositories": 4,
    "ecosystem_status": "healthy"
  },
  "integration_status": {
    "integration_counts": {
      "shadowscrolls_integration": 2,
      "legio_integration": 1,
      "triumvirate_integration": 4,
      "automation_integration": 3
    },
    "integration_coverage": {
      "shadowscrolls_integration": 50.0,
      "legio_integration": 25.0,
      "triumvirate_integration": 100.0,
      "automation_integration": 75.0
    },
    "status": "partial"
  },
  "recommendations": [
    {
      "type": "integration",
      "priority": "medium",
      "message": "Add ShadowScrolls support to remaining repositories"
    }
  ]
}
```

### ShadowScrolls Attestation

```json
{
  "scroll_id": "#MirrorWatcher-abc123def456",
  "timestamp": "2025-08-18T19:00:00Z",
  "system": "MirrorWatcherAI Automation",
  "operation": "Triune Ecosystem Analysis",
  "data_hash": "sha256:1234567890abcdef...",
  "metadata": {
    "repositories_analyzed": 4,
    "successful_analyses": 4,
    "ecosystem_health": {
      "average_compliance_score": 82.3,
      "ecosystem_status": "healthy"
    },
    "version": "1.0.0"
  },
  "attestation": {
    "witness": "ShadowScrolls External Attestation",
    "integrity": {
      "hash_verified": true,
      "structure_valid": true,
      "timestamp_valid": true,
      "checksum": "abcd1234"
    },
    "completeness": {
      "all_required_present": true,
      "missing_fields": [],
      "completeness_score": 100
    },
    "authenticity": true
  },
  "submission": {
    "status": "submitted",
    "response": {"id": "scroll_123"},
    "url": "https://api.shadowscrolls.com/v1/scrolls"
  }
}
```

### MirrorLineage Record

```json
{
  "execution_id": "uuid-1234-5678-9abc-def123456789",
  "timestamp": "2025-08-18T19:00:00Z",
  "version": "1.0.0",
  "operation": "mirror_watcher_analysis",
  "previous_hash": "sha256:previous...",
  "current_hash": "sha256:current...",
  "attestation_reference": {
    "scroll_id": "#MirrorWatcher-abc123def456",
    "attestation_hash": "sha256:attestation...",
    "timestamp": "2025-08-18T19:00:00Z"
  },
  "deltas": {
    "type": "delta_execution",
    "repository_changes": [
      {
        "repository": "Triune-Oracle/triune-swarm-engine",
        "changes": {
          "has_changes": true,
          "field_changes": [
            {
              "field": "stars",
              "previous": 41,
              "current": 42,
              "change_type": "increase"
            }
          ],
          "metric_changes": {
            "community_score": {
              "previous": 55,
              "current": 57,
              "delta": 2
            }
          }
        }
      }
    ],
    "new_repositories": [],
    "removed_repositories": [],
    "execution_metadata": {
      "duration": 300,
      "change_summary": "1 repositories modified, 0 added, 0 removed"
    }
  },
  "metadata": {
    "repositories_count": 4,
    "successful_analyses": 4,
    "ecosystem_health_score": 82.3,
    "changes_detected": 1
  },
  "integrity": {
    "chain_validated": true,
    "hash_chain": "sha256:chain...",
    "signatures": {
      "analysis_signature": "sig1234",
      "attestation_signature": "sig5678",
      "combined_signature": "sig9abc"
    }
  }
}
```

### Legio-Cognito Archive

```json
{
  "scroll_metadata": {
    "type": "MirrorWatcherAI_Results",
    "version": "1.0.0",
    "created_at": "2025-08-18T19:00:00Z",
    "archive_id": "mirror_watcher_20250818_190000_abc12345",
    "classification": "ecosystem_analysis",
    "retention": "permanent",
    "access_level": "triune_internal"
  },
  "content": {
    "analysis_results": {},
    "shadowscrolls_attestation": {},
    "lineage_record": {},
    "execution_summary": {
      "execution_timestamp": "2025-08-18T19:00:00Z",
      "repositories_analyzed": 4,
      "successful_analyses": 4,
      "ecosystem_health_score": 82.3,
      "recommendations_count": 2,
      "archive_classification": "routine"
    }
  },
  "integrity": {
    "content_hash": "sha256:content...",
    "package_hash": "sha256:package...",
    "verification": {
      "attestation_verified": true,
      "lineage_verified": true,
      "analysis_verified": true
    }
  },
  "legio_metadata": {
    "scroll_classification": "standard",
    "indexing_tags": [
      "mirror_watcher",
      "ecosystem_analysis",
      "triune_oracle",
      "swarm_engine",
      "health_healthy"
    ],
    "search_keywords": [
      "ecosystem", "analysis", "repositories", 
      "health", "compliance", "python", "javascript"
    ],
    "related_scrolls": []
  }
}
```

### Triune Monitor Status

```json
{
  "system": "MirrorWatcherAI",
  "timestamp": "2025-08-18T19:00:00Z",
  "status": {
    "level": "success",
    "health_score": 82.3,
    "ecosystem_status": "healthy",
    "message": "✅ Ecosystem healthy - 4 repositories analyzed, compliance at 82.3%"
  },
  "metrics": {
    "repositories_analyzed": 4,
    "successful_analyses": 4,
    "failed_analyses": 0,
    "recommendations_count": 2,
    "critical_recommendations": 0,
    "analysis_success_rate": 100.0,
    "active_repositories": 4
  },
  "integration_status": {
    "shadowscrolls": {
      "enabled": true,
      "status": "operational",
      "last_attestation": "2025-08-18T19:00:00Z"
    },
    "legio_cognito": {
      "enabled": true,
      "status": "operational", 
      "last_archive": "2025-08-18T19:00:00Z"
    },
    "automation": {
      "status": "operational",
      "coverage": 75.0,
      "automated_repositories": 3,
      "total_repositories": 4
    }
  },
  "alerts": [
    {
      "type": "info",
      "message": "System operating normally",
      "action": "No action required"
    }
  ],
  "next_execution": "2025-08-19T06:00:00Z",
  "dashboard_data": {
    "ecosystem_overview": {
      "total_repositories": 4,
      "health_score": 82.3,
      "active_repositories": 4,
      "status": "healthy"
    },
    "repository_summary": [
      {
        "name": "triune-swarm-engine",
        "language": "Python",
        "stars": 42,
        "compliance_score": 85.5,
        "last_updated": "2025-08-18T15:30:00Z"
      }
    ],
    "language_distribution": [
      {"language": "Python", "usage": 12345},
      {"language": "JavaScript", "usage": 5678}
    ],
    "recent_recommendations": [],
    "trends": {
      "health_trend": "stable",
      "repository_growth": "stable", 
      "automation_trend": "improving",
      "compliance_trend": "stable"
    }
  }
}
```

## 🔧 Shell Script APIs

### Setup Script

```bash
./scripts/mirror_watcher/setup.sh
```

**Functions:**
- Environment validation
- Dependency installation
- Directory structure creation
- Configuration verification
- Installation testing

### Deploy Keys Management

```bash
# Setup deploy keys for all repositories
./scripts/mirror_watcher/deploy_keys.sh setup

# Generate new SSH key
./scripts/mirror_watcher/deploy_keys.sh generate my_key

# Add deploy key to repository
./scripts/mirror_watcher/deploy_keys.sh add Triune-Oracle/repo ~/.ssh/key

# List deploy keys
./scripts/mirror_watcher/deploy_keys.sh list Triune-Oracle/repo

# Verify access
./scripts/mirror_watcher/deploy_keys.sh verify Triune-Oracle/repo ~/.ssh/key

# Rotate all keys
./scripts/mirror_watcher/deploy_keys.sh rotate
```

### Legio-Cognito Archive

```bash
# Archive results
./scripts/mirror_watcher/legio_archive.sh archive results.json

# List archives
./scripts/mirror_watcher/legio_archive.sh list

# Retrieve archive
./scripts/mirror_watcher/legio_archive.sh retrieve archive_id

# Verify integrity
./scripts/mirror_watcher/legio_archive.sh verify archive.json

# Cleanup old archives
./scripts/mirror_watcher/legio_archive.sh cleanup 30
```

### Triune Monitor Sync

```bash
# Sync status
./scripts/mirror_watcher/monitor_sync.sh sync results.json

# Send alert
./scripts/mirror_watcher/monitor_sync.sh alert type "message" priority

# Show current status
./scripts/mirror_watcher/monitor_sync.sh status

# Show history
./scripts/mirror_watcher/monitor_sync.sh history 10

# Cleanup old status files
./scripts/mirror_watcher/monitor_sync.sh cleanup 30
```

## 🚀 GitHub Actions API

### Workflow Triggers

```yaml
# Scheduled execution
on:
  schedule:
    - cron: '0 6 * * *'  # Daily at 06:00 UTC

# Manual trigger
on:
  workflow_dispatch:
    inputs:
      debug:
        description: 'Enable debug logging'
        type: boolean
      config_override:
        description: 'Custom configuration file'
        type: string
```

### Workflow Outputs

- **Artifacts**: `mirror-watcher-results-{run_number}`
- **Retention**: 90 days
- **Contents**: Results JSON, lineage records, local storage

## 🔒 Authentication & Authorization

### Required Permissions

| Service | Permission | Scope |
|---------|------------|-------|
| GitHub API | `repo`, `workflow`, `read:org` | Repository access |
| ShadowScrolls | `attestation:write` | Create attestations |
| Legio-Cognito | `scroll:write`, `archive:write` | Archive scrolls |
| Triune Monitor | `status:write`, `alert:write` | Update status |

### Security Best Practices

- Use GitHub repository secrets for API keys
- Rotate tokens every 90 days
- Use minimum required permissions
- Enable audit logging
- Monitor API usage

## 📈 Error Handling

### API Error Responses

```json
{
  "status": "failed",
  "error": "Detailed error message",
  "timestamp": "2025-08-18T19:00:00Z",
  "context": {
    "operation": "analysis",
    "repository": "Triune-Oracle/repo",
    "step": "github_api_call"
  }
}
```

### Common Error Codes

| Code | Description | Action |
|------|-------------|---------|
| `AUTH_FAILED` | Authentication failed | Check API key |
| `RATE_LIMITED` | Rate limit exceeded | Wait and retry |
| `NETWORK_ERROR` | Network connectivity issue | Check connection |
| `VALIDATION_ERROR` | Input validation failed | Check input format |
| `SERVICE_UNAVAILABLE` | External service down | Use local fallback |

---

**📋 Complete API documentation for seamless integration with MirrorWatcherAI**