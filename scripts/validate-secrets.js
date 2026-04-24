#!/usr/bin/env node

const { validateSecretConfiguration } = require('../src/core/secret_validation');

try {
  validateSecretConfiguration({
    context: 'ci',
    enforce: true,
  });
  console.log('✅ CI secret validation passed.');
} catch (error) {
  console.error('❌ CI secret validation failed.');
  process.exit(1);
}
