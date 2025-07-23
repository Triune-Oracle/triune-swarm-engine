// CID Verification Utility
// Validates IPFS Content Identifiers and checks their availability across gateways

const axios = require('axios');
const crypto = require('crypto');
const config = require('../config/pinata-config');

class CIDVerifier {
    constructor() {
        this.gateways = config.gateways;
        this.timeout = 10000; // 10 second timeout per gateway
    }

    /**
     * Verify CID exists and is accessible across multiple gateways
     */
    async verifyCID(cid, options = {}) {
        const verifyAll = options.verifyAll || false;
        const requiredGateways = options.requiredGateways || 2;
        
        console.log(`🔍 Verifying CID: ${cid}`);
        
        const results = {
            cid,
            valid: false,
            accessible: 0,
            total: this.gateways.length,
            gateways: {},
            metadata: {},
            errors: []
        };

        const promises = this.gateways.map(async (gateway) => {
            try {
                const url = `${gateway}/${cid}`;
                const response = await axios.head(url, { 
                    timeout: this.timeout,
                    validateStatus: (status) => status < 500 // Accept redirects
                });
                
                results.gateways[gateway] = {
                    accessible: true,
                    status: response.status,
                    contentType: response.headers['content-type'],
                    contentLength: response.headers['content-length'],
                    responseTime: Date.now()
                };
                
                results.accessible++;
                
                // Get metadata from first successful response
                if (!results.metadata.contentType) {
                    results.metadata = {
                        contentType: response.headers['content-type'],
                        contentLength: parseInt(response.headers['content-length']) || 0,
                        lastModified: response.headers['last-modified'],
                        etag: response.headers['etag']
                    };
                }
                
                return { gateway, success: true };
            } catch (error) {
                results.gateways[gateway] = {
                    accessible: false,
                    error: error.message,
                    status: error.response?.status
                };
                
                results.errors.push(`${gateway}: ${error.message}`);
                return { gateway, success: false, error: error.message };
            }
        });

        // Wait for all gateway checks to complete
        if (verifyAll) {
            await Promise.all(promises);
        } else {
            // Wait until we have enough successful responses or all complete
            let completed = 0;
            const gatewayResults = [];
            
            for (const promise of promises) {
                const result = await promise;
                gatewayResults.push(result);
                completed++;
                
                if (results.accessible >= requiredGateways || completed === promises.length) {
                    break;
                }
            }
        }

        // Determine if CID is considered valid
        results.valid = results.accessible >= Math.min(requiredGateways, this.gateways.length);
        
        // Log results
        if (results.valid) {
            console.log(`✅ CID verified: ${results.accessible}/${results.total} gateways accessible`);
        } else {
            console.log(`❌ CID verification failed: only ${results.accessible}/${results.total} gateways accessible`);
        }
        
        return results;
    }

    /**
     * Verify multiple CIDs in batch
     */
    async batchVerify(cids, options = {}) {
        console.log(`🔍 Batch verifying ${cids.length} CIDs...`);
        
        const concurrency = options.concurrency || 3;
        const results = [];
        
        for (let i = 0; i < cids.length; i += concurrency) {
            const batch = cids.slice(i, i + concurrency);
            const promises = batch.map(cid => this.verifyCID(cid, options));
            const batchResults = await Promise.all(promises);
            results.push(...batchResults);
            
            console.log(`📦 Verified batch ${Math.floor(i/concurrency) + 1}/${Math.ceil(cids.length/concurrency)}`);
        }
        
        const summary = {
            total: cids.length,
            valid: results.filter(r => r.valid).length,
            invalid: results.filter(r => !r.valid).length,
            averageAccessibility: results.reduce((sum, r) => sum + r.accessible, 0) / results.length
        };
        
        console.log(`📊 Batch verification complete: ${summary.valid}/${summary.total} valid CIDs`);
        console.log(`📈 Average gateway accessibility: ${summary.averageAccessibility.toFixed(1)}/${this.gateways.length}`);
        
        return {
            results,
            summary
        };
    }

    /**
     * Check if CID matches expected content hash
     */
    async verifyContentIntegrity(cid, expectedHash = null, options = {}) {
        const hashAlgorithm = options.hashAlgorithm || 'sha256';
        
        try {
            // Download content from first available gateway
            let content = null;
            let contentGateway = null;
            
            for (const gateway of this.gateways) {
                try {
                    const url = `${gateway}/${cid}`;
                    const response = await axios.get(url, { 
                        timeout: this.timeout,
                        responseType: 'arraybuffer'
                    });
                    
                    content = response.data;
                    contentGateway = gateway;
                    break;
                } catch (error) {
                    continue; // Try next gateway
                }
            }
            
            if (!content) {
                return {
                    valid: false,
                    error: 'Could not download content from any gateway'
                };
            }
            
            // Calculate content hash
            const hash = crypto.createHash(hashAlgorithm);
            hash.update(content);
            const calculatedHash = hash.digest('hex');
            
            const result = {
                valid: true,
                cid,
                contentHash: calculatedHash,
                hashAlgorithm,
                contentSize: content.length,
                downloadedFrom: contentGateway
            };
            
            // Compare with expected hash if provided
            if (expectedHash) {
                result.hashMatch = calculatedHash === expectedHash;
                result.expectedHash = expectedHash;
                
                if (!result.hashMatch) {
                    console.log(`⚠️  Hash mismatch for CID ${cid}`);
                    console.log(`   Expected: ${expectedHash}`);
                    console.log(`   Actual:   ${calculatedHash}`);
                }
            }
            
            return result;
        } catch (error) {
            return {
                valid: false,
                error: error.message
            };
        }
    }

