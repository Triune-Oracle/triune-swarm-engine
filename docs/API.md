# MirrorWatcherAI API Reference

## Overview

MirrorWatcherAI provides a comprehensive API for automated repository analysis and ecosystem integration. This document covers all available modules, classes, and functions.

## Core Modules

### CLI Module (`src.mirror_watcher_ai.cli`)

#### Main CLI Class

```python
class MirrorWatcherCLI:
    """Main CLI interface for MirrorWatcherAI automation system."""
    
    async def initialize_components(self, config: Dict[str, Any]) -> None
    async def run_analysis(self, targets: list, output_format: str = 'json') -> Dict[str, Any]
    async def automated_daily_run(self, config_path: str) -> Dict[str, Any]
```

#### CLI Commands

- `daily` - Run automated daily analysis
- `analyze <repositories>` - Run manual analysis on specified repositories  
- `version` - Show version information

#### Usage Examples

```bash
# Daily automated run
python3 -m src.mirror_watcher_ai.cli daily

# Manual analysis
python3 -m src.mirror_watcher_ai.cli analyze owner/repo --output ./results

# Version check
python3 -m src.mirror_watcher_ai.cli version
```

### Analyzer Module (`src.mirror_watcher_ai.analyzer`)

#### TriuneAnalyzer Class

```python
class TriuneAnalyzer:
    """Comprehensive analyzer for Triune ecosystem repositories."""
    
    def __init__(self, config: Dict[str, Any])
    
    async def analyze_repositories(self, repositories: List[str]) -> Dict[str, Any]
    async def analyze_single_repository(self, repository: str) -> Dict[str, Any]
    async def get_repository_info(self, owner: str, repo: str) -> Dict[str, Any]
    async def analyze_structure(self, repo_path: str) -> Dict[str, Any]
    async def analyze_code_metrics(self, repo_path: str) -> Dict[str, Any]
    async def analyze_dependencies(self, repo_path: str) -> Dict[str, Any]
    async def analyze_security(self, repo_path: str) -> Dict[str, Any]
    async def analyze_performance(self, repo_path: str) -> Dict[str, Any]
    async def analyze_git_metrics(self, repo_path: str) -> Dict[str, Any]
    
    def calculate_quality_score(self, analysis: Dict[str, Any]) -> float
    def generate_recommendations(self, analysis: Dict[str, Any]) -> List[str]
```

#### Configuration Options

```json
{
  "depth": "comprehensive|basic",
  "include_dependencies": true|false,
  "security_scan": true|false,
  "performance_metrics": true|false,
  "timeout_seconds": 300
}
```

#### Analysis Output Structure

```json
{
  "repository": "owner/repo",
  "info": {
    "name": "repo",
    "language": "Python",
    "stars": 100,
    "forks": 25
  },
  "structure": {
    "total_files": 150,
    "total_size_bytes": 1048576,
    "language_composition": {
      "Python": {"files": 50, "percentage": 70.5}
    }
  },
  "code_metrics": {
    "total_lines": 5000,
    "code_lines": 3500,
    "comment_lines": 750,
    "comment_ratio": 15.0
  },
  "security": {
    "security_score": 8.5,
    "potential_issues": [],
    "security_files_present": ["SECURITY.md"]
  },
  "quality_score": 8.2,
  "recommendations": ["Add more tests", "Improve documentation"]
}
```

### ShadowScrolls Module (`src.mirror_watcher_ai.shadowscrolls`)

#### ShadowScrollsClient Class

```python
class ShadowScrollsClient:
    """Client for ShadowScrolls external attestation system."""
    
    def __init__(self, endpoint: Optional[str] = None, api_key: Optional[str] = None)
    
    async def submit_analysis(self, analysis_results: Dict[str, Any], lineage_entry: Dict[str, Any]) -> Dict[str, Any]
    async def verify_attestation(self, attestation_id: str) -> Dict[str, Any]
    async def get_lineage_chain(self, lineage_hash: str) -> Dict[str, Any]
    async def health_check(self) -> Dict[str, Any]
```

