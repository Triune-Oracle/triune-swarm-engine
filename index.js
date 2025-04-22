const functions = require("firebase-functions");
const admin = require("firebase-admin");
const fs = require("fs");
const { ethers } = require("ethers");

admin.initializeApp();
const PRIVATE_KEY = functions.config().swarm.private_key;
const INFURA_ID = functions.config().swarm.infura_id;
const TOKEN_ADDRESS = functions.config().swarm.token_address;
const TO_ADDRESS = functions.config().swarm.to_address;
const AMOUNT = "10.0";

const TOKEN_ABI = [
  "function transfer(address to, uint amount) public returns (bool)",
  "function decimals() view returns (uint8)"
];

exports.app = functions.https.onRequest(async (req, res) => {
  try {
    const provider = new ethers.providers.InfuraProvider("mainnet", INFURA_ID);
    const wallet = new ethers.Wallet(PRIVATE_KEY, provider);
    const token = new ethers.Contract(TOKEN_ADDRESS, TOKEN_ABI, wallet);

    const decimals = await token.decimals();
    const parsedAmount = ethers.utils.parseUnits(AMOUNT, decimals);
    const tx = await token.transfer(TO_ADDRESS, parsedAmount);
    await tx.wait();

    const logEntry = {
      to: TO_ADDRESS,
      token: TOKEN_ADDRESS,
      amount: AMOUNT,
      txHash: tx.hash,
      timestamp: new Date().toISOString(),
    };

    fs.appendFileSync("token_payout_log.ndjson", JSON.stringify(logEntry) + "\n");
    res.send(`Payout success: ${tx.hash}`);
  } catch (err) {
    console.error(err);
    res.status(500).send("Payout failed");
  }
});