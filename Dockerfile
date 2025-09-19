# Use official Node.js runtime with Python
FROM node:18

# Install Python and pip
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy backend files
COPY backend/ ./

# Install Node.js dependencies
RUN npm install

# Install Python dependencies (break-system-packages is safe in Docker)
RUN pip3 install --no-cache-dir --break-system-packages -r requirements.txt

# Expose port
EXPOSE 5003

# Start the application
CMD ["npm", "start"]
