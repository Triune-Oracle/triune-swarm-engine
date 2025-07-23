// Enhanced IPFS Node Manager with Pinata API Integration
// Handles IPFS/Web3.Storage pinning with fallback mechanisms

const axios = require('axios');
const FormData = require('form-data');
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

class IPFSNodeManager {
    constructor(pinataApiKey, pinataSecret, infuraProjectId = null) {
        this.pinataApiKey = pinataApiKey;
        this.pinataSecret = pinataSecret;
        this.infuraProjectId = infuraProjectId;
        this.pinataBaseURL = 'https://api.pinata.cloud';
        this.infuraBaseURL = 'https://ipfs.infura.io:5001/api/v0';
        this.maxRetries = 3;
        this.retryDelay = 2000; // 2 seconds
    }

    /**
     * Upload file to IPFS via Pinata with retry logic
     */
    async uploadFile(filePath, options = {}) {
        const fileName = options.name || path.basename(filePath);
        const metadata = options.metadata || {};
        
        for (let attempt = 1; attempt <= this.maxRetries; attempt++) {
            try {
                console.log(`Upload attempt ${attempt}/${this.maxRetries} for ${fileName}`);
                
                const form = new FormData();
                form.append('file', fs.createReadStream(filePath));
                
                const pinataMetadata = JSON.stringify({
                    name: fileName,
                    keyvalues: {
                        ...metadata,
                        uploadedAt: new Date().toISOString(),
                        scrollType: metadata.scrollType || 'unknown',
                        rarity: metadata.rarity || 'common'
                    }
                });
                
                form.append('pinataMetadata', pinataMetadata);
                
                if (options.pinataOptions) {
                    form.append('pinataOptions', JSON.stringify(options.pinataOptions));
                }

                const response = await axios.post(
                    `${this.pinataBaseURL}/pinning/pinFileToIPFS`,
                    form,
                    {
                        headers: {
                            ...form.getHeaders(),
                            'pinata_api_key': this.pinataApiKey,
                            'pinata_secret_api_key': this.pinataSecret
                        },
                        timeout: 60000 // 60 second timeout
                    }
                );

                const result = {
                    success: true,
                    cid: response.data.IpfsHash,
                    size: response.data.PinSize,
                    timestamp: response.data.Timestamp,
                    pinataUrl: `https://gateway.pinata.cloud/ipfs/${response.data.IpfsHash}`,
                    publicUrl: `https://ipfs.io/ipfs/${response.data.IpfsHash}`
                };

                console.log(`✅ Successfully uploaded ${fileName}:`, result.cid);
                return result;

            } catch (error) {
                console.error(`❌ Upload attempt ${attempt} failed:`, error.message);
                
                if (attempt === this.maxRetries) {
                    // Try fallback to Infura if available
                    if (this.infuraProjectId) {
                        console.log('🔄 Attempting fallback upload to Infura...');
                        return await this.uploadToInfura(filePath, options);
                    }
                    throw new Error(`Failed to upload ${fileName} after ${this.maxRetries} attempts: ${error.message}`);
                }
                
                await this.delay(this.retryDelay * attempt);
            }
        }
    }

    /**
     * Upload JSON metadata to IPFS
     */
    async uploadJSON(jsonData, fileName, options = {}) {
        const tempFile = path.join('/tmp', `${fileName}.json`);
        
        try {
            fs.writeFileSync(tempFile, JSON.stringify(jsonData, null, 2));
            const result = await this.uploadFile(tempFile, {
                name: fileName,
                metadata: {
                    type: 'metadata',
                    ...options.metadata
                },
                ...options
            });
            
            return result;
        } finally {
            // Clean up temp file
            if (fs.existsSync(tempFile)) {
                fs.unlinkSync(tempFile);
            }
        }
    }

