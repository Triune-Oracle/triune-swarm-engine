
// dashboard.js – Terminal-based yield dashboard for Triune Swarm Engine

const fs = require('fs');

// Load logs and memory
const payouts = JSON.parse(fs.readFileSync('./payout_log.json', 'utf-8'));
const memory = JSON.parse(fs.readFileSync('./memory/swarm_memory_log.json', 'utf-8'));
const state = JSON.parse(fs.readFileSync('./memory/agent_state.json', 'utf-8'));

function formatUSD(value) {
  return `$${parseFloat(value).toFixed(4)}`;
}

// Earnings Summary
const totalEarnings = payouts.reduce((sum, p) => sum + parseFloat(p.est_value_usd), 0);
console.log("\n=== Triune Swarm Engine: Yield Dashboard ===\n");

console.log(`Total Earnings:        ${formatUSD(totalEarnings)}`);
console.log(`Total Payout Events:   ${payouts.length}`);
console.log(`Tasks Logged:          ${memory.length}`);

// Agent-specific Stats
console.log("\n-- Agent Activity --");
Object.entries(state).forEach(([agent, info]) => {
  console.log(`${agent.padEnd(8)} | Last Task: ${info.last_task.padEnd(10)} | Status: ${info.status}`);
});

// Last 3 Tasks
console.log("\n-- Recent Tasks --");
memory.slice(-3).reverse().forEach((entry, i) => {
  console.log(`#${memory.length - i}: ${entry.agent} → ${entry.action} "${entry.input.slice(0, 30)}..."`);
});