    /**
     * Monitor CID availability over time
     */
    async monitorCID(cid, options = {}) {
        const duration = options.duration || 60000; // 1 minute default
        const interval = options.interval || 10000; // 10 seconds default
        const maxChecks = Math.floor(duration / interval);
        
        console.log(`📊 Monitoring CID ${cid} for ${duration/1000}s (${maxChecks} checks)`);
        
        const monitoring = {
            cid,
            checks: [],
            summary: {
                totalChecks: 0,
                successfulChecks: 0,
                averageAccessibility: 0,
                uptime: 0
            }
        };
        
        for (let i = 0; i < maxChecks; i++) {
            const checkStart = Date.now();
            const verification = await this.verifyCID(cid, { verifyAll: false, requiredGateways: 1 });
            const checkDuration = Date.now() - checkStart;
            
            monitoring.checks.push({
                timestamp: new Date().toISOString(),
                accessible: verification.accessible,
                total: verification.total,
                duration: checkDuration,
                valid: verification.valid
            });
            
            monitoring.summary.totalChecks++;
            if (verification.valid) {
                monitoring.summary.successfulChecks++;
            }
            
            if (i < maxChecks - 1) {
                await this.delay(interval);
            }
        }
        
        // Calculate summary statistics
        monitoring.summary.averageAccessibility = 
            monitoring.checks.reduce((sum, check) => sum + check.accessible, 0) / monitoring.checks.length;
        monitoring.summary.uptime = 
            (monitoring.summary.successfulChecks / monitoring.summary.totalChecks) * 100;
        
        console.log(`📈 Monitoring complete: ${monitoring.summary.uptime.toFixed(1)}% uptime`);
        
        return monitoring;
    }

    /**
     * Get comprehensive CID information
     */
    async getCIDInfo(cid) {
        console.log(`ℹ️  Getting comprehensive info for CID: ${cid}`);
        
        const info = {
            cid,
            timestamp: new Date().toISOString(),
            verification: null,
            integrity: null,
            pinStatus: null
        };
        
        try {
            // Basic verification
            info.verification = await this.verifyCID(cid, { verifyAll: true });
            
            // Content integrity check
            if (info.verification.valid) {
                info.integrity = await this.verifyContentIntegrity(cid);
            }
            
            // Check pin status (if we have access to the IPFS node manager)
            try {
                const IPFSNodeManager = require('../ipfs_node_manager');
                if (config.pinata.apiKey) {
                    const ipfsManager = new IPFSNodeManager(
                        config.pinata.apiKey, 
                        config.pinata.secret
                    );
                    info.pinStatus = await ipfsManager.getPinStatus(cid);
                }
            } catch (error) {
                info.pinStatus = { error: 'Could not check pin status' };
            }
            
            return info;
        } catch (error) {
            info.error = error.message;
            return info;
        }
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
        const verifier = new CIDVerifier();
        const args = process.argv.slice(2);
        
        if (args.length === 0) {
            console.log('Usage: node cid-verification.js <cid> [options]');
            console.log('Options:');
            console.log('  --all          Verify all gateways');
            console.log('  --monitor=60   Monitor for N seconds');
            console.log('  --info         Get comprehensive info');
            process.exit(1);
        }
        
        const cid = args[0];
        const options = {
            verifyAll: args.includes('--all'),
            monitor: args.find(arg => arg.startsWith('--monitor=')),
            info: args.includes('--info')
        };
        
        try {
            if (options.info) {
                const info = await verifier.getCIDInfo(cid);
                console.log(JSON.stringify(info, null, 2));
            } else if (options.monitor) {
                const duration = parseInt(options.monitor.split('=')[1]) * 1000;
                const monitoring = await verifier.monitorCID(cid, { duration });
                console.log(JSON.stringify(monitoring, null, 2));
            } else {
                const result = await verifier.verifyCID(cid, options);
                console.log(JSON.stringify(result, null, 2));
            }
        } catch (error) {
            console.error('Verification failed:', error.message);
            process.exit(1);
        }
    }
}

main();

module.exports = CIDVerifier;