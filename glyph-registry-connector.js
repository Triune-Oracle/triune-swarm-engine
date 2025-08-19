// glyph-registry-connector.js - Manages constellation visualizations and glyph data

const fs = require('fs');
const path = require('path');

class GlyphRegistryConnector {
  constructor() {
    this.glyphNodes = new Map();
    this.constellation = {
      nodes: [],
      edges: [],
      metadata: {}
    };
    this.rotationHistory = [];
    this.themes = new Map();
    this.activeTheme = 'cosmic';
    this.initialize();
  }

  initialize() {
    this.loadGlyphRegistry();
    this.loadConstellationData();
    this.loadThemeConfigurations();
    this.setupDefaultThemes();
    console.log('Glyph Registry Connector initialized');
  }

  // Add a new glyph node to the constellation
  addGlyphNode(nodeData) {
    const nodeId = nodeData.id || this.generateNodeId();
    
    const glyphNode = {
      id: nodeId,
      type: nodeData.type || 'default',
      position: nodeData.position || this.generateRandomPosition(),
      properties: nodeData.properties || {},
      connections: [],
      createdAt: new Date().toISOString(),
      lastUpdated: new Date().toISOString(),
      metadata: nodeData.metadata || {}
    };
    
    // Ensure properties object has required fields
    if (!glyphNode.properties.size) {
      glyphNode.properties.size = this.getDefaultNodeSize(glyphNode.type);
    }
    if (!glyphNode.properties.color) {
      glyphNode.properties.color = this.getNodeColor(glyphNode.type);
    }
    if (!glyphNode.properties.label) {
      glyphNode.properties.label = glyphNode.id;
    }
    
    this.glyphNodes.set(nodeId, glyphNode);
    this.updateConstellation();
    
    console.log(`Glyph node added: ${nodeId} (${glyphNode.type})`);
    return glyphNode;
  }

  // Update existing glyph node
  updateGlyphNode(nodeId, updates) {
    const node = this.glyphNodes.get(nodeId);
    
    if (!node) {
      throw new Error(`Glyph node not found: ${nodeId}`);
    }
    
    // Merge updates
    Object.assign(node, updates);
    node.lastUpdated = new Date().toISOString();
    
    this.updateConstellation();
    
    console.log(`Glyph node updated: ${nodeId}`);
    return node;
  }

  // Remove glyph node
  removeGlyphNode(nodeId) {
    const node = this.glyphNodes.get(nodeId);
    
    if (!node) {
      throw new Error(`Glyph node not found: ${nodeId}`);
    }
    
    // Remove all connections to this node
    this.removeNodeConnections(nodeId);
    
    // Remove the node
    this.glyphNodes.delete(nodeId);
    this.updateConstellation();
    
    console.log(`Glyph node removed: ${nodeId}`);
  }

  // Create connection between nodes
  connectNodes(nodeId1, nodeId2, connectionData = {}) {
    const node1 = this.glyphNodes.get(nodeId1);
    const node2 = this.glyphNodes.get(nodeId2);
    
    if (!node1 || !node2) {
      throw new Error('One or both nodes not found');
    }
    
    const connection = {
      id: this.generateConnectionId(),
      from: nodeId1,
      to: nodeId2,
      type: connectionData.type || 'default',
      strength: connectionData.strength || 1.0,
      properties: connectionData.properties || {},
      createdAt: new Date().toISOString()
    };
    
    // Add connection to both nodes
    node1.connections.push(connection.id);
    node2.connections.push(connection.id);
    
    this.updateConstellation();
    
    console.log(`Nodes connected: ${nodeId1} <-> ${nodeId2}`);
    return connection;
  }

  // Update constellation data structure
  updateConstellation() {
    // Convert glyph nodes to constellation format
    this.constellation.nodes = Array.from(this.glyphNodes.values()).map(node => {
      // Ensure position exists
      if (!node.position) {
        node.position = this.generateRandomPosition();
      }
      
      return {
        id: node.id,
        type: node.type,
        x: node.position.x,
        y: node.position.y,
        z: node.position.z || 0,
        size: node.properties.size || this.getDefaultNodeSize(node.type),
        color: node.properties.color || this.getNodeColor(node.type),
        label: node.properties.label || node.id,
        metadata: node.metadata
      };
    });
    
    // Update edges from connections
    this.constellation.edges = this.getActiveConnections().map(conn => ({
      id: conn.id,
      source: conn.from,
      target: conn.to,
      type: conn.type,
      strength: conn.strength,
      color: this.getConnectionColor(conn.type),
      width: this.getConnectionWidth(conn.strength)
    }));
    
    // Update metadata
    this.constellation.metadata = {
      nodeCount: this.glyphNodes.size,
      edgeCount: this.constellation.edges.length,
      lastUpdated: new Date().toISOString(),
      theme: this.activeTheme,
      rotationAngle: this.getCurrentRotationAngle()
    };
    
    this.saveConstellationData();
  }

