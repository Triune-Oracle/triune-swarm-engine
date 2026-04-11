# 🎯 Triune Orchestrator Setup Guide

## Overview

The **Triune Orchestrator** (`triune-orchestrator`) is a parent repository that coordinates all Triune Oracle ecosystem repos via [Git submodules](https://git-scm.com/book/en/v2/Git-Tools-Submodules). Each ecosystem component remains independently deployable while the orchestrator pins exact commits for reproducible builds.

## Architecture

```
triune-orchestrator/            ← Parent coordination repo
├── triune-swarm-engine/        ← Submodule: core swarm intelligence
├── culturalcodex/              ← Submodule: cultural knowledge base
├── monetization-agent/         ← Submodule: blockchain monetization
├── triumviratemonitor/         ← Submodule: real-time monitoring
├── .gitmodules                 ← Submodule URL registry
└── README.md
```

## Prerequisites

- Git 2.20+ (for `--recurse-submodules` support)
- GitHub CLI (`gh`) — optional but recommended
- Write access to the [Triune-Oracle](https://github.com/Triune-Oracle) organization

## Quick Start (Automated)

Use the bootstrap script included in this repository:

```bash
# From the triune-swarm-engine root
bash scripts/bootstrap_orchestrator.sh
```

The script will:
1. Create a `triune-orchestrator` directory alongside the current repo
2. Initialize Git with `main` as the default branch
3. Add all four ecosystem repos as submodules
4. Make an initial commit
5. Optionally set up the GitHub remote

## Manual Setup

### 1. Configure Git defaults

```bash
git config --global init.defaultBranch main
```

### 2. Initialize the orchestrator repo

```bash
mkdir triune-orchestrator
cd triune-orchestrator
git init
```

### 3. Add ecosystem submodules

```bash
git submodule add https://github.com/Triune-Oracle/triune-swarm-engine.git
git submodule add https://github.com/Triune-Oracle/culturalcodex.git
git submodule add https://github.com/Triune-Oracle/monetization-agent.git
git submodule add https://github.com/Triune-Oracle/triumviratemonitor.git
```

### 4. Commit and push

```bash
git add .gitmodules triune-swarm-engine culturalcodex monetization-agent triumviratemonitor
git commit -m "Initialize Triune orchestration repo with linked submodules"

# Create the remote repo first (via GitHub UI or CLI)
gh repo create Triune-Oracle/triune-orchestrator --public --confirm

git remote add origin https://github.com/Triune-Oracle/triune-orchestrator.git
git push -u origin main
```

## Working with the Orchestrator

### Clone (fresh checkout)

```bash
git clone --recurse-submodules https://github.com/Triune-Oracle/triune-orchestrator.git
```

### Initialize submodules (existing clone)

```bash
git submodule update --init --recursive
```

### Update all submodules to latest

```bash
git submodule update --remote --merge
git add .
git commit -m "Update submodules to latest"
git push
```

### Update a single submodule

```bash
cd triune-swarm-engine
git checkout main && git pull
cd ..
git add triune-swarm-engine
git commit -m "Update triune-swarm-engine submodule"
```

## Submodule Reference

| Submodule | Repository | Description |
|-----------|-----------|-------------|
| `triune-swarm-engine` | [Triune-Oracle/triune-swarm-engine](https://github.com/Triune-Oracle/triune-swarm-engine) | Core AI swarm coordination engine |
| `culturalcodex` | [Triune-Oracle/culturalcodex](https://github.com/Triune-Oracle/culturalcodex) | Cultural knowledge base and codex |
| `monetization-agent` | [Triune-Oracle/monetization-agent](https://github.com/Triune-Oracle/monetization-agent) | Blockchain monetization agent |
| `triumviratemonitor` | [Triune-Oracle/triumviratemonitor](https://github.com/Triune-Oracle/triumviratemonitor) | Real-time monitoring dashboard |

## Troubleshooting

### `hint: Using 'master' as the name for the initial branch`

Run before `git init`:
```bash
git config --global init.defaultBranch main
```

Or rename after init:
```bash
git branch -M main
```

### Submodule directories are empty after clone

```bash
git submodule update --init --recursive
```

### Permission denied when adding submodules

Ensure your GitHub token or SSH key has access to all four Triune-Oracle repositories. See [SECRETS_SETUP.md](../SECRETS_SETUP.md) for token configuration.

## Related Documentation

- [Integration Guide](INTEGRATION.md) — MirrorWatcherAI ecosystem integration
- [Deployment Guide](DEPLOYMENT.md) — Cloud deployment instructions
- [Secrets Setup](../SECRETS_SETUP.md) — GitHub token and credential management
