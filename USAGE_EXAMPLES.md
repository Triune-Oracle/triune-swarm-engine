# 📚 Mirror Watcher Usage Examples

> **Quick reference guide for using the Triune Swarm Engine secrets configuration and Mirror Watcher automation system**

## 🚀 Quick Start

### 1. Interactive Setup (Recommended)
```bash
# Run the interactive setup wizard
./scripts/setup-secrets.sh

# Follow the prompts to enter:
# - GitHub Personal Access Token
# - ShadowScrolls API endpoint
# - ShadowScrolls API key
```

### 2. Silent Setup (Automation-Friendly)
```bash
# Setup with all parameters provided
./scripts/setup-secrets.sh \
  --token "ghp_your_github_token_here" \
  --endpoint "https://api.shadowscrolls.your-domain.com/v1" \
  --key "ss_live_your_api_key_here" \
  --validate
```

### 3. Validate Your Configuration
```bash
# Run all validation checks
python3 scripts/validate-setup.py

# Run specific checks
python3 scripts/validate-setup.py --check-secrets
python3 scripts/validate-setup.py --check-api
python3 scripts/validate-setup.py --check-structure
```

## 🔧 Configuration Examples

### Environment File Structure
The setup script creates `.env.local` with this structure:

```bash
# Mirror Watcher Automation Configuration
REPO_SYNC_TOKEN=ghp_your_actual_token_here
SHADOWSCROLLS_ENDPOINT=https://api.shadowscrolls.your-domain.com/v1
SHADOWSCROLLS_API_KEY=ss_live_your_actual_key_here

# Development Environment Settings
NODE_ENV=development
# DEBUG=triune:*  # Uncomment for debug logging
```

### Custom Environment Files
```bash
# Use a custom environment file location
./scripts/setup-secrets.sh --file ".env.production"

# Create backup of existing file
./scripts/setup-secrets.sh --backup

# Validate custom environment file
python3 scripts/validate-setup.py --env-file ".env.production"
```

## 🔍 Validation Examples

### Check Secret Formats
```bash
# Validate secret presence and format compliance
python3 scripts/validate-setup.py --check-secrets

# Expected output for valid secrets:
# ✅ secrets_presence: PASSED
# ✅ secret_formats: PASSED
```

### Test API Connectivity
```bash
# Test GitHub and ShadowScrolls API connectivity
python3 scripts/validate-setup.py --check-api

# Debug API issues
python3 scripts/validate-setup.py --check-api --debug
```

### JSON Output for Integration
```bash
# Get validation results in JSON format
python3 scripts/validate-setup.py --json > validation-results.json

# Check specific components programmatically
python3 scripts/validate-setup.py --check-structure --json | jq '.overall_status'
```

## 🛡️ Security Examples

### Token Generation
1. **GitHub Personal Access Token**:
   - Go to: https://github.com/settings/tokens
   - Click "Generate new token (classic)"
   - Required scopes: `repo`, `workflow`, `read:org`
   - Copy token starting with `ghp_`

2. **ShadowScrolls API Key**:
   - Access your ShadowScrolls dashboard
   - Navigate to API Management → API Keys
   - Create key with permissions: `Read/Write Scrolls`, `Read Lineage Metadata`
   - Copy key starting with `ss_live_`

### Security Validation
```bash
# Check environment security configuration
python3 scripts/validate-setup.py --check-permissions

# Verify .gitignore protection
grep -n "\.env\.local" .gitignore

# Check file permissions
ls -la .env.local
```

## 🔄 Integration Workflow Examples

### GitHub Actions Integration
```yaml
# Example GitHub workflow step
- name: Sync with Mirror Watcher
  env:
    REPO_SYNC_TOKEN: ${{ secrets.REPO_SYNC_TOKEN }}
    SHADOWSCROLLS_ENDPOINT: ${{ secrets.SHADOWSCROLLS_ENDPOINT }}
    SHADOWSCROLLS_API_KEY: ${{ secrets.SHADOWSCROLLS_API_KEY }}
  run: |
    python3 scripts/validate-setup.py --check-api
    # Your mirror sync logic here
```

### ShadowScrolls Reporting
```bash
# View initial setup report
cat .shadowscrolls/reports/initial-setup-20250818-171022.json | jq '.scroll_metadata'

# Expected scroll structure:
{
  "scroll_id": "#001 – Initial Mirror Setup",
  "timestamp": "2025-08-18T17:10:22Z",
  "system": "Mirror Watcher Automation"
}
```

### Local Development
```bash
# Load environment in your shell
set -a
source .env.local
set +a

# Test environment loading
echo "Token prefix: ${REPO_SYNC_TOKEN:0:4}..."
echo "Endpoint: $SHADOWSCROLLS_ENDPOINT"
```

## 🐛 Troubleshooting Examples

### Common Issues and Solutions

#### Issue: "Bad credentials" error
```bash
# Diagnosis
python3 scripts/validate-setup.py --check-api --debug

# Solution
# 1. Check token validity
curl -H "Authorization: token $REPO_SYNC_TOKEN" https://api.github.com/user

# 2. Verify token scopes
curl -H "Authorization: token $REPO_SYNC_TOKEN" \
     https://api.github.com/user -I | grep -i x-oauth-scopes
```

