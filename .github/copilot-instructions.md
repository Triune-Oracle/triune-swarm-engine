# Dependency Management Instructions
- Always prioritize updating to the latest secure and stable versions.
- If a security vulnerability is detected, run `npm audit fix` first.
- Ensure that updates in `package.json` are reflected in `package-lock.json`.
- Do not ignore lockfile-only upgrades if they resolve broad security advisories.
