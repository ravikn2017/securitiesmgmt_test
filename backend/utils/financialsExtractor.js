const { spawn } = require("child_process");
const path = require("path");

async function getLatestPriceFromYFinance(symbol) {
  return new Promise((resolve, reject) => {
    const pythonScript = path.join(__dirname, "yfinanceextractor.py");
    // Try different Python commands to handle cross-platform compatibility
    const pythonCommand = process.platform === "win32" ? "python" : "python3";
    const pythonProcess = spawn(pythonCommand, [pythonScript, symbol, "price"]);

    let data = "";
    let error = "";

    pythonProcess.stdout.on("data", (chunk) => {
      data += chunk;
    });

    pythonProcess.stderr.on("data", (chunk) => {
      error += chunk;
    });

    pythonProcess.on("error", (err) => {
      console.error("Python process error:", err);
      if (err.code === "ENOENT") {
        reject(
          new Error(
            `Python not found. Please install Python and ensure it's in your PATH. Error: ${err.message}`
          )
        );
      } else {
        reject(new Error(`Failed to start Python process: ${err.message}`));
      }
    });

    pythonProcess.on("close", (code) => {
      console.log(`Python process exited with code: ${code}`);
      if (error) console.error("Python stderr:", error);
      if (data) console.log("Python stdout:", data);

      if (code !== 0) {
        reject(new Error(`Python process exited with code ${code}: ${error}`));
        return;
      }
      try {
        const priceData = JSON.parse(data);
        resolve(priceData);
      } catch (e) {
        reject(new Error(`Failed to parse Python output: ${e.message}`));
      }
    });
  });
}

module.exports = {
  getLatestPriceFromYFinance,
};
