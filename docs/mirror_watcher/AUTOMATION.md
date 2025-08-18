# MirrorWatcherAI Automation Guide

> **Complete guide for setting up, configuring, and managing the MirrorWatcherAI automation system.**

## 🚀 Quick Start

### 1. One-Command Setup

```bash
# Run the automated setup script
./scripts/mirror_watcher/setup.sh
```

This will:
- ✅ Check Python installation and dependencies
- ✅ Install required packages
- ✅ Create directory structure
- ✅ Validate configuration
- ✅ Test the installation

### 2. Configure Secrets

```bash
# Interactive secret configuration
./scripts/setup-secrets.sh --interactive
```

Required secrets:
- `REPO_SYNC_TOKEN`: GitHub Personal Access Token
- `SHADOWSCROLLS_ENDPOINT`: ShadowScrolls API endpoint
- `SHADOWSCROLLS_API_KEY`: ShadowScrolls API key

Optional (with local fallback):
- `LEGIO_COGNITO_ENDPOINT`: Legio-Cognito API endpoint
- `LEGIO_COGNITO_API_KEY`: Legio-Cognito API key
- `TRIUNE_MONITOR_ENDPOINT`: Triune Monitor API endpoint
- `TRIUNE_MONITOR_API_KEY`: Triune Monitor API key

### 3. Validate Setup

```bash
# Validate complete installation
python3 -m src.mirror_watcher_ai.cli --validate
```

### 4. First Execution

```bash
# Run your first analysis
python3 -m src.mirror_watcher_ai.cli --analyze --output first_run.json
```

## ⚙️ Detailed Setup

### Prerequisites

- **Python 3.8+** with pip
- **Git** with GitHub access
- **curl** for API testing
- **jq** for JSON processing (optional but recommended)

### Step-by-Step Installation

#### 1. Environment Preparation

```bash
# Navigate to project root
cd /path/to/triune-swarm-engine

# Verify Python version
python3 --version  # Should be 3.8 or higher

# Install dependencies
pip install -r requirements.txt

# Install MirrorWatcherAI dependencies
pip install aiohttp>=3.8.0
```

#### 2. Directory Structure Creation

```bash
# Create required directories
mkdir -p .shadowscrolls/reports
mkdir -p .mirror_lineage/deltas
mkdir -p .legio_cognito/archive
mkdir -p .triune_monitor

# Set appropriate permissions
chmod 755 .shadowscrolls .mirror_lineage .legio_cognito .triune_monitor
```

#### 3. Configuration Setup

```bash
# Verify configuration files exist
ls -la config/mirror_watcher/
# Should show: default.json, repositories.json, attestation.json, legio_config.json

# Verify shell scripts exist and are executable
ls -la scripts/mirror_watcher/
# Should show executable scripts: setup.sh, deploy_keys.sh, legio_archive.sh, monitor_sync.sh
```

#### 4. GitHub Actions Workflow

```bash
# Verify workflow file exists
ls -la .github/workflows/mirror-watcher-daily.yml

# The workflow will run automatically daily at 06:00 UTC
# It can also be triggered manually from the GitHub Actions tab
```

## 🔐 Secret Management

### GitHub Repository Secrets

Configure these secrets in your GitHub repository settings:

1. Go to `Settings` → `Secrets and variables` → `Actions`
2. Click `New repository secret`
3. Add each required secret:

| Secret Name | Description | Example |
|-------------|-------------|---------|
| `REPO_SYNC_TOKEN` | GitHub Personal Access Token | `ghp_xxxxxxxxxxxx` |
| `SHADOWSCROLLS_ENDPOINT` | ShadowScrolls API URL | `https://api.shadowscrolls.com/v1` |
| `SHADOWSCROLLS_API_KEY` | ShadowScrolls API key | `ss_live_xxxxxxxxx` |
| `LEGIO_COGNITO_ENDPOINT` | Legio-Cognito API URL | `https://api.legio-cognito.com/v1` |
| `LEGIO_COGNITO_API_KEY` | Legio-Cognito API key | `lc_xxxxxxxxx` |
| `TRIUNE_MONITOR_ENDPOINT` | Triune Monitor API URL | `https://api.triune-monitor.com/v1` |
| `TRIUNE_MONITOR_API_KEY` | Triune Monitor API key | `tm_xxxxxxxxx` |

### Local Development Secrets

For local development, create a `.env.local` file:

```bash
# Mirror Watcher Automation Configuration
REPO_SYNC_TOKEN=ghp_your_actual_token_here
SHADOWSCROLLS_ENDPOINT=https://api.shadowscrolls.your-domain.com/v1
SHADOWSCROLLS_API_KEY=ss_live_your_actual_key_here

# Optional integrations
LEGIO_COGNITO_ENDPOINT=https://api.legio-cognito.your-domain.com/v1
LEGIO_COGNITO_API_KEY=lc_your_actual_key_here
TRIUNE_MONITOR_ENDPOINT=https://api.triune-monitor.your-domain.com/v1
TRIUNE_MONITOR_API_KEY=tm_your_actual_key_here

# Development settings
NODE_ENV=development
# DEBUG=triune:*  # Uncomment for debug logging
```

