const fs = require("fs");
const { ethers } = require("ethers");

const PRIVATE_KEY = process.env.PRIVATE_KEY;
const INFURA_ID = process.env.INFURA_ID;
const CHAIN = process.env.CHAIN || "mainnet";
const TOKEN_ADDRESS = "0xTokenAddressHere";
const TOKEN_ABI = [
  "function transfer(address to, uint256 amount) public returns (bool)",
  "function decimals() view returns (uint8)"
];

const chainMap = {
  mainnet: "homestead",
  polygon: "polygon-mainnet",
  arbitrum: "arbitrum-mainnet",
};

async function processPayouts() {
  const provider = new ethers.providers.InfuraProvider(chainMap[CHAIN], INFURA_ID);
  const wallet = new ethers.Wallet(PRIVATE_KEY, provider);
  const token = new ethers.Contract(TOKEN_ADDRESS, TOKEN_ABI, wallet);

  const recipients = JSON.parse(fs.readFileSync("../../payout_queue.json", "utf8"));
  const decimals = await token.decimals();

  for (const entry of recipients) {
    const parsedAmount = ethers.utils.parseUnits(entry.amount, decimals);
    try {
      const tx = await token.transfer(entry.to, parsedAmount);
      await tx.wait();
      console.log(`Paid ${entry.amount} to ${entry.to}: ${tx.hash}`);
    } catch (e) {
      console.error(`Failed payout to ${entry.to}:`, e);
    }
  }
}

processPayouts();