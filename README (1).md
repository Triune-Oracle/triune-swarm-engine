# MCP Tool Resolver

This project provides a CLI and REST API to resolve the correct command configuration for a given tool based on MCP server definitions. It supports variable resolution, wildcard tool support, and CI compatibility.

## 📦 Install

```bash
npm install
```

## 🛠️ CLI Usage

```bash
node mcpToolResolver.js --tool toolA --config ./mcpConfig.json
```

## 🌐 REST API Usage

```bash
MCP_REST_MODE=1 node mcpToolResolver.js
```

Then POST to:

```
http://localhost:3000/resolve-tool
```

Body:

```json
{
  "tool": "toolA",
  "config": {
    "mcpServers": {
      "server1": {
        "tools": ["toolA"],
        "command": "$TOOL_HOME/bin/tool",
        "args": ["--config", "$TOOL_CONFIG"],
        "env": {
          "TOOL_HOME": "/usr/local/toolA",
          "TOOL_CONFIG": "${TOOL_HOME}/conf/config.json"
        }
      }
    }
  }
}
```

## 🐳 Docker

```bash
docker build -t mcp-resolver .
docker run -p 3000:3000 -e MCP_REST_MODE=1 mcp-resolver
```

## ✅ GitHub Actions

Included in `.github/workflows/test.yml` to validate CLI execution.

---

**Maintained by:** [Triune-Oracle](https://github.com/Triune-Oracle)
