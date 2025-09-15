//const CompanyCurrentFinancials = require("../models/CompanyCurrentFinancialsModel");
const {
  //getFinancialsFromYFinance,
  getLatestPriceFromYFinance,
} = require("../utils/financialsExtractor");
const catchAsync = require("../utils/catchAsync");
const APIFeatures = require("../utils/apiFeatures");

exports.getLatestPriceBySymbol = catchAsync(async (req, res) => {
  const symbol = req.params.symbol || req.query.symbol;
  if (!symbol) {
    return res
      .status(400)
      .json({ status: "fail", message: "Company symbol is required" });
  }
  const priceData = await getLatestPriceFromYFinance(symbol);
  res.status(200).json({
    status: "success",
    data: priceData,
  });
  console.log(`Fetched latest price for ${symbol}`, priceData);
});
