# MirrorWatcherAI Deployment Guide

## Overview

MirrorWatcherAI is a complete automation system designed for comprehensive repository monitoring and analysis within the Triune Oracle ecosystem. This guide covers the deployment and configuration process for achieving zero-manual-intervention operation.

## Prerequisites

### System Requirements
- **Python**: 3.9 or higher
- **Git**: Latest version
- **Network**: Internet access for GitHub API and ShadowScrolls
- **Storage**: Minimum 1GB for analysis results and lineage data

### GitHub Repository Requirements
- **Secrets Configuration**: Required for automated operation
- **Actions Enabled**: GitHub Actions must be available
- **Permissions**: Repository admin access for secrets configuration

## Deployment Process

### Step 1: Environment Setup

1. **Clone the repository** (if not already done):
   ```bash
   git clone https://github.com/Triune-Oracle/triune-swarm-engine.git
   cd triune-swarm-engine
   ```

2. **Run the automated setup script**:
   ```bash
   chmod +x scripts/setup_mirror_watcher.sh
   ./scripts/setup_mirror_watcher.sh
   ```

   The setup script will:
   - Validate Python installation
   - Install required dependencies
   - Create directory structure
   - Validate configuration files
   - Test module imports
   - Initialize the lineage system

### Step 2: GitHub Secrets Configuration

Configure the following secrets in your GitHub repository settings:

#### Required Secrets

| Secret Name | Description | Format |
|-------------|-------------|---------|
| `REPO_SYNC_TOKEN` | GitHub Personal Access Token | `ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx` |
| `SHADOWSCROLLS_ENDPOINT` | ShadowScrolls API endpoint | `https://api.shadowscrolls.triune-oracle.com/v1` |
| `SHADOWSCROLLS_API_KEY` | ShadowScrolls authentication key | `ss_live_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx` |

#### Optional Secrets (Ecosystem Integration)

| Secret Name | Description | Default Behavior |
|-------------|-------------|------------------|
| `LEGIO_COGNITO_API_KEY` | Legio-Cognito authentication | Mock integration |
| `TRIUMVIRATE_MONITOR_API_KEY` | Triumvirate Monitor authentication | Mock integration |

#### GitHub Personal Access Token Setup

1. Go to GitHub Settings → Developer settings → Personal access tokens
2. Generate a new token with the following scopes:
   - `repo` (Full control of private repositories)
   - `workflow` (Update GitHub Action workflows)
   - `read:org` (Read org and team membership)

### Step 3: Configuration Customization

#### Analysis Configuration

Edit `config/mirror_watcher_config.json` to customize analysis parameters:

```json
{
  "analysis": {
    "depth": "comprehensive",
    "include_dependencies": true,
    "security_scan": true,
    "performance_metrics": true,
    "timeout_seconds": 300
  },
  "targets": [
    "Triune-Oracle/triune-swarm-engine",
    "Triune-Oracle/your-other-repo"
  ]
}
```

#### Endpoint Configuration

Edit `config/triune_endpoints.json` for ecosystem integration:

```json
{
  "legio_cognito": "https://api.legio-cognito.triune-oracle.com/v1",
  "triumvirate_monitor": "https://api.triumvirate-monitor.triune-oracle.com/v1",
  "shadowscrolls": "https://api.shadowscrolls.triune-oracle.com/v1"
}
```

### Step 4: Workflow Activation

The GitHub Actions workflow is automatically configured for:
- **Daily execution** at 06:00 UTC
- **Manual execution** via workflow dispatch
- **Error handling** with automatic issue creation
- **Artifact retention** for 90 days

#### Manual Workflow Execution

1. Go to the Actions tab in your GitHub repository
2. Select "MirrorWatcherAI Automation"
3. Click "Run workflow"
4. Optionally specify custom targets or configuration

### Step 5: Verification

#### Health Check

Run a health check to verify all components:

```bash
python3 -m src.mirror_watcher_ai.cli --help
```

#### Manual Analysis Test

Execute a manual analysis to test the system:

```bash
python3 -m src.mirror_watcher_ai.cli analyze Triune-Oracle/triune-swarm-engine --output ./test_results
```

#### Service Health Check

Check external service connectivity:

```bash
python3 scripts/triune_sync.py health
```

## Operational Procedures

### Daily Automated Operation

Once deployed, the system operates automatically:

1. **06:00 UTC**: Workflow triggers
2. **Analysis Phase**: Comprehensive repository analysis
3. **Attestation Phase**: ShadowScrolls external witnessing
4. **Integration Phase**: Triune ecosystem synchronization
5. **Archival Phase**: Results storage and lineage update

