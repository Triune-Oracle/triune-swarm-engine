// wallet-signature-verifier.js - Enhanced wallet signature verification for transmutation events

const fs = require('fs');
const path = require('path');

// Try to import ethers, fallback to demo mode if not available
let ethers;
try {
  ethers = require('ethers');
} catch (e) {
  console.log('⚠️  Ethers.js not available, running in demo mode');
  ethers = null;
}

class WalletSignatureVerifier {
  constructor() {
    this.pendingSignatures = new Map();
    this.verifiedSignatures = new Map();
    this.trustedAddresses = new Set();
    this.signatureHistory = [];
    this.initialize();
  }

  initialize() {
    this.loadTrustedAddresses();
    this.loadSignatureHistory();
    console.log('Wallet Signature Verifier initialized');
  }

  // Request signature for a transmutation event
  requestSignature(event, requiredSigner = null) {
    const signatureId = this.generateSignatureId();
    const message = this.createSignatureMessage(event);
    
    // Create message hash without ethers for demo
    const messageHash = 'demo-hash-' + Date.now();
    
    const signatureRequest = {
      id: signatureId,
      eventId: event.id,
      message,
      messageHash,
      event,
      requiredSigner,
      requestedAt: new Date().toISOString(),
      status: 'pending',
      expiresAt: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString() // 24 hours
    };
    
    this.pendingSignatures.set(signatureId, signatureRequest);
    this.saveSignatureHistory();
    
    console.log(`Signature requested: ${signatureId} for event: ${event.id}`);
    return signatureRequest;
  }

  // Verify a signature
  async verifySignature(signatureId, signature, signerAddress) {
    const request = this.pendingSignatures.get(signatureId);
    
    if (!request) {
      throw new Error(`Signature request not found: ${signatureId}`);
    }
    
    if (request.status !== 'pending') {
      throw new Error(`Signature request already processed: ${signatureId}`);
    }
    
    // Check if expired
    if (new Date() > new Date(request.expiresAt)) {
      request.status = 'expired';
      throw new Error(`Signature request expired: ${signatureId}`);
    }
    
    // Check required signer if specified
    if (request.requiredSigner && request.requiredSigner.toLowerCase() !== signerAddress.toLowerCase()) {
      throw new Error(`Invalid signer. Required: ${request.requiredSigner}, Provided: ${signerAddress}`);
    }
    
    try {
      // Verify the signature
      const isValid = await this.validateEthereumSignature(request.message, signature, signerAddress);
      
      if (!isValid) {
        request.status = 'invalid';
        throw new Error('Invalid signature');
      }
      
      // Mark as verified
      request.status = 'verified';
      request.signature = signature;
      request.signerAddress = signerAddress;
      request.verifiedAt = new Date().toISOString();
      
      // Move to verified signatures
      this.verifiedSignatures.set(signatureId, request);
      this.pendingSignatures.delete(signatureId);
      
      // Add to signature history
      this.signatureHistory.push({
        signatureId,
        eventId: request.eventId,
        eventType: request.event.type,
        signerAddress,
        verifiedAt: request.verifiedAt,
        message: request.message.substring(0, 100) + '...' // Truncate for storage
      });
      
      this.saveSignatureHistory();
      
      console.log(`Signature verified: ${signatureId} by ${signerAddress}`);
      return request;
      
    } catch (error) {
      request.status = 'failed';
      request.error = error.message;
      throw error;
    }
  }

  // Validate Ethereum signature
  async validateEthereumSignature(message, signature, expectedAddress) {
    try {
      // Check if ethers is available
      if (!ethers) {
        // Demo mode validation
        const isValidSignature = signature.startsWith('0x') && signature.length > 100;
        const isValidAddress = expectedAddress.startsWith('0x') && expectedAddress.length === 42;
        return isValidSignature && isValidAddress;
      }
      
      // Production mode with ethers.js
      const messageHash = ethers.utils.hashMessage(message);
      const recoveredAddress = ethers.utils.recoverAddress(messageHash, signature);
      const isValidAddress = recoveredAddress.toLowerCase() === expectedAddress.toLowerCase();
      
      if (!isValidAddress) {
        console.log(`Address mismatch: expected ${expectedAddress}, recovered ${recoveredAddress}`);
        return false;
      }
      
      return true;
      
    } catch (error) {
      console.error('Signature validation error:', error);
      return false;
    }
  }

