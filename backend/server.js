// 4) START SERVER
const dotenv = require("dotenv");

// Only load config.env in development
if (process.env.NODE_ENV !== "production") {
  dotenv.config({ path: "./config.env" });
}

const app = require("./app");

console.log(app.get("env")); // This will log the current environment

const port = process.env.PORT || 3002;

// Use 0.0.0.0 for Railway (production), localhost for development
const host = process.env.NODE_ENV === "production" ? "0.0.0.0" : "localhost";

app.listen(port, host, () => {
  console.log(`App is running on ${host}:${port}...`);
  console.log(`Environment: ${process.env.NODE_ENV || "development"}`);
});
