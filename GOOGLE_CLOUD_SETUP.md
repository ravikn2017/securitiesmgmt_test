# Google Cloud CLI Setup & Deployment Guide

## 📋 Complete command sequence for deploying Securities Management API to Google Cloud Run

### 🔐 Step 1: Authentication Setup

```bash
# Authenticate with Google Cloud (for environments with SSL/firewall issues)
gcloud auth application-default login --no-launch-browser
```

**Process:**

1. Opens browser authentication URL
2. Complete sign-in prompts in browser
3. Copy verification code back to terminal
4. Credentials saved to: `C:\Users\[USERNAME]\AppData\Roaming\gcloud\application_default_credentials.json`

---

### 📂 Step 2: Project Management

```bash
# List available projects
gcloud projects list

# Output example:
# PROJECT_ID                NAME              PROJECT_NUMBER
# fine-blueprint-472411-g6  My First Project  256165489318
```

```bash
# Update project name (avoid special characters like underscores)
# ❌ This fails: gcloud projects update fine-blueprint-472411-g6 --name="Securities_Mgmt_Test"
# ✅ This works:
gcloud projects update fine-blueprint-472411-g6 --name="Securities Mgmt Test"
```

```bash
# Set active project
gcloud config set project fine-blueprint-472411-g6
```

```bash
# Set quota project to avoid billing/quota warnings
gcloud auth application-default set-quota-project fine-blueprint-472411-g6
```

---

### ⚙️ Step 3: Enable Required Services

```bash
# Enable Cloud Build API (for building containers)
gcloud services enable cloudbuild.googleapis.com

# Enable Cloud Run API (for deploying containers)
gcloud services enable run.googleapis.com
```

---

### 🚀 Step 4: Deployment

```bash
# Navigate to project directory
cd C:\Training\SecuritiesMgmt_Test

# Deploy to Cloud Run (Basic - API Only)
gcloud run deploy securitiesmgmt-api \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 5003 \
  --memory 1Gi \
  --cpu 1 \
  --set-env-vars NODE_ENV=production
```

**Windows Command Prompt (single line - Basic):**

```cmd
gcloud run deploy securitiesmgmt-api --source . --platform managed --region us-central1 --allow-unauthenticated --port 5003 --memory 1Gi --cpu 1 --set-env-vars NODE_ENV=production
```

### 🗄️ Option B: Deploy with MongoDB Connection

**Windows Command Prompt (single line - Full with MongoDB):**

```cmd
gcloud run deploy securitiesmgmt-api --source . --platform managed --region us-central1 --allow-unauthenticated --port 5003 --memory 1Gi --cpu 1 --set-env-vars NODE_ENV=production,ALLOWED_ORIGINS=https://securities-management.vercel.app,DATABASE=mongodb+srv://ravikn2025_db_user:9WGrDnorpzekIfGi@clusterravikn.zczj2q7.mongodb.net/securities_management?retryWrites=true&w=majority&appName=securities-management&ssl=true&authSource=admin&serverSelectionTimeoutMS=5000&connectTimeoutMS=10000,FINANCE_API_KEY=sk-live-zCvH53Qfaot3d0e1avUfgu0FCouV2z8KOcc6Uvs6,JWT_EXPIRES_IN=90d,JWT_COOKIE_EXPIRES_IN=90
```

**Alternative: Deploy First, Then Add Environment Variables**

```cmd
# Step 1: Basic deployment
gcloud run deploy securitiesmgmt-api --source . --platform managed --region us-central1 --allow-unauthenticated --port 5003 --memory 1Gi --cpu 1

# Step 2: Add environment variables
gcloud run services update securitiesmgmt-api --region=us-central1 --set-env-vars NODE_ENV=production,ALLOWED_ORIGINS=https://securities-management.vercel.app

# Step 3: Add database connection (separate for readability)
gcloud run services update securitiesmgmt-api --region=us-central1 --set-env-vars DATABASE="mongodb+srv://ravikn2025_db_user:9WGrDnorpzekIfGi@clusterravikn.zczj2q7.mongodb.net/securities_management?retryWrites=true&w=majority&appName=securities-management&ssl=true&authSource=admin&serverSelectionTimeoutMS=5000&connectTimeoutMS=10000"

# Step 4: Add API keys and JWT settings
gcloud run services update securitiesmgmt-api --region=us-central1 --set-env-vars FINANCE_API_KEY=sk-live-zCvH53Qfaot3d0e1avUfgu0FCouV2z8KOcc6Uvs6,JWT_EXPIRES_IN=90d,JWT_COOKIE_EXPIRES_IN=90
```

