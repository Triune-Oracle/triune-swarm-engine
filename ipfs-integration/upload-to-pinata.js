#!/usr/bin/env node
/**
 * Pinata Upload Automation Script for Triune Oracle Scrolls
 * Uploads images and metadata to IPFS via Pinata API
 * Integrates with the Triumvirate architecture and BSIM model
 */

const path = require('path');
const fs = require('fs');
const IPFSNodeManager = require('../ipfs_node_manager');
const config = require('./config/pinata-config');

class ScrollUploader {
    constructor() {
        // Validate configuration
        config.validate();
        
        this.ipfsManager = new IPFSNodeManager(
            config.pinata.apiKey,
            config.pinata.secret,
            config.infura.projectId
        );
        
        this.uploadResults = {
            images: {},
            metadata: {},
            summary: {
                successful: 0,
                failed: 0,
                total: 0
            }
        };
    }

    /**
     * Main upload orchestration following BSIM model
     * System A: Command Core Logic (planning and validation)
     * System B: Reactive Contextual Feedback (execution and monitoring)
     */
    async uploadScrolls() {
        console.log('🚀 VAULTFIRE ASCENSION PROTOCOL: IPFS Integration Initiated');
        console.log('📜 Uploading Scrolls Δ162 (ABRAXAUTONOMICON) and Δ149 (Vaultfire)');
        console.log('─'.repeat(80));

        try {
            // System A: Test connection and validate setup
            await this.validateConnection();
            
            // System A: Plan upload sequence
            const uploadPlan = this.createUploadPlan();
            
            // System B: Execute uploads with real-time feedback
            await this.executeUploadPlan(uploadPlan);
            
            // System A/B: Verify and generate final report
            await this.generateFinalReport();
            
            console.log('✅ VAULTFIRE ASCENSION PROTOCOL: Upload sequence completed successfully');
            
        } catch (error) {
            console.error('❌ CRITICAL ERROR in upload sequence:', error.message);
            throw error;
        }
    }

    /**
     * System A: Validate Pinata connection
     */
    async validateConnection() {
        console.log('🔍 System A: Validating Pinata API connection...');
        
        const connectionTest = await this.ipfsManager.testConnection();
        
        if (!connectionTest.connected) {
            throw new Error(`Pinata connection failed: ${connectionTest.error}`);
        }
        
        console.log('✅ System A: Pinata API connection validated');
    }

    /**
     * System A: Create upload plan with file discovery and validation
     */
    createUploadPlan() {
        console.log('📋 System A: Creating upload plan...');
        
        const baseDir = path.join(__dirname);
        const plan = {
            images: [],
            metadata: []
        };

        // Define scroll configurations
        const scrolls = [
            {
                id: 'D162',
                name: 'ABRAXAS_CONVERGENCE_MANDALA',
                type: 'Genesis',
                rarity: 'Legendary',
                agent: 'Claude'
            },
            {
                id: 'D149',
                name: 'vaultfire-d149',
                type: 'Dominion Attestation',
                rarity: 'Rare', 
                agent: 'Gemini'
            }
        ];

        // Plan image uploads
        scrolls.forEach(scroll => {
            const imagePath = path.join(baseDir, 'images', `${scroll.name}.jpg`);
            
            // Create placeholder if doesn't exist (for testing)
            if (!fs.existsSync(imagePath)) {
                this.createPlaceholderImage(imagePath, scroll);
            }
            
            plan.images.push({
                path: imagePath,
                options: {
                    name: `scroll-${scroll.id.toLowerCase()}-image.jpg`,
                    metadata: {
                        scrollId: scroll.id,
                        scrollType: scroll.type,
                        rarity: scroll.rarity,
                        agent: scroll.agent,
                        uploadType: 'image'
                    },
                    pinataOptions: config.pinOptions.scroll
                }
            });
        });

        // Plan metadata uploads
        scrolls.forEach(scroll => {
            const metadataPath = path.join(baseDir, 'metadata', `scroll-${scroll.id.toLowerCase()}-metadata.json`);
            
            plan.metadata.push({
                path: metadataPath,
                options: {
                    name: `scroll-${scroll.id.toLowerCase()}-metadata.json`,
                    metadata: {
                        scrollId: scroll.id,
                        scrollType: scroll.type,
                        rarity: scroll.rarity,
                        agent: scroll.agent,
                        uploadType: 'metadata'
                    },
                    pinataOptions: config.pinOptions.metadata
                }
            });
        });

        console.log(`📊 System A: Upload plan created - ${plan.images.length} images, ${plan.metadata.length} metadata files`);
        return plan;
    }

