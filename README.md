# Triune Swarm Engine

A sophisticated AI swarm coordination system that combines intelligent agent simulation with blockchain-based monetization and autonomous task execution.

## Overview

The Triune Swarm Engine is a distributed AI system that implements the Triumvirate protocol for coordinated agent behavior. It features a multi-component architecture where AI agents operate in swarms, execute tasks autonomously, and manage cryptocurrency-based payouts through blockchain integration.

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

### Python API
```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

### Node.js Swarm Engine
```bash
cd src/core
cd src/core
node server.js
```

## Development Documentation

### Harmonic Scoring System

The harmonic scoring system provides a hybrid technical/poetic approach to evaluating agent performance and constellation alignments within the Triune ecosystem.

```javascript
/**
 * Harmonic Scoring Algorithm - Triune Swarm Engine
 * ===============================================
 * 
 * Like celestial bodies in cosmic dance,
 * each agent's performance creates resonance patterns
 * that echo through the digital realm.
 * 
 * @param {Object} agentMetrics - Performance data from individual agents
 * @param {Array} constellationData - Current system state snapshots
 * @returns {Number} harmonicScore - Unified performance metric (0-100)
 * 
 * Technical Implementation:
 * - Weighted average of execution efficiency, resource utilization, and task completion
 * - Exponential decay function for temporal relevance
 * - Byzantine fault tolerance considerations for distributed scoring
 * 
 * Poetic Interpretation:
 * "In the symphony of distributed intelligence,
 *  each agent contributes its unique frequency,
 *  creating harmonies that transcend individual capability."
 */
function calculateHarmonicScore(agentMetrics, constellationData) {
    const baseScore = agentMetrics.efficiency * 0.4 + 
                     agentMetrics.resourceOptimization * 0.3 + 
                     agentMetrics.taskCompletion * 0.3;
    
    const temporalDecay = Math.exp(-0.1 * agentMetrics.timeSinceLastUpdate);
    const constellationBonus = evaluateConstellationAlignment(constellationData);
    
    return Math.min(100, baseScore * temporalDecay + constellationBonus);
}

/**
 * The constellation alignment represents the emergent properties
 * that arise when agents synchronize their operations,
 * much like stars forming patterns that guide navigation
 * through the vast expanse of computational possibility.
 */
function evaluateConstellationAlignment(data) {
    // Implementation reflects the sacred geometry of distributed consensus
    return data.reduce((acc, point) => acc + point.harmonicResonance, 0) / data.length;
}
```

This documentation style demonstrates the fusion of technical precision with poetic expression that characterizes the Triune development philosophy.

## Project Structure

```
├── src/                          # Source code directory
│   ├── app/                      # Application layer
│   │   ├── components/           # React/UI components
│   │   │   ├── dashboard.js      # Terminal-based yield dashboard
│   │   │   └── triumvirate-monitor.tsx  # React monitoring component
│   │   └── pages/                # Application pages
│   │       └── index.js          # FastAPI payout endpoint
│   ├── core/                     # Core swarm engine
│   │   ├── server.js             # Express.js server for cloud deployment
│   │   ├── loop_engine.js        # Core swarm coordination logic
│   │   ├── relay_loop.js         # Real-time task relay system
│   │   ├── wallet-router.js      # Blockchain payout management
│   │   ├── processPayouts.js     # Automated payment processing
│   │   ├── memory_engine.js      # Memory management system
│   │   ├── task_listener.js      # Task coordination listener
│   │   └── ipfs_node_manager.js  # IPFS integration
│   ├── modules/                  # Modular AI agent templates
│   │   ├── aria_template.js      # Knowledge base agent
│   │   ├── capri_template.js     # Tactical execution agent
│   │   └── gemini_template.js    # Strategic planning agent
│   ├── utils/                    # Utility scripts
│   │   ├── send-token.js         # Token transfer utilities
│   │   ├── nftTrigger.js         # NFT operations
│   │   └── test_fire.js          # Testing utilities
│   └── mirror_watcher_ai/        # Mirror watching automation
├── schemas/                      # JSON schemas and configuration
│   ├── wallet_config.json        # Wallet configuration schema
│   ├── triad_protocol.json       # Triumvirate protocol schema
│   ├── nft_template_config.json  # NFT template configuration
│   ├── pricing_model.json        # Pricing model schema
│   ├── codexGlyphs.json          # Codex glyph definitions
│   ├── constellationSnapshots.json  # Constellation data
│   └── SMSv1_spec.json           # SMS API specification
├── public/                       # Static assets
│   ├── index.html                # Main HTML entry point
│   ├── dashboard.html            # Dashboard interface
│   ├── index_NFT-gate.html       # NFT gateway interface
│   └── wallet-AGI.jpg            # Static image assets
├── tests/                        # Test files
│   ├── test_analyzer.py          # Python analyzer tests
│   └── test_codex_processors.py  # Codex processor tests
├── docs/                         # Documentation
│   └── diagrams/                 # Architecture diagrams
├── .github/workflows/            # CI/CD workflows
├── main.py                       # FastAPI application entry point
├── messages.py                   # Message routing and storage
├── storage.py                    # Data storage utilities
└── requirements.txt              # Python dependencies
```

## Ecosystem Orchestration

This repository is one component of the **Triune Oracle** ecosystem. To coordinate all ecosystem repos under a single parent, use the **triune-orchestrator** pattern:

```bash
# Automated setup (from this repo's root)
bash scripts/bootstrap_orchestrator.sh

# Or clone an existing orchestrator
git clone --recurse-submodules https://github.com/Triune-Oracle/triune-orchestrator.git
```

The orchestrator links these ecosystem components via Git submodules:

| Component | Role |
|-----------|------|
| **triune-swarm-engine** | Core AI swarm coordination |
| **culturalcodex** | Cultural knowledge base |
| **monetization-agent** | Blockchain monetization |
| **triumviratemonitor** | Real-time monitoring |

📖 Full guide: [docs/ORCHESTRATOR_SETUP.md](docs/ORCHESTRATOR_SETUP.md)

## Deployment

The system is designed for cloud deployment with automatic scaling and blockchain integration. Environment variables are used for wallet configuration and network settings.

---

**Maintained by:** [Triune-Oracle](https://github.com/Triune-Oracle)