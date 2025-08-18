# 🔑 Deploy Keys Setup Guide

This guide explains how to set up SSH deploy keys for secure repository access with the Mirror Watcher automation system.

## 🎯 Overview

Deploy keys provide secure, read-only access to repositories without requiring personal access tokens or user credentials. The Mirror Watcher system can automatically generate these keys for you.

## 🚀 Automated Setup Process

### Step 1: Run the Workflow
1. Navigate to your repository's **Actions** tab
2. Select **Repository File Sync & Mirror Watcher**
3. Click **Run workflow**
4. The workflow will automatically generate SSH keys

### Step 2: Download Generated Keys
1. After workflow completion, go to the **Artifacts** section
2. Download `mirror-watcher-analysis-{run-number}`
3. Extract `deploy_key_secret.txt` (contains base64-encoded private key)

### Step 3: Configure Repository Access
1. Navigate to target repository settings
2. Go to **Settings** → **Deploy keys** → **Add deploy key**
3. Paste the public key from workflow output
4. Choose appropriate access level:
   - ✅ **Read-only** (recommended for analysis)
   - ⚠️ **Write access** (only if needed for mirroring operations)

## 🔧 Manual Key Generation (Alternative)

If you prefer to generate keys manually:

```bash
# Generate SSH key pair
ssh-keygen -t ed25519 -C "mirror-watcher-$(date +%Y%m%d)" -f deploy_key -N ""

# Display public key for repository configuration
cat deploy_key.pub

# Store private key securely
base64 -w 0 deploy_key > deploy_key_secret.txt
```

## 🔒 Security Best Practices

### Key Management
- **Rotate keys regularly** (recommended: every 90 days)
- **Use read-only access** unless write operations required
- **Store private keys as encrypted secrets** in repository settings
- **Monitor key usage** in repository security logs

### Access Control
- **Principle of least privilege**: Grant minimum required access
- **Repository-specific keys**: Use different keys for different repositories
- **Audit access regularly**: Review deploy key usage and permissions

### Environment Variables
Store the private key as a repository secret:

1. Go to **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret**
3. Name: `DEPLOY_PRIVATE_KEY`
4. Value: Base64-encoded private key from `deploy_key_secret.txt`

## 🔍 Verification Steps

### Test Key Access
```bash
# Test SSH connection (replace with your repository)
ssh -T git@github.com -i deploy_key

# Expected output: Successfully authenticated
```

### Verify in Workflow
The Mirror Watcher workflow automatically verifies key functionality:
- ✅ SSH key generation
- ✅ Public key fingerprint validation  
- ✅ Connection testing
- ✅ Repository access verification

## 🛠️ Troubleshooting

### Common Issues

**Issue**: Permission denied (publickey)
```bash
# Solution: Verify key is properly configured
ssh-add deploy_key
ssh -T git@github.com
```

**Issue**: Repository not found
```bash
# Solution: Check repository URL and access permissions
git ls-remote git@github.com:username/repository.git
```

**Issue**: Key already in use
```bash
# Solution: Generate new key with different comment
ssh-keygen -t ed25519 -C "mirror-watcher-backup-$(date +%Y%m%d)" -f deploy_key_backup
```

### Workflow Debugging
Check workflow logs for detailed error information:
1. Go to **Actions** tab
2. Select failed workflow run
3. Review **Setup Deploy Keys** job logs
4. Check **Mirror Analysis** job for access issues

## 📋 Key Rotation Process

### Quarterly Rotation (Recommended)
1. **Generate new key pair** using automated workflow
2. **Update repository deploy keys** with new public key
3. **Update repository secrets** with new private key
4. **Test new key functionality** with manual workflow run
5. **Remove old key** from repository deploy keys
6. **Document rotation** in security audit logs

### Emergency Rotation
If key compromise suspected:
1. **Immediately revoke** old deploy key in repository settings
2. **Generate new key pair** immediately
3. **Update all affected repositories**
4. **Audit access logs** for unauthorized usage
5. **Update security documentation**

## 🎊 Success Verification

Your deploy key setup is successful when:
- ✅ Automated key generation completes without errors
- ✅ Public key is properly configured in target repository
- ✅ Private key is securely stored as repository secret
- ✅ Mirror Watcher workflow runs successfully
- ✅ Repository analysis completes with proper authentication

## 📞 Support

For additional help:
- 📖 **Documentation**: Check workflow logs and error messages
- 🐛 **Issues**: Create GitHub issue with detailed error information
- 🔒 **Security**: Email security@triune-oracle.com for security-related issues
- 💬 **Discussions**: Use GitHub Discussions for questions

---

**Next Steps**: After deploy key setup, proceed to the [Automation Checklist](./AUTOMATION_CHECKLIST.md) to verify complete system functionality.