#### Environment Variables

- `SHADOWSCROLLS_ENDPOINT` - API endpoint URL
- `SHADOWSCROLLS_API_KEY` - Authentication key

#### Attestation Response

```json
{
  "status": "success",
  "attestation_id": "att_xxxxxxxxxxxx",
  "witness_hash": "abc123...",
  "timestamp": "2025-08-18T06:00:00Z",
  "verification_url": "https://...",
  "submission_hash": "def456..."
}
```

### Lineage Module (`src.mirror_watcher_ai.lineage`)

#### MirrorLineage Class

```python
class MirrorLineage:
    """Immutable lineage tracking system with cryptographic verification."""
    
    def __init__(self, config: Dict[str, Any])
    
    async def create_entry(self, analysis_results: Dict[str, Any], start_time: datetime) -> Dict[str, Any]
    async def verify_entry(self, entry_id: str) -> Dict[str, Any]
    async def get_lineage_chain(self, limit: Optional[int] = None) -> Dict[str, Any]
    async def export_lineage(self, output_path: str, format: str = 'json') -> Dict[str, Any]
```

#### Configuration Options

```json
{
  "encryption": true,
  "hash_algorithm": "sha256|sha512",
  "compression": true,
  "storage_path": "./.lineage"
}
```

#### Lineage Entry Structure

```json
{
  "id": "lineage_20250818_060000_123456",
  "hash": "abc123...",
  "timestamp": "2025-08-18T06:00:00Z",
  "previous_hash": "def456...",
  "verification_hash": "ghi789...",
  "chain_position": 42,
  "status": "created"
}
```

### Triune Integration Module (`src.mirror_watcher_ai.triune_integration`)

#### TriuneIntegrator Class

```python
class TriuneIntegrator:
    """Integration manager for Triune ecosystem services."""
    
    def __init__(self, config: Dict[str, Any])
    
    async def sync_results(self, analysis_results: Dict[str, Any], attestation_result: Dict[str, Any]) -> Dict[str, Any]
    async def health_check(self) -> Dict[str, Any]
```

#### Service Integration

##### Legio-Cognito
- **Purpose**: Automatic scroll archival
- **Endpoint**: `LEGIO_COGNITO_API_KEY` environment variable
- **Data**: Analysis summaries and insights

##### Triumvirate Monitor  
- **Purpose**: Real-time dashboard updates
- **Endpoint**: `TRIUMVIRATE_MONITOR_API_KEY` environment variable
- **Data**: Status metrics and quality scores

##### Swarm Engine
- **Purpose**: Local file integration
- **Location**: `./swarm_data/` directory
- **Data**: Complete analysis results

## Utility Scripts

### Setup Script (`scripts/setup_mirror_watcher.sh`)

Automated deployment and configuration script.

```bash
./scripts/setup_mirror_watcher.sh
```

**Functions:**
- Validates Python installation
- Installs dependencies
- Creates directory structure
- Tests module imports
- Initializes lineage system

### Deploy Keys Manager (`scripts/deploy_keys_manager.py`)

Secure key management with automatic rotation.

```bash
# Store a new key
python3 scripts/deploy_keys_manager.py store my_key --key-value "secret123"

# Retrieve a key
python3 scripts/deploy_keys_manager.py retrieve my_key

# List all keys
python3 scripts/deploy_keys_manager.py list

# Check rotation needs
python3 scripts/deploy_keys_manager.py check-rotation
```

### Triune Sync (`scripts/triune_sync.py`)

Manual ecosystem synchronization.

```bash
# Sync latest analysis
python3 scripts/triune_sync.py sync

# Health check
python3 scripts/triune_sync.py health
```

## Configuration Files

### Main Configuration (`config/mirror_watcher_config.json`)

