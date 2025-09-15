// 4) START SERVER
const dotenv = require("dotenv");

dotenv.config({ path: "./config.env" });

const app = require("./app");

console.log(app.get("env")); // This will log the current environment, e.g., 'development'
//console.log(process.env);

//const mongoose = require("mongoose");

// Use local database for development, Atlas for production
// const DB =
//   process.env.NODE_ENV === "development"
//     ? process.env.DATABASE_LOCAL
//     : process.env.DATABASE;

// mongoose
//   .connect(DB, {
//     //useNewUrlParser: true,
//     // useCreateIndex: true,
//     // useFindAndModify: false,
//   })
//   //.then((con) => {
//   .then(() => {
//     //console.log(con.connections);
//     console.log("DB Connection Succesful !!");
//   });

//const port = 3002;
const port = process.env.PORT || 3002; // Use the PORT from environment variables or default to 3001
app.listen(port, () => {
  console.log(`App is running on port ${port}...`);
});
