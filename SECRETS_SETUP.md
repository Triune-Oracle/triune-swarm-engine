# 🔐 Secrets Configuration Guide

> **Mirror Watcher Automation Setup**  
> Complete guide for configuring GitHub repository secrets and ShadowScrolls integration

## Overview

The Triune Swarm Engine requires secure configuration of three critical secrets to enable the Mirror Watcher automation system and ShadowScrolls reporting integration. This guide provides comprehensive instructions for both GitHub repository administrators and local development environments.

## Required Secrets

### 1. `REPO_SYNC_TOKEN`
**Purpose**: GitHub Personal Access Token for automated file synchronization  
**Scope**: Repository file operations, workflow dispatch, actions  
**Format**: `ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

### 2. `SHADOWSCROLLS_ENDPOINT`  
**Purpose**: API endpoint for the ShadowScrolls logging and reporting system  
**Format**: `https://shadowscrolls.api.endpoint.com/v1`  
**Example**: `https://api.shadowscrolls.triune-oracle.com/v1`

### 3. `SHADOWSCROLLS_API_KEY`
**Purpose**: Authentication key for ShadowScrolls API access  
**Format**: `ss_live_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`  
**Permissions**: Write access to scroll logs, read access to lineage metadata

## 🏛️ GitHub Repository Secrets Setup

### Step 1: Access Repository Settings

1. Navigate to your repository: `https://github.com/Triune-Oracle/triune-swarm-engine`
2. Click on **Settings** tab
3. In the left sidebar, click **Secrets and variables** → **Actions**

### Step 2: Create Repository Secrets

#### REPO_SYNC_TOKEN Setup

1. **Create Personal Access Token**:
   - Go to GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
   - Click **Generate new token (classic)**
   - Token name: `Triune Swarm Engine Sync`
   - Expiration: `90 days` (recommended)
   - Scopes required:
     ```
     ✅ repo (Full control of private repositories)
     ✅ workflow (Update GitHub Action workflows)
     ✅ read:org (Read org and team membership)
     ```

2. **Add to Repository Secrets**:
   - Click **New repository secret**
   - Name: `REPO_SYNC_TOKEN`
   - Value: Your generated token (starts with `ghp_`)
   - Click **Add secret**

#### SHADOWSCROLLS_ENDPOINT Setup

1. **Obtain ShadowScrolls Endpoint**:
   - Contact your ShadowScrolls administrator
   - Or check your ShadowScrolls dashboard for API endpoints
   - Format: `https://api.shadowscrolls.your-domain.com/v1`

2. **Add to Repository Secrets**:
   - Click **New repository secret**
   - Name: `SHADOWSCROLLS_ENDPOINT`
   - Value: Your ShadowScrolls API endpoint URL
   - Click **Add secret**

#### SHADOWSCROLLS_API_KEY Setup

1. **Generate ShadowScrolls API Key**:
   - Log into your ShadowScrolls dashboard
   - Navigate to API Management → API Keys
   - Click **Create New Key**
   - Name: `Triune Swarm Engine Integration`
   - Permissions: `Read/Write Scrolls`, `Read Lineage Metadata`
   - Copy the generated key (starts with `ss_live_`)

2. **Add to Repository Secrets**:
   - Click **New repository secret**
   - Name: `SHADOWSCROLLS_API_KEY`
   - Value: Your ShadowScrolls API key
   - Click **Add secret**

### Step 3: Verify Secrets Configuration

After adding all secrets, your repository secrets should show:
```
REPO_SYNC_TOKEN         ••••••••
SHADOWSCROLLS_ENDPOINT  ••••••••
SHADOWSCROLLS_API_KEY   ••••••••
```

## 🖥️ Local Development Setup

### Environment Variables

Create a `.env.local` file in your project root:

```bash
# Mirror Watcher Configuration
REPO_SYNC_TOKEN=ghp_your_token_here
SHADOWSCROLLS_ENDPOINT=https://api.shadowscrolls.your-domain.com/v1
SHADOWSCROLLS_API_KEY=ss_live_your_key_here

# Optional: Local development overrides
NODE_ENV=development
DEBUG=triune:*
```