  // Create standardized signature message
  createSignatureMessage(event) {
    const message = [
      'Triune Swarm Engine - Transmutation Event Verification',
      '',
      `Event ID: ${event.id}`,
      `Event Type: ${event.type}`,
      `Timestamp: ${event.timestamp}`,
      `Details: ${event.details}`,
      '',
      'By signing this message, you verify the authenticity',
      'and authorize the processing of this transmutation event.',
      '',
      `Nonce: ${Date.now()}`
    ].join('\n');
    
    return message;
  }

  // Multi-signature verification for critical events
  async requestMultiSignature(event, requiredSigners, threshold = null) {
    if (!threshold) {
      threshold = Math.ceil(requiredSigners.length / 2); // Majority by default
    }
    
    const multiSigId = this.generateMultiSigId();
    const signatures = {};
    
    // Create individual signature requests
    const requests = requiredSigners.map(signer => {
      const request = this.requestSignature(event, signer);
      signatures[signer] = { requestId: request.id, status: 'pending' };
      return request;
    });
    
    const multiSigRequest = {
      id: multiSigId,
      eventId: event.id,
      requiredSigners,
      threshold,
      signatures,
      requests: requests.map(r => r.id),
      status: 'pending',
      createdAt: new Date().toISOString(),
      expiresAt: new Date(Date.now() + 48 * 60 * 60 * 1000).toISOString() // 48 hours
    };
    
    console.log(`Multi-signature request created: ${multiSigId} (${threshold}/${requiredSigners.length} required)`);
    return multiSigRequest;
  }

  // Check multi-signature completion
  checkMultiSignatureStatus(multiSigId) {
    // This would be implemented to track multi-sig progress
    // For now, return a placeholder
    return {
      id: multiSigId,
      status: 'pending',
      completedSignatures: 0,
      requiredSignatures: 0
    };
  }

  // Add trusted address
  addTrustedAddress(address, metadata = {}) {
    const normalizedAddress = address.toLowerCase();
    this.trustedAddresses.add(normalizedAddress);
    
    this.saveTrustedAddresses();
    
    console.log(`Trusted address added: ${address}`);
  }

  // Remove trusted address
  removeTrustedAddress(address) {
    const normalizedAddress = address.toLowerCase();
    this.trustedAddresses.delete(normalizedAddress);
    
    this.saveTrustedAddresses();
    
    console.log(`Trusted address removed: ${address}`);
  }

  // Check if address is trusted
  isTrustedAddress(address) {
    return this.trustedAddresses.has(address.toLowerCase());
  }

  // Get pending signature requests
  getPendingSignatures() {
    return Array.from(this.pendingSignatures.values());
  }

  // Get verified signatures
  getVerifiedSignatures(limit = 100) {
    return Array.from(this.verifiedSignatures.values()).slice(-limit);
  }

  // Get signature history
  getSignatureHistory(limit = 100) {
    return this.signatureHistory.slice(-limit).reverse();
  }

  // Cleanup expired signatures
  cleanupExpiredSignatures() {
    const now = new Date();
    let expiredCount = 0;
    
    for (const [id, request] of this.pendingSignatures.entries()) {
      if (new Date(request.expiresAt) < now) {
        request.status = 'expired';
        this.pendingSignatures.delete(id);
        expiredCount++;
      }
    }
    
    if (expiredCount > 0) {
      console.log(`Cleaned up ${expiredCount} expired signature requests`);
    }
    
    return expiredCount;
  }

