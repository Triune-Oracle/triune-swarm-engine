
const { ethers } = require("ethers");
const fs = require("fs");

// ENV Variables
const PRIVATE_KEY = process.env.PRIVATE_KEY || "your-private-key";
const TO_ADDRESS = process.env.TO_ADDRESS || "0xb9e9eea050A88b9a9392aDe0b6129493A606336c";
const AMOUNT_WETH = process.env.AMOUNT_WETH || "0.01";
const WETH_CONTRACT_ADDRESS = "0x7ceB23fD6bC0adD59E62ac25578270cFf1b9f619"; // WETH on Polygon

// ERC-20 ABI
const ERC20_ABI = [
  "function transfer(address to, uint amount) public returns (bool)"
];

async function sendWETHPayout() {
  const provider = new ethers.providers.JsonRpcProvider("https://polygon-mainnet.infura.io/v3/6edb5e2370db44ae9bce1d0805f14ea9");
  const wallet = new ethers.Wallet(PRIVATE_KEY, provider);
  const WETH = new ethers.Contract(WETH_CONTRACT_ADDRESS, ERC20_ABI, wallet);

  try {
    const amountInWei = ethers.utils.parseEther(AMOUNT_WETH);
    const tx = await WETH.transfer(TO_ADDRESS, amountInWei);
    await tx.wait();

    const logEntry = {
      to: TO_ADDRESS,
      token: "WETH",
      amount: AMOUNT_WETH,
      txHash: tx.hash,
      timestamp: new Date().toISOString(),
    };

    fs.appendFileSync("payout_log.json", JSON.stringify(logEntry) + ",\n");
    console.log("WETH payout sent:", tx.hash);
  } catch (err) {
    console.error("Error sending WETH payout:", err);
  }
}

async function swarmLoop() {
  console.log("Swarm loop running on Polygon WETH mode...");
  let cycle = 0;

  setInterval(async () => {
    cycle++;
    console.log("Cycle", cycle);

    // Trigger WETH payout every 5 cycles
    if (cycle % 5 === 0) {
      console.log("Initiating autonomous WETH payout...");
      await sendWETHPayout();
    }

  }, 60000); // 60 seconds
}

swarmLoop();
