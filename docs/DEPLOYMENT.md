# MirrorWatcherAI Deployment Guide

## Overview

The MirrorWatcherAI Complete Automation System provides zero manual intervention analysis for the Triune Oracle ecosystem. This guide covers deployment, configuration, and operational procedures.

## Quick Start

### 1. Initial Setup

```bash
# Clone the repository (if not already done)
git clone https://github.com/Triune-Oracle/triune-swarm-engine.git
cd triune-swarm-engine

# Run the setup script
./scripts/setup_mirror_watcher.sh

# Configure secrets
./scripts/setup-secrets.sh --interactive

# Validate the setup
python scripts/validate-setup.py
```

### 2. GitHub Actions Configuration

1. **Required Secrets**: Configure these in your GitHub repository settings:
   - `REPO_SYNC_TOKEN`: GitHub Personal Access Token with repo, workflow, read:org scopes
   - `SHADOWSCROLLS_ENDPOINT`: ShadowScrolls API endpoint URL
   - `SHADOWSCROLLS_API_KEY`: ShadowScrolls authentication key
   - `LEGIO_COGNITO_ENDPOINT`: Legio-Cognito archival service endpoint
   - `LEGIO_COGNITO_API_KEY`: Legio-Cognito authentication key
   - `TRIUMVIRATE_MONITOR_ENDPOINT`: Triumvirate Monitor dashboard endpoint
   - `TRIUMVIRATE_MONITOR_API_KEY`: Triumvirate Monitor authentication key

2. **Workflow Activation**: The workflow is automatically scheduled for daily execution at 06:00 UTC.

### 3. Manual Testing

```bash
# Test the CLI interface
python -m src.mirror_watcher_ai.cli --help

# Run analysis on specific repositories
python -m src.mirror_watcher_ai.cli --repositories "https://github.com/Triune-Oracle/triune-swarm-engine" --verbose

# Run automated cycle
python -m src.mirror_watcher_ai.cli --automated --debug
```

## Architecture

### Core Components

1. **MirrorWatcherAI CLI** (`src/mirror_watcher_ai/cli.py`)
   - Async execution engine
   - Error handling and recovery
   - Configuration management

2. **Triune Analyzer** (`src/mirror_watcher_ai/analyzer.py`)
   - Repository analysis engine
   - Code metrics and quality assessment
   - Parallel processing capabilities

3. **ShadowScrolls Integration** (`src/mirror_watcher_ai/shadowscrolls.py`)
   - External attestation and witnessing
   - Cryptographic verification
   - Multi-witness attestation support

4. **MirrorLineage-Δ** (`src/mirror_watcher_ai/lineage.py`)
   - Immutable audit trails
   - Session tracking and verification
   - Cryptographic proof generation

5. **Triune Ecosystem Integration** (`src/mirror_watcher_ai/triune_integration.py`)
   - Legio-Cognito archival
   - Triumvirate Monitor sync
   - Swarm Engine native integration

### Data Flow

```
1. GitHub Actions Trigger (06:00 UTC daily)
   ↓
2. MirrorWatcherAI CLI Initialization
   ↓
3. Swarm Engine Repository Discovery
   ↓
4. Parallel Repository Analysis
   ↓
5. MirrorLineage-Δ Immutable Logging
   ↓
6. ShadowScrolls External Attestation
   ↓
7. Legio-Cognito Archival
   ↓
8. Triumvirate Monitor Dashboard Update
   ↓
9. Artifact Generation and 90-day Retention
```

## Configuration

### Primary Configuration (`config/mirror_watcher_config.json`)

```json
{
  "analyzer": {
    "parallel_analysis": true,
    "max_workers": 4,
    "timeout_seconds": 1800
  },
  "shadowscrolls": {
    "attestation_enabled": true,
    "multi_witness": true,
    "witness_count": 3
  },
  "lineage": {
    "immutable_logging": true,
    "cryptographic_verification": true,
    "retention_days": 90
  }
}
```

### Endpoint Configuration (`config/triune_endpoints.json`)

Defines all Triune ecosystem service endpoints with failover support.

### Swarm Engine Integration (`triune_config.json`)

```json
{
  "mirror_watcher": {
    "enabled": true,
    "target_repositories": [
      "https://github.com/Triune-Oracle/triune-swarm-engine",
      "https://github.com/Triune-Oracle/triune-memory-core"
    ],
    "analysis_schedule": "0 6 * * *",
    "automation_enabled": true
  }
}
```

## Security

### Cryptographic Verification

- **SHA-256** hashing for data integrity
- **HMAC signatures** for attestation authenticity
- **Multi-witness** attestation for enhanced security
- **Immutable logging** with tamper-proof audit trails

