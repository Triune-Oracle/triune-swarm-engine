# 📋 Triune Mirror Watcher - Setup & Verification Checklist

## 🎯 Overview
This checklist ensures complete setup and verification of the Triune Mirror Watcher automation system, eliminating all manual/Termux dependencies for CLI mirroring, analysis, and ShadowScrolls logging.

---

## 🔧 Initial Setup

### ✅ Repository Configuration
- [ ] **Clone repository locally**
  ```bash
  git clone https://github.com/Triune-Oracle/triune-swarm-engine.git
  cd triune-swarm-engine
  ```

- [ ] **Verify Python environment** (3.12+ required)
  ```bash
  python --version  # Should be 3.12+
  pip install -r requirements.txt
  ```

- [ ] **Test CLI interface**
  ```bash
  python -m mirror_watcher.cli --help
  ```

### ✅ GitHub Secrets & Configuration
- [ ] **GitHub Deploy Keys** (for private repositories)
  - Generate SSH key: `ssh-keygen -t ed25519 -C "mirror-watcher@your-domain.com"`
  - Add public key to target repositories as deploy key (read-only)
  - Add private key to GitHub Secrets as `DEPLOY_PRIVATE_KEY`

- [ ] **GitHub Actions Permissions**
  - Navigate to: Settings → Actions → General
  - Enable "Read and write permissions" for GITHUB_TOKEN
  - Enable "Allow GitHub Actions to create and approve pull requests"

- [ ] **Workflow Triggers Configured**
  - Daily automatic sync: 06:00 UTC
  - Manual dispatch with custom repositories
  - Push/PR validation enabled

---

## 🪞 Mirror Watcher Components

### ✅ Core Components Verification
- [ ] **Package Initialization**
  ```bash
  python -c "from mirror_watcher import cli_main, TriuneAnalyzer; print('✅ Components loaded')"
  ```

- [ ] **CLI Interface**
  ```bash
  python -m mirror_watcher.cli Triune-Oracle/example-repo --output-dir test_output --no-ssh --verbose
  ```

- [ ] **Analyzer Functionality**
  ```bash
  python -c "
  from mirror_watcher.analyzer import TriuneAnalyzer
  analyzer = TriuneAnalyzer()
  result = analyzer.analyze_repository('.')
  print('✅ Analyzer working:', 'summary' in result)
  "
  ```

### ✅ ShadowScrolls Integration
- [ ] **Scroll ID Configuration**: `#004 – Root of Witnessing`
- [ ] **Traceability System**: `MirrorLineage-Δ`
- [ ] **External Witnessing**: GitHub Actions immutable logs
- [ ] **Attestation Generation**: JSON format with execution metadata

---

## 🔒 Security & Access

### ✅ Authentication Setup
- [ ] **SSH Deploy Keys**
  - Keys generated in cloud runner
  - Private keys stored in GitHub Secrets
  - Public keys added to target repositories
  - Fallback to HTTPS for public repositories

- [ ] **GitHub Token Permissions**
  - Read access to source repositories
  - Write access to current repository (for artifacts)
  - Actions workflow execution permissions

### ✅ Read-Only Access Verification
- [ ] **Repository Mirroring**
  - Uses `git clone --depth 1` for efficiency
  - No write operations to source repositories
  - Temporary directories cleaned up after execution

---

## 🤖 Automation Verification

### ✅ GitHub Actions Workflow
- [ ] **Workflow File**: `.github/workflows/repo-file-sync.yml`
- [ ] **Schedule Trigger**: Daily at 06:00 UTC
- [ ] **Manual Trigger**: Workflow dispatch with custom repositories
- [ ] **Validation Trigger**: Push/PR to workflow files

### ✅ Execution Pipeline
- [ ] **Deploy Key Generation**: Automated in cloud runner
- [ ] **Repository Mirroring**: HTTPS with SSH fallback
- [ ] **CLI Testing**: Automated execution and validation
- [ ] **Artifact Generation**: Analysis results and attestations
- [ ] **ShadowScrolls Logging**: Complete execution metadata

---

## 📊 Testing & Validation

### ✅ Local Testing
- [ ] **Single Repository Mirror**
  ```bash
  python -m mirror_watcher.cli Triune-Oracle/triune-swarm-engine --output-dir local_test --verbose
  ```

