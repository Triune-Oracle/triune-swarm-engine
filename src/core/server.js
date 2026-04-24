
// server.js – Entrypoint for Triune Swarm deployment on Render
const express = require('express');
const app = express();
const port = process.env.PORT || 3000;

const { spawn } = require('child_process');
const path = require('path');
const { Pool } = require('pg');
const { parse } = require('pg-connection-string');
const { validateSecretConfiguration } = require('./secret_validation');

const parsePositiveInt = (value, fallback) => {
  const parsed = Number.parseInt(value || '', 10);
  return Number.isFinite(parsed) && parsed > 0 ? parsed : fallback;
};

validateSecretConfiguration({
  context: 'startup',
  enforce: process.env.NODE_ENV === 'production',
  requiredSecrets: process.env.NODE_ENV === 'production' ? ['DATABASE_URL'] : [],
});

const rateLimitWindowMs = parsePositiveInt(process.env.RATE_LIMIT_WINDOW_MS, 60_000);
const rateLimitMaxRequests = parsePositiveInt(process.env.RATE_LIMIT_MAX_REQUESTS, 120);
const rateLimitByIp = new Map();
let lastRateLimitCleanupAt = 0;

app.use((req, res, next) => {
  const now = Date.now();
  const forwardedFor = req.headers['x-forwarded-for'];
  const forwardedIp = Array.isArray(forwardedFor) ? forwardedFor[0] : forwardedFor?.split(',')[0]?.trim();
  const key = forwardedIp || req.ip || req.socket?.remoteAddress || `${req.method}:${req.path}:anonymous`;
  const current = rateLimitByIp.get(key);

  if (!current || now - current.windowStart >= rateLimitWindowMs) {
    rateLimitByIp.set(key, { windowStart: now, count: 1 });
    res.setHeader('X-RateLimit-Limit', String(rateLimitMaxRequests));
    res.setHeader('X-RateLimit-Remaining', String(rateLimitMaxRequests - 1));
    return next();
  }

  current.count += 1;
  res.setHeader('X-RateLimit-Limit', String(rateLimitMaxRequests));
  res.setHeader('X-RateLimit-Remaining', String(Math.max(rateLimitMaxRequests - current.count, 0)));

  if (current.count > rateLimitMaxRequests) {
    return res.status(429).send('Too many requests');
  }

  if (rateLimitByIp.size > 10_000 && now - lastRateLimitCleanupAt >= rateLimitWindowMs) {
    lastRateLimitCleanupAt = now;
    for (const [ip, bucket] of rateLimitByIp.entries()) {
      if (now - bucket.windowStart >= rateLimitWindowMs) {
        rateLimitByIp.delete(ip);
      }
    }
    while (rateLimitByIp.size > 10_000) {
      const oldestKey = rateLimitByIp.keys().next().value;
      rateLimitByIp.delete(oldestKey);
    }
  }

  return next();
});

// Verify DB connectivity on startup
if (process.env.DATABASE_URL) {
  const dbConnectionTimeoutMs = parsePositiveInt(process.env.DB_CONNECTION_TIMEOUT_MS, 5_000);
  const dbIdleTimeoutMs = parsePositiveInt(process.env.DB_IDLE_TIMEOUT_MS, 10_000);
  const dbQueryTimeoutMs = parsePositiveInt(process.env.DB_QUERY_TIMEOUT_MS, 10_000);
  const dbStatementTimeoutMs = parsePositiveInt(process.env.DB_STATEMENT_TIMEOUT_MS, 10_000);
  const cfg = parse(process.env.DATABASE_URL);
  console.log('DB target:', {
    host: cfg.host,
    database: cfg.database,
    sslmode: process.env.DATABASE_URL.includes('sslmode=require') ? 'require' : 'missing',
  });

  const pool = new Pool({
    connectionString: process.env.DATABASE_URL,
    connectionTimeoutMillis: dbConnectionTimeoutMs,
    idleTimeoutMillis: dbIdleTimeoutMs,
    query_timeout: dbQueryTimeoutMs,
    statement_timeout: dbStatementTimeoutMs,
    ssl: process.env.NODE_ENV === 'production'
      ? { rejectUnauthorized: true }
      : { rejectUnauthorized: false },
  });

  pool
    .query('SELECT now() as now, current_database() as db, current_user as user')
    .then(r => {
      console.log('DB ping ok:', r.rows[0]);
      pool.end();
    })
    .catch(e => {
      console.error('DB ping failed:', e.message);
      pool.end();
    });
} else {
  console.warn('DATABASE_URL not set – skipping DB startup ping');
}

// Serve static dashboard log preview (simple HTML could be added later)
app.get('/', (req, res) => {
  res.send('<h2>Triune Swarm Engine is running in the cloud.</h2><p>Task relay and monetization active.</p>');
});

// Trigger swarm loop and payout check on boot
app.listen(port, () => {
  console.log(`Swarm Engine cloud server running on port ${port}`);

  // Simulate running core engine (replace with actual modules as needed)
  const relay = spawn('node', [path.join(__dirname, 'relay_loop.js')], { stdio: 'inherit' });
  const payouts = spawn('node', [path.join(__dirname, 'wallet-router.js')], { stdio: 'inherit' });

  relay.on('close', code => console.log(`Relay loop exited with code ${code}`));
  payouts.on('close', code => console.log(`Payout router exited with code ${code}`));
});