#### Issue: ShadowScrolls connection failed
```bash
# Diagnosis
python3 scripts/validate-setup.py --check-api

# Solution - Test endpoint manually
curl -H "Authorization: Bearer $SHADOWSCROLLS_API_KEY" \
     "$SHADOWSCROLLS_ENDPOINT/health"

# Check endpoint format
echo $SHADOWSCROLLS_ENDPOINT | grep -E '^https?://[a-zA-Z0-9.-]+(/.*)?$'
```

#### Issue: Invalid secret format
```bash
# Check current secret formats
python3 scripts/validate-setup.py --check-secrets --debug

# Valid formats:
# REPO_SYNC_TOKEN: ghp_[36 characters]
# SHADOWSCROLLS_ENDPOINT: https://domain.com/path
# SHADOWSCROLLS_API_KEY: ss_live_[32 characters]
```

#### Issue: Permission denied
```bash
# Check file permissions
ls -la .env.local scripts/

# Fix script permissions
chmod +x scripts/setup-secrets.sh scripts/validate-setup.py

# Check environment file access
python3 scripts/validate-setup.py --check-permissions
```

## 🧪 Testing Examples

### Run Integration Tests
```bash
# Execute comprehensive test suite
./scripts/test-integration.sh

# This will demonstrate:
# - Setup script functionality
# - Validation script capabilities
# - Secret format examples
# - Security best practices
# - Complete workflow walkthrough
```

### Manual Testing Steps
```bash
# 1. Backup current configuration
cp .env.local .env.local.backup 2>/dev/null || echo "No existing config"

# 2. Test setup with dummy values
./scripts/setup-secrets.sh \
  --token "ghp_1234567890123456789012345678901234567890" \
  --endpoint "https://api.shadowscrolls.example.com/v1" \
  --key "ss_live_12345678901234567890123456789012" \
  --file ".env.test"

# 3. Validate test configuration
python3 scripts/validate-setup.py --env-file ".env.test" --check-secrets

# 4. Clean up test files
rm .env.test
```

## 📊 Monitoring Examples

### ShadowScrolls Report Analysis
```bash
# View current setup status
jq '.configuration_status' .shadowscrolls/reports/initial-setup-20250818-171022.json

# Check validation checklist
jq '.validation_checklist.setup_verification' .shadowscrolls/reports/initial-setup-20250818-171022.json

# Monitor integration readiness
jq '.validation_checklist.integration_readiness' .shadowscrolls/reports/initial-setup-20250818-171022.json
```

### Continuous Validation
```bash
# Create validation monitoring script
cat > monitor-setup.sh << 'EOF'
#!/bin/bash
while true; do
  echo "$(date): Running validation..."
  python3 scripts/validate-setup.py --quiet
  echo "$(date): Validation complete"
  sleep 300  # Check every 5 minutes
done
EOF

chmod +x monitor-setup.sh
```

## 🔗 Integration with Other Tools

### Docker Integration
```dockerfile
# Dockerfile example
FROM python:3.12-slim

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY scripts/ scripts/
COPY .shadowscrolls/ .shadowscrolls/

# Validate setup during build
RUN python3 scripts/validate-setup.py --check-structure

ENV NODE_ENV=production
CMD ["python3", "your-app.py"]
```

### CI/CD Pipeline Integration
```yaml
# Example pipeline step
validate-setup:
  script:
    - python3 scripts/validate-setup.py --check-secrets --json > validation.json
    - |
      if [ "$(jq -r '.overall_status' validation.json)" != "PASSED" ]; then
        echo "❌ Setup validation failed"
        jq '.results[] | select(.passed == false)' validation.json
        exit 1
      fi
    - echo "✅ Setup validation passed"
```

## 📚 Advanced Usage

### Custom Validation Rules
```python
# Extend validate-setup.py for custom checks
def validate_custom_requirements(self) -> ValidationResult:
    result = ValidationResult("custom_requirements")
    
    # Add your custom validation logic
    if self.secrets.get('CUSTOM_SECRET'):
        result.add_info("Custom secret is configured")
        result.set_passed(True)
    else:
        result.add_warning("Custom secret not configured")
    
    return result
```

### Environment-Specific Configuration
```bash
# Development environment
./scripts/setup-secrets.sh --file ".env.development"

# Staging environment  
./scripts/setup-secrets.sh --file ".env.staging"

# Production environment
./scripts/setup-secrets.sh --file ".env.production"

# Validate all environments
for env in development staging production; do
  echo "Validating $env environment..."
  python3 scripts/validate-setup.py --env-file ".env.$env"
done
```

---

## 🎯 Quick Reference Commands

| Task | Command |
|------|---------|
| Interactive setup | `./scripts/setup-secrets.sh` |
| Silent setup | `./scripts/setup-secrets.sh -t TOKEN -e ENDPOINT -k KEY` |
| Full validation | `python3 scripts/validate-setup.py` |
| Secrets only | `python3 scripts/validate-setup.py --check-secrets` |
| API tests | `python3 scripts/validate-setup.py --check-api` |
| JSON output | `python3 scripts/validate-setup.py --json` |
| Debug mode | `python3 scripts/validate-setup.py --debug` |
| Run tests | `./scripts/test-integration.sh` |
| View report | `cat .shadowscrolls/reports/initial-setup-*.json` |

## 📖 Further Reading

- [SECRETS_SETUP.md](SECRETS_SETUP.md) - Complete setup guide
- [GitHub Actions Secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [ShadowScrolls Documentation](https://docs.shadowscrolls.com/api)

---

**💡 Pro Tip**: Run `./scripts/test-integration.sh` to see all these examples in action!