    /**
     * Batch upload multiple files
     */
    async batchUpload(files, options = {}) {
        const results = [];
        const concurrency = options.concurrency || 3;
        
        console.log(`🚀 Starting batch upload of ${files.length} files (concurrency: ${concurrency})`);
        
        for (let i = 0; i < files.length; i += concurrency) {
            const batch = files.slice(i, i + concurrency);
            const promises = batch.map(async (file) => {
                try {
                    const result = await this.uploadFile(file.path, file.options || {});
                    return { ...result, originalPath: file.path };
                } catch (error) {
                    return { 
                        success: false, 
                        error: error.message, 
                        originalPath: file.path 
                    };
                }
            });
            
            const batchResults = await Promise.all(promises);
            results.push(...batchResults);
            
            console.log(`📦 Completed batch ${Math.floor(i/concurrency) + 1}/${Math.ceil(files.length/concurrency)}`);
        }
        
        const successful = results.filter(r => r.success);
        const failed = results.filter(r => !r.success);
        
        console.log(`✅ Batch upload complete: ${successful.length} successful, ${failed.length} failed`);
        
        return {
            successful,
            failed,
            summary: {
                total: files.length,
                successful: successful.length,
                failed: failed.length
            }
        };
    }

    /**
     * Verify CID integrity
     */
    async verifyCID(cid) {
        try {
            const response = await axios.head(`https://gateway.pinata.cloud/ipfs/${cid}`, {
                timeout: 10000
            });
            
            return {
                valid: response.status === 200,
                contentLength: response.headers['content-length'],
                contentType: response.headers['content-type']
            };
        } catch (error) {
            return {
                valid: false,
                error: error.message
            };
        }
    }

    /**
     * Get pin status from Pinata
     */
    async getPinStatus(cid) {
        try {
            const response = await axios.get(
                `${this.pinataBaseURL}/data/pinList?hashContains=${cid}`,
                {
                    headers: {
                        'pinata_api_key': this.pinataApiKey,
                        'pinata_secret_api_key': this.pinataSecret
                    }
                }
            );

            const pins = response.data.rows;
            if (pins.length > 0) {
                return {
                    pinned: true,
                    status: pins[0].status,
                    pinDate: pins[0].date_pinned,
                    metadata: pins[0].metadata
                };
            }
            
            return { pinned: false };
        } catch (error) {
            throw new Error(`Failed to get pin status: ${error.message}`);
        }
    }

    /**
     * Fallback upload to Infura
     */
    async uploadToInfura(filePath, options = {}) {
        if (!this.infuraProjectId) {
            throw new Error('Infura project ID not configured');
        }
        
        try {
            const form = new FormData();
            form.append('file', fs.createReadStream(filePath));
            
            const response = await axios.post(
                `${this.infuraBaseURL}/add`,
                form,
                {
                    headers: {
                        ...form.getHeaders(),
                        'Authorization': `Basic ${Buffer.from(this.infuraProjectId + ':').toString('base64')}`
                    }
                }
            );
            
            return {
                success: true,
                cid: response.data.Hash,
                size: response.data.Size,
                provider: 'infura',
                publicUrl: `https://ipfs.io/ipfs/${response.data.Hash}`
            };
        } catch (error) {
            throw new Error(`Infura fallback failed: ${error.message}`);
        }
    }

    /**
     * Utility function to add delay
     */
    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    /**
     * Generate deterministic CID for content (for verification)
     */
    generateContentHash(content) {
        return crypto.createHash('sha256').update(content).digest('hex');
    }

    /**
     * Test connection to Pinata API
     */
    async testConnection() {
        try {
            const response = await axios.get(
                `${this.pinataBaseURL}/data/testAuthentication`,
                {
                    headers: {
                        'pinata_api_key': this.pinataApiKey,
                        'pinata_secret_api_key': this.pinataSecret
                    }
                }
            );
            
            return {
                connected: true,
                message: response.data.message
            };
        } catch (error) {
            return {
                connected: false,
                error: error.message
            };
        }
    }
}

module.exports = IPFSNodeManager;
