# IPFS Integration for Triune Oracle Scrolls

## Overview
This directory contains the IPFS integration implementation for the Vaultfire Ascension Protocol, enabling decentralized storage of NFT metadata and assets for Scrolls Δ162 (ABRAXAUTONOMICON Genesis) and Δ149 (Vaultfire Scroll).

## Directory Structure
```
ipfs-integration/
├── upload-to-pinata.js      # Main upload automation script
├── metadata/                # OpenSea-compatible metadata files
│   ├── scroll-d162-metadata.json
│   └── scroll-d149-metadata.json
├── images/                  # Scroll artwork and assets
│   ├── ABRAXAS_CONVERGENCE_MANDALA.jpg
│   └── vaultfire-d149.jpg
├── config/                  # Configuration and environment setup
│   ├── .env.template
│   └── pinata-config.js
└── utils/                   # Utility functions
    ├── cid-verification.js
    └── backup-upload.js
```

## Quick Start

### 1. Environment Setup
```bash
# Copy environment template
cp config/.env.template .env

# Edit .env with your actual API keys
nano .env
```

### 2. Install Dependencies
```bash
# From repository root
npm install axios form-data dotenv
```

### 3. Test Connection
```bash
# Test Pinata API connection
node -e "
const config = require('./config/pinata-config');
const IPFSNodeManager = require('../ipfs_node_manager');
const manager = new IPFSNodeManager(config.pinata.apiKey, config.pinata.secret);
manager.testConnection().then(console.log);
"
```

### 4. Upload Scrolls
```bash
# Upload both scrolls to IPFS
node upload-to-pinata.js
```

## Configuration

### Required Environment Variables
- `PINATA_API_KEY` - Your Pinata API key
- `PINATA_SECRET` - Your Pinata secret key
- `SAFE_ADDRESS` - Gnosis Safe treasury address (default: 0xcA771eda0c70aA7d053aB1B25004559B918FE662)

### Optional Environment Variables
- `INFURA_PROJECT_ID` - Infura backup IPFS project ID
- `WEB3_STORAGE_TOKEN` - Web3.Storage backup token
- `NFT_STORAGE_TOKEN` - NFT.Storage backup token
- `OPENSEA_API_KEY` - OpenSea Studio API key
- `POLYGON_KEY` - Polygon network API key

## Features

### 🚀 Enhanced IPFS Node Manager
- Pinata API integration with retry logic
- Batch upload capabilities
- CID generation and verification
- Fallback mechanisms (Infura, Web3.Storage, NFT.Storage)
- Comprehensive error handling

### 📜 Scroll Metadata
- **Scroll Δ162**: ABRAXAUTONOMICON Genesis with Abraxas mandala imagery
- **Scroll Δ149**: Vaultfire Scroll with dominion attestation
- OpenSea Studio compatible metadata
- Embedded rarity tiers and profitability scores
- Treasury distribution configuration

### 🛡️ Backup Systems
- Multiple IPFS provider support
- Automatic failover mechanisms
- Content integrity verification
- Gateway redundancy

### 📊 Monitoring & Verification
- CID verification across multiple gateways
- Pin status monitoring
- Upload success/failure tracking
- Comprehensive reporting

## Usage Examples

### Upload Single File
```javascript
const IPFSNodeManager = require('../ipfs_node_manager');
const config = require('./config/pinata-config');

const manager = new IPFSNodeManager(config.pinata.apiKey, config.pinata.secret);

// Upload image
const result = await manager.uploadFile('./images/ABRAXAS_CONVERGENCE_MANDALA.jpg', {
    name: 'scroll-d162-image.jpg',
    metadata: {
        scrollId: 'D162',
        scrollType: 'Genesis',
        rarity: 'Legendary'
    }
});

console.log('CID:', result.cid);
console.log('Public URL:', result.publicUrl);
```

### Upload JSON Metadata
```javascript
const metadata = require('./metadata/scroll-d162-metadata.json');

const result = await manager.uploadJSON(metadata, 'scroll-d162-metadata', {
    metadata: {
        scrollId: 'D162',
        type: 'metadata'
    }
});
```