  // Rotate the constellation
  rotateConstellation(angle) {
    const rotation = {
      id: this.generateRotationId(),
      angle,
      timestamp: new Date().toISOString(),
      affectedNodes: Array.from(this.glyphNodes.keys())
    };
    
    // Apply rotation to all nodes
    for (const node of this.glyphNodes.values()) {
      const newPosition = this.rotatePosition(node.position, angle);
      node.position = newPosition;
      node.lastUpdated = new Date().toISOString();
    }
    
    this.rotationHistory.push(rotation);
    
    // Keep only last 100 rotations
    if (this.rotationHistory.length > 100) {
      this.rotationHistory = this.rotationHistory.slice(-100);
    }
    
    this.updateConstellation();
    
    console.log(`Constellation rotated by ${angle} degrees`);
    return rotation;
  }

  // Apply theme to constellation
  applyTheme(themeName) {
    const theme = this.themes.get(themeName);
    
    if (!theme) {
      throw new Error(`Theme not found: ${themeName}`);
    }
    
    this.activeTheme = themeName;
    
    // Apply theme colors and styles to nodes
    for (const node of this.glyphNodes.values()) {
      if (!node.properties.customColor) {
        node.properties.color = this.getNodeColor(node.type, theme);
      }
      node.lastUpdated = new Date().toISOString();
    }
    
    this.updateConstellation();
    
    console.log(`Theme applied: ${themeName}`);
  }

  // Process transmutation events into glyph updates
  processTransmutationEvent(event) {
    switch (event.type) {
      case 'ci_cd':
        this.processCiCdEvent(event);
        break;
      case 'contributor_onboarding':
        this.processContributorEvent(event);
        break;
      case 'artifact_bundling':
        this.processArtifactEvent(event);
        break;
      case 'theme_rotation':
        this.processThemeEvent(event);
        break;
      default:
        this.processGenericEvent(event);
    }
  }

  // Process CI/CD events
  processCiCdEvent(event) {
    // Create or update deployment node
    const nodeId = `cicd-${this.extractBranchFromEvent(event)}`;
    
    if (this.glyphNodes.has(nodeId)) {
      this.updateGlyphNode(nodeId, {
        properties: {
          ...this.glyphNodes.get(nodeId).properties,
          lastDeployment: event.timestamp,
          deploymentCount: (this.glyphNodes.get(nodeId).properties.deploymentCount || 0) + 1
        },
        metadata: { lastEvent: event.id }
      });
    } else {
      this.addGlyphNode({
        id: nodeId,
        type: 'deployment',
        properties: {
          branch: this.extractBranchFromEvent(event),
          lastDeployment: event.timestamp,
          deploymentCount: 1,
          size: 1.2
        },
        metadata: { createdFromEvent: event.id }
      });
    }
  }

  // Process contributor events
  processContributorEvent(event) {
    const username = this.extractUsernameFromEvent(event);
    const nodeId = `contributor-${username}`;
    
    if (this.glyphNodes.has(nodeId)) {
      this.updateGlyphNode(nodeId, {
        properties: {
          ...this.glyphNodes.get(nodeId).properties,
          lastActivity: event.timestamp,
          activityCount: (this.glyphNodes.get(nodeId).properties.activityCount || 0) + 1
        }
      });
    } else {
      this.addGlyphNode({
        id: nodeId,
        type: 'contributor',
        properties: {
          username,
          joinedAt: event.timestamp,
          activityCount: 1,
          size: 1.0,
          label: username
        },
        metadata: { createdFromEvent: event.id }
      });
    }
    
    // Connect to central hub if it exists
    const hubNodeId = 'hub-central';
    if (this.glyphNodes.has(hubNodeId)) {
      this.connectNodes(nodeId, hubNodeId, {
        type: 'contribution',
        strength: 0.8
      });
    }
  }

  // Process artifact events
  processArtifactEvent(event) {
    const artifactName = this.extractArtifactFromEvent(event);
    const nodeId = `artifact-${artifactName}`;
    
    this.addGlyphNode({
      id: nodeId,
      type: 'artifact',
      properties: {
        artifactName,
        createdAt: event.timestamp,
        size: 0.8,
        label: artifactName
      },
      metadata: { createdFromEvent: event.id, ipfsHash: event.ipfsHash }
    });
  }

