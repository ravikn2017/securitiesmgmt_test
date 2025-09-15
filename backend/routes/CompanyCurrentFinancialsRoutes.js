const express = require("express");
const router = express.Router();
const companyCurrentFinancialsController = require("../controllers/CompanyCurrentFinancialsController");

// Route to fetch and store current financials
// router.get(
//   "/fetchAndStore/:symbol",
//   companyCurrentFinancialsController.fetchAndStoreCurrentFinancials
// );

// // Route to fetch and store update current financials (always replaces existing data)
// router.get(
//   "/fetchAndStoreUpdate/:symbol",
//   companyCurrentFinancialsController.fetchAndStoreUpdateCurrentFinancials
// );

// // Route to get financials by symbol
// router.get(
//   "/viewBySymbol/:symbol",
//   companyCurrentFinancialsController.getCurrentFinancialsBySymbol
// );

// // Route to get all companies' current financials
// router.get("/", companyCurrentFinancialsController.getAllCurrentFinancials);

// Route to fetch real-time price data from Yahoo Finance
router.get(
  "/price/:symbol",
  companyCurrentFinancialsController.getLatestPriceBySymbol
);

module.exports = router;