### Monitoring and Alerts

#### Success Indicators
- ✅ Workflow completes without errors
- ✅ Analysis artifacts are generated
- ✅ ShadowScrolls attestation is successful
- ✅ No failure issues are created

#### Failure Handling
- ❌ Automatic GitHub issue creation
- ❌ Detailed error logs in workflow
- ❌ Artifact preservation for debugging
- ❌ Retry mechanisms for transient failures

### Manual Intervention Scenarios

#### Common Issues and Solutions

1. **Authentication Failures**
   - Verify GitHub token validity
   - Check ShadowScrolls API key
   - Rotate keys if necessary

2. **Network Connectivity Issues**
   - Check endpoint configurations
   - Verify firewall settings
   - Test external service health

3. **Analysis Failures**
   - Review target repository list
   - Check repository permissions
   - Validate configuration syntax

#### Emergency Procedures

If automated operation fails:

1. **Check the latest workflow run** in GitHub Actions
2. **Download artifacts** for detailed analysis
3. **Run manual diagnosis**:
   ```bash
   python3 -m src.mirror_watcher_ai.cli daily --config ./config/mirror_watcher_config.json
   ```
4. **Review logs** in `.lineage/` and `results/` directories

### Maintenance Tasks

#### Key Rotation (Recommended: 90 days)

Use the deploy keys manager:

```bash
python3 scripts/deploy_keys_manager.py check-rotation --max-age-days 90
python3 scripts/deploy_keys_manager.py rotate <key_name>
```

#### Configuration Updates

1. Update configuration files in `config/`
2. Test changes manually before next automated run
3. Monitor subsequent workflow executions

#### Scaling Considerations

For high-volume analysis:
- Increase workflow timeout (default: 60 minutes)
- Adjust analysis depth in configuration
- Consider repository prioritization

## Integration Details

### ShadowScrolls Integration

- **Purpose**: External attestation and immutable logging
- **Data Flow**: Analysis results → Hash calculation → Attestation submission
- **Verification**: Cryptographic proof of analysis integrity

### Triune Ecosystem Integration

#### Legio-Cognito
- **Purpose**: Automatic scroll archival
- **Data**: Analysis summaries and insights
- **Retention**: Permanent historical record

#### Triumvirate Monitor
- **Purpose**: Real-time dashboard updates
- **Data**: Status metrics and quality scores
- **Access**: Mobile and web interfaces

#### Swarm Engine
- **Purpose**: Native Python integration
- **Data**: Complete analysis results
- **Storage**: Local file system integration

## Security Considerations

### Data Protection
- All secrets are encrypted in GitHub
- Local lineage data uses cryptographic hashing
- API communications use HTTPS/TLS

### Access Control
- Repository permissions control access
- API keys have service-specific scopes
- Audit logs track all operations

### Compliance
- Complete audit trails in lineage system
- Immutable attestation records
- Tamper-proof logging mechanisms

## Troubleshooting

### Common Error Messages

| Error | Cause | Solution |
|-------|-------|----------|
| "Module import failed" | Missing dependencies | Run setup script |
| "Authentication failed" | Invalid API keys | Check GitHub secrets |
| "Network timeout" | Connectivity issues | Verify endpoints |
| "Analysis failed" | Repository access | Check permissions |

### Debug Commands

```bash
# Check module imports
python3 -c "from src.mirror_watcher_ai import *; print('OK')"

# Test configuration
python3 -m json.tool config/mirror_watcher_config.json

# Verify lineage
ls -la .lineage/

# Check results
ls -la results/
```

### Log Locations

- **Workflow logs**: GitHub Actions interface
- **Local logs**: `mirror_watcher.log`
- **Lineage logs**: `.lineage/rotation_log.json`
- **Swarm logs**: `swarm_memory_log.json`

## Support and Maintenance

### Regular Health Checks

Run monthly:
```bash
python3 scripts/triune_sync.py health
python3 scripts/deploy_keys_manager.py list
```

### Performance Monitoring

Track metrics:
- Analysis execution time
- Success/failure rates
- Resource utilization
- Network latency

### Version Updates

To update MirrorWatcherAI:
1. Pull latest repository changes
2. Run setup script again
3. Test with manual execution
4. Monitor automated runs

---

**🎯 Deployment Target**: First automated run at 06:00 UTC following deployment completion

**📊 Success Criteria**: Zero manual intervention required after initial setup

**🛡️ Security**: Enterprise-grade with complete audit capabilities