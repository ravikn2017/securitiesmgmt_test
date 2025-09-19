// 4) START SERVER
const dotenv = require("dotenv");

// Only load config.env for local development
// Cloud platforms provide environment variables directly, doesn't need config.env
if (!process.env.PORT || process.env.PORT === "5001") {
  // Local development - load config.env
  dotenv.config({ path: "./config.env" });
} else {
  // Production - don't load config.env
  console.log(
    "Using production environment variables (not loading config.env)"
  );
}

const app = require("./app");

console.log(app.get("env")); // This will log the current environment

const port = process.env.PORT || 5003;

// Cloud platforms need 0.0.0.0 binding for load balancer
const server = app.listen(port, "0.0.0.0", () => {
  console.log(`🚀 App running on 0.0.0.0:${port}`);
  console.log(`📊 Environment: ${process.env.NODE_ENV || "development"}`);
  console.log(`✅ Server ready for requests`);
});

// Add error handling
server.on("error", (err) => {
  console.error("❌ Server error:", err);
});