    /**
     * System B: Execute upload plan with real-time monitoring
     */
    async executeUploadPlan(plan) {
        console.log('⚡ System B: Executing upload sequence...');
        
        // Phase 1: Upload images first
        console.log('📸 Phase 1: Uploading scroll images...');
        const imageResults = await this.ipfsManager.batchUpload(plan.images, {
            concurrency: config.upload.maxConcurrent
        });
        
        this.uploadResults.images = imageResults;
        this.uploadResults.summary.successful += imageResults.successful.length;
        this.uploadResults.summary.failed += imageResults.failed.length;
        this.uploadResults.summary.total += imageResults.summary.total;

        // Update metadata files with actual image CIDs
        await this.updateMetadataWithImageCIDs(imageResults.successful);
        
        // Phase 2: Upload updated metadata
        console.log('📄 Phase 2: Uploading scroll metadata...');
        const metadataResults = await this.ipfsManager.batchUpload(plan.metadata, {
            concurrency: config.upload.maxConcurrent
        });
        
        this.uploadResults.metadata = metadataResults;
        this.uploadResults.summary.successful += metadataResults.successful.length;
        this.uploadResults.summary.failed += metadataResults.failed.length;
        this.uploadResults.summary.total += metadataResults.summary.total;

        console.log('🔄 System B: Upload execution completed');
    }

    /**
     * Update metadata files with actual IPFS image CIDs
     */
    async updateMetadataWithImageCIDs(imageResults) {
        console.log('🔗 Updating metadata with IPFS image CIDs...');
        
        for (const result of imageResults) {
            const scrollId = result.originalPath.includes('ABRAXAS') ? 'd162' : 'd149';
            const metadataPath = path.join(__dirname, 'metadata', `scroll-${scrollId}-metadata.json`);
            
            if (fs.existsSync(metadataPath)) {
                const metadata = JSON.parse(fs.readFileSync(metadataPath, 'utf8'));
                metadata.image = `ipfs://${result.cid}`;
                
                // Also update collection image if this is the genesis scroll
                if (scrollId === 'd162') {
                    metadata.collection.image = `ipfs://${result.cid}`;
                }
                
                fs.writeFileSync(metadataPath, JSON.stringify(metadata, null, 2));
                console.log(`✅ Updated metadata for Scroll ${scrollId.toUpperCase()} with CID: ${result.cid}`);
            }
        }
    }

