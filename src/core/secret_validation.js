const DEFAULT_SECRET_KEYS = [
  'DATABASE_URL',
  'PRIVATE_KEY',
  'INFURA_ID',
  'STRIPE_SECRET_KEY',
  'STRIPE_WEBHOOK_SECRET',
  'VERCEL_TOKEN',
  'GH_PAT',
  'SS_API_KEY',
  'OPENAI_API_KEY',
];

const PLACEHOLDER_TOKENS = [
  'changeme',
  'change-me',
  'example',
  'password',
  'secret',
  'your-',
  'your_',
  'your ',
  'test',
  'dummy',
  'placeholder',
  '123',
  '1234',
  '12345',
  '123456',
];

const LEAKED_PATTERNS = [
  /^gh[pousr]_[A-Za-z0-9]{20,}$/,
  /^sk_(live|test)_[A-Za-z0-9]{16,}$/,
  /^AKIA[0-9A-Z]{16}$/,
  /^AIza[0-9A-Za-z\-_]{20,}$/,
  /^xox[baprs]-[A-Za-z0-9-]{10,}$/,
  /^0x[a-fA-F0-9]{64}$/,
];

function parseList(value) {
  return (value || '')
    .split(',')
    .map((item) => item.trim())
    .filter(Boolean);
}

function isPlaceholder(value) {
  const normalized = value.trim().toLowerCase();
  return PLACEHOLDER_TOKENS.some((token) => normalized === token || normalized.includes(token));
}

function hasKnownLeakPattern(value) {
  return LEAKED_PATTERNS.some((pattern) => pattern.test(value.trim()));
}

function validateSecretConfiguration(options = {}) {
  const context = options.context || 'runtime';
  const enforce = options.enforce ?? (process.env.CI === 'true');
  const allowWeak = process.env.ALLOW_WEAK_SECRETS === '1';

  const explicitRequired = options.requiredSecrets || parseList(process.env.REQUIRED_SECRET_VARS);
  const requiredSecrets = explicitRequired.length > 0 ? explicitRequired : [];

  const candidateSecrets = new Set([
    ...DEFAULT_SECRET_KEYS,
    ...requiredSecrets,
    ...parseList(process.env.SECRET_VALIDATION_KEYS),
  ]);

  const issues = [];

  for (const secretName of requiredSecrets) {
    const value = process.env[secretName];
    if (!value || !value.trim()) {
      issues.push(`${secretName}: missing`);
      continue;
    }
  }

  for (const secretName of candidateSecrets) {
    const value = process.env[secretName];
    if (!value || !value.trim()) {
      continue;
    }

    if (isPlaceholder(value)) {
      issues.push(`${secretName}: placeholder value detected`);
      continue;
    }

    if (value.trim().length < 12) {
      issues.push(`${secretName}: value too short`);
      continue;
    }

    if (hasKnownLeakPattern(value)) {
      issues.push(`${secretName}: matches known leaked/unsafe token pattern`);
    }
  }

  if (issues.length === 0) {
    return { ok: true, enforce, issues: [] };
  }

  const message = `[secret-validation:${context}] ${issues.join('; ')}`;

  if (allowWeak) {
    console.warn(`${message} (bypassed by ALLOW_WEAK_SECRETS=1)`);
    return { ok: true, enforce: false, issues };
  }

  if (enforce) {
    throw new Error(message);
  }

  console.warn(`${message} (warning only)`);
  return { ok: false, enforce: false, issues };
}

module.exports = {
  validateSecretConfiguration,
};
