@echo off
REM Build and Push Script for Python AI Plugin to Snowflake (Windows)
REM This script builds the Docker image and pushes it to Snowflake Image Repository

REM Configuration - Update these values
set SNOWFLAKE_ACCOUNT=
set SNOWFLAKE_USER=
set SNOWFLAKE_PASSWORD=
set REGISTRY_URL=-.registry.snowflakecomputing.com
set IMAGE_REPO_URL=%REGISTRY_URL%/snowflake/default_image_store/ml_repo
set IMAGE_TAG=python-ai:latest

echo Checking if Docker Desktop is running...
docker version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Docker Desktop is not running!
    echo Please start Docker Desktop and try again.
    pause
    exit /b 1
)

echo Docker is running. Proceeding with build...

echo Building Docker image...
cd python_ai_plugin
docker build -t %IMAGE_TAG% .
if %errorlevel% neq 0 (
    echo ERROR: Docker build failed!
    pause
    exit /b 1
)

echo Tagging image for Snowflake repository...
docker tag %IMAGE_TAG% %IMAGE_REPO_URL%/%IMAGE_TAG%
if %errorlevel% neq 0 (
    echo ERROR: Docker tag failed!
    pause
    exit /b 1
)

echo Logging into Snowflake Docker registry...
echo Note: Using registry URL: %REGISTRY_URL%
echo %SNOWFLAKE_PASSWORD% | docker login %REGISTRY_URL% -u %SNOWFLAKE_USER% --password-stdin
if %errorlevel% neq 0 (
    echo ERROR: Docker login failed!
    echo Please check your Snowflake credentials and network connection.
    pause
    exit /b 1
)

echo Pushing image to Snowflake...
docker push %IMAGE_REPO_URL%/%IMAGE_TAG%
if %errorlevel% neq 0 (
    echo ERROR: Docker push failed!
    pause
    exit /b 1
)

echo.
echo ============================================================================
echo SUCCESS! Docker image pushed to Snowflake successfully!
echo ============================================================================
echo.
echo NEXT STEPS:
echo 1. Open Snowflake Snowsight in your browser
echo 2. Copy and paste the SQL from: snowflake_service_deployment.sql
echo 3. Run the SQL script to create your Python AI service
echo 4. Note down the endpoint URL from the SHOW ENDPOINTS command
echo 5. Install your Moodle plugin and configure it with the endpoint URL
echo.
echo The SQL script is ready in: snowflake_service_deployment.sql
echo.
echo ============================================================================

pause
