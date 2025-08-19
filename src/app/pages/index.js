const fs = require("fs");
const express = require("express");
const { ethers } = require("ethers");

const app = express();
app.use(express.json());

const PRIVATE_KEY = process.env.PRIVATE_KEY;
const INFURA_ID = process.env.INFURA_ID;
const TOKEN_ADDRESS = process.env.TOKEN_ADDRESS;
const TO_ADDRESS = process.env.TO_ADDRESS;
const AMOUNT = "10.0";

const TOKEN_ABI = [
  "function transfer(address to, uint amount) public returns (bool)",
  "function decimals() view returns (uint8)"
];

app.post("/payout", async (req, res) => {
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

    fs.appendFileSync("../../token_payout_log.ndjson", JSON.stringify(logEntry) + "\n");
    res.send(`Payout sent: ${tx.hash}`);
  } catch (err) {
    console.error(err);
    res.status(500).send("Payout failed");
  }
});

app.listen(3000, () => console.log("Payout API running on port 3000"));