// Simulates IPFS upload from swarm output and handles transmutation event processing

const AutomationAdapter = require('./automation-adapter');
const IpfsNodeManager = require('./ipfs_node_manager');
const { EventEmitter } = require('events');

class TaskListener extends EventEmitter {
  constructor() {
    super();
    this.automationAdapter = new AutomationAdapter();
    this.ipfsManager = new IpfsNodeManager();
    this.isListening = false;
    this.taskQueue = [];
    this.walletSignatures = new Map();
    this.initialize();
  }

  initialize() {
    console.log('Task Listener initialized');
    
    // Connect to automation adapter events
    this.setupAutomationEvents();
    
    // Start listening for tasks
    this.startListening();
    
    // Setup periodic processing
    this.setupPeriodicProcessing();
  }

  setupAutomationEvents() {
    // Listen for transmutation events
    this.automationAdapter.on('transmutation-logged', (event) => {
      this.processTransmutationTask(event);
    });
    
    // Listen for artifact uploads
    this.automationAdapter.on('artifact-uploaded', (data) => {
      this.handleArtifactUploaded(data);
    });
    
    // Listen for constellation updates
    this.automationAdapter.on('constellation-update', (data) => {
      this.handleConstellationUpdate(data);
    });
    
    console.log('Automation event listeners setup complete');
  }

  startListening() {
    if (this.isListening) return;
    
    this.isListening = true;
    console.log('Task Listener started');
    
    // Simulate task generation for demonstration
    this.simulateSwarmTasks();
  }

  stopListening() {
    this.isListening = false;
    console.log('Task Listener stopped');
  }

  // Process transmutation events as tasks
  processTransmutationTask(event) {
    const task = {
      id: `task-${event.id}`,
      type: 'transmutation',
      event,
      status: 'queued',
      createdAt: new Date().toISOString(),
      priority: this.getTaskPriority(event.type)
    };
    
    this.addTaskToQueue(task);
    console.log(`Transmutation task queued: ${task.id}`);
  }

  // Add task to processing queue
  addTaskToQueue(task) {
    this.taskQueue.push(task);
    
    // Sort by priority (higher priority first)
    this.taskQueue.sort((a, b) => b.priority - a.priority);
    
    // Emit task added event
    this.emit('task-added', task);
    
    // Process queue if not already processing
    this.processTaskQueue();
  }

  // Process tasks from the queue
  async processTaskQueue() {
    if (this.taskQueue.length === 0) return;
    
    const task = this.taskQueue.shift();
    task.status = 'processing';
    task.startedAt = new Date().toISOString();
    
    this.emit('task-started', task);
    
    try {
      await this.executeTask(task);
      task.status = 'completed';
      task.completedAt = new Date().toISOString();
      this.emit('task-completed', task);
    } catch (error) {
      task.status = 'failed';
      task.error = error.message;
      task.failedAt = new Date().toISOString();
      this.emit('task-failed', task);
      console.error(`Task ${task.id} failed:`, error);
    }
    
    // Continue processing queue
    if (this.taskQueue.length > 0) {
      setTimeout(() => this.processTaskQueue(), 100);
    }
  }

  // Execute different types of tasks
  async executeTask(task) {
    switch (task.type) {
      case 'transmutation':
        await this.executeTransmutationTask(task);
        break;
      case 'ipfs_upload':
        await this.executeIpfsUploadTask(task);
        break;
      case 'wallet_verification':
        await this.executeWalletVerificationTask(task);
        break;
      case 'glyph_update':
        await this.executeGlyphUpdateTask(task);
        break;
      default:
        throw new Error(`Unknown task type: ${task.type}`);
    }
  }

  // Execute transmutation-specific tasks
  async executeTransmutationTask(task) {
    const { event } = task;
    
    switch (event.type) {
      case 'artifact_bundling':
        await this.handleArtifactBundling(event);
        break;
      case 'ci_cd':
        await this.handleCiCdProcessing(event);
        break;
      case 'contributor_onboarding':
        await this.handleContributorProcessing(event);
        break;
      case 'theme_rotation':
        await this.handleThemeProcessing(event);
        break;
      default:
        console.log(`Processing general transmutation event: ${event.type}`);
    }
  }

