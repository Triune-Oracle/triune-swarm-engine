const { ethers } = require("ethers");
const fs = require("fs");

const PRIVATE_KEY = process.env.PRIVATE_KEY;
const INFURA_ID = process.env.INFURA_ID || "your-infura-id";
const CHAIN = process.env.CHAIN || "mainnet";

const TO_ADDRESS = "0xRecipientWalletAddress";
const TOKEN_ADDRESS = "0xTokenContractAddress";
const AMOUNT = "10.0";
const TOKEN_ABI = [
  "function transfer(address to, uint amount) public returns (bool)",
  "function decimals() view returns (uint8)"
];

const chainMap = {
  mainnet: "homestead",
  goerli: "goerli",
  sepolia: "sepolia",
  polygon: "polygon-mainnet",
  arbitrum: "arbitrum-mainnet",
  optimism: "optimism-mainnet",
};

async function sendTokenPayout() {
  if (!PRIVATE_KEY || !INFURA_ID) {
    console.error("Missing PRIVATE_KEY or INFURA_ID.");
    process.exit(1);
  }

  const network = chainMap[CHAIN.toLowerCase()];
  if (!network) {
    console.error(`Unsupported chain "${CHAIN}". Supported: ${Object.keys(chainMap).join(", ")}`);
    process.exit(1);
  }

  const provider = new ethers.providers.InfuraProvider(network, INFURA_ID);
  const wallet = new ethers.Wallet(PRIVATE_KEY, provider);
  const token = new ethers.Contract(TOKEN_ADDRESS, TOKEN_ABI, wallet);

  try {
    const decimals = await token.decimals();
    const parsedAmount = ethers.utils.parseUnits(AMOUNT, decimals);
    const tx = await token.transfer(TO_ADDRESS, parsedAmount);
    await tx.wait();

    const logEntry = {
      to: TO_ADDRESS,
      token: TOKEN_ADDRESS,
      amount: AMOUNT,
      chain: CHAIN,
      txHash: tx.hash,
      timestamp: new Date().toISOString(),
    };

    fs.appendFileSync("token_payout_log.ndjson", JSON.stringify(logEntry) + "\n");
    console.log(`Token payout sent on ${CHAIN}:`, tx.hash);
  } catch (err) {
    console.error(`Error sending token payout on ${CHAIN}:`, err);
  }
}

sendTokenPayout();