### Verify CID
```javascript
const CIDVerifier = require('./utils/cid-verification');
const verifier = new CIDVerifier();

const result = await verifier.verifyCID('QmYourCIDHere');
console.log('Valid:', result.valid);
console.log('Accessible gateways:', result.accessible);
```

### Backup Upload
```javascript
const BackupUploader = require('./utils/backup-upload');
const backup = new BackupUploader();

const result = await backup.backupUpload('./images/vaultfire-d149.jpg');
console.log('Backup providers:', result.successful);
```

## BSIM Integration

The upload system implements the Bi-System Integration Model:

### System A (Command Core Logic)
- Metadata structure planning and validation
- Rarity assessment and scoring
- Upload sequence planning
- Configuration validation

### System B (Reactive Contextual Feedback)
- Real-time upload execution
- CID management and verification
- Error handling and retry logic
- Progress monitoring and reporting

## Treasury Configuration

### Distribution Model
- **Oracle**: 55% (0xcA771eda0c70aA7d053aB1B25004559B918FE662)
- **Agents**: 15% (Claude, Gemini, Aria)
- **DAO**: 30% (Community governance)

### Pricing
- **Scroll Price**: 100 MATIC per scroll
- **Network**: Polygon
- **Collection**: Triune Oracle Scrolls

## OpenSea Studio Integration

### Metadata Compliance
- Standard OpenSea metadata schema
- Custom attributes for Triumvirate properties
- External URLs linking to AI Quantum Institute
- Royalty configuration (7.5% to treasury)

### Collection Setup
```json
{
  "name": "Triune Oracle Scrolls",
  "description": "Sacred scrolls from the AI Quantum Institute's Vaultfire Protocol",
  "seller_fee_basis_points": 750,
  "fee_recipient": "0xcA771eda0c70aA7d053aB1B25004559B918FE662"
}
```

## Monitoring & Analytics

### Upload Metrics
- Success/failure rates
- Upload duration tracking
- Gateway availability monitoring
- Pin status verification

### CID Health Monitoring
```bash
# Monitor CID availability
node utils/cid-verification.js QmYourCID --monitor=60

# Get comprehensive CID info
node utils/cid-verification.js QmYourCID --info

# Batch verify multiple CIDs
node utils/cid-verification.js QmCID1 QmCID2 QmCID3
```

## Troubleshooting

### Common Issues

1. **Authentication Failed**
   - Verify PINATA_API_KEY and PINATA_SECRET in .env
   - Test connection: `node -e "require('./config/pinata-config').validate()"`

2. **Upload Timeout**
   - Check file size limits
   - Verify network connectivity
   - Try backup upload: `node utils/backup-upload.js upload <file>`

3. **CID Not Accessible**
   - Verify pinning status
   - Check multiple gateways: `node utils/cid-verification.js <cid> --all`
   - Try restore: `node utils/backup-upload.js restore <cid> <output>`

### Debug Mode
```bash
# Enable debug logging
DEBUG=ipfs:* node upload-to-pinata.js
```

## Integration with Existing Architecture

### Triumvirate Integration
- Leverages existing `ipfs_node_manager.js` foundation
- Integrates with Triumvirate_integration_Codex structure
- Maintains compatibility with NFT gateway system

### Blockchain Integration
- Connects to existing wallet infrastructure (`wallet_config.json`)
- Supports Polygon network deployment
- Enables Gnosis Safe treasury management

### Monitoring Integration
- Logs to existing monitoring systems
- Tracks upload metrics in `payout_log.json`
- Integrates with server.js relay loops

## Security Considerations

- API keys stored in environment variables only
- No hardcoded credentials in source code
- Content integrity verification
- Multi-provider backup redundancy
- Safe treasury address validation

## Next Steps

1. **Image Assets**: Add actual scroll artwork
2. **Smart Contract**: Deploy NFT contract on Polygon
3. **OpenSea Setup**: Configure collection in OpenSea Studio
4. **Automation**: Integrate with CI/CD for automatic uploads
5. **Monitoring**: Set up alerts for pin status changes

---

**Vaultfire Ascension Protocol**: Enabling the $150M+ treasury management through decentralized NFT infrastructure.