```json
{
  "analysis": {
    "depth": "comprehensive",
    "include_dependencies": true,
    "security_scan": true,
    "performance_metrics": true,
    "timeout_seconds": 300
  },
  "shadowscrolls": {
    "endpoint": "https://api.shadowscrolls.triune-oracle.com/v1",
    "timeout_seconds": 30,
    "retry_attempts": 3
  },
  "lineage": {
    "encryption": true,
    "hash_algorithm": "sha256",
    "compression": true,
    "storage_path": "./.lineage"
  },
  "triune": {
    "legio_cognito": true,
    "triumvirate_monitor": true,
    "auto_archive": true
  },
  "targets": [
    "Triune-Oracle/triune-swarm-engine",
    "Triune-Oracle/triune-memory-core"
  ],
  "scheduling": {
    "daily_run_time": "06:00",
    "timezone": "UTC"
  }
}
```

### Endpoints Configuration (`config/triune_endpoints.json`)

```json
{
  "legio_cognito": "https://api.legio-cognito.triune-oracle.com/v1",
  "triumvirate_monitor": "https://api.triumvirate-monitor.triune-oracle.com/v1",
  "swarm_engine": "local",
  "shadowscrolls": "https://api.shadowscrolls.triune-oracle.com/v1"
}
```

## GitHub Actions Integration

### Workflow File (`.github/workflows/mirror-watcher-automation.yml`)

**Triggers:**
- Daily at 06:00 UTC (`cron: '0 6 * * *'`)
- Manual execution (`workflow_dispatch`)

**Required Secrets:**
- `REPO_SYNC_TOKEN` - GitHub Personal Access Token
- `SHADOWSCROLLS_ENDPOINT` - ShadowScrolls API endpoint
- `SHADOWSCROLLS_API_KEY` - ShadowScrolls authentication

**Optional Secrets:**
- `LEGIO_COGNITO_API_KEY` - Legio-Cognito authentication
- `TRIUMVIRATE_MONITOR_API_KEY` - Triumvirate Monitor authentication

**Outputs:**
- Analysis artifacts (90-day retention)
- Execution logs
- Status badges
- Automatic issue creation on failure

## Error Handling

### Common Errors

| Error Type | Cause | Solution |
|------------|-------|----------|
| `ModuleNotFoundError` | Missing dependencies | Run `pip install -r requirements_mirror_watcher.txt` |
| `Authentication failed` | Invalid API keys | Check GitHub secrets configuration |
| `Network timeout` | Connectivity issues | Verify endpoint URLs and network access |
| `Analysis failed` | Repository access issues | Check repository permissions and token scopes |

### Logging

**Log Levels:**
- `INFO` - Normal operation
- `WARNING` - Non-critical issues  
- `ERROR` - Operation failures
- `DEBUG` - Detailed debugging info

**Log Locations:**
- Console output
- `mirror_watcher.log` (local execution)
- GitHub Actions logs (automated execution)
- `.lineage/rotation_log.json` (audit trail)

## Performance Considerations

### Resource Usage

- **Memory**: ~100MB for typical analysis
- **Storage**: ~10MB per analysis result
- **Network**: Depends on repository size and count
- **CPU**: Moderate during analysis phase

### Optimization Tips

- Reduce analysis depth for faster execution
- Limit target repository count
- Use compression for lineage storage
- Configure appropriate timeouts

### Scaling

For high-volume analysis:
- Increase GitHub Actions timeout
- Use parallel analysis (already implemented)
- Consider repository prioritization
- Monitor rate limits for external APIs

## Security

### Data Protection

- All secrets encrypted in GitHub
- Local lineage uses cryptographic hashing
- API communications over HTTPS/TLS
- No sensitive data in logs

### Access Control

- Repository permissions control access
- API keys scoped to specific services
- Audit logs for all operations
- Immutable attestation records

### Compliance

- Complete audit trails
- Cryptographic verification
- External attestation
- Tamper-proof logging

---

**For detailed deployment instructions, see [DEPLOYMENT.md](DEPLOYMENT.md)**

**For integration examples, see [INTEGRATION.md](INTEGRATION.md)**