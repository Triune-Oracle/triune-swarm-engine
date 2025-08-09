# Secret Synchronization for Triune-Oracle Repositories

## Overview

This setup automates synchronizing GitHub Actions secrets across multiple repositories in the `Triune-Oracle` organization.

## Requirements

- A GitHub Personal Access Token (PAT) with `repo` and `admin:repo_hook` scopes.
- Add this PAT to the GitHub repository secrets as `GH_PAT`.
- A local `secrets.json` file containing the secrets to sync.

## Usage

1. Update `secrets.json` with the secret names and values you want to propagate.
2. Commit and push `set-secrets.js` and `.github/workflows/set-secrets.yml` files.
3. Trigger the workflow manually via the Actions tab, or rely on the weekly schedule.
4. The workflow will log the status of secret updates per repository.

## Security Notes

- **Never commit real secrets publicly.** Use `.gitignore` to exclude `secrets.json`.
- Rotate your PAT regularly.
- Ensure only trusted collaborators have write access to the workflow and secrets.

---

This automation empowers the Triune-Oracle swarm with seamless secret management to maintain sovereignty and security.