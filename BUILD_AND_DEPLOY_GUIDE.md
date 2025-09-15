# 🐳 Docker Build and Deploy Guide for Python AI Plugin

This guide walks you through building and deploying your Python AI plugin to Snowflake step by step.

## Prerequisites

- ✅ Docker Desktop installed and running
- ✅ Snowflake account with MOODLE_ROLE access
- ✅ Python AI plugin files ready

---

## Step 1: Create Snowflake Image Repository

**Before building your Docker image**, you need to create an image repository in Snowflake and get the exact registry URL.

### 1.1 Run SQL in Snowflake Snowsight

Open Snowflake Snowsight and run this SQL:

```sql
-- First, create the image repository to get the exact URL
USE ROLE MOODLE_ROLE;
USE DATABASE moodle_app;

CREATE OR REPLACE IMAGE REPOSITORY moodle_app.public.python_ai_repo;

-- Show the repository details to get the exact registry URL
SHOW IMAGE REPOSITORIES;
```

### 1.2 Note Down Your Repository URL

After running the SQL, look for the `repository_url` in the results. It will look something like:

```
plqnvnr-sg37212.registry.snowflakecomputing.com/moodle_app/public/python_ai_repo
```

**Copy this entire URL** - you'll need it in the next step.

---

## Step 2: Configure Build Script

### 2.1 Open build_and_push.bat

Open the `build_and_push.bat` file in your text editor.

### 2.2 Update Configuration

Fill in your Snowflake details and repository URL:

```batch
REM Configuration - Update these values
set SNOWFLAKE_ACCOUNT=your_account_id
set SNOWFLAKE_USER=your_username
set SNOWFLAKE_PASSWORD=your_password
set REGISTRY_URL=your_registry_url_from_step_1
```

**Example:**
```batch
REM Configuration - Update these values
set SNOWFLAKE_ACCOUNT=ACCOUNT
set SNOWFLAKE_USER=USER
set SNOWFLAKE_PASSWORD=PASS
set REGISTRY_URL=-.registry.snowflakecomputing.com
```

### 2.3 Update Image Repository URL

Update the `IMAGE_REPO_URL` line to match your repository from Step 1:

```batch
set IMAGE_REPO_URL=%REGISTRY_URL%/moodle_app/public/python_ai_repo
```

---

## Step 3: Build and Push Docker Image

### 3.1 Ensure Docker Desktop is Running

Make sure Docker Desktop is started and running on your machine.

### 3.2 Run the Build Script

Open PowerShell in your project directory and run:

```powershell
.\build_and_push.bat
```

### 3.3 Expected Output

You should see output like this:

```
Checking if Docker Desktop is running...
Docker is running. Proceeding with build...
Building Docker image...
[+] Building 71.6s (12/12) FINISHED
...
Tagging image for Snowflake repository...
Logging into Snowflake Docker registry...
Note: Using registry URL: your-registry-url
Login Succeeded
Pushing image to Snowflake...
...
============================================================================
SUCCESS! Docker image pushed to Snowflake successfully!
============================================================================
```

---

## Step 4: Deploy Python Service in Snowflake

After successful Docker push, run this SQL in Snowflake Snowsight:

```sql
-- Step 1: Set up role and database
USE ROLE MOODLE_ROLE;
USE DATABASE moodle_app;

-- Step 2: Create compute pool for Python application
CREATE OR REPLACE COMPUTE POOL python_ai_pool
MIN_NODES = 1
MAX_NODES = 3
INSTANCE_FAMILY = CPU_X64_XS
AUTO_SUSPEND_SECS = 3600;

-- Step 3: Check compute pool status (wait until ACTIVE)
SELECT * FROM INFORMATION_SCHEMA.COMPUTE_POOLS WHERE NAME = 'PYTHON_AI_POOL';

-- Step 4: Create service for Python AI application
-- NOTE: Update your credentials and API keys
CREATE OR REPLACE SERVICE moodle_app.public.python_ai_service
IN COMPUTE POOL python_ai_pool
FROM SPECIFICATION $$
spec:
  containers:
  - name: python-ai-container
    image: /moodle_app/public/python_ai_repo/python-ai:latest
    env:
      SNOWFLAKE_ACCOUNT: your_account_id
      SNOWFLAKE_USER: your_username
      SNOWFLAKE_PASSWORD: your_password
      SNOWFLAKE_WAREHOUSE: COMPUTE_WH
      SNOWFLAKE_DATABASE: moodle_app
      SNOWFLAKE_SCHEMA: public
      OPENAI_API_KEY: your_openai_key_if_available
      GEMINI_API_KEY: your_gemini_key_if_available
      LOG_LEVEL: INFO
      CORS_ORIGINS: "*"
    resources:
      requests:
        memory: 1Gi
        cpu: 0.5
      limits:
        memory: 2Gi
        cpu: 1
  endpoints:
  - name: python-ai-endpoint
    port: 8000
    public: true
$$;

-- Step 5: Check service status
SHOW SERVICES;
SELECT SYSTEM$GET_SERVICE_STATUS('moodle_app.public.python_ai_service');

-- Step 6: Get service endpoint URL (SAVE THIS URL!)
SHOW ENDPOINTS IN SERVICE moodle_app.public.python_ai_service;
```

---

## Step 5: Test Your Deployment

### 5.1 Test Health Endpoint

Replace `<your-endpoint-url>` with the URL from Step 4.6:

```sql
SELECT SYSTEM$SEND_REQUEST('GET', '<your-endpoint-url>/health', {}, {});
```

### 5.2 Expected Response

You should get a JSON response like:

```json
{
  "status": "ok",
  "version": "1.0.0",
  "providers": {
    "openai": false,
    "gemini": false,
    "snowflake": true
  }
}
```

---

## 🔧 Troubleshooting

### Docker Issues

**Error: Docker Desktop not running**
```
Solution: Start Docker Desktop and wait for it to fully load
```

**Error: Registry login failed**
```
Solution: 
1. Check your Snowflake credentials
2. Verify the registry URL from Step 1
3. Ensure your account has proper permissions
```

### Snowflake Service Issues

**Service won't start**
```sql
-- Check compute pool status
SELECT * FROM INFORMATION_SCHEMA.COMPUTE_POOLS WHERE NAME = 'PYTHON_AI_POOL';

-- Check service logs
SELECT SYSTEM$GET_SERVICE_LOGS('moodle_app.public.python_ai_service', 0, 'python-ai-container', 100);
```

---

## 📝 Summary Checklist

- [ ] Created Snowflake image repository
- [ ] Got repository URL from Snowflake
- [ ] Updated build_and_push.bat with credentials and repository URL
- [ ] Successfully built and pushed Docker image
- [ ] Created Snowflake service with SQL script
- [ ] Got service endpoint URL
- [ ] Tested health endpoint
- [ ] Ready to configure Moodle plugin

---

## Next Steps

Once your Python service is running:

1. **Install Moodle Plugin**: Upload and install `local_ai_question_gen`
2. **Configure Plugin**: Set the endpoint URL in plugin settings
3. **Test Integration**: Generate questions using the AI plugin

**🎉 Your Python AI service is now deployed and ready to use with Moodle!**
