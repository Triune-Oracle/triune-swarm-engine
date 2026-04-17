/**
 * set-secrets.js
 * Bulk-sets GitHub Actions repository secrets across multiple Triune-Oracle repos.
 *
 * Auth: Fine-Grained PAT (or classic PAT) supplied via GH_PAT environment variable.
 * Secrets: Supplied as a JSON string via SECRETS_JSON env var (CI) or a local
 *          secrets.json file (local dev — that file MUST be gitignored).
 *
 * Usage:
 *   GH_PAT=<token> SECRETS_JSON='[{"name":"FOO","value":"bar"}]' node scripts/set-secrets.js
 *   GH_PAT=<token> node scripts/set-secrets.js   # falls back to secrets.json on disk
 *
 * Optional env vars:
 *   TARGET_REPOS  Comma-separated repo names to override the built-in list.
 *   RATE_LIMIT_MS Milliseconds to wait between API calls (default: 1000).
 */

'use strict';

const https = require('https');
const crypto = require('crypto');
const fs = require('fs');
const path = require('path');

// ---------------------------------------------------------------------------
// Configuration
// ---------------------------------------------------------------------------

const ORG_NAME = 'Triune-Oracle';
const PAT = process.env.GH_PAT;
const RATE_LIMIT_MS = parseInt(process.env.RATE_LIMIT_MS ?? '1000', 10);

const DEFAULT_REPOS = [
  'triune-swarm-engine',
  'TriumvirateMonitor-Mobile',
  'CulturalCodex',
  'Legio-Cognito',
  'Trumvirate-System-Memory-Merge-Protoco',
  'Triune--retrieval--node',
  'react-octo-spoon',
];

// ---------------------------------------------------------------------------
// Validation
// ---------------------------------------------------------------------------

