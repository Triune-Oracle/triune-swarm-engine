// wallet_router.js – Reads payout logs and simulates routing to wallet

const fs = require('fs');
const config = require('../../schemas/wallet_config.json');

function summarizePayouts() {
  const log = JSON.parse(fs.readFileSync('../../payout_log.json', 'utf-8'));
  const total = log.reduce((sum, entry) => sum + parseFloat(entry.est_value_usd), 0);
  console.log(`\n[Wallet Router] Total Earnings: $${total.toFixed(4)} USD`);

  if (total >= config.min_payout_threshold_usd) {
    console.log(`[Wallet Router] ✅ Threshold reached. Simulate routing to ${config.wallet_address} on ${config.network}`);
  } else {
    console.log(`[Wallet Router] ❌ Threshold not met (${total.toFixed(4)} < ${config.min_payout_threshold_usd})`);
  }
}

summarizePayouts();
