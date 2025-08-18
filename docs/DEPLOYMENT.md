# 🚀 MirrorWatcherAI Deployment Guide

## Overview

MirrorWatcherAI is a comprehensive automation system designed for complete cloud-based execution with zero manual intervention. This guide covers the deployment process for production environments.

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                      MirrorWatcherAI System                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐     │
│  │   CLI Module    │  │   Analyzer      │  │ ShadowScrolls   │     │
│  │   (async)       │  │   (GitHub API)  │  │  (Attestation)  │     │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘     │
│                                                                     │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐     │
│  │  Lineage-Δ      │  │ Triune Connector│  │ GitHub Actions  │     │
│  │  (SQLite DB)    │  │ (Ecosystem)     │  │  (Automation)   │     │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘     │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      Triune Ecosystem                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐     │
│  │ Legio-Cognito   │  │ Triumvirate     │  │ Swarm Engine    │     │
│  │ (Archival)      │  │ Monitor         │  │ (Python 76.3%)  │     │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘     │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

## Prerequisites

### Required Software
- Python 3.9+ (3.11 recommended)
- Git
- curl, jq (for setup scripts)
- GitHub CLI (optional, for enhanced security)

### Required Secrets
The following secrets must be configured in GitHub repository settings:

| Secret Name | Description | Format | Required |
|-------------|-------------|---------|----------|
| `REPO_SYNC_TOKEN` | GitHub Personal Access Token | `ghp_...` | ✅ Yes |
| `SHADOWSCROLLS_ENDPOINT` | ShadowScrolls API endpoint | URL | ✅ Yes |
| `SHADOWSCROLLS_API_KEY` | ShadowScrolls API key | `ss_live_...` | ✅ Yes |
| `LEGIO_COGNITO_API_KEY` | Legio-Cognito API key | `lc_...` | ⚠️ Optional |
| `TRIUMVIRATE_MONITOR_API_KEY` | Monitor API key | `tm_...` | ⚠️ Optional |
| `SWARM_ENGINE_API_KEY` | Swarm Engine API key | `se_...` | ⚠️ Optional |

## Quick Deployment

### 1. Automated Setup

```bash
# Run the setup script
./scripts/setup_mirror_watcher.sh

# For production deployment
./scripts/setup_mirror_watcher.sh --force

# For preview (dry run)
./scripts/setup_mirror_watcher.sh --dry-run
```

### 2. Configure Secrets

#### Option A: Using GitHub Web Interface
1. Navigate to repository Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Add each required secret from the table above

#### Option B: Using Deploy Keys Manager
```bash
# Generate API keys
python3 scripts/deploy_keys_manager.py generate-key --prefix ss_live_ --length 32

# Validate existing configuration
python3 scripts/deploy_keys_manager.py validate

# Check key expiration
python3 scripts/deploy_keys_manager.py check-expiration

# Generate comprehensive report
python3 scripts/deploy_keys_manager.py report
```

### 3. Validation

```bash
# Validate complete setup
python3 scripts/validate-setup.py

# Test system health
python3 -m src.mirror_watcher_ai.cli health

# Test CLI functionality
python3 -m src.mirror_watcher_ai.cli --help
```

## Configuration

### Core Configuration

Configuration is managed through JSON files in the `config/` directory:

- **`mirror_watcher_config.json`**: Core system configuration
- **`triune_endpoints.json`**: Ecosystem service endpoints

### Key Configuration Options

```json
{
  "execution_schedule": {
    "daily_run_time": "06:00",
    "timezone": "UTC",
    "enabled": true
  },
  "analysis_configuration": {
    "default_repositories": [
      "triune-swarm-engine",
      "legio-cognito",
      "triumvirate-monitor"
    ],
    "security_scanning": {
      "enabled": true,
      "severity_threshold": "medium"
    }
  },
  "error_handling": {
    "retry_policy": {
      "max_attempts": 3,
      "exponential_backoff": true
    },
    "notification_policy": {
      "critical_errors": true
    }
  }
}
```

## GitHub Actions Deployment

### Workflow Configuration

The automation workflow is configured in `.github/workflows/mirror-watcher-automation.yml`:

- **Schedule**: Daily at 06:00 UTC
- **Manual Triggers**: Available via Actions tab
- **Timeout**: 30 minutes maximum
- **Artifact Retention**: 90 days

### Workflow Steps

1. **Environment Setup**: Python 3.11, dependencies installation
2. **Health Check**: System component validation
3. **Analysis Execution**: Repository analysis and metrics collection
4. **ShadowScrolls Attestation**: Cryptographic verification
5. **Ecosystem Sync**: Integration with Triune services
6. **Reporting**: Comprehensive execution reports
7. **Artifact Upload**: Results preservation

### Manual Execution

```bash
# Trigger via GitHub CLI (if authenticated)
gh workflow run "🔍 MirrorWatcherAI Automation"

# With custom parameters
gh workflow run "🔍 MirrorWatcherAI Automation" \
  -f analysis_type=security_focus \
  -f force_sync=true
```

## Local Development

### Development Setup

```bash
# Clone repository
git clone https://github.com/Triune-Oracle/triune-swarm-engine.git
cd triune-swarm-engine

# Install dependencies
pip install -r requirements.txt

# Run setup
./scripts/setup_mirror_watcher.sh --verbose

# Configure local environment
cp .env.mirror_watcher .env.local
# Edit .env.local with your API keys
```

### Development Commands

