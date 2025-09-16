const { spawn } = require("child_process");
const path = require("path");

async function getLatestPriceFromYFinance(symbol) {
  return new Promise((resolve, reject) => {
    const pythonScript = path.join(__dirname, "yfinanceextractor.py");

    // For Railway/Nix environment, use the Python with access to installed packages
    let pythonCommand;
    let pythonArgs = [pythonScript, symbol, "price"];

    if (process.env.NODE_ENV === "production") {
      // Railway/Nix: Use python3 with proper environment
      pythonCommand = "python3";
      // Add environment variables for Nix Python packages
    } else {
      // Local development
      pythonCommand = process.platform === "win32" ? "python" : "python3";
    }

    console.log(`🐍 Using Python command: ${pythonCommand}`);
    console.log(`📄 Python script: ${pythonScript}`);
    console.log(`🔧 Environment: ${process.env.NODE_ENV}`);
    console.log(`📍 PYTHONPATH: ${process.env.PYTHONPATH || "not set"}`);
    console.log(`🛣️ PATH: ${process.env.PATH?.slice(0, 200)}...`);

    const pythonProcess = spawn(pythonCommand, pythonArgs, {
      env: {
        ...process.env,
        // Ensure Python can find Nix packages
        PYTHONPATH: process.env.PYTHONPATH || "",
        PATH: process.env.PATH || "",
      },
      shell: process.env.NODE_ENV === "production", // Use shell in production for Nix environment
    });

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
