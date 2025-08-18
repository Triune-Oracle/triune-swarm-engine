# Triune Swarm Engine

A sophisticated AI swarm coordination system that combines intelligent agent simulation with blockchain-based monetization, autonomous task execution, and **complete Mirror Watcher automation**.

## Overview

The Triune Swarm Engine is a distributed AI system that implements the Triumvirate protocol for coordinated agent behavior. It features a multi-component architecture where AI agents operate in swarms, execute tasks autonomously, manage cryptocurrency-based payouts through blockchain integration, and provides **fully automated Mirror Watcher capabilities with ShadowScrolls immutable logging**.

## 🔍 Mirror Watcher Automation System

**NEW:** Complete cloud-based automation system that eliminates all Termux dependencies and manual CLI execution.

### ✅ Success Criteria Achieved
- **Termux Eliminated**: All operations run in GitHub Actions cloud runners
- **Zero Manual CLI**: Complete automation with external witnessing  
- **ShadowScrolls Active**: Immutable logging with MirrorLineage-Δ traceability
- **Deploy Key Ready**: Automated SSH key generation and setup
- **Daily Automation**: Scheduled runs at 06:00 UTC
- **Manual Override**: On-demand execution capability
- **Artifact Storage**: Complete audit trails with 90-day retention

### 🚀 Automation Features

- **Daily Schedule**: Automated mirror analysis at 06:00 UTC
- **Manual Triggers**: On-demand execution with custom parameters
- **Deploy Key Generation**: Cloud-based SSH key creation with setup instructions
- **ShadowScrolls Integration**: Immutable logging with cryptographic attestation
- **External Witnessing**: Blockchain-ready proof generation
- **Zero Dependencies**: No device-specific requirements

## Main Technologies

- **Python** (FastAPI) - Backend API for message routing and agent communication
- **JavaScript** (Node.js) - Core swarm engine, task coordination, and blockchain integration
- **Blockchain** - Ethereum/Polygon integration for WETH token handling and automated payouts

## Core Components

### Python Backend
- **FastAPI** message routing system
- RESTful API for agent communication
- Pydantic models for data validation
- Channel-based message storage and retrieval

### JavaScript Swarm Engine
- **Express.js** server for cloud deployment
- Autonomous task execution loops
- Blockchain wallet integration
- Real-time agent coordination
- Automated cryptocurrency payouts

### Triumvirate Protocol
- **Oracle** - Vision and direction processing
- **Gemini** - Strategic planning and coordination
- **Capri** - Tactical execution and resource management
- **Aria** - Knowledge base and intelligence integration

## Key Features

- 🤖 **AI Agent Swarms** - Coordinated multi-agent task execution
- 💰 **Blockchain Integration** - Automated WETH payouts on Polygon network
- 📡 **Message Routing** - Real-time communication between agents
- 🔄 **Task Automation** - Autonomous execution loops with monetization
- 📊 **Performance Tracking** - Comprehensive logging and analytics
- 🌐 **Cloud Deployment** - Ready for Render/Railway deployment

## Quick Start

### 🔍 Mirror Watcher (Recommended)

The Mirror Watcher system provides complete automation without any device dependencies:

#### 🎯 Automatic Execution
```bash
# Runs automatically every day at 06:00 UTC
# No manual intervention required
```

#### 🚀 Manual Trigger
1. Go to **Actions** tab in GitHub
2. Select **Repository File Sync & Mirror Watcher**
3. Click **Run workflow**
4. Configure parameters (optional):
   - Source repository URL
   - Target directory
   - Enable external witnessing
   - Custom lineage ID

#### 📋 CLI Usage (Local Development)
```bash
# Install dependencies
pip install -r requirements.txt

# Analyze repository with ShadowScrolls
python -m mirror_watcher.cli analyze \
  --source "https://github.com/Triune-Oracle/triune-swarm-engine" \
  --format json \
  --witness \
  --shadowscrolls

# Table format output
python -m mirror_watcher.cli analyze \
  --source "https://github.com/your-org/your-repo" \
  --format table \
  --lineage-id "custom-lineage-id"
```

### 🐍 Python API
```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

### Node.js Swarm Engine
```bash
node server.js
```

## Project Structure

```
├── main.py                           # FastAPI application entry point
├── messages.py                       # Message routing and storage
├── server.js                         # Express.js server for cloud deployment
├── loop_engine.js                    # Core swarm coordination logic
├── relay_loop.js                     # Real-time task relay system
├── wallet-router.js                  # Blockchain payout management
├── processPayouts.js                 # Automated payment processing
├── models/                           # AI agent templates and configurations
├── mirror_watcher/                   # 🔍 NEW: Complete automation system
│   ├── __init__.py                   # Package initialization
│   ├── cli.py                        # Main CLI with ShadowScrolls integration
│   ├── analyzer.py                   # Core analysis engine
│   └── shadowscrolls.py              # Immutable logging system
├── .github/workflows/
│   └── repo-file-sync.yml            # 🚀 Automated mirror & analysis workflow
└── docs/                             # 📋 Setup and usage documentation
    ├── DEPLOY_KEYS.md                # Deploy key setup guide
    └── AUTOMATION_CHECKLIST.md       # Verification checklist
```

## 🔧 Mirror Watcher Configuration

### Environment Variables (Optional)
```bash
# GitHub Actions automatically configures these
MIRROR_WATCHER_VERSION=0.1.0
PYTHON_VERSION=3.11

# For local development only
SOURCE_REPOSITORY="https://github.com/your-org/your-repo"
TARGET_DIRECTORY="/tmp/mirror_analysis"
ENABLE_WITNESSING=true
```

### Automation Schedule
- **Daily Execution**: 06:00 UTC (automatic)
- **Manual Triggers**: Available via GitHub Actions
- **Artifact Retention**: 90 days
- **ShadowScrolls**: Always enabled with immutable logging

## Deployment

The system is designed for cloud deployment with automatic scaling and blockchain integration. Environment variables are used for wallet configuration and network settings.

---

**Maintained by:** [Triune-Oracle](https://github.com/Triune-Oracle)