```bash
# Run full analysis
python3 -m src.mirror_watcher_ai.cli analyze

# Scan specific repositories
python3 -m src.mirror_watcher_ai.cli scan --repositories triune-swarm-engine

# Create attestation
python3 -m src.mirror_watcher_ai.cli attest --data analysis_results.json

# Sync ecosystem
python3 -m src.mirror_watcher_ai.cli sync

# Health check
python3 -m src.mirror_watcher_ai.cli health
```

### Testing

```bash
# Run integration tests
./scripts/test-integration.sh

# Validate setup
python3 scripts/validate-setup.py --debug

# Test Triune sync
python3 scripts/triune_sync.py health
```

## Monitoring & Observability

### Health Monitoring

The system provides comprehensive health monitoring:

```bash
# System health check
python3 -m src.mirror_watcher_ai.cli health

# Component-specific checks
python3 scripts/validate-setup.py --check-api
python3 scripts/validate-setup.py --check-permissions
```

### Logs & Artifacts

- **Application Logs**: `logs/mirror_watcher.log`
- **Audit Logs**: `logs/keys_audit.log`
- **GitHub Artifacts**: Available in Actions tab (90-day retention)
- **Local Artifacts**: `artifacts/` directory

### Dashboard

Local dashboard available at:
- **HTML Dashboard**: `.shadowscrolls/dashboard/dashboard.html`
- **JSON Status**: `.shadowscrolls/dashboard/current_status.json`

## Security

### Security Features

- **Cryptographic Attestation**: SHA-256 with HMAC signatures
- **Immutable Logging**: Tamper-proof audit trails
- **Encrypted Secrets**: GitHub repository secrets encryption
- **Access Control**: Minimal permission requirements
- **Audit Trails**: Comprehensive logging of all operations

### Security Best Practices

1. **Token Scopes**: Use minimal required scopes
2. **Key Rotation**: Regular API key rotation (60-90 days)
3. **Environment Isolation**: Separate keys for dev/prod
4. **Monitoring**: Enable security alert notifications
5. **Backup**: Maintain secure backup of configurations

## Troubleshooting

### Common Issues

#### 1. Import Errors
```bash
# Install missing dependencies
pip install aiohttp aiosqlite requests

# Verify Python path
python3 -c "import sys; print(sys.path)"
```

#### 2. GitHub API Errors
```bash
# Check token validity
python3 scripts/deploy_keys_manager.py validate --secret REPO_SYNC_TOKEN

# Verify repository access
curl -H "Authorization: token $REPO_SYNC_TOKEN" \
     https://api.github.com/repos/Triune-Oracle/triune-swarm-engine
```

#### 3. Database Issues
```bash
# Reinitialize database
rm -f .shadowscrolls/lineage/mirror_lineage.db
python3 -c "import asyncio; from src.mirror_watcher_ai.lineage import MirrorLineageLogger; asyncio.run(MirrorLineageLogger()._initialize_database())"
```

#### 4. Permission Errors
```bash
# Fix file permissions
chmod +x scripts/*.sh
chmod 644 config/*.json
```

### Debug Mode

Enable debug logging:

```bash
# Set environment variable
export MIRROR_WATCHER_DEBUG=true

# Run with verbose output
python3 -m src.mirror_watcher_ai.cli health --verbose
```

### Support Channels

- **Documentation**: This guide and inline code comments
- **Validation**: `python3 scripts/validate-setup.py`
- **Health Check**: `python3 -m src.mirror_watcher_ai.cli health`
- **Logs**: Check `logs/` directory for detailed error information

## Production Deployment Checklist

### Pre-Deployment

- [ ] All required secrets configured in GitHub
- [ ] Setup script executed successfully
- [ ] Validation passes without errors
- [ ] Health check returns "healthy" status
- [ ] GitHub Actions workflow syntax validated

### Post-Deployment

- [ ] First scheduled run completed successfully (06:00 UTC)
- [ ] Artifacts generated and accessible
- [ ] ShadowScrolls attestation created
- [ ] Triune ecosystem sync completed
- [ ] Monitoring dashboards updated
- [ ] No critical alerts generated

### Maintenance

- [ ] Monitor daily execution logs
- [ ] Review security alerts weekly
- [ ] Rotate API keys quarterly
- [ ] Update dependencies monthly
- [ ] Backup configuration files regularly

## Performance Optimization

### Resource Usage

- **Memory**: ~1GB maximum per execution
- **Storage**: ~100MB for 90 days of artifacts
- **Network**: ~50MB data transfer per execution
- **CPU**: ~5 minutes execution time

### Optimization Tips

1. **Parallel Processing**: Enabled by default for repository analysis
2. **Caching**: 30-minute cache for GitHub API responses
3. **Rate Limiting**: 60 requests/minute to respect API limits
4. **Compression**: Level 6 compression for artifacts
5. **Cleanup**: Automatic cleanup of old data

## Version Information

- **MirrorWatcherAI**: v1.0.0
- **Python Compatibility**: 3.9+
- **GitHub Actions**: ubuntu-latest
- **Dependencies**: See `requirements.txt`

## Next Steps

After successful deployment:

1. **Monitor First Run**: Check execution at 06:00 UTC tomorrow
2. **Review Artifacts**: Verify analysis results and attestations
3. **Configure Alerts**: Set up notification preferences
4. **Documentation**: Review integration guides for ecosystem services
5. **Optimization**: Fine-tune configuration based on initial results

The MirrorWatcherAI system is now ready for production operation with complete automation and zero manual intervention required.