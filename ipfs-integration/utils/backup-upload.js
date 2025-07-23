// Backup Upload Utility
// Provides fallback upload mechanisms for IPFS content

const axios = require('axios');
const FormData = require('form-data');
const fs = require('fs');
const path = require('path');
const config = require('../config/pinata-config');

class BackupUploader {
    constructor() {
        this.infuraProjectId = config.infura.projectId;
        this.infuraBaseURL = config.infura.baseURL;
        this.maxRetries = 3;
        this.retryDelay = 3000;
    }

    /**
     * Upload to Infura IPFS as backup
     */
    async uploadToInfura(filePath, options = {}) {
        if (!this.infuraProjectId) {
            throw new Error('Infura project ID not configured - cannot use backup upload');
        }

        const fileName = options.name || path.basename(filePath);
        console.log(`🔄 Backup upload to Infura: ${fileName}`);

        for (let attempt = 1; attempt <= this.maxRetries; attempt++) {
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
                        },
                        timeout: 60000
                    }
                );

                const result = {
                    success: true,
                    provider: 'infura',
                    cid: response.data.Hash,
                    size: response.data.Size,
                    name: response.data.Name,
                    publicUrl: `https://ipfs.io/ipfs/${response.data.Hash}`,
                    infuraUrl: `https://infura-ipfs.io/ipfs/${response.data.Hash}`,
                    timestamp: new Date().toISOString()
                };

                console.log(`✅ Infura backup successful: ${result.cid}`);
                return result;

            } catch (error) {
                console.error(`❌ Infura backup attempt ${attempt} failed:`, error.message);
                
                if (attempt === this.maxRetries) {
                    throw new Error(`Infura backup failed after ${this.maxRetries} attempts: ${error.message}`);
                }
                
                await this.delay(this.retryDelay * attempt);
            }
        }
    }

    /**
     * Upload to Web3.Storage as secondary backup
     */
    async uploadToWeb3Storage(filePath, options = {}) {
        const web3StorageToken = process.env.WEB3_STORAGE_TOKEN;
        
        if (!web3StorageToken) {
            console.log('⚠️  Web3.Storage token not configured - skipping Web3.Storage backup');
            return { success: false, error: 'Web3.Storage token not configured' };
        }

        const fileName = options.name || path.basename(filePath);
        console.log(`🔄 Backup upload to Web3.Storage: ${fileName}`);

        try {
            const form = new FormData();
            form.append('file', fs.createReadStream(filePath), fileName);

            const response = await axios.post(
                'https://api.web3.storage/upload',
                form,
                {
                    headers: {
                        ...form.getHeaders(),
                        'Authorization': `Bearer ${web3StorageToken}`
                    },
                    timeout: 60000
                }
            );

            const result = {
                success: true,
                provider: 'web3.storage',
                cid: response.data.cid,
                publicUrl: `https://ipfs.io/ipfs/${response.data.cid}`,
                web3StorageUrl: `https://${response.data.cid}.ipfs.w3s.link`,
                timestamp: new Date().toISOString()
            };

            console.log(`✅ Web3.Storage backup successful: ${result.cid}`);
            return result;

        } catch (error) {
            console.error(`❌ Web3.Storage backup failed:`, error.message);
            return { success: false, error: error.message };
        }
    }

    /**
     * Upload to NFT.Storage as tertiary backup
     */
    async uploadToNFTStorage(filePath, options = {}) {
        const nftStorageToken = process.env.NFT_STORAGE_TOKEN;
        
        if (!nftStorageToken) {
            console.log('⚠️  NFT.Storage token not configured - skipping NFT.Storage backup');
            return { success: false, error: 'NFT.Storage token not configured' };
        }

        const fileName = options.name || path.basename(filePath);
        console.log(`🔄 Backup upload to NFT.Storage: ${fileName}`);

        try {
            const form = new FormData();
            form.append('file', fs.createReadStream(filePath), fileName);

            const response = await axios.post(
                'https://api.nft.storage/upload',
                form,
                {
                    headers: {
                        ...form.getHeaders(),
                        'Authorization': `Bearer ${nftStorageToken}`
                    },
                    timeout: 60000
                }
            );

            const result = {
                success: true,
                provider: 'nft.storage',
                cid: response.data.value.cid,
                publicUrl: `https://ipfs.io/ipfs/${response.data.value.cid}`,
                nftStorageUrl: `https://${response.data.value.cid}.ipfs.nftstorage.link`,
                timestamp: new Date().toISOString()
            };

            console.log(`✅ NFT.Storage backup successful: ${result.cid}`);
            return result;

        } catch (error) {
            console.error(`❌ NFT.Storage backup failed:`, error.message);
            return { success: false, error: error.message };
        }
    }

    /**
     * Comprehensive backup upload with multiple providers
     */
    async backupUpload(filePath, options = {}) {
        const fileName = options.name || path.basename(filePath);
        console.log(`🛡️  Starting comprehensive backup upload: ${fileName}`);

        const results = {
            fileName,
            filePath,
            timestamp: new Date().toISOString(),
            providers: {},
            successful: [],
            failed: [],
            summary: {
                total: 0,
                successful: 0,
                failed: 0
            }
        };

        // Define backup providers in order of preference
        const providers = [
            { name: 'infura', method: this.uploadToInfura.bind(this) },
            { name: 'web3.storage', method: this.uploadToWeb3Storage.bind(this) },
            { name: 'nft.storage', method: this.uploadToNFTStorage.bind(this) }
        ];

        // Attempt upload to each provider
        for (const provider of providers) {
            results.summary.total++;
            
            try {
                const result = await provider.method(filePath, options);
                results.providers[provider.name] = result;
                
                if (result.success) {
                    results.successful.push(provider.name);
                    results.summary.successful++;
                    console.log(`✅ ${provider.name} backup: SUCCESS`);
                } else {
                    results.failed.push(provider.name);
                    results.summary.failed++;
                    console.log(`❌ ${provider.name} backup: FAILED - ${result.error}`);
                }
            } catch (error) {
                results.providers[provider.name] = {
                    success: false,
                    error: error.message
                };
                results.failed.push(provider.name);
                results.summary.failed++;
                console.log(`❌ ${provider.name} backup: ERROR - ${error.message}`);
            }
        }

        // Log summary
        console.log(`🛡️  Backup upload complete: ${results.summary.successful}/${results.summary.total} providers successful`);
        
        if (results.summary.successful === 0) {
            console.log('⚠️  WARNING: All backup uploads failed!');
        } else {
            console.log(`✅ Content backed up to: ${results.successful.join(', ')}`);
        }

        return results;
    }

    /**
     * Batch backup upload
     */
    async batchBackupUpload(files, options = {}) {
        console.log(`🛡️  Starting batch backup upload of ${files.length} files`);
        
        const concurrency = options.concurrency || 2; // Lower concurrency for backups
        const results = [];

        for (let i = 0; i < files.length; i += concurrency) {
            const batch = files.slice(i, i + concurrency);
            const promises = batch.map(async (file) => {
                try {
                    const result = await this.backupUpload(file.path, file.options || {});
                    return { ...result, originalFile: file };
                } catch (error) {
                    return {
                        fileName: path.basename(file.path),
                        filePath: file.path,
                        error: error.message,
                        originalFile: file
                    };
                }
            });

            const batchResults = await Promise.all(promises);
            results.push(...batchResults);
            
            console.log(`📦 Backup batch ${Math.floor(i/concurrency) + 1}/${Math.ceil(files.length/concurrency)} complete`);
        }

        // Generate summary
        const summary = {
            totalFiles: files.length,
            successfulFiles: results.filter(r => r.summary && r.summary.successful > 0).length,
            failedFiles: results.filter(r => !r.summary || r.summary.successful === 0).length,
            providerStats: {}
        };

        // Calculate provider statistics
        const providers = ['infura', 'web3.storage', 'nft.storage'];
        providers.forEach(provider => {
            const providerResults = results.filter(r => r.providers && r.providers[provider]);
            const successful = providerResults.filter(r => r.providers[provider].success).length;
            
            summary.providerStats[provider] = {
                attempted: providerResults.length,
                successful,
                successRate: providerResults.length > 0 ? (successful / providerResults.length * 100).toFixed(1) : 0
            };
        });

        console.log(`🛡️  Batch backup complete:`);
        console.log(`   📊 Files: ${summary.successfulFiles}/${summary.totalFiles} successfully backed up`);
        Object.entries(summary.providerStats).forEach(([provider, stats]) => {
            console.log(`   📈 ${provider}: ${stats.successful}/${stats.attempted} (${stats.successRate}%)`);
        });

        return {
            results,
            summary
        };
    }

    /**
     * Restore file from backup providers
     */
    async restoreFromBackup(cid, outputPath) {
        console.log(`🔄 Attempting to restore CID ${cid} from backup providers`);

        const gateways = [
            'https://infura-ipfs.io/ipfs',
            'https://ipfs.io/ipfs',
            'https://cloudflare-ipfs.com/ipfs',
            'https://dweb.link/ipfs'
        ];

        for (const gateway of gateways) {
            try {
                const url = `${gateway}/${cid}`;
                console.log(`🔄 Trying gateway: ${gateway}`);
                
                const response = await axios.get(url, {
                    responseType: 'stream',
                    timeout: 30000
                });

                const writer = fs.createWriteStream(outputPath);
                response.data.pipe(writer);

                await new Promise((resolve, reject) => {
                    writer.on('finish', resolve);
                    writer.on('error', reject);
                });

                console.log(`✅ Successfully restored from ${gateway}`);
                return {
                    success: true,
                    gateway,
                    outputPath,
                    cid
                };

            } catch (error) {
                console.log(`❌ Failed to restore from ${gateway}: ${error.message}`);
                continue;
            }
        }

        throw new Error(`Failed to restore CID ${cid} from any backup provider`);
    }

    /**
     * Utility delay function
     */
    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}

// CLI usage
async function main() {
    if (require.main === module) {
        const backupUploader = new BackupUploader();
        const args = process.argv.slice(2);
        
        if (args.length === 0) {
            console.log('Usage:');
            console.log('  node backup-upload.js upload <file-path>');
            console.log('  node backup-upload.js restore <cid> <output-path>');
            process.exit(1);
        }
        
        const command = args[0];
        
        try {
            if (command === 'upload') {
                const filePath = args[1];
                if (!filePath || !fs.existsSync(filePath)) {
                    throw new Error('File path required and must exist');
                }
                
                const result = await backupUploader.backupUpload(filePath);
                console.log(JSON.stringify(result, null, 2));
                
            } else if (command === 'restore') {
                const cid = args[1];
                const outputPath = args[2];
                if (!cid || !outputPath) {
                    throw new Error('CID and output path required');
                }
                
                const result = await backupUploader.restoreFromBackup(cid, outputPath);
                console.log(JSON.stringify(result, null, 2));
                
            } else {
                throw new Error(`Unknown command: ${command}`);
            }
        } catch (error) {
            console.error('Operation failed:', error.message);
            process.exit(1);
        }
    }
}

main();

module.exports = BackupUploader;