**⚠️ Security Warning**: Never commit `.env.local` to version control!

### Using the Setup Script

Run the automated setup script:

```bash
# Make script executable
chmod +x scripts/setup-secrets.sh

# Run interactive setup
./scripts/setup-secrets.sh

# Or run with parameters
./scripts/setup-secrets.sh --token "ghp_xxx" --endpoint "https://api.xxx" --key "ss_live_xxx"
```

## 🔍 Configuration Validation

### Automated Validation

Use the provided validation script:

```bash
# Install Python dependencies
pip install -r requirements.txt

# Run validation
python scripts/validate-setup.py

# Run specific validation
python scripts/validate-setup.py --check-secrets
python scripts/validate-setup.py --check-api
python scripts/validate-setup.py --check-permissions
```

### Manual Verification

#### 1. Test GitHub Token
```bash
curl -H "Authorization: token $REPO_SYNC_TOKEN" \
     https://api.github.com/user
```

#### 2. Test ShadowScrolls Endpoint
```bash
curl -H "Authorization: Bearer $SHADOWSCROLLS_API_KEY" \
     "$SHADOWSCROLLS_ENDPOINT/health"
```

#### 3. Test Mirror Watcher Integration
```bash
# Trigger test sync
curl -X POST \
  -H "Authorization: token $REPO_SYNC_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/repos/Triune-Oracle/triune-swarm-engine/dispatches \
  -d '{"event_type":"test_mirror_sync"}'
```

## 🚨 Security Best Practices

### Token Management
- **Rotate tokens every 90 days**
- **Use minimum required permissions**
- **Monitor token usage in GitHub Settings**
- **Revoke unused or compromised tokens immediately**

### Environment Security
- **Never commit secrets to version control**
- **Use `.gitignore` for environment files**
- **Encrypt sensitive files in production**
- **Use secret management tools in production environments**

### Access Control
- **Limit repository secret access to necessary team members**
- **Use environment-specific secrets for different deployment stages**
- **Implement secret rotation policies**
- **Monitor secret access logs**

## 🔧 Troubleshooting

### Common Issues

#### 1. "Bad credentials" error
- Verify `REPO_SYNC_TOKEN` is correctly set
- Check token expiration date
- Ensure token has required scopes

#### 2. ShadowScrolls API connection failed
- Verify `SHADOWSCROLLS_ENDPOINT` URL format
- Check `SHADOWSCROLLS_API_KEY` validity
- Test network connectivity to endpoint

#### 3. Permission denied errors
- Verify repository access permissions
- Check organization settings for token restrictions
- Confirm API key permissions in ShadowScrolls dashboard

### Debug Commands

```bash
# Check environment variables
./scripts/validate-setup.py --debug

# Test individual components
python -c "
import os
print('Repo Token:', 'SET' if os.getenv('REPO_SYNC_TOKEN') else 'MISSING')
print('SS Endpoint:', 'SET' if os.getenv('SHADOWSCROLLS_ENDPOINT') else 'MISSING')  
print('SS API Key:', 'SET' if os.getenv('SHADOWSCROLLS_API_KEY') else 'MISSING')
"

# Validate token scopes
curl -H "Authorization: token $REPO_SYNC_TOKEN" \
     https://api.github.com/user \
     -I | grep -i x-oauth-scopes
```

## 📞 Support

### Getting Help
- **Documentation**: Check this guide and repository README
- **Issues**: Create GitHub issue with `secrets-config` label
- **Security**: Email security concerns to `security@triune-oracle.com`
- **ShadowScrolls Support**: Contact your ShadowScrolls administrator

### Resources
- [GitHub Personal Access Tokens Documentation](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token)
- [GitHub Actions Secrets Documentation](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [ShadowScrolls API Documentation](https://docs.shadowscrolls.com/api)

---

**🛡️ Security Notice**: This configuration enables automated synchronization between your repository and external services. Ensure all team members understand the security implications and follow proper secret management practices.

**📋 Checklist**: Use `scripts/validate-setup.py` to verify your configuration meets all requirements for the Mirror Watcher automation system.