  // Handle artifact bundling tasks
  async handleArtifactBundling(event) {
    console.log(`Processing artifact bundling for event: ${event.id}`);
    
    // Extract artifact information from event
    const artifactName = this.extractArtifactName(event.details);
    const artifactPath = `./artifacts/${artifactName}`;
    
    // Check if artifact exists
    const fs = require('fs');
    if (!fs.existsSync(artifactPath)) {
      throw new Error(`Artifact not found: ${artifactPath}`);
    }
    
    // Upload to IPFS
    const uploadResult = await this.ipfsManager.uploadArtifactToWeb3Storage(artifactPath, {
      eventId: event.id,
      artifactType: 'bundle',
      uploadedBy: 'task-listener'
    });
    
    if (!uploadResult.success) {
      throw new Error(`IPFS upload failed: ${uploadResult.error}`);
    }
    
    // Store IPFS hash in event
    this.automationAdapter.emit('artifact-uploaded', {
      eventId: event.id,
      ipfsHash: uploadResult.ipfsHash,
      url: uploadResult.url
    });
    
    console.log(`Artifact bundled and uploaded to IPFS: ${uploadResult.ipfsHash}`);
  }

  // Handle CI/CD processing
  async handleCiCdProcessing(event) {
    console.log(`Processing CI/CD event: ${event.id}`);
    
    // Store event data on IPFS for permanent record
    const storageResult = await this.ipfsManager.storeTransmutationEvent(event);
    
    if (storageResult.success) {
      console.log(`CI/CD event stored on IPFS: ${storageResult.ipfsHash}`);
    }
    
    // Trigger wallet signature verification if needed
    if (event.details.includes('merge') || event.details.includes('deploy')) {
      await this.requestWalletSignature(event);
    }
  }

  // Handle contributor processing
  async handleContributorProcessing(event) {
    console.log(`Processing contributor onboarding: ${event.id}`);
    
    // Create contributor profile data
    const contributorData = {
      eventId: event.id,
      username: this.extractUsernameFromEvent(event),
      onboardedAt: event.timestamp,
      status: 'active'
    };
    
    // Store on IPFS
    const storageResult = await this.ipfsManager.uploadJsonToIpfs(
      contributorData,
      `contributor-${contributorData.username}.json`,
      { type: 'contributor-profile' }
    );
    
    if (storageResult.success) {
      console.log(`Contributor profile stored on IPFS: ${storageResult.ipfsHash}`);
    }
  }

  // Handle theme processing
  async handleThemeProcessing(event) {
    console.log(`Processing theme rotation: ${event.id}`);
    
    // Update glyph registry with theme changes
    const themeData = {
      eventId: event.id,
      theme: this.extractThemeFromEvent(event),
      appliedAt: event.timestamp,
      previousTheme: 'default' // This would be tracked in a real implementation
    };
    
    // Store theme configuration
    const storageResult = await this.ipfsManager.uploadJsonToIpfs(
      themeData,
      `theme-config-${Date.now()}.json`,
      { type: 'theme-configuration' }
    );
    
    if (storageResult.success) {
      console.log(`Theme configuration stored on IPFS: ${storageResult.ipfsHash}`);
    }
  }

  // Request wallet signature for verification
  async requestWalletSignature(event) {
    const signatureTask = {
      id: `signature-${event.id}`,
      type: 'wallet_verification',
      event,
      status: 'queued',
      createdAt: new Date().toISOString(),
      priority: 8 // High priority for security
    };
    
    this.addTaskToQueue(signatureTask);
  }

  // Execute wallet verification task
  async executeWalletVerificationTask(task) {
    const { event } = task;
    
    console.log(`Executing wallet verification for event: ${event.id}`);
    
    // Create message to sign
    const message = this.createSignatureMessage(event);
    
    // Store signature request
    this.walletSignatures.set(event.id, {
      message,
      timestamp: new Date().toISOString(),
      status: 'pending'
    });
    
    // Emit signature request event
    this.emit('signature-requested', {
      eventId: event.id,
      message,
      type: event.type
    });
    
    console.log(`Signature requested for event: ${event.id}`);
  }

  // Handle signature verification
  verifySignature(eventId, signature, address) {
    const signatureData = this.walletSignatures.get(eventId);
    
    if (!signatureData) {
      throw new Error(`No signature request found for event: ${eventId}`);
    }
    
    // In a real implementation, this would verify the signature cryptographically
    const isValid = this.validateSignature(signatureData.message, signature, address);
    
    if (isValid) {
      signatureData.status = 'verified';
      signatureData.signature = signature;
      signatureData.address = address;
      signatureData.verifiedAt = new Date().toISOString();
      
      this.emit('signature-verified', { eventId, address, signature });
      console.log(`Signature verified for event: ${eventId}`);
    } else {
      signatureData.status = 'invalid';
      throw new Error('Invalid signature');
    }
  }

