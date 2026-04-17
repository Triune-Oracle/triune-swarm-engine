/**
 * tscp-integrity.js
 * TSCP-PL provenance utility — compute and verify integrity hashes for
 * Triumvirate Standup Codex Protocol (TSCP-PL) documents.
 *
 * Usage (CLI):
 *   # Sign a document (adds verification_hash + signed_at, prints result):
 *   node scripts/tscp-integrity.js sign schemas/triad_protocol.json
 *
 *   # Verify a previously signed document:
 *   node scripts/tscp-integrity.js verify schemas/triad_protocol.json
 *
 *   # Sign with an Ed25519 private key (PEM file) for immutable_signature:
 *   node scripts/tscp-integrity.js sign schemas/triad_protocol.json --key path/to/private.pem
 *
 * Programmatic API (require):
 *   const { computeHash, signDocument, verifyDocument } = require('./tscp-integrity');
 */

'use strict';

const crypto = require('crypto');
const fs = require('fs');
const path = require('path');

// ---------------------------------------------------------------------------
// Core helpers
// ---------------------------------------------------------------------------

/**
 * Returns a stable JSON string for hashing — integrity fields are excluded
 * so that signing a document is idempotent.
 * @param {object} doc
 * @returns {string}
 */
function canonicalize(doc) {
  const copy = JSON.parse(JSON.stringify(doc));
  if (copy.integrity) {
    copy.integrity.verification_hash = '';
    copy.integrity.immutable_signature = '';
    copy.integrity.signed_at = '';
  }
  // Sort keys recursively for deterministic output
  return JSON.stringify(sortKeys(copy), null, 0);
}

/**
 * Recursively sorts object keys alphabetically.
 * @param {*} value
 * @returns {*}
 */
function sortKeys(value) {
  if (Array.isArray(value)) return value.map(sortKeys);
  if (value !== null && typeof value === 'object') {
    return Object.keys(value)
      .sort()
      .reduce((acc, k) => { acc[k] = sortKeys(value[k]); return acc; }, {});
  }
  return value;
}

/**
 * Computes the SHA-256 hash of the canonical document representation.
 * @param {object} doc
 * @returns {string}  hex-encoded hash prefixed with "sha256:"
 */
function computeHash(doc) {
  const canonical = canonicalize(doc);
  const hash = crypto.createHash('sha256').update(canonical, 'utf-8').digest('hex');
  return `sha256:${hash}`;
}

/**
 * Signs the canonical representation with an Ed25519 private key.
 * @param {object} doc
 * @param {crypto.KeyObject} privateKey  Ed25519 private key
 * @returns {string}  base64url-encoded signature prefixed with "ed25519:"
 */
function sign(doc, privateKey) {
  const canonical = canonicalize(doc);
  const signature = crypto.sign(null, Buffer.from(canonical, 'utf-8'), privateKey);
  return `ed25519:${signature.toString('base64url')}`;
}

/**
 * Verifies the Ed25519 signature on a document.
 * @param {object} doc
 * @param {crypto.KeyObject} publicKey  Ed25519 public key
 * @returns {boolean}
 */
function verifySignature(doc, publicKey) {
  const stored = (doc.integrity && doc.integrity.immutable_signature) || '';
  if (!stored.startsWith('ed25519:')) return false;
  const sigBytes = Buffer.from(stored.slice('ed25519:'.length), 'base64url');
  const canonical = canonicalize(doc);
  return crypto.verify(null, Buffer.from(canonical, 'utf-8'), publicKey, sigBytes);
}

// ---------------------------------------------------------------------------
// High-level document operations
// ---------------------------------------------------------------------------

/**
 * Stamps verification_hash and signed_at into the document's integrity block.
 * Optionally adds an immutable_signature if a private key is provided.
 *
 * @param {object} doc                    Parsed TSCP-PL document
 * @param {crypto.KeyObject|null} privateKey  Optional Ed25519 private key
 * @returns {object}  A new document object with integrity fields populated
 */
function signDocument(doc, privateKey = null) {
  const stamped = JSON.parse(JSON.stringify(doc));
  if (!stamped.integrity) {
    stamped.integrity = { protocol: 'TSCP-PL', version: '1.0.0', hash_algorithm: 'sha256', signature_algorithm: 'ed25519' };
  }
  stamped.integrity.verification_hash = computeHash(stamped);
  stamped.integrity.signed_at = new Date().toISOString();
  if (privateKey) {
    stamped.integrity.immutable_signature = sign(stamped, privateKey);
  } else {
    stamped.integrity.immutable_signature = '';
  }
  return stamped;
}