---

### 📊 Step 5: Deployment Results

**Successful Deployment Output:**

```
Building using Dockerfile and deploying container to Cloud Run service [securitiesmgmt-api] in project [fine-blueprint-472411-g6] region [us-central1]
✓ Building and deploying new service... Done.
  ✓ Uploading sources...
  ✓ Building Container...
  ✓ Creating Revision...
  ✓ Routing traffic...
  ✓ Setting IAM Policy...
Done.
Service [securitiesmgmt-api] revision [securitiesmgmt-api-00001-tgc] has been deployed and is serving 100 percent of traffic.
Service URL: https://securitiesmgmt-api-256165489318.us-central1.run.app
```

---

## 🔧 Additional Useful Commands

### View Logs

```bash
# Real-time log streaming
gcloud logging tail "resource.type=cloud_run_revision AND resource.labels.service_name=securitiesmgmt-api" --project=fine-blueprint-472411-g6

# Recent logs
gcloud logs read "resource.type=cloud_run_revision AND resource.labels.service_name=securitiesmgmt-api" --limit=50 --project=fine-blueprint-472411-g6
```

### Service Management

```bash
# Check service status
gcloud run services describe securitiesmgmt-api --region=us-central1 --project=fine-blueprint-472411-g6

# List revisions
gcloud run revisions list --service=securitiesmgmt-api --region=us-central1 --project=fine-blueprint-472411-g6

# Update environment variables
gcloud run services update securitiesmgmt-api --region=us-central1 --set-env-vars KEY=VALUE --project=fine-blueprint-472411-g6
```

### Build Management

```bash
# View build history
gcloud builds list --project=fine-blueprint-472411-g6

# Get specific build logs
gcloud builds log [BUILD_ID] --region=us-central1
```

---

## 🎯 Key Configuration Details

- **Project ID**: `fine-blueprint-472411-g6`
- **Service Name**: `securitiesmgmt-api`
- **Region**: `us-central1`
- **Memory**: `1Gi`
- **CPU**: `1`
- **Port**: `5003`
- **Public URL**: `https://securitiesmgmt-api-256165489318.us-central1.run.app`

### Environment Variables (when using MongoDB option):

- **NODE_ENV**: `production`
- **ALLOWED_ORIGINS**: `https://securities-management.vercel.app`
- **DATABASE**: MongoDB Atlas connection string
- **FINANCE_API_KEY**: Finance API key for additional services
- **JWT_EXPIRES_IN**: `90d`
- **JWT_COOKIE_EXPIRES_IN**: `90`

---

## ⚠️ Important Notes

1. **Authentication**: Use `--no-launch-browser` flag for corporate networks with SSL issues
2. **Project Names**: Avoid special characters; use spaces instead of underscores
3. **Quota Project**: Always set quota project to avoid billing warnings
4. **Dockerfile Fix**: Added `--break-system-packages` to pip install for Python 3.11+ compatibility
5. **Windows CLI**: Use single-line commands in Command Prompt (backslash continuation doesn't work)
6. **Build Repository**: First deployment creates `cloud-run-source-deploy` repository automatically

---

## 🚀 API Endpoints

Base URL: `https://securitiesmgmt-api-256165489318.us-central1.run.app`

- **Price Data**: `/api/v1/companyCurrentFinancials/price/{SYMBOL}`
- **Full Financials**: `/api/v1/companyCurrentFinancials/{SYMBOL}`
- **Quarterly Data**: `/api/v1/companyCurrentFinancials/quarterly/{SYMBOL}`

**Example**: `https://securitiesmgmt-api-256165489318.us-central1.run.app/api/v1/companyCurrentFinancials/price/OFSS.NS`

---

## 🎉 Success Metrics

- ✅ **Yahoo Finance API**: Working without 429 errors (vs Railway Edge interference)
- ✅ **Python Integration**: yfinance + Node.js functioning perfectly
- ✅ **Real Data**: Fetching actual stock prices and financial data
- ✅ **Production Ready**: 1GB memory, scalable architecture
- ✅ **Cost Effective**: Within Google Cloud Run free tier limits
