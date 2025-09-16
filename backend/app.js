const qs = require("qs");
const express = require("express");
//const { get } = require('http');
const morgan = require("morgan"); // Importing morgan for logging HTTP requests

const cors = require("cors");

const companyCurrentFinancialsRouter = require("./routes/CompanyCurrentFinancialsRoutes"); // Importing the company

const app = express();

app.set("query parser", (str) => qs.parse(str));

//This is our own middleware function
// 1) MIDDLEWARES

// CORS configuration - Enable Cross-Origin Resource Sharing

const corsOptions = {
  origin: function (origin, callback) {
    // Allow requests with no origin (like mobile apps or curl requests)

    if (!origin) return callback(null, true);

    // In development, allow all origins

    if (process.env.NODE_ENV === "development") {
      return callback(null, true);
    }

    // In production, check against allowed origins from environment variable

    const allowedOrigins = process.env.ALLOWED_ORIGINS
      ? process.env.ALLOWED_ORIGINS.split(",")
      : [];

    if (allowedOrigins.indexOf(origin) !== -1) {
      callback(null, true);
    } else {
      callback(new Error("Not allowed by CORS"));
    }
  },

  credentials: true,

  optionsSuccessStatus: 200,
};

app.use(cors(corsOptions));

if (process.env.NODE_ENV === "development") {
  app.use(morgan("dev")); // Using morgan to log requests in 'dev' format
}

app.use(express.json()); // Middleware to parse JSON bodies

app.use((req, res, next) => {
  console.log(`🔍 REQUEST: ${req.method} ${req.url} from ${req.ip}`);
  next(); // Call the next middleware in the stack
});

app.use((req, res, next) => {
  req.requestTime = new Date().toISOString();
  next(); // Call the next middleware in the stack
});

// 2) ROUTES

// Simple health check for Railway
app.get("/", (req, res) => {
  res.json({ status: "API running", timestamp: new Date().toISOString() });
});

app.use("/api/v1/companyCurrentFinancials", companyCurrentFinancialsRouter);

module.exports = app;
