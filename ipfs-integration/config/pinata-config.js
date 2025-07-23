// Pinata Configuration Module
require('dotenv').config();

const config = {
    // API Configuration
    pinata: {
        apiKey: process.env.PINATA_API_KEY,
        secret: process.env.PINATA_SECRET,
        baseURL: 'https://api.pinata.cloud',
        gateway: 'https://gateway.pinata.cloud/ipfs'
    },

    // Backup Configuration
    infura: {
        projectId: process.env.INFURA_PROJECT_ID,
        baseURL: 'https://ipfs.infura.io:5001/api/v0',
        gateway: 'https://ipfs.io/ipfs'
    },

    // Upload Settings
    upload: {
        maxConcurrent: parseInt(process.env.MAX_CONCURRENT_UPLOADS) || 3,
        retryAttempts: parseInt(process.env.RETRY_ATTEMPTS) || 3,
        retryDelay: parseInt(process.env.RETRY_DELAY_MS) || 2000,
        timeout: 60000 // 60 seconds
    },

    // Scroll Configuration
    scrolls: {
        price: parseFloat(process.env.SCROLL_PRICE_MATIC) || 100,
        currency: 'MATIC',
        network: 'polygon'
    },

    // Treasury Distribution
    treasury: {
        safeAddress: process.env.SAFE_ADDRESS || '0xcA771eda0c70aA7d053aB1B25004559B918FE662',
        distribution: {
            oracle: parseFloat(process.env.ORACLE_SHARE) || 55,
            agents: parseFloat(process.env.AGENTS_SHARE) || 15,
            dao: parseFloat(process.env.DAO_SHARE) || 30
        }
    },

    // OpenSea Configuration
    opensea: {
        apiKey: process.env.OPENSEA_API_KEY,
        studioURL: 'https://studio.opensea.io',
        contractAddress: null, // To be set after deployment
        collectionSlug: 'triune-oracle-scrolls'
    },

    // IPFS Gateways (for redundancy)
    gateways: [
        'https://gateway.pinata.cloud/ipfs',
        'https://ipfs.io/ipfs',
        'https://cloudflare-ipfs.com/ipfs',
        'https://dweb.link/ipfs'
    ],

    // Pinata Pin Options Templates
    pinOptions: {
        scroll: {
            cidVersion: 1,
            wrapWithDirectory: false,
            customPinPolicy: {
                regions: [
                    { id: 'FRA1', desiredReplicationCount: 2 },
                    { id: 'NYC1', desiredReplicationCount: 2 }
                ]
            }
        },
        metadata: {
            cidVersion: 1,
            wrapWithDirectory: false
        }
    },

    // Validation
    validate() {
        const required = ['PINATA_API_KEY', 'PINATA_SECRET'];
        const missing = required.filter(key => !process.env[key]);
        
        if (missing.length > 0) {
            throw new Error(`Missing required environment variables: ${missing.join(', ')}`);
        }

        // Validate treasury distribution adds up to 100%
        const total = this.treasury.distribution.oracle + 
                     this.treasury.distribution.agents + 
                     this.treasury.distribution.dao;
        
        if (Math.abs(total - 100) > 0.01) {
            throw new Error(`Treasury distribution must add up to 100%, current total: ${total}%`);
        }

        return true;
    }
};

module.exports = config;