### GitHub Personal Access Token Setup

1. Go to GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Click "Generate new token (classic)"
3. Configure:
   - **Name**: `Triune Swarm Engine Sync`
   - **Expiration**: `90 days` (recommended)
   - **Scopes**: 
     - ✅ `repo` (Full control of private repositories)
     - ✅ `workflow` (Update GitHub Action workflows)
     - ✅ `read:org` (Read org and team membership)

## 🕐 Automation Configuration

### Daily Schedule

The system runs automatically every day at **06:00 UTC**:

```yaml
# .github/workflows/mirror-watcher-daily.yml
on:
  schedule:
    - cron: '0 6 * * *'  # Daily at 06:00 UTC
```

### Manual Execution

You can trigger the workflow manually:

1. Go to GitHub Actions tab
2. Select "MirrorWatcherAI Daily Automation"
3. Click "Run workflow"
4. Optionally enable debug logging

### Execution Timeline

- **Duration**: ~10-15 minutes
- **Next Run**: Automatically calculated (tomorrow 06:00 UTC)
- **Timeout**: 30 minutes maximum
- **Retry**: Automatic retry on transient failures

## 📊 Monitoring & Alerts

### Health Monitoring

The system monitors several health indicators:

#### Ecosystem Health Score (0-100%)
- **90-100%**: ✅ Excellent - All repositories compliant
- **70-89%**: ℹ️ Good - Minor improvements needed
- **50-69%**: ⚠️ Warning - Attention required
- **<50%**: 🚨 Critical - Immediate action needed

#### Repository Compliance Checks
- ✅ README documentation
- ✅ License file
- ✅ .gitignore configuration
- ✅ GitHub Actions workflows
- ✅ Triune-specific patterns
- ✅ Integration markers

#### Integration Status
- **ShadowScrolls**: External attestation status
- **Legio-Cognito**: Archival system status
- **Triune Monitor**: Mobile monitoring status
- **Automation**: Workflow execution status

### Alert Configuration

Alerts are automatically generated based on thresholds:

```json
{
  "alert_thresholds": {
    "health_score_critical": 50,
    "health_score_warning": 70,
    "max_failed_repos": 2,
    "max_critical_recommendations": 2
  }
}
```

### Mobile Dashboard

Access real-time status via TtriumvirateMonitor-Mobile:
- Ecosystem overview
- Repository compliance scores
- Recent recommendations
- Integration status
- Historical trends

## 🔧 Configuration Management

### Repository Configuration

Edit `config/mirror_watcher/repositories.json` to modify monitoring:

```json
{
  "repositories": [
    {
      "name": "Triune-Oracle/triune-swarm-engine",
      "priority": "critical",
      "thresholds": {
        "minimum_compliance_score": 80,
        "required_workflows": 2,
        "max_open_issues": 10
      }
    }
  ]
}
```

### Analysis Configuration

Modify `config/mirror_watcher/default.json` for analysis settings:

```json
{
  "analysis": {
    "depth": "comprehensive",
    "include_metrics": true,
    "parallel_processing": true,
    "timeout": 300,
    "retry_attempts": 3
  }
}
```

### Integration Configuration

Configure external services in respective config files:

- `attestation.json`: ShadowScrolls configuration
- `legio_config.json`: Legio-Cognito archival settings

## 🛠️ Maintenance Tasks

### Regular Maintenance

#### Weekly Tasks
```bash
# Check system health
python3 -m src.mirror_watcher_ai.cli --validate

# Review recent executions
./scripts/mirror_watcher/monitor_sync.sh history 7

# Check local storage usage
du -sh .shadowscrolls .mirror_lineage .legio_cognito .triune_monitor
```

#### Monthly Tasks
```bash
# Clean up old artifacts (90+ days)
./scripts/mirror_watcher/legio_archive.sh cleanup 90
./scripts/mirror_watcher/monitor_sync.sh cleanup 90

# Review and rotate API keys (every 90 days)
# Update GitHub repository secrets as needed

# Review repository list and thresholds
# Edit config/mirror_watcher/repositories.json if needed
```

### Troubleshooting

#### Common Issues

**1. Validation Errors**
```bash
# Check environment variables
python3 -m src.mirror_watcher_ai.cli --validate

# Test specific APIs
curl -H "Authorization: Bearer $SHADOWSCROLLS_API_KEY" $SHADOWSCROLLS_ENDPOINT/health
```

**2. GitHub Actions Failures**
- Check repository secrets configuration
- Verify GitHub token permissions
- Review workflow logs in Actions tab
- Check for rate limiting

**3. Integration Failures**
All integrations have local fallback storage:
- ShadowScrolls → `.shadowscrolls/reports/`
- Legio-Cognito → `.legio_cognito/archive/`
- Triune Monitor → `.triune_monitor/`

**4. Permission Errors**
```bash
# Fix file permissions
chmod 755 .shadowscrolls .mirror_lineage .legio_cognito .triune_monitor
chmod +x scripts/mirror_watcher/*.sh
```

