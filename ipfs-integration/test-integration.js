#!/usr/bin/env node
/**
 * Test script for IPFS integration
 * Validates setup and configuration without requiring API keys
 */

const path = require('path');
const fs = require('fs');

console.log('🧪 IPFS Integration Test Suite');
console.log('═'.repeat(50));

// Test 1: Directory structure
console.log('📁 Testing directory structure...');
const requiredPaths = [
    'config/pinata-config.js',
    'config/.env.template',
    'metadata/scroll-d162-metadata.json',
    'metadata/scroll-d149-metadata.json',
    'images/ABRAXAS_CONVERGENCE_MANDALA.jpg',
    'images/vaultfire-d149.jpg',
    'utils/cid-verification.js',
    'utils/backup-upload.js',
    'upload-to-pinata.js'
];

let structureValid = true;
requiredPaths.forEach(filePath => {
    const fullPath = path.join(__dirname, filePath);
    if (fs.existsSync(fullPath)) {
        console.log(`  ✅ ${filePath}`);
    } else {
        console.log(`  ❌ ${filePath} - MISSING`);
        structureValid = false;
    }
});

// Test 2: Configuration validation
console.log('\n⚙️  Testing configuration...');
try {
    const config = require('./config/pinata-config');
    console.log('  ✅ Configuration module loads successfully');
    
    // Test config structure
    const requiredConfigKeys = ['pinata', 'upload', 'scrolls', 'treasury', 'opensea'];
    requiredConfigKeys.forEach(key => {
        if (config[key]) {
            console.log(`  ✅ Config section: ${key}`);
        } else {
            console.log(`  ⚠️  Config section missing: ${key}`);
        }
    });
    
} catch (error) {
    console.log(`  ❌ Configuration error: ${error.message}`);
}

// Test 3: Metadata validation
console.log('\n📜 Testing metadata files...');
const scrolls = ['d162', 'd149'];
scrolls.forEach(scrollId => {
    try {
        const metadataPath = path.join(__dirname, 'metadata', `scroll-${scrollId}-metadata.json`);
        const metadata = JSON.parse(fs.readFileSync(metadataPath, 'utf8'));
        
        // Validate required OpenSea fields
        const requiredFields = ['name', 'description', 'image', 'attributes'];
        const missingFields = requiredFields.filter(field => !metadata[field]);
        
        if (missingFields.length === 0) {
            console.log(`  ✅ Scroll ${scrollId.toUpperCase()} metadata valid`);
            console.log(`    📛 Name: ${metadata.name}`);
            console.log(`    🏷️  Attributes: ${metadata.attributes.length}`);
        } else {
            console.log(`  ❌ Scroll ${scrollId.toUpperCase()} missing fields: ${missingFields.join(', ')}`);
        }
    } catch (error) {
        console.log(`  ❌ Scroll ${scrollId.toUpperCase()} metadata error: ${error.message}`);
    }
});

// Test 4: Module imports
console.log('\n📦 Testing module imports...');
try {
    const IPFSNodeManager = require('../ipfs_node_manager');
    console.log('  ✅ IPFSNodeManager imports successfully');
    
    // Test class instantiation (without API keys)
    try {
        const manager = new IPFSNodeManager('test', 'test');
        console.log('  ✅ IPFSNodeManager can be instantiated');
    } catch (error) {
        console.log(`  ⚠️  IPFSNodeManager instantiation: ${error.message}`);
    }
    
} catch (error) {
    console.log(`  ❌ IPFSNodeManager import error: ${error.message}`);
}

try {
    const CIDVerifier = require('./utils/cid-verification');
    console.log('  ✅ CIDVerifier imports successfully');
} catch (error) {
    console.log(`  ❌ CIDVerifier import error: ${error.message}`);
}

try {
    const BackupUploader = require('./utils/backup-upload');
    console.log('  ✅ BackupUploader imports successfully');
} catch (error) {
    console.log(`  ❌ BackupUploader import error: ${error.message}`);
}

try {
    const ScrollUploader = require('./upload-to-pinata');
    console.log('  ✅ ScrollUploader imports successfully');
} catch (error) {
    console.log(`  ❌ ScrollUploader import error: ${error.message}`);
}

// Test 5: Dependencies
console.log('\n📚 Testing dependencies...');
const requiredDeps = ['axios', 'form-data', 'dotenv'];
requiredDeps.forEach(dep => {
    try {
        require(dep);
        console.log(`  ✅ ${dep} available`);
    } catch (error) {
        console.log(`  ❌ ${dep} missing - run: npm install ${dep}`);
    }
});

// Test 6: File permissions and sizes
console.log('\n📏 Testing file properties...');
requiredPaths.forEach(filePath => {
    const fullPath = path.join(__dirname, filePath);
    if (fs.existsSync(fullPath)) {
        const stats = fs.statSync(fullPath);
        if (stats.size > 0) {
            console.log(`  ✅ ${filePath} (${stats.size} bytes)`);
        } else {
            console.log(`  ⚠️  ${filePath} is empty`);
        }
    }
});

// Summary
console.log('\n📊 Test Summary');
console.log('═'.repeat(50));
if (structureValid) {
    console.log('✅ IPFS Integration setup appears valid');
    console.log('🚀 Ready for production use with proper API keys');
    console.log('\n📋 Next steps:');
    console.log('   1. Copy config/.env.template to .env');
    console.log('   2. Fill in your Pinata API credentials');
    console.log('   3. Replace placeholder images with actual artwork');
    console.log('   4. Run: node upload-to-pinata.js');
} else {
    console.log('❌ IPFS Integration setup has issues');
    console.log('🔧 Please fix the missing files and try again');
}

console.log('\n🔗 Resources:');
console.log('   📖 Documentation: ./README.md');
console.log('   🔑 Pinata API: https://pinata.cloud');
console.log('   🌊 OpenSea Studio: https://studio.opensea.io');
console.log('   💰 Gnosis Safe: 0xcA771eda0c70aA7d053aB1B25004559B918FE662');