  // Get signature statistics
  getSignatureStats() {
    const totalRequests = this.signatureHistory.length;
    const verifiedCount = this.signatureHistory.filter(s => s.verifiedAt).length;
    const pendingCount = this.pendingSignatures.size;
    const trustedAddressCount = this.trustedAddresses.size;
    
    return {
      totalRequests,
      verifiedCount,
      pendingCount,
      trustedAddressCount,
      verificationRate: totalRequests > 0 ? (verifiedCount / totalRequests * 100).toFixed(2) + '%' : '0%'
    };
  }

  // Batch verify signatures
  async batchVerifySignatures(verifications) {
    const results = [];
    
    for (const verification of verifications) {
      try {
        const result = await this.verifySignature(
          verification.signatureId,
          verification.signature,
          verification.signerAddress
        );
        results.push({ success: true, signatureId: verification.signatureId, result });
      } catch (error) {
        results.push({ 
          success: false, 
          signatureId: verification.signatureId, 
          error: error.message 
        });
      }
    }
    
    return results;
  }

  // Export signature data for audit
  exportSignatureAudit(startDate = null, endDate = null) {
    let auditData = this.signatureHistory;
    
    if (startDate) {
      auditData = auditData.filter(s => new Date(s.verifiedAt) >= new Date(startDate));
    }
    
    if (endDate) {
      auditData = auditData.filter(s => new Date(s.verifiedAt) <= new Date(endDate));
    }
    
    return {
      exportedAt: new Date().toISOString(),
      dateRange: { startDate, endDate },
      totalSignatures: auditData.length,
      signatures: auditData,
      trustedAddresses: Array.from(this.trustedAddresses)
    };
  }

  // File operations
  saveTrustedAddresses() {
    try {
      const data = Array.from(this.trustedAddresses);
      fs.writeFileSync(
        path.join(__dirname, 'trusted_addresses.json'),
        JSON.stringify(data, null, 2)
      );
    } catch (error) {
      console.error('Failed to save trusted addresses:', error);
    }
  }

  loadTrustedAddresses() {
    try {
      const filePath = path.join(__dirname, 'trusted_addresses.json');
      if (fs.existsSync(filePath)) {
        const data = JSON.parse(fs.readFileSync(filePath, 'utf8'));
        this.trustedAddresses = new Set(data);
        console.log(`Loaded ${this.trustedAddresses.size} trusted addresses`);
      }
    } catch (error) {
      console.error('Failed to load trusted addresses:', error);
      this.trustedAddresses = new Set();
    }
  }

  saveSignatureHistory() {
    try {
      const data = {
        pendingSignatures: Array.from(this.pendingSignatures.entries()),
        verifiedSignatures: Array.from(this.verifiedSignatures.entries()),
        signatureHistory: this.signatureHistory
      };
      
      fs.writeFileSync(
        path.join(__dirname, 'signature_history.json'),
        JSON.stringify(data, null, 2)
      );
    } catch (error) {
      console.error('Failed to save signature history:', error);
    }
  }

  loadSignatureHistory() {
    try {
      const filePath = path.join(__dirname, 'signature_history.json');
      if (fs.existsSync(filePath)) {
        const data = JSON.parse(fs.readFileSync(filePath, 'utf8'));
        
        this.pendingSignatures = new Map(data.pendingSignatures || []);
        this.verifiedSignatures = new Map(data.verifiedSignatures || []);
        this.signatureHistory = data.signatureHistory || [];
        
        console.log(`Loaded signature history: ${this.signatureHistory.length} records`);
      }
    } catch (error) {
      console.error('Failed to load signature history:', error);
      this.pendingSignatures = new Map();
      this.verifiedSignatures = new Map();
      this.signatureHistory = [];
    }
  }

  // Utility functions
  generateSignatureId() {
    return `sig-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }

  generateMultiSigId() {
    return `multisig-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }
}

module.exports = WalletSignatureVerifier;