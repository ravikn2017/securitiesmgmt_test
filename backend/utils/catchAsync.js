// This is to replace the try-catch block in async functions

module.exports = (fn) => {
  return (req, res, next) => {
    fn(req, res, next).catch(next); // Call the function and catch any errors, passing them to the next middleware
  };
};