  // Process theme events
  processThemeEvent(event) {
    const themeName = this.extractThemeFromEvent(event);
    
    if (this.themes.has(themeName)) {
      this.applyTheme(themeName);
    }
    
    // Create theme node
    const nodeId = `theme-${themeName}`;
    this.addGlyphNode({
      id: nodeId,
      type: 'theme',
      properties: {
        themeName,
        appliedAt: event.timestamp,
        size: 0.6
      },
      metadata: { createdFromEvent: event.id }
    });
  }

  // Process generic events
  processGenericEvent(event) {
    const nodeId = `event-${event.id}`;
    
    this.addGlyphNode({
      id: nodeId,
      type: 'event',
      properties: {
        eventType: event.type,
        timestamp: event.timestamp,
        size: 0.5
      },
      metadata: { eventData: event }
    });
  }

  // Get constellation data for visualization
  getConstellationData() {
    return {
      ...this.constellation,
      themes: Array.from(this.themes.keys()),
      activeTheme: this.activeTheme,
      stats: this.getConstellationStats()
    };
  }

  // Get constellation statistics
  getConstellationStats() {
    const nodeTypes = {};
    const connectionTypes = {};
    
    for (const node of this.glyphNodes.values()) {
      nodeTypes[node.type] = (nodeTypes[node.type] || 0) + 1;
    }
    
    for (const connection of this.getActiveConnections()) {
      connectionTypes[connection.type] = (connectionTypes[connection.type] || 0) + 1;
    }
    
    return {
      totalNodes: this.glyphNodes.size,
      totalConnections: this.getActiveConnections().length,
      nodeTypes,
      connectionTypes,
      rotationCount: this.rotationHistory.length,
      lastRotation: this.rotationHistory[this.rotationHistory.length - 1]?.timestamp,
      activeTheme: this.activeTheme
    };
  }

  // Setup default themes
  setupDefaultThemes() {
    const themes = {
      cosmic: {
        name: 'Cosmic',
        colors: {
          deployment: '#4F46E5',
          contributor: '#10B981',
          artifact: '#F59E0B',
          theme: '#8B5CF6',
          event: '#6B7280',
          default: '#374151'
        },
        background: '#111827',
        connections: '#374151'
      },
      neon: {
        name: 'Neon',
        colors: {
          deployment: '#00FFFF',
          contributor: '#00FF00',
          artifact: '#FFFF00',
          theme: '#FF00FF',
          event: '#FF6600',
          default: '#FFFFFF'
        },
        background: '#000000',
        connections: '#333333'
      },
      solar: {
        name: 'Solar',
        colors: {
          deployment: '#FF6B35',
          contributor: '#F7931E',
          artifact: '#FFD23F',
          theme: '#EE4266',
          event: '#540D6E',
          default: '#F15025'
        },
        background: '#FDF2E9',
        connections: '#8B4513'
      }
    };
    
    for (const [name, theme] of Object.entries(themes)) {
      this.themes.set(name, theme);
    }
  }

  // Utility functions
  generateNodeId() {
    return `node-${Date.now()}-${Math.random().toString(36).substr(2, 6)}`;
  }

  generateConnectionId() {
    return `conn-${Date.now()}-${Math.random().toString(36).substr(2, 6)}`;
  }

  generateRotationId() {
    return `rot-${Date.now()}-${Math.random().toString(36).substr(2, 6)}`;
  }

  generateRandomPosition() {
    return {
      x: (Math.random() - 0.5) * 200,
      y: (Math.random() - 0.5) * 200,
      z: (Math.random() - 0.5) * 100
    };
  }

  rotatePosition(position, angle) {
    const radians = (angle * Math.PI) / 180;
    const cos = Math.cos(radians);
    const sin = Math.sin(radians);
    
    return {
      x: position.x * cos - position.y * sin,
      y: position.x * sin + position.y * cos,
      z: position.z
    };
  }

  getDefaultNodeSize(type) {
    const sizes = {
      deployment: 1.5,
      contributor: 1.2,
      artifact: 1.0,
      theme: 0.8,
      event: 0.6,
      default: 1.0
    };
    
    return sizes[type] || sizes.default;
  }

  getNodeColor(type, theme = null) {
    const activeTheme = theme || this.themes.get(this.activeTheme);
    
    if (activeTheme && activeTheme.colors[type]) {
      return activeTheme.colors[type];
    }
    
    return activeTheme?.colors.default || '#374151';
  }

  getConnectionColor(type) {
    const activeTheme = this.themes.get(this.activeTheme);
    return activeTheme?.connections || '#374151';
  }

