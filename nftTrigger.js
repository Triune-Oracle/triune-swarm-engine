const chokidar = require("chokidar");
const { exec } = require("child_process");

chokidar.watch("./minted_nfts/").on("add", (path) => {
  console.log(`NFT minted: ${path}`);
  exec("node send-token.js", (err, stdout) => {
    if (err) return console.error(err);
    console.log(stdout);
  });
});