### Access Control

- **Bearer token** authentication for all APIs
- **Encrypted secrets** management via GitHub Actions
- **Secure communication** with TLS 1.3
- **Rate limiting** and audit logging

### Secret Management

1. **GitHub Secrets**: Primary storage for API keys and tokens
2. **Environment Isolation**: Development and production separation
3. **Token Rotation**: Automatic rotation capabilities
4. **Audit Trails**: Complete access logging

## Monitoring & Observability

### Real-time Monitoring

- **Triumvirate Monitor**: Mobile dashboard with live updates
- **GitHub Actions**: Workflow status and artifact management
- **ShadowScrolls**: External attestation verification
- **Performance Metrics**: Execution time and resource usage

### Alerting

- **Failure Notifications**: Automatic alerts on analysis failures
- **Performance Thresholds**: Monitoring for degraded performance
- **Security Events**: Alerts for security-related incidents
- **Compliance Monitoring**: Audit trail verification

### Artifacts

- **Analysis Results**: JSON output with comprehensive metrics
- **Attestation Records**: ShadowScrolls verification proofs
- **Audit Logs**: MirrorLineage-Δ immutable records
- **Performance Data**: Execution metrics and timing

## Operational Procedures

### Daily Operations

The system operates with **zero manual intervention**:

1. **06:00 UTC**: Automated GitHub Actions trigger
2. **Analysis Execution**: Comprehensive repository analysis
3. **Attestation**: ShadowScrolls external witnessing
4. **Archival**: Legio-Cognito scroll preservation
5. **Dashboard Update**: Real-time status sync
6. **Artifact Storage**: 90-day retention

### Manual Operations

#### Emergency Analysis

```bash
# Trigger immediate analysis
python -m src.mirror_watcher_ai.cli --automated --debug

# Analyze specific repository
python -m src.mirror_watcher_ai.cli --repositories "repo-url" --output-format json
```

#### Configuration Updates

```bash
# Validate configuration changes
python scripts/validate-setup.py --check-structure

# Test API connectivity
python scripts/validate-setup.py --check-api
```

#### Troubleshooting

```bash
# Check system status
./scripts/setup_mirror_watcher.sh --validate-config

# Review logs
find .shadowscrolls -name "*.json" -type f | head -5

# Verify attestations
python -c "
from src.mirror_watcher_ai.shadowscrolls import ShadowScrollsIntegration
import asyncio
ss = ShadowScrollsIntegration()
print(asyncio.run(ss.list_attestations(limit=5)))
"
```

## Performance Optimization

### Parallel Processing

- **Multi-threaded analysis**: Up to 4 concurrent workers
- **Async I/O**: Non-blocking API calls
- **Resource management**: Memory and CPU optimization
- **Caching**: Intelligent result caching

### Scalability

- **Horizontal scaling**: Support for multiple repositories
- **Load balancing**: Distributed witness nodes
- **Failover**: Automatic backup service utilization
- **Resource limits**: Configurable constraints

## Compliance & Audit

### Immutable Records

- **MirrorLineage-Δ**: Tamper-proof audit trails
- **Cryptographic verification**: SHA-256 integrity checks
- **Session tracking**: Complete operation lineage
- **Long-term retention**: 90-day default with extension options

### External Attestation

- **ShadowScrolls**: Independent witness verification
- **Multi-node consensus**: Distributed attestation
- **Verification proofs**: Cryptographic evidence
- **Public verifiability**: External audit capabilities

### Compliance Standards

- **SOC 2 Type II**: Security and availability controls
- **ISO 27001**: Information security management
- **GDPR**: Data protection compliance
- **Enterprise audit**: Complete audit trail support

## Troubleshooting

### Common Issues

1. **Import Errors**
   ```bash
   pip install --user aiohttp aiosqlite
   ```

2. **Configuration Errors**
   ```bash
   python -m json.tool config/mirror_watcher_config.json
   ```

3. **API Connectivity**
   ```bash
   python scripts/validate-setup.py --check-api --debug
   ```

4. **Permission Issues**
   ```bash
   chmod +x scripts/*.sh
   ```

### Debug Mode

```bash
# Enable comprehensive debugging
python -m src.mirror_watcher_ai.cli --automated --debug

# Check component initialization
python -c "
from src.mirror_watcher_ai import *
print('All modules imported successfully')
"
```

### Support

- **Documentation**: Complete API reference in `docs/`
- **Integration Tests**: Comprehensive test suite
- **Community**: GitHub Discussions and Issues
- **Enterprise**: Direct support via Triune Oracle

---

**Next Steps**: After deployment, review the [Integration Guide](INTEGRATION.md) and [API Documentation](API.md) for advanced configuration options.