  getConnectionWidth(strength) {
    return Math.max(1, strength * 3);
  }

  getCurrentRotationAngle() {
    return this.rotationHistory.reduce((total, rotation) => total + rotation.angle, 0) % 360;
  }

  getActiveConnections() {
    const connections = [];
    
    for (const node of this.glyphNodes.values()) {
      for (const connectionId of node.connections) {
        // This is a simplified approach - in a real implementation,
        // you'd have a separate connections map
        const connection = this.findConnectionById(connectionId);
        if (connection && !connections.find(c => c.id === connectionId)) {
          connections.push(connection);
        }
      }
    }
    
    return connections;
  }

  findConnectionById(connectionId) {
    // Placeholder - in a real implementation, this would look up actual connections
    return null;
  }

  removeNodeConnections(nodeId) {
    const node = this.glyphNodes.get(nodeId);
    if (node) {
      node.connections = [];
    }
  }

  // Event extraction utilities
  extractBranchFromEvent(event) {
    const match = event.details.match(/branch[:\s]+([^\s,]+)/i);
    return match ? match[1] : 'main';
  }

  extractUsernameFromEvent(event) {
    const match = event.details.match(/contributor[:\s]+([^\s,]+)/i);
    return match ? match[1] : 'unknown';
  }

  extractArtifactFromEvent(event) {
    const match = event.details.match(/Artifact bundled: (.+)/);
    return match ? match[1] : 'unknown-artifact';
  }

  extractThemeFromEvent(event) {
    const match = event.details.match(/theme[:\s]+([^\s,]+)/i);
    return match ? match[1] : 'default';
  }

  // File operations
  saveGlyphRegistry() {
    try {
      const data = Array.from(this.glyphNodes.entries());
      fs.writeFileSync(
        path.join(__dirname, 'glyph_registry.json'),
        JSON.stringify(data, null, 2)
      );
    } catch (error) {
      console.error('Failed to save glyph registry:', error);
    }
  }

  loadGlyphRegistry() {
    try {
      const filePath = path.join(__dirname, 'glyph_registry.json');
      if (fs.existsSync(filePath)) {
        const data = JSON.parse(fs.readFileSync(filePath, 'utf8'));
        this.glyphNodes = new Map(data);
        
        // Ensure all loaded nodes have proper structure
        for (const [nodeId, node] of this.glyphNodes.entries()) {
          if (!node.position) {
            node.position = this.generateRandomPosition();
          }
          if (!node.properties) {
            node.properties = {};
          }
          if (!node.connections) {
            node.connections = [];
          }
          if (!node.properties.size) {
            node.properties.size = this.getDefaultNodeSize(node.type || 'default');
          }
          if (!node.properties.color) {
            node.properties.color = this.getNodeColor(node.type || 'default');
          }
          if (!node.properties.label) {
            node.properties.label = nodeId;
          }
        }
        
        console.log(`Loaded ${this.glyphNodes.size} glyph nodes`);
      }
    } catch (error) {
      console.error('Failed to load glyph registry:', error);
      this.glyphNodes = new Map();
    }
  }

  saveConstellationData() {
    try {
      const data = {
        constellation: this.constellation,
        rotationHistory: this.rotationHistory,
        activeTheme: this.activeTheme
      };
      
      fs.writeFileSync(
        path.join(__dirname, 'constellation_data.json'),
        JSON.stringify(data, null, 2)
      );
    } catch (error) {
      console.error('Failed to save constellation data:', error);
    }
  }

  loadConstellationData() {
    try {
      const filePath = path.join(__dirname, 'constellation_data.json');
      if (fs.existsSync(filePath)) {
        const data = JSON.parse(fs.readFileSync(filePath, 'utf8'));
        this.constellation = data.constellation || { nodes: [], edges: [], metadata: {} };
        this.rotationHistory = data.rotationHistory || [];
        this.activeTheme = data.activeTheme || 'cosmic';
        console.log('Loaded constellation data');
      }
    } catch (error) {
      console.error('Failed to load constellation data:', error);
    }
  }

  loadThemeConfigurations() {
    try {
      const filePath = path.join(__dirname, 'themes.json');
      if (fs.existsSync(filePath)) {
        const data = JSON.parse(fs.readFileSync(filePath, 'utf8'));
        this.themes = new Map(Object.entries(data));
        console.log(`Loaded ${this.themes.size} themes`);
      }
    } catch (error) {
      console.error('Failed to load theme configurations:', error);
    }
  }
}

module.exports = GlyphRegistryConnector;