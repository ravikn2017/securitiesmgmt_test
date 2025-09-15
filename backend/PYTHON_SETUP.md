# Python Setup Guide for Securities Management Backend

## Overview

This guide documents the Python setup process for the Securities Management backend, including compatibility fixes and deployment instructions for Railway platform.

## Issue Encountered

Initially encountered Python execution error when calling the API:

```
Error: Python process exited with code 9009: Python was not found; run without arguments to install from the Microsoft Store, or disable this shortcut from Settings > Apps > Advanced app settings > App execution aliases.
```

## Solutions Implemented

### 1. Cross-Platform Python Command Fix

**Problem**: The code was using `python3` command which doesn't exist on Windows.

**Fix**: Updated `backend/utils/financialsExtractor.js` to use platform-specific Python commands:

```javascript
// Before
const pythonProcess = spawn("python3", [pythonScript, symbol, "price"]);

// After
const pythonCommand = process.platform === "win32" ? "python" : "python3";
const pythonProcess = spawn(pythonCommand, [pythonScript, symbol, "price"]);
```

### 2. Enhanced Error Handling

Added proper error handling for Python installation issues:

```javascript
pythonProcess.on("error", (err) => {
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
```

### 3. File Organization

**Problem**: `requirements.txt` was in the root directory instead of the backend folder.

**Fix**: Moved `requirements.txt` to `backend/requirements.txt` for better organization since:

- Python script is in `backend/utils/yfinanceextractor.py`
- Node.js dependencies are in `backend/package.json`
- Python dependencies should be in `backend/requirements.txt`

### 4. Python 3.13 Compatibility

**Problem**: Original package versions were incompatible with Python 3.13.

**Solution**: Updated `backend/requirements.txt` with compatible versions:

```txt
# Before (Python 3.13 incompatible)
numpy==1.24.3
pandas==2.0.3
yfinance==0.2.28
openpyxl==3.1.2
requests==2.31.0

# After (Python 3.13 compatible)
numpy>=1.26.0
pandas>=2.1.0
yfinance>=0.2.28
openpyxl>=3.1.2
requests>=2.31.0
```

## Local Development Setup

### Prerequisites

1. **Install Python 3.8 or higher** (3.11+ recommended)

   - Download from [python.org](https://www.python.org/downloads/)
   - During installation, check "Add Python to PATH"

2. **Verify Python installation**:
   ```bash
   python --version
   # Should show Python 3.x.x
   ```

### Installation Steps

1. **Navigate to backend directory**:

   ```bash
   cd backend
   ```

2. **Upgrade pip and install build tools**:

   ```bash
   python -m pip install --upgrade pip
   python -m pip install --upgrade setuptools wheel
   ```

3. **Install Python dependencies**:

   ```bash
   python -m pip install -r requirements.txt
   ```

4. **Install Node.js dependencies**:

   ```bash
   npm install
   ```

5. **Start the server**:
   ```bash
   npm start
   ```

## Railway Platform Deployment

### 1. Nixpacks Configuration

Ensure your `nixpacks.toml` (in project root) includes Python support:

```toml
[start]
cmd = "cd backend && npm start"

[build]
cmd = "cd backend && npm install"

[providers]
nodejs = "18"
python = "3.11"  # Use 3.11 for better compatibility

[phases.setup]
cmds = [
  "cd backend && python -m pip install --upgrade pip setuptools wheel",
  "cd backend && python -m pip install -r requirements.txt"
]
```

### 2. Environment Variables

Set the following environment variables in Railway:

- `NODE_ENV=production`
- `PORT=5001` (or Railway's dynamic port)
- Any other environment variables from your `config.env`

### 3. File Structure for Deployment

```
project-root/
├── nixpacks.toml          # Railway build configuration
├── backend/
│   ├── requirements.txt   # Python dependencies
│   ├── package.json       # Node.js dependencies
│   ├── utils/
│   │   ├── financialsExtractor.js  # Fixed Python command
│   │   └── yfinanceextractor.py    # Python script
│   └── ... (other backend files)
```

### 4. Deployment Checklist

- [ ] `requirements.txt` is in `backend/` folder
- [ ] Python versions in `requirements.txt` use `>=` for flexibility
- [ ] `nixpacks.toml` includes Python 3.11 provider
- [ ] Environment variables are set in Railway dashboard
- [ ] Build commands install both Node.js and Python dependencies

## Testing

After deployment, test the API endpoint:

```
GET https://your-railway-domain.com/api/v1/companyCurrentFinancials/price/OFSS.NS
```

## Dependencies

### Python Packages

- `numpy>=1.26.0` - Numerical computing
- `pandas>=2.1.0` - Data manipulation and analysis
- `yfinance>=0.2.28` - Yahoo Finance data
- `openpyxl>=3.1.2` - Excel file handling
- `requests>=2.31.0` - HTTP requests

### Node.js Packages

- `express` - Web framework
- `cors` - Cross-origin resource sharing
- `dotenv` - Environment variables
- `mongoose` - MongoDB integration
- Other packages as listed in `package.json`

## Troubleshooting

### Common Issues

1. **"Python not found"**: Ensure Python is installed and in PATH
2. **"Cannot import setuptools"**: Run `pip install --upgrade setuptools wheel`
3. **Package version conflicts**: Use the updated `requirements.txt` with `>=` versions
4. **Railway build fails**: Check `nixpacks.toml` configuration and build logs

### Error Codes

- `9009`: Python executable not found in PATH
- `1`: Python package installation failed
- Build errors: Usually indicate missing dependencies or configuration issues

## Notes for Future Updates

- Keep Python version compatibility in mind when updating packages
- Test locally before deploying to Railway
- Monitor Railway build logs for any Python-related issues
- Consider using virtual environments in local development for isolation
