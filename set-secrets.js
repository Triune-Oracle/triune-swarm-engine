/**
 * set-secrets.js
 * 
 * Sets or updates GitHub repository secrets across multiple repositories
 * in the Triune-Oracle organization.
 * 
 * Requires a GitHub Personal Access Token (PAT) with repo and admin:repo_hook scopes
 * set as the environment variable GH_PAT.
 */

import fetch from 'node-fetch';
import fs from 'fs/promises';
import sodium from 'tweetsodium';

const ORG_NAME = 'Triune-Oracle';  // Change if needed
const PAT = process.env.GH_PAT;

if (!PAT) {
  console.error('Error: GH_PAT environment variable is not set.');
  process.exit(1);
}

// List of repos to update secrets on
const repos = [
  'triune-swarm-engine',
  'TriumvirateMonitor-Mobile',
  'CulturalCodex',
  'Legio-Cognito',
  'Trumvirate-System-Memory-Merge-Protoco',
  'Triune--retrieval--node',
  'react-octo-spoon'
];

// Load secrets from a local JSON file (secrets.json)
async function loadSecrets() {
  try {
    const data = await fs.readFile('./secrets.json', 'utf-8');
    return JSON.parse(data);
  } catch (err) {
    console.error('Failed to load secrets.json:', err);
    process.exit(1);
  }
}

// Encrypt secret per GitHub API requirements
function encryptSecret(publicKey, secretValue) {
  const messageBytes = Buffer.from(secretValue);
  const keyBytes = Buffer.from(publicKey, 'base64');
  const encryptedBytes = sodium.seal(messageBytes, keyBytes);
  return Buffer.from(encryptedBytes).toString('base64');
}

async function setSecret(repo, secretName, secretValue) {
  try {
    // Fetch the repo's public key
    const keyResponse = await fetch(`https://api.github.com/repos/${ORG_NAME}/${repo}/actions/secrets/public-key`, {
      headers: { Authorization: `token ${PAT}` }
    });

    if (!keyResponse.ok) {
      const text = await keyResponse.text();
      throw new Error(`Failed to get public key: ${text}`);
    }

    const { key, key_id } = await keyResponse.json();

    // Encrypt the secret value
    const encryptedValue = encryptSecret(key, secretValue);

    // PUT the secret
    const putResponse = await fetch(`https://api.github.com/repos/${ORG_NAME}/${repo}/actions/secrets/${secretName}`, {
      method: 'PUT',
      headers: {
        Authorization: `token ${PAT}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        encrypted_value: encryptedValue,
        key_id
      })
    });

    if (!putResponse.ok) {
      const text = await putResponse.text();
      throw new Error(`Failed to set secret: ${text}`);
    }

    console.log(`[${new Date().toISOString()}] Secret '${secretName}' set in '${repo}'`);
  } catch (error) {
    console.error(`[${new Date().toISOString()}] Error setting secret '${secretName}' in '${repo}':`, error.message);
  }
}

(async () => {
  const secrets = await loadSecrets();

  for (const repo of repos) {
    for (const { name, value } of secrets) {
      await setSecret(repo, name, value);
    }
  }

  console.log('Secret update process completed.');
})();