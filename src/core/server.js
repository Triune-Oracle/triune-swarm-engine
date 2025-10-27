
// server.js – Entrypoint for Triune Swarm deployment on Render
const express = require('express');
const app = express();
const port = process.env.PORT || 3000;

const { spawn } = require('child_process');
const path = require('path');

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
