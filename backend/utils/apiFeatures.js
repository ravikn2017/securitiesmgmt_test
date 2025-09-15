// API Features for Tour Model
// Classes

class APIFeatures {
  constructor(query, queryString) {
    this.query = query; // Mongoose query object
    this.queryString = queryString; // Request query parameters
  }

  //BUILD QUERY methods
  filter() {
    // 1A) FILTERING
    const queryObj = { ...this.queryString };
    const excludedFields = ['page', 'sort', 'limit', 'fields'];
    excludedFields.forEach((el) => delete queryObj[el]);

    //console.log(req.query, queryObj);

    // 1B) ADVANCED FILTERING
    let queryStr = JSON.stringify(queryObj);
    queryStr = queryStr.replace(/\b(gte|gt|lte|lt)\b/g, (match) => `$${match}`); //There is some problem with this
    console.log(JSON.parse(queryStr));
    //const query = Tour.find(JSON.parse(queryStr));
    this.query = this.query.find(JSON.parse(queryStr));
    return this; // Return the instance for method chaining
  }

  sort() {
    // 2) SORTING
    if (this.queryString.sort) {
      // sort=price or sort=price,-ratingsAverage
      const sortBy = this.queryString.sort.split(',').join(' ');
      //console.log(sortBy);
      this.query = this.query.sort(sortBy);
    } else {
      // Default sorting
      this.query = this.query.sort('-createdAt _id'); // Sort by createdAt in descending order and then by _id
    }
    return this; // Return the instance for method chaining
  }

  limitFields() {
    // 3) FIELD LIMITING
    if (this.queryString.fields) {
      // fields=name,price
      const fields = this.queryString.fields.split(',').join(' ');
      this.query = this.query.select(fields);
    } else {
      // Exclude __v and createdAt fields
      this.query = this.query.select('-__v');
    }
    return this; // Return the instance for method chaining
  }

  paginate() {
    // 4) PAGINATION
    const page = this.queryString.page * 1 || 1; // Convert to number, default to 1
    const limit = this.queryString.limit * 1 || 100; // Convert to number, default to 100
    const skip = (page - 1) * limit; // Calculate the number of documents to skip
    //console.log(page, limit, skip);
    this.query = this.query.skip(skip).limit(limit);

    return this; // Return the instance for method chaining
  }
}

module.exports = APIFeatures;