/**
 * Verifies the integrity of a TSCP-PL document.
 * Checks:
 *   1. verification_hash matches the document content
 *   2. immutable_signature (if present and a public key is supplied)
 *
 * @param {object} doc
 * @param {crypto.KeyObject|null} publicKey  Optional Ed25519 public key for signature check
 * @returns {{ valid: boolean; hashMatch: boolean; signatureMatch: boolean|null; errors: string[] }}
 */
function verifyDocument(doc, publicKey = null) {
  const errors = [];
  const stored = doc.integrity && doc.integrity.verification_hash;

  if (!stored) {
    errors.push('integrity.verification_hash is missing');
    return { valid: false, hashMatch: false, signatureMatch: null, errors };
  }

  const expected = computeHash(doc);
  const hashMatch = stored === expected;
  if (!hashMatch) {
    errors.push(`Hash mismatch — stored: ${stored}, expected: ${expected}`);
  }

  let signatureMatch = null;
  if (publicKey && doc.integrity && doc.integrity.immutable_signature) {
    signatureMatch = verifySignature(doc, publicKey);
    if (!signatureMatch) {
      errors.push('Ed25519 signature verification failed');
    }
  }

  return { valid: hashMatch && (signatureMatch !== false), hashMatch, signatureMatch, errors };
}

// ---------------------------------------------------------------------------
// CLI
// ---------------------------------------------------------------------------

if (require.main === module) {
  const [,, command, filePath, ...rest] = process.argv;

  const usage = `
Usage:
  node scripts/tscp-integrity.js sign   <file.json> [--key <private.pem>]
  node scripts/tscp-integrity.js verify <file.json> [--key <public.pem>]
`.trim();

  if (!command || !filePath) {
    console.error(usage);
    process.exit(1);
  }

  const absPath = path.resolve(filePath);
  if (!fs.existsSync(absPath)) {
    console.error(`File not found: ${absPath}`);
    process.exit(1);
  }

  let doc;
  try {
    doc = JSON.parse(fs.readFileSync(absPath, 'utf-8'));
  } catch {
    console.error(`Failed to parse JSON: ${absPath}`);
    process.exit(1);
  }

  // Optional key flag
  const keyFlagIdx = rest.indexOf('--key');
  let keyPath = keyFlagIdx !== -1 ? rest[keyFlagIdx + 1] : null;
  let keyObj = null;
  if (keyPath) {
    const absKey = path.resolve(keyPath);
    if (!fs.existsSync(absKey)) {
      console.error(`Key file not found: ${absKey}`);
      process.exit(1);
    }
    const pem = fs.readFileSync(absKey, 'utf-8');
    keyObj = command === 'sign'
      ? crypto.createPrivateKey(pem)
      : crypto.createPublicKey(pem);
  }

  if (command === 'sign') {
    const signed = signDocument(doc, keyObj);
    const out = JSON.stringify(signed, null, 4);
    // Write back in-place and also print
    fs.writeFileSync(absPath, out + '\n', 'utf-8');
    console.log(out);
    console.error(`\n✓  Signed — verification_hash: ${signed.integrity.verification_hash}`);
  } else if (command === 'verify') {
    const result = verifyDocument(doc, keyObj);
    if (result.valid) {
      console.log(`✓  Document integrity verified`);
      console.log(`   Hash:      ${doc.integrity.verification_hash}`);
      console.log(`   Signed at: ${doc.integrity.signed_at || '(not set)'}`);
      if (result.signatureMatch !== null) {
        console.log(`   Signature: ${result.signatureMatch ? 'valid' : 'INVALID'}`);
      }
    } else {
      console.error('✗  Integrity verification FAILED:');
      result.errors.forEach(e => console.error(`   - ${e}`));
      process.exit(1);
    }
  } else {
    console.error(`Unknown command: ${command}`);
    console.error(usage);
    process.exit(1);
  }
}

// ---------------------------------------------------------------------------
// Exports (programmatic use)
// ---------------------------------------------------------------------------

module.exports = { computeHash, signDocument, verifyDocument, canonicalize };
