# Security Note — Exposed Secrets

## What Happened

A literal Ethereum private key (`PRIVATE_KEY`) and Infura project ID (`INFURA_ID`) were found committed in plain text inside `.env.example` in this repository's git history. These values have been replaced with placeholders in this PR.

**The old values must be treated as fully compromised regardless of whether funds were present.**

---

## Immediate Actions Required

- [ ] **Rotate the private key** — generate a new wallet/key pair. Never reuse the old key.
- [ ] **Move any funds** off the compromised wallet address immediately if not already done.
- [ ] **Revoke and regenerate the Infura project** — delete the old Infura project ID and create a new one. Update all services that used the old ID.
- [ ] **Scan the full org** for any other committed secrets (use `gitleaks`, `trufflehog`, or GitHub Advanced Security secret scanning).
- [ ] **Verify CI/GitHub Actions** do not inject live secrets from unsafe sources (e.g., hardcoded in workflow files or checked-in `.env` files). All secrets must be stored in GitHub Actions Secrets or a secrets manager and injected at runtime only.

---

## History Purge Required

Replacing the values in `.env.example` **does not remove the secrets from git history**. The old values remain visible in previous commits. A history purge **must** be performed after keys are rotated.

> ⚠️ This PR does NOT perform any history rewrite. The purge will be carried out in a separate operation after you confirm rotation is complete.

### Purge with git filter-repo (recommended)

```bash
# Run locally or in a CI environment with proper permissions
git clone --mirror git@github.com:Triune-Oracle/triune-swarm-engine.git
git filter-repo --invert-paths --path .env.example
git push --force
```

### Purge with BFG (alternative)

```bash
bfg --delete-files .env.example
git reflog expire --expire=now --all && git gc --prune=now --aggressive
git push --force
```

---

## Maintainer Checklist

- [ ] Rotate affected private key (EVM wallet)
- [ ] Revoke and replace the Infura project ID
- [ ] Update all services/deployments using the old credentials
- [ ] Run org-wide secret scan and resolve any additional findings
- [ ] Perform history purge (see commands above) after rotation is confirmed
- [ ] Confirm CI/GitHub Actions workflows use only environment-injected secrets — no secrets hardcoded in any committed file
- [ ] After purge, force-push and notify all collaborators to re-clone