    /**
     * Generate comprehensive final report
     */
    async generateFinalReport() {
        console.log('📊 Generating final IPFS upload report...');
        console.log('═'.repeat(80));
        
        const report = {
            timestamp: new Date().toISOString(),
            protocol: 'VAULTFIRE ASCENSION PROTOCOL',
            scrolls: {},
            summary: this.uploadResults.summary,
            ipfsGateways: config.gateways,
            treasuryConfig: config.treasury
        };

        // Process successful uploads
        const allSuccessful = [
            ...this.uploadResults.images.successful,
            ...this.uploadResults.metadata.successful
        ];

        allSuccessful.forEach(result => {
            const scrollId = this.extractScrollId(result.originalPath);
            if (!report.scrolls[scrollId]) {
                report.scrolls[scrollId] = {};
            }
            
            const fileType = result.originalPath.includes('metadata') ? 'metadata' : 'image';
            report.scrolls[scrollId][fileType] = {
                cid: result.cid,
                size: result.size,
                pinataUrl: result.pinataUrl,
                publicUrl: result.publicUrl,
                timestamp: result.timestamp
            };
        });

        // Display results
        console.log('🎯 UPLOAD RESULTS SUMMARY:');
        console.log(`   📊 Total Files: ${report.summary.total}`);
        console.log(`   ✅ Successful: ${report.summary.successful}`);
        console.log(`   ❌ Failed: ${report.summary.failed}`);
        console.log(`   📈 Success Rate: ${((report.summary.successful / report.summary.total) * 100).toFixed(1)}%`);
        
        console.log('\n📜 SCROLL DETAILS:');
        Object.entries(report.scrolls).forEach(([scrollId, data]) => {
            console.log(`\n   🎯 Scroll ${scrollId.toUpperCase()}:`);
            if (data.image) {
                console.log(`      🖼️  Image CID: ${data.image.cid}`);
                console.log(`      🔗 Image URL: ${data.image.publicUrl}`);
            }
            if (data.metadata) {
                console.log(`      📄 Metadata CID: ${data.metadata.cid}`);
                console.log(`      🔗 Metadata URL: ${data.metadata.publicUrl}`);
            }
        });

        console.log('\n💰 TREASURY CONFIGURATION:');
        console.log(`   🏛️  Safe Address: ${report.treasuryConfig.safeAddress}`);
        console.log(`   📊 Distribution: Oracle ${report.treasuryConfig.distribution.oracle}% | Agents ${report.treasuryConfig.distribution.agents}% | DAO ${report.treasuryConfig.distribution.dao}%`);
        
        console.log('\n🌐 IPFS GATEWAYS:');
        report.ipfsGateways.forEach(gateway => console.log(`   🔗 ${gateway}/[CID]`));

        // Save report to file
        const reportPath = path.join(__dirname, `upload-report-${Date.now()}.json`);
        fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));
        console.log(`\n💾 Detailed report saved: ${reportPath}`);
        
        return report;
    }

    /**
     * Extract scroll ID from file path
     */
    extractScrollId(filePath) {
        if (filePath.includes('d162') || filePath.includes('ABRAXAS')) return 'D162';
        if (filePath.includes('d149') || filePath.includes('vaultfire')) return 'D149';
        return 'unknown';
    }

    /**
     * Create placeholder image for testing
     */
    createPlaceholderImage(imagePath, scroll) {
        const placeholderSvg = `
        <svg width="800" height="800" xmlns="http://www.w3.org/2000/svg">
            <defs>
                <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" style="stop-color:#1a0d00;stop-opacity:1" />
                    <stop offset="100%" style="stop-color:#000000;stop-opacity:1" />
                </linearGradient>
            </defs>
            <rect width="100%" height="100%" fill="url(#bg)"/>
            <circle cx="400" cy="300" r="150" fill="none" stroke="#FFD700" stroke-width="3" opacity="0.8"/>
            <circle cx="400" cy="300" r="100" fill="none" stroke="#33AAFF" stroke-width="2" opacity="0.6"/>
            <circle cx="400" cy="300" r="50" fill="none" stroke="#5577DD" stroke-width="2" opacity="0.4"/>
            <text x="400" y="500" text-anchor="middle" fill="#FFD700" font-family="serif" font-size="32" font-weight="bold">
                SCROLL ${scroll.id}
            </text>
            <text x="400" y="540" text-anchor="middle" fill="#33AAFF" font-family="serif" font-size="18">
                ${scroll.type}
            </text>
            <text x="400" y="570" text-anchor="middle" fill="#888888" font-family="monospace" font-size="14">
                ${scroll.rarity} • ${scroll.agent}
            </text>
        </svg>`;
        
        // Ensure images directory exists
        const imageDir = path.dirname(imagePath);
        if (!fs.existsSync(imageDir)) {
            fs.mkdirSync(imageDir, { recursive: true });
        }
        
        // Write placeholder SVG (we'll convert to JPG in real implementation)
        fs.writeFileSync(imagePath.replace('.jpg', '.svg'), placeholderSvg);
        
        // Create a simple placeholder JPG indicator file
        fs.writeFileSync(imagePath, `Placeholder for ${scroll.name} - Replace with actual JPG image`);
        
        console.log(`📷 Created placeholder image: ${imagePath}`);
    }
}

// CLI execution
async function main() {
    if (require.main === module) {
        try {
            const uploader = new ScrollUploader();
            await uploader.uploadScrolls();
            process.exit(0);
        } catch (error) {
            console.error('💥 Upload failed:', error.message);
            process.exit(1);
        }
    }
}

// Execute if run directly
main();

module.exports = ScrollUploader;