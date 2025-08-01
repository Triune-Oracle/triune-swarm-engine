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
node server.js
```

## Project Structure

```
├── main.py              # FastAPI application entry point
├── messages.py          # Message routing and storage
├── server.js            # Express.js server for cloud deployment
├── loop_engine.js       # Core swarm coordination logic
├── relay_loop.js        # Real-time task relay system
├── wallet-router.js     # Blockchain payout management
├── processPayouts.js    # Automated payment processing
└── models/              # AI agent templates and configurations
```

## Deployment

The system is designed for cloud deployment with automatic scaling and blockchain integration. Environment variables are used for wallet configuration and network settings.

---

**Maintained by:** [Triune-Oracle](https://github.com/Triune-Oracle)