  // Execute glyph update task
  async executeGlyphUpdateTask(task) {
    console.log(`Executing glyph update task: ${task.id}`);
    
    // Update constellation visualization
    const glyphData = {
      taskId: task.id,
      updateType: 'constellation',
      timestamp: new Date().toISOString(),
      glyphChanges: task.glyphChanges || []
    };
    
    // Store glyph update on IPFS
    const storageResult = await this.ipfsManager.uploadJsonToIpfs(
      glyphData,
      `glyph-update-${Date.now()}.json`,
      { type: 'glyph-update' }
    );
    
    if (storageResult.success) {
      console.log(`Glyph update stored on IPFS: ${storageResult.ipfsHash}`);
    }
  }

  // Handle uploaded artifacts
  handleArtifactUploaded(data) {
    console.log(`Artifact uploaded successfully: ${data.ipfsHash}`);
    
    // Pin the artifact for persistence
    this.ipfsManager.pinArtifact(data.ipfsHash)
      .then(result => {
        if (result.success) {
          console.log(`Artifact pinned: ${data.ipfsHash}`);
        }
      })
      .catch(error => {
        console.error('Failed to pin artifact:', error);
      });
  }

  // Handle constellation updates
  handleConstellationUpdate(data) {
    console.log(`Constellation update received: ${data.glyphCount} glyphs`);
    
    // Create glyph update task
    const glyphTask = {
      id: `glyph-${Date.now()}`,
      type: 'glyph_update',
      data,
      status: 'queued',
      createdAt: new Date().toISOString(),
      priority: 5
    };
    
    this.addTaskToQueue(glyphTask);
  }

  // Simulate swarm tasks for demonstration
  simulateSwarmTasks() {
    setInterval(() => {
      if (!this.isListening) return;
      
      // Randomly generate different types of tasks
      const taskTypes = ['artifact_bundling', 'contributor_onboarding', 'ci_cd', 'theme_rotation'];
      const randomType = taskTypes[Math.floor(Math.random() * taskTypes.length)];
      
      if (Math.random() < 0.3) { // 30% chance to generate a task
        const mockEvent = {
          id: `mock-${Date.now()}`,
          type: randomType,
          status: 'active',
          timestamp: new Date().toISOString(),
          details: `Simulated ${randomType} event`
        };
        
        this.processTransmutationTask(mockEvent);
      }
    }, 10000); // Check every 10 seconds
  }

  // Setup periodic processing for maintenance tasks
  setupPeriodicProcessing() {
    // Clean up old tasks every hour
    setInterval(() => {
      this.cleanupOldTasks();
    }, 60 * 60 * 1000);
    
    // Clean up old IPFS storage records weekly
    setInterval(() => {
      this.ipfsManager.cleanupOldRecords();
    }, 7 * 24 * 60 * 60 * 1000);
  }

  cleanupOldTasks() {
    const cutoffDate = new Date(Date.now() - 24 * 60 * 60 * 1000); // 24 hours ago
    const beforeCount = this.taskQueue.length;
    
    this.taskQueue = this.taskQueue.filter(task => 
      new Date(task.createdAt) > cutoffDate
    );
    
    const removedCount = beforeCount - this.taskQueue.length;
    if (removedCount > 0) {
      console.log(`Cleaned up ${removedCount} old tasks`);
    }
  }

  // Utility functions
  getTaskPriority(eventType) {
    const priorities = {
      'ci_cd': 9,
      'artifact_bundling': 7,
      'contributor_onboarding': 6,
      'theme_rotation': 4,
      'blockchain_event': 8,
      'nft_minted': 5
    };
    
    return priorities[eventType] || 3;
  }

  extractArtifactName(details) {
    const match = details.match(/Artifact bundled: (.+)/);
    return match ? match[1] : 'unknown-artifact';
  }

  extractUsernameFromEvent(event) {
    const match = event.details.match(/contributor[:\s]+([^\s,]+)/i);
    return match ? match[1] : 'unknown-user';
  }

  extractThemeFromEvent(event) {
    const match = event.details.match(/theme[:\s]+([^\s,]+)/i);
    return match ? match[1] : 'default';
  }

  createSignatureMessage(event) {
    return `Verify transmutation event: ${event.id} of type ${event.type} at ${event.timestamp}`;
  }

  validateSignature(message, signature, address) {
    // Placeholder signature validation
    // In a real implementation, this would use ethers.js to verify the signature
    return signature && signature.length > 100 && address && address.startsWith('0x');
  }

  // Public API methods
  getQueueStatus() {
    return {
      queueLength: this.taskQueue.length,
      isListening: this.isListening,
      totalProcessed: this.totalProcessed || 0
    };
  }

  getTaskHistory(limit = 50) {
    // This would return completed tasks from a persistent store
    return [];
  }
}

// Export both the class and a singleton instance
const taskListener = new TaskListener();

module.exports = { TaskListener, taskListener };
