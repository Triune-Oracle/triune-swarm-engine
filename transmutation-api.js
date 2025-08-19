// transmutation-api.js - API server for RitualNodeTransmutation integration

const express = require('express');
const cors = require('cors');
const { taskListener } = require('./task_listener');
const AutomationAdapter = require('./automation-adapter');
const IpfsNodeManager = require('./ipfs_node_manager');

const app = express();
const port = process.env.TRANSMUTATION_PORT || 3001;

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static('public'));

// Initialize services
const automationAdapter = new AutomationAdapter();
const ipfsManager = new IpfsNodeManager();

// Connect the automation adapter to task listener
automationAdapter.connectComponent('TransmutationAPI');

// API Routes

// Automation Adapter Routes
app.post('/api/automation/connect', (req, res) => {
  try {
    const { component } = req.body;
    const result = automationAdapter.connectComponent(component);
    res.json(result);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.get('/api/automation/status', (req, res) => {
  res.json({
    connectedComponents: automationAdapter.getConnectedComponents(),
    queueStatus: taskListener.getQueueStatus(),
    timestamp: new Date().toISOString()
  });
});

// Transmutation Event Routes
app.post('/api/transmutation/log', (req, res) => {
  try {
    const event = req.body;
    const result = automationAdapter.logTransmutationEvent(event);
    res.json(result);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.get('/api/transmutation/logs', (req, res) => {
  try {
    const limit = parseInt(req.query.limit) || 100;
    const logs = automationAdapter.getTransmutationLogs(limit);
    res.json(logs);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.post('/api/transmutation/trigger', (req, res) => {
  try {
    const { type, details, metadata } = req.body;
    
    const event = {
      id: `manual-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      type,
      status: 'active',
      timestamp: new Date().toISOString(),
      details: details || `Manual ${type} trigger`,
      metadata: metadata || {}
    };
    
    const result = automationAdapter.logTransmutationEvent(event);
    res.json({ success: true, event, result });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Contributor Routes
app.post('/api/contributors/onboard', (req, res) => {
  try {
    const { eventId, details } = req.body;
    
    // Process contributor onboarding
    const username = extractUsernameFromDetails(details);
    
    // Log the onboarding completion
    automationAdapter.logTransmutationEvent({
      type: 'contributor_onboarding_completed',
      status: 'completed',
      details: `Contributor ${username} onboarding processed`,
      relatedEventId: eventId
    });
    
    res.json({ 
      success: true, 
      message: `Contributor ${username} onboarded successfully`,
      username 
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.get('/api/contributors', (req, res) => {
  try {
    const fs = require('fs');
    const path = require('path');
    const contributorsPath = path.join(__dirname, 'contributors.json');
    
    if (fs.existsSync(contributorsPath)) {
      const contributors = JSON.parse(fs.readFileSync(contributorsPath, 'utf8'));
      res.json(contributors);
    } else {
      res.json([]);
    }
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Artifact Routes
app.post('/api/artifacts/bundle', async (req, res) => {
  try {
    const { eventId, details } = req.body;
    
    // Extract artifact name
    const artifactName = extractArtifactNameFromDetails(details);
    
    // Check if artifact exists
    const fs = require('fs');
    const artifactPath = `./artifacts/${artifactName}`;
    
    if (!fs.existsSync('./artifacts')) {
      fs.mkdirSync('./artifacts', { recursive: true });
    }
    
    // Create a sample artifact if it doesn't exist
    if (!fs.existsSync(artifactPath)) {
      const sampleArtifact = {
        name: artifactName,
        createdAt: new Date().toISOString(),
        eventId,
        type: 'transmutation-artifact',
        data: `Sample artifact data for ${artifactName}`
      };
      fs.writeFileSync(artifactPath, JSON.stringify(sampleArtifact, null, 2));
    }
    
    // Upload to IPFS
    const uploadResult = await ipfsManager.uploadArtifactToWeb3Storage(artifactPath, {
      eventId,
      artifactType: 'bundle',
      uploadedBy: 'transmutation-api'
    });
    
    if (uploadResult.success) {
      res.json({
        success: true,
        ipfsHash: uploadResult.ipfsHash,
        url: uploadResult.url,
        artifactName
      });
    } else {
      res.status(500).json({ 
        error: 'IPFS upload failed',
        details: uploadResult.error 
      });
    }
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.get('/api/artifacts', (req, res) => {
  try {
    const storageHistory = ipfsManager.getStorageHistory();
    res.json(storageHistory);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.get('/api/artifacts/stats', (req, res) => {
  try {
    const stats = ipfsManager.getStorageStats();
    res.json(stats);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Dashboard Routes
app.post('/api/dashboard/rotate-theme', (req, res) => {
  try {
    const { eventId, details } = req.body;
    
    const theme = extractThemeFromDetails(details);
    
    // Log theme rotation completion
    automationAdapter.logTransmutationEvent({
      type: 'theme_rotation_completed',
      status: 'completed',
      details: `Dashboard theme rotated to ${theme}`,
      relatedEventId: eventId,
      metadata: { theme }
    });
    
    res.json({ 
      success: true, 
      message: `Theme rotated to ${theme}`,
      theme 
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Wallet Signature Routes
app.post('/api/wallet/sign', (req, res) => {
  try {
    const { eventId, signature, address } = req.body;
    
    // Verify the signature using task listener
    taskListener.verifySignature(eventId, signature, address);
    
    res.json({ 
      success: true, 
      message: 'Signature verified successfully',
      eventId,
      address
    });
  } catch (error) {
    res.status(400).json({ error: error.message });
  }
});

app.get('/api/wallet/pending-signatures', (req, res) => {
  try {
    // Get pending signature requests
    const pendingSignatures = Array.from(taskListener.walletSignatures.entries())
      .filter(([_, data]) => data.status === 'pending')
      .map(([eventId, data]) => ({ eventId, ...data }));
    
    res.json(pendingSignatures);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Glyph Registry Routes
app.get('/api/glyph-registry', (req, res) => {
  try {
    const registry = automationAdapter.getGlyphRegistry();
    res.json(registry);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.post('/api/glyph-registry/update', (req, res) => {
  try {
    const { type, data } = req.body;
    
    automationAdapter.updateGlyphRegistry(type, data);
    
    res.json({ 
      success: true, 
      message: `Glyph registry updated: ${type}` 
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Scheduled Rituals Routes
app.post('/api/rituals/execute', (req, res) => {
  try {
    const { ritualType } = req.body;
    
    automationAdapter.executeScheduledRitual(ritualType);
    
    res.json({ 
      success: true, 
      message: `Ritual executed: ${ritualType}` 
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// IPFS Routes
app.post('/api/ipfs/upload', async (req, res) => {
  try {
    const { data, filename, metadata } = req.body;
    
    const result = await ipfsManager.uploadJsonToIpfs(data, filename, metadata);
    
    res.json(result);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.get('/api/ipfs/retrieve/:hash', async (req, res) => {
  try {
    const { hash } = req.params;
    
    const result = await ipfsManager.retrieveArtifact(hash);
    
    if (result.success) {
      res.json({ success: true, data: result.data.toString() });
    } else {
      res.status(404).json(result);
    }
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// CI/CD Integration Routes
app.post('/api/cicd/webhook', (req, res) => {
  try {
    const { action, branch, commit, repository } = req.body;
    
    // Log CI/CD event
    const event = {
      type: 'ci_cd',
      status: 'completed',
      details: `CI/CD ${action} on ${branch}: ${commit?.message || 'No message'}`,
      metadata: {
        action,
        branch,
        commit,
        repository: repository?.name
      }
    };
    
    automationAdapter.logTransmutationEvent(event);
    
    res.json({ 
      success: true, 
      message: 'CI/CD webhook processed',
      eventId: event.id 
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Health Check Route
app.get('/api/health', (req, res) => {
  res.json({
    status: 'healthy',
    timestamp: new Date().toISOString(),
    services: {
      automationAdapter: !!automationAdapter,
      taskListener: taskListener.isListening,
      ipfsManager: !!ipfsManager
    }
  });
});

// Error handling middleware
app.use((error, req, res, next) => {
  console.error('API Error:', error);
  res.status(500).json({ 
    error: 'Internal server error',
    message: error.message 
  });
});

// Utility functions
function extractUsernameFromDetails(details) {
  const match = details.match(/contributor[:\s]+([^\s,]+)/i);
  return match ? match[1] : 'unknown-user';
}

function extractArtifactNameFromDetails(details) {
  const match = details.match(/Artifact bundled: (.+)/);
  return match ? match[1] : `artifact-${Date.now()}.json`;
}

function extractThemeFromDetails(details) {
  const match = details.match(/theme[:\s]+([^\s,]+)/i);
  return match ? match[1] : 'default';
}

// Event listeners for real-time updates
taskListener.on('task-completed', (task) => {
  console.log(`Task completed: ${task.id}`);
});

taskListener.on('signature-requested', (data) => {
  console.log(`Signature requested for event: ${data.eventId}`);
});

automationAdapter.on('transmutation-logged', (event) => {
  console.log(`Transmutation event logged: ${event.type} - ${event.id}`);
});

// Start server
app.listen(port, () => {
  console.log(`Transmutation API server running on port ${port}`);
  console.log(`Health check: http://localhost:${port}/api/health`);
});

module.exports = app;