#### Debug Mode

Enable detailed logging for troubleshooting:

```bash
# CLI debug mode
python3 -m src.mirror_watcher_ai.cli --analyze --debug

# Workflow debug mode
# Trigger workflow manually with debug input enabled
```

#### Log Analysis

```bash
# View recent logs
ls -la .shadowscrolls/reports/
ls -la .mirror_lineage/deltas/
ls -la .legio_cognito/archive/

# Check GitHub Actions logs
# Go to Actions tab → Select workflow run → View logs
```

## 📈 Performance Optimization

### Resource Usage

Current performance characteristics:
- **Memory**: ~100MB peak usage
- **Network**: ~50MB per execution
- **Storage**: ~10MB per daily execution
- **CPU**: Low (API-based analysis)

### Optimization Settings

#### Parallel Processing
```json
{
  "analysis": {
    "parallel_processing": true,
    "max_concurrent_requests": 10
  }
}
```

#### Rate Limiting
```json
{
  "github": {
    "rate_limit_aware": true,
    "rate_limit_delay": 1
  }
}
```

#### Timeouts
```json
{
  "timeouts": {
    "github_api": 30,
    "shadowscrolls": 30,
    "legio_cognito": 60,
    "triune_monitor": 30
  }
}
```

## 🔄 Backup & Recovery

### Data Backup

Important data is automatically backed up:

1. **Local Fallback Storage**: All integrations store data locally
2. **GitHub Artifacts**: 90-day retention of execution results
3. **Legio-Cognito**: Permanent archival of all results
4. **MirrorLineage**: Complete audit trail with integrity chains

### Recovery Procedures

#### Service Recovery
```bash
# If external services are restored, data can be backfilled
# Example: Re-submit local ShadowScrolls attestations
for file in .shadowscrolls/reports/*.json; do
  echo "Resubmitting: $file"
  # Custom resubmission logic here
done
```

#### Configuration Recovery
```bash
# Restore from version control
git checkout HEAD -- config/mirror_watcher/

# Regenerate secrets
./scripts/setup-secrets.sh --interactive
```

## 📊 Reporting & Analytics

### Built-in Reports

The system generates comprehensive reports:

1. **Execution Summary**: Overall health and metrics
2. **Repository Analysis**: Individual repository compliance
3. **Integration Status**: External service connectivity
4. **Trend Analysis**: Historical performance data
5. **Recommendations**: Actionable improvement suggestions

### Custom Reports

Extract data for custom analysis:

```bash
# Export recent results
python3 -m src.mirror_watcher_ai.cli --analyze --output analysis.json

# Extract specific metrics with jq
jq '.analysis.ecosystem_health' analysis.json
jq '.analysis.repositories | keys' analysis.json
jq '.analysis.recommendations' analysis.json
```

### Historical Analysis

```bash
# Review lineage history
ls -la .mirror_lineage/deltas/

# Analyze trends
./scripts/mirror_watcher/monitor_sync.sh history 30
```

## 🚀 Advanced Configuration

### Custom Repository Patterns

Add custom compliance patterns:

```json
{
  "compliance": {
    "custom_patterns": {
      "has_security_policy": "required",
      "has_code_of_conduct": "recommended",
      "has_contributing_guide": "recommended"
    }
  }
}
```

### Extended Monitoring

Add additional repositories:

```json
{
  "repositories": [
    "Triune-Oracle/new-repository",
    "External-Org/monitored-repo"
  ]
}
```

### Custom Alerts

Configure custom alert thresholds:

```json
{
  "custom_alerts": {
    "low_activity_threshold": 30,
    "high_issue_count": 20,
    "security_alerts": true
  }
}
```

## 🔮 Future Enhancements

### Planned Features

- [ ] **Multi-organization support**: Monitor multiple GitHub organizations
- [ ] **Custom compliance rules**: User-defined compliance patterns
- [ ] **Advanced analytics**: Machine learning-based trend analysis
- [ ] **Real-time notifications**: Instant alert delivery
- [ ] **Webhook integration**: Real-time event processing
- [ ] **Performance metrics**: Advanced performance monitoring

### Extension Points

The system is designed for easy extension:

1. **New Analysis Modules**: Add to `src/mirror_watcher_ai/`
2. **Custom Integrations**: Extend integration capabilities
3. **Additional Workflows**: Create specialized automation
4. **Custom Dashboards**: Build custom monitoring interfaces

## 📞 Support

### Getting Help

1. **Documentation**: Review this guide and API documentation
2. **Logs**: Check GitHub Actions logs and local artifacts
3. **Validation**: Run diagnostic commands
4. **Community**: Contact Triune Oracle team

### Best Practices

1. **Regular monitoring**: Check dashboard weekly
2. **Prompt action**: Address critical alerts quickly
3. **Keep updated**: Rotate API keys every 90 days
4. **Review recommendations**: Implement suggested improvements
5. **Monitor trends**: Watch for degrading performance

---

**🤖 Complete automation guide for zero-intervention operation of the MirrorWatcherAI system**

*Next execution: Tomorrow at 06:00 UTC*