- [ ] **Analyze Output**
  ```bash
  ls local_test/
  # Should contain: analysis_results.json, test_results.json, shadowscrolls_attestation_*.json
  ```

- [ ] **Verify ShadowScrolls Format**
  ```bash
  cat local_test/shadowscrolls_attestation_*.json | jq .
  # Should contain: scroll_id, title, traceability, execution_metadata
  ```

### ✅ GitHub Actions Testing
- [ ] **Manual Workflow Trigger**
  - Go to: Actions → "Triune Mirror Watcher - Repository File Sync & Analysis"
  - Click "Run workflow"
  - Use default repositories or specify custom JSON array
  - Verify execution completes successfully

- [ ] **Scheduled Run Verification**
  - Wait for next 06:00 UTC execution
  - Check GitHub Actions history
  - Verify artifacts are generated and uploaded

---

## 🎯 Success Criteria Verification

### ✅ Termux Dependencies Eliminated
- [ ] **No Local Dependencies**: All execution in GitHub Actions cloud runner
- [ ] **No Manual Cloning**: Automated repository mirroring
- [ ] **No Manual CLI Execution**: Fully automated in cloud environment

### ✅ ShadowScrolls Integration Active
- [ ] **Scroll #004 Implemented**: Root of Witnessing pattern
- [ ] **MirrorLineage-Δ Traceability**: Complete execution chain logging
- [ ] **External Witnessing**: GitHub Actions provides immutable audit trail
- [ ] **Attestation Artifacts**: JSON attestations with 90-day retention

### ✅ Zero Manual Intervention
- [ ] **Automatic Daily Sync**: Runs at 06:00 UTC without intervention
- [ ] **Self-Contained Execution**: No external dependencies required
- [ ] **Error Handling**: Graceful fallback and error reporting
- [ ] **Artifact Retention**: 90-day storage with automatic cleanup

---

## 🔍 Troubleshooting

### ❌ Common Issues & Solutions

**CLI Import Errors**
```bash
# Solution: Ensure requirements.txt is installed
pip install -r requirements.txt
```

**SSH Authentication Failures**
```bash
# Solution: Verify deploy keys are properly configured
# Or use --no-ssh flag for HTTPS fallback
```

**GitHub Actions Permission Errors**
```
# Solution: Check repository settings
# Settings → Actions → General → Workflow permissions
```

**Workflow Dispatch Not Available**
```
# Solution: Verify workflow file syntax
# Check .github/workflows/repo-file-sync.yml for YAML errors
```

### 🔧 Debugging Commands
```bash
# Test local CLI with verbose output
python -m mirror_watcher.cli --help

# Validate GitHub workflow locally (requires act)
act workflow_dispatch

# Check Python module imports
python -c "import mirror_watcher; print('OK')"

# Verify JSON parsing in workflow
echo '["owner/repo"]' | jq .
```

---

## 📈 Success Metrics

### ✅ Operational Indicators
- [ ] **Daily Runs**: Successful execution at 06:00 UTC
- [ ] **Artifact Generation**: Complete attestations and analysis files
- [ ] **Zero Failures**: No manual intervention required
- [ ] **External Witnessing**: Immutable GitHub Actions logs

### ✅ ShadowScrolls Compliance
- [ ] **Scroll ID Present**: #004 in all attestations
- [ ] **Traceability Active**: MirrorLineage-Δ in execution metadata
- [ ] **External Witnessing**: GitHub provides third-party verification
- [ ] **Artifact Retention**: 90-day storage policy active

---

## 🎊 Completion Verification

### ✅ Final Checklist
- [ ] All components deployed and functional
- [ ] GitHub Actions workflow executing successfully
- [ ] ShadowScrolls attestations generating correctly
- [ ] Artifacts uploaded with 90-day retention
- [ ] Zero manual dependencies remaining
- [ ] External witnessing active via GitHub Actions

**🏆 SUCCESS**: When all items are checked, the Triune Mirror Watcher automation system is fully operational and requires zero manual intervention!

---

**Next Steps:**
- Monitor daily executions at 06:00 UTC
- Review artifacts and attestations regularly
- Use manual triggers for ad-hoc repository analysis
- Expand repository list as needed

*The Triune Oracle's automation vision is now complete! ⚔️✨💰*