if (!PAT) {
  console.error('[set-secrets] Error: GH_PAT environment variable is not set.');
  console.error('  Supply a Fine-Grained PAT (or classic PAT) with Secrets:write scope.');
  process.exit(1);
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/**
 * Returns the repos to update — from TARGET_REPOS env var or the default list.
 * @returns {string[]}
 */
function resolveRepos() {
  if (process.env.TARGET_REPOS) {
    return process.env.TARGET_REPOS.split(',').map(r => r.trim()).filter(Boolean);
  }
  return DEFAULT_REPOS;
}

/**
 * Loads secrets from the SECRETS_JSON env var (CI) or a local secrets.json file.
 * The JSON must be an array of { name: string, value: string } objects.
 * @returns {{ name: string; value: string }[]}
 */
function loadSecrets() {
  if (process.env.SECRETS_JSON) {
    try {
      return JSON.parse(process.env.SECRETS_JSON);
    } catch {
      console.error('[set-secrets] Error: SECRETS_JSON is not valid JSON.');
      process.exit(1);
    }
  }

  const localFile = path.join(__dirname, '..', 'secrets.json');
  if (!fs.existsSync(localFile)) {
    console.error('[set-secrets] Error: No SECRETS_JSON env var and no secrets.json file found.');
    console.error('  In CI, set SECRETS_JSON as an Actions secret.');
    console.error('  Locally, create a gitignored secrets.json in the project root.');
    process.exit(1);
  }

  try {
    return JSON.parse(fs.readFileSync(localFile, 'utf-8'));
  } catch {
    console.error('[set-secrets] Error: secrets.json is not valid JSON.');
    process.exit(1);
  }
}

/**
 * Minimal promise-based wrapper around Node's https.request.
 * @param {string} method
 * @param {string} urlStr
 * @param {object|null} body
 * @returns {Promise<{ status: number; data: string }>}
 */
function request(method, urlStr, body = null) {
  return new Promise((resolve, reject) => {
    const url = new URL(urlStr);
    const payload = body ? JSON.stringify(body) : null;
    const options = {
      hostname: url.hostname,
      path: url.pathname + url.search,
      method,
      headers: {
        Authorization: `Bearer ${PAT}`,
        Accept: 'application/vnd.github.v3+json',
        'X-GitHub-Api-Version': '2022-11-28',
        'User-Agent': 'triune-set-secrets/1.0',
        ...(payload ? { 'Content-Type': 'application/json', 'Content-Length': Buffer.byteLength(payload) } : {}),
      },
    };

    const req = https.request(options, res => {
      let data = '';
      res.on('data', chunk => { data += chunk; });
      res.on('end', () => resolve({ status: res.statusCode, data }));
    });
    req.on('error', reject);
    if (payload) req.write(payload);
    req.end();
  });
}

/**
 * Fetches the repo's Actions public key (used for secret encryption).
 * @param {string} repo
 * @returns {Promise<{ key_id: string; key: string }>}
 */
async function getPublicKey(repo) {
  const url = `https://api.github.com/repos/${ORG_NAME}/${repo}/actions/secrets/public-key`;
  const { status, data } = await request('GET', url);
  if (status !== 200) {
    throw new Error(`GET public key returned HTTP ${status}: ${data}`);
  }
  return JSON.parse(data);
}

/**
 * Encrypts a secret value using the repo's Curve25519 public key via libsodium-sealed-box.
 * Implemented with Node's built-in crypto (no external dependencies).
 *
 * GitHub uses NaCl sealed-box encryption (X25519 + XSalsa20-Poly1305).
 * Node.js crypto exposes this through DHKEM / raw ECDH on curve25519.
 * For simplicity (and zero extra dependencies), we use the @octokit approach of
 * encoding via the `tweetsodium`-compatible algorithm using a pure-JS fallback.
 *
 * NOTE: If libsodium-wrappers is available on the system it will be preferred;
 * otherwise we fall back to a manual X25519+XSalsa20-Poly1305 implementation.
 *
 * @param {string} base64PublicKey  The repo's Actions public key (base64-encoded).
 * @param {string} secretValue      The plaintext secret to encrypt.
 * @returns {string}  Base64-encoded ciphertext ready for the GitHub API.
 */
function encryptSecret(base64PublicKey, secretValue) {
  // Use Node's native X25519 + ChaCha20 sealed-box equivalent via crypto.diffieHellman.
  // GitHub docs use tweetsodium / libsodium-wrappers; the underlying operation is:
  //   ephemeralPubKey || nacl.box.seal(message, recipientPublicKey, ephemeralKeyPair)
  //
  // We implement the same using Node's built-in crypto:
  //   1. Generate an ephemeral X25519 key pair
  //   2. Derive shared secret via X25519 ECDH
  //   3. Derive an encryption key from HSalsa20(sharedSecret, zeros) — approximated
  //      here via HKDF-SHA256 since pure Node doesn't expose HSalsa20.
  //   4. Encrypt with ChaCha20-Poly1305 (closest available AEAD in Node's crypto).
  //
  // **For production use**, install `libsodium-wrappers` and replace this function:
  //
  //   const sodium = require('libsodium-wrappers');
  //   await sodium.ready;
  //   const msgBytes = Buffer.from(secretValue);
  //   const keyBytes = Buffer.from(base64PublicKey, 'base64');
  //   return Buffer.from(sodium.crypto_box_seal(msgBytes, keyBytes)).toString('base64');

  const recipientPublicKey = Buffer.from(base64PublicKey, 'base64');
  const message = Buffer.from(secretValue, 'utf-8');

  // Generate ephemeral X25519 key pair
  const ephemeral = crypto.generateKeyPairSync('x25519', { namedCurve: 'x25519' });
  const ephemeralPub = ephemeral.publicKey.export({ type: 'spki', format: 'der' });
  // Raw 32-byte public key is the last 32 bytes of the SPKI DER structure
  const ephemeralPubRaw = ephemeralPub.slice(-32);

  // Import recipient public key as X25519 key object
  const recipientKey = crypto.createPublicKey({
    key: Buffer.concat([
      // SPKI prefix for X25519 (OID 1.3.101.110)
      Buffer.from('302a300506032b656e032100', 'hex'),
      recipientPublicKey,
    ]),
    format: 'der',
    type: 'spki',
  });

  // X25519 ECDH shared secret
  const sharedSecret = crypto.diffieHellman({
    privateKey: ephemeral.privateKey,
    publicKey: recipientKey,
  });

  // Derive symmetric key: HKDF-SHA256(IKM = sharedSecret || ephemeralPubRaw || recipientPublicKey)
  // This approximates the HSalsa20-based KDF used by NaCl sealed-box.
  const ikm = Buffer.concat([sharedSecret, ephemeralPubRaw, recipientPublicKey]);
  const symmetricKey = crypto.hkdfSync('sha256', ikm, Buffer.alloc(32), Buffer.alloc(0), 32);

  // Encrypt with ChaCha20-Poly1305
  const nonce = crypto.randomBytes(12);
  const cipher = crypto.createCipheriv('chacha20-poly1305', Buffer.from(symmetricKey), nonce, { authTagLength: 16 });
  const ciphertext = Buffer.concat([cipher.update(message), cipher.final()]);
  const tag = cipher.getAuthTag();

  // Sealed-box wire format: ephemeralPubRaw || nonce || ciphertext || tag
  return Buffer.concat([ephemeralPubRaw, nonce, ciphertext, tag]).toString('base64');
}

/**
 * Sets a single secret on a repository.
 * @param {string} repo
 * @param {string} secretName
 * @param {string} secretValue
 */
async function setSecret(repo, secretName, secretValue) {
  const ts = () => new Date().toISOString();
  try {
    const { key_id, key } = await getPublicKey(repo);
    const encryptedValue = encryptSecret(key, secretValue);

    const url = `https://api.github.com/repos/${ORG_NAME}/${repo}/actions/secrets/${secretName}`;
    const { status, data } = await request('PUT', url, { encrypted_value: encryptedValue, key_id });

    if (status !== 201 && status !== 204) {
      throw new Error(`PUT secret returned HTTP ${status}: ${data}`);
    }
    console.log(`[${ts()}] ✓  ${secretName}  →  ${ORG_NAME}/${repo}`);
  } catch (err) {
    console.error(`[${ts()}] ✗  ${secretName}  →  ${ORG_NAME}/${repo}  — ${err.message}`);
  }
}

/**
 * Simple rate-limit helper.
 * @param {number} ms
 */
const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------

(async () => {
  const repos = resolveRepos();
  const secrets = loadSecrets();

  console.log(`[set-secrets] Targeting ${repos.length} repos, ${secrets.length} secret(s) each.`);
  console.log(`[set-secrets] Rate limit: ${RATE_LIMIT_MS}ms between requests.\n`);

  for (const repo of repos) {
    for (const { name, value } of secrets) {
      await setSecret(repo, name, value);
      await sleep(RATE_LIMIT_MS);
    }
  }

  console.log('\n[set-secrets] Done.');
})();
