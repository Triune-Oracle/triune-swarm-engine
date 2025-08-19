// Handles IPFS/Web3.Storage pinning for artifact storage and transmutation events

const fs = require('fs');
const path = require('path');
const FormData = require('form-data');
const fetch = require('node-fetch');

class IpfsNodeManager {
  constructor() {
    this.web3StorageToken = process.env.WEB3_STORAGE_TOKEN;
    this.pinataApiKey = process.env.PINATA_API_KEY;
    this.pinataSecretKey = process.env.PINATA_SECRET_KEY;
    this.artifactStorage = [];
    this.initialize();
  }

  initialize() {
    console.log('IPFS Node Manager initialized');
    this.loadStorageHistory();
  }

  // Upload artifact to IPFS via Web3.Storage
  async uploadArtifactToWeb3Storage(filePath, metadata = {}) {
    try {
      if (!this.web3StorageToken) {
        throw new Error('Web3.Storage token not configured');
      }

      const fileBuffer = fs.readFileSync(filePath);
      const fileName = path.basename(filePath);
      
      const formData = new FormData();
      formData.append('file', fileBuffer, fileName);

      const response = await fetch('https://api.web3.storage/upload', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${this.web3StorageToken}`,
          ...formData.getHeaders()
        },
        body: formData
      });

      if (!response.ok) {
        throw new Error(`Web3.Storage upload failed: ${response.statusText}`);
      }

      const result = await response.json();
      const ipfsHash = result.cid;

      // Log successful upload
      const uploadRecord = {
        ipfsHash,
        fileName,
        filePath,
        uploadedAt: new Date().toISOString(),
        size: fileBuffer.length,
        metadata,
        provider: 'web3.storage'
      };

      this.artifactStorage.push(uploadRecord);
      this.saveStorageHistory();

      console.log(`Artifact uploaded to IPFS: ${ipfsHash}`);
      return { success: true, ipfsHash, url: `https://${ipfsHash}.ipfs.w3s.link` };

    } catch (error) {
      console.error('Web3.Storage upload failed:', error);
      return { success: false, error: error.message };
    }
  }

  // Upload artifact to IPFS via Pinata
  async uploadArtifactToPinata(filePath, metadata = {}) {
    try {
      if (!this.pinataApiKey || !this.pinataSecretKey) {
        throw new Error('Pinata API credentials not configured');
      }

      const fileBuffer = fs.readFileSync(filePath);
      const fileName = path.basename(filePath);
      
      const formData = new FormData();
      formData.append('file', fileBuffer, fileName);
      
      // Add metadata
      const pinataMetadata = {
        name: fileName,
        keyvalues: metadata
      };
      formData.append('pinataMetadata', JSON.stringify(pinataMetadata));

      const response = await fetch('https://api.pinata.cloud/pinning/pinFileToIPFS', {
        method: 'POST',
        headers: {
          'pinata_api_key': this.pinataApiKey,
          'pinata_secret_api_key': this.pinataSecretKey,
          ...formData.getHeaders()
        },
        body: formData
      });

      if (!response.ok) {
        throw new Error(`Pinata upload failed: ${response.statusText}`);
      }

      const result = await response.json();
      const ipfsHash = result.IpfsHash;

      // Log successful upload
      const uploadRecord = {
        ipfsHash,
        fileName,
        filePath,
        uploadedAt: new Date().toISOString(),
        size: fileBuffer.length,
        metadata,
        provider: 'pinata'
      };

      this.artifactStorage.push(uploadRecord);
      this.saveStorageHistory();

      console.log(`Artifact uploaded to IPFS via Pinata: ${ipfsHash}`);
      return { success: true, ipfsHash, url: `https://gateway.pinata.cloud/ipfs/${ipfsHash}` };

    } catch (error) {
      console.error('Pinata upload failed:', error);
      return { success: false, error: error.message };
    }
  }

  // Upload JSON data directly to IPFS
  async uploadJsonToIpfs(data, fileName = 'data.json', metadata = {}) {
    try {
      // Create temporary file
      const tempDir = path.join(__dirname, 'temp');
      if (!fs.existsSync(tempDir)) {
        fs.mkdirSync(tempDir);
      }
      
      const tempFilePath = path.join(tempDir, fileName);
      fs.writeFileSync(tempFilePath, JSON.stringify(data, null, 2));

      // Upload to IPFS
      const result = await this.uploadArtifactToWeb3Storage(tempFilePath, {
        ...metadata,
        contentType: 'application/json'
      });

      // Clean up temporary file
      fs.unlinkSync(tempFilePath);

      return result;

    } catch (error) {
      console.error('JSON upload to IPFS failed:', error);
      return { success: false, error: error.message };
    }
  }

  // Bundle multiple artifacts and upload to IPFS
  async bundleAndUploadArtifacts(artifactPaths, bundleName = 'artifact-bundle') {
    try {
      const archiver = require('archiver');
      const tempDir = path.join(__dirname, 'temp');
      if (!fs.existsSync(tempDir)) {
        fs.mkdirSync(tempDir);
      }

      const bundlePath = path.join(tempDir, `${bundleName}.zip`);
      const output = fs.createWriteStream(bundlePath);
      const archive = archiver('zip', { zlib: { level: 9 } });

      return new Promise((resolve, reject) => {
        output.on('close', async () => {
          try {
            // Upload bundle to IPFS
            const result = await this.uploadArtifactToWeb3Storage(bundlePath, {
              bundleName,
              artifactCount: artifactPaths.length,
              contentType: 'application/zip'
            });

            // Clean up bundle file
            fs.unlinkSync(bundlePath);

            if (result.success) {
              console.log(`Artifact bundle uploaded: ${result.ipfsHash}`);
            }

            resolve(result);
          } catch (error) {
            reject(error);
          }
        });

        archive.on('error', reject);
        archive.pipe(output);

        // Add files to archive
        artifactPaths.forEach(filePath => {
          if (fs.existsSync(filePath)) {
            const fileName = path.basename(filePath);
            archive.file(filePath, { name: fileName });
          }
        });

        archive.finalize();
      });

    } catch (error) {
      console.error('Artifact bundling failed:', error);
      return { success: false, error: error.message };
    }
  }

  // Store transmutation event data on IPFS
  async storeTransmutationEvent(event) {
    try {
      const eventData = {
        ...event,
        storedAt: new Date().toISOString(),
        network: 'triune-swarm-engine'
      };

      const fileName = `transmutation-${event.id || Date.now()}.json`;
      const result = await this.uploadJsonToIpfs(eventData, fileName, {
        eventType: event.type,
        eventId: event.id,
        component: 'transmutation-storage'
      });

      if (result.success) {
        console.log(`Transmutation event stored on IPFS: ${result.ipfsHash}`);
      }

      return result;

    } catch (error) {
      console.error('Failed to store transmutation event on IPFS:', error);
      return { success: false, error: error.message };
    }
  }

  // Retrieve artifact from IPFS
  async retrieveArtifact(ipfsHash, outputPath = null) {
    try {
      const gateways = [
        `https://${ipfsHash}.ipfs.w3s.link`,
        `https://gateway.pinata.cloud/ipfs/${ipfsHash}`,
        `https://ipfs.io/ipfs/${ipfsHash}`
      ];

      for (const gateway of gateways) {
        try {
          const response = await fetch(gateway);
          if (response.ok) {
            if (outputPath) {
              const buffer = await response.buffer();
              fs.writeFileSync(outputPath, buffer);
              console.log(`Artifact retrieved and saved to: ${outputPath}`);
              return { success: true, path: outputPath };
            } else {
              const data = await response.buffer();
              return { success: true, data };
            }
          }
        } catch (gatewayError) {
          console.warn(`Gateway ${gateway} failed:`, gatewayError.message);
          continue;
        }
      }

      throw new Error('All IPFS gateways failed');

    } catch (error) {
      console.error('Failed to retrieve artifact from IPFS:', error);
      return { success: false, error: error.message };
    }
  }

  // Pin artifact to ensure persistence
  async pinArtifact(ipfsHash) {
    try {
      if (!this.pinataApiKey || !this.pinataSecretKey) {
        console.warn('Pinata credentials not available for pinning');
        return { success: false, error: 'No pinning service configured' };
      }

      const response = await fetch('https://api.pinata.cloud/pinning/pinByHash', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'pinata_api_key': this.pinataApiKey,
          'pinata_secret_api_key': this.pinataSecretKey
        },
        body: JSON.stringify({
          hashToPin: ipfsHash,
          pinataMetadata: {
            name: `pinned-${ipfsHash}`,
            keyvalues: {
              pinnedAt: new Date().toISOString(),
              service: 'triune-swarm-engine'
            }
          }
        })
      });

      if (response.ok) {
        console.log(`Artifact pinned successfully: ${ipfsHash}`);
        return { success: true, ipfsHash };
      } else {
        const error = await response.text();
        throw new Error(`Pinning failed: ${error}`);
      }

    } catch (error) {
      console.error('Failed to pin artifact:', error);
      return { success: false, error: error.message };
    }
  }

  // Get storage history
  getStorageHistory() {
    return this.artifactStorage.slice().reverse(); // Return copy, newest first
  }

  // Get storage statistics
  getStorageStats() {
    const totalFiles = this.artifactStorage.length;
    const totalSize = this.artifactStorage.reduce((sum, record) => sum + (record.size || 0), 0);
    const providers = [...new Set(this.artifactStorage.map(record => record.provider))];
    
    return {
      totalFiles,
      totalSize,
      providers,
      averageSize: totalFiles > 0 ? Math.round(totalSize / totalFiles) : 0
    };
  }

  // Cleanup old storage records
  cleanupOldRecords(maxAge = 90) { // days
    const cutoffDate = new Date(Date.now() - maxAge * 24 * 60 * 60 * 1000);
    const beforeCount = this.artifactStorage.length;
    
    this.artifactStorage = this.artifactStorage.filter(record => 
      new Date(record.uploadedAt) > cutoffDate
    );
    
    const removedCount = beforeCount - this.artifactStorage.length;
    if (removedCount > 0) {
      this.saveStorageHistory();
      console.log(`Cleaned up ${removedCount} old storage records`);
    }
    
    return removedCount;
  }

  // File system operations
  saveStorageHistory() {
    try {
      fs.writeFileSync(
        path.join(__dirname, 'ipfs_storage_history.json'),
        JSON.stringify(this.artifactStorage, null, 2)
      );
    } catch (error) {
      console.error('Failed to save storage history:', error);
    }
  }

  loadStorageHistory() {
    try {
      const historyPath = path.join(__dirname, 'ipfs_storage_history.json');
      if (fs.existsSync(historyPath)) {
        const data = fs.readFileSync(historyPath, 'utf8');
        this.artifactStorage = JSON.parse(data);
        console.log(`Loaded ${this.artifactStorage.length} IPFS storage records`);
      }
    } catch (error) {
      console.error('Failed to load storage history:', error);
      this.artifactStorage = [];
    }
  }
}

module.exports = IpfsNodeManager;
