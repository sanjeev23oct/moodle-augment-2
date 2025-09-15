@echo off
REM Build and Push Script for Python AI Services to Snowflake (Windows)
REM This script builds Docker images for both AI services and pushes them to Snowflake Image Repository

REM Configuration - Update these values
set SNOWFLAKE_ACCOUNT=
set SNOWFLAKE_USER=
set SNOWFLAKE_PASSWORD=
set REGISTRY_URL=-.registry.snowflakecomputing.com
set IMAGE_REPO_URL=%REGISTRY_URL%/snowflake/default_image_store/ml_repo

REM Image configurations
set AI_PLUGIN_TAG=python-ai:latest
set QUESTION_GEN_TAG=python-question-generator:latest

REM Service selection (set to "all", "ai-plugin", or "question-generator")
set SERVICE=%1
if "%SERVICE%"=="" set SERVICE=all

echo ============================================================================
echo Building and Pushing Python AI Services to Snowflake
echo Service(s) to build: %SERVICE%
echo ============================================================================

echo Checking if Docker Desktop is running...
docker version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Docker Desktop is not running!
    echo Please start Docker Desktop and try again.
    pause
    exit /b 1
)

echo Docker is running. Proceeding with build...

REM Build services based on selection
if "%SERVICE%"=="ai-plugin" (
    echo.
    echo ============================================================================
    echo Building AI Plugin...
    echo ============================================================================
    cd python_ai_plugin
    docker build -t %AI_PLUGIN_TAG% .
    if %errorlevel% neq 0 (
        echo ERROR: Docker build failed for AI Plugin!
        pause
        exit /b 1
    )
    echo Tagging AI Plugin image for Snowflake repository...
    docker tag %AI_PLUGIN_TAG% %IMAGE_REPO_URL%/%AI_PLUGIN_TAG%
    if %errorlevel% neq 0 (
        echo ERROR: Docker tag failed for AI Plugin!
        pause
        exit /b 1
    )
    cd ..
) else if "%SERVICE%"=="question-generator" (
    echo.
    echo ============================================================================
    echo Building Question Generator...
    echo ============================================================================
    cd python_question_generator
    docker build -t %QUESTION_GEN_TAG% .
    if %errorlevel% neq 0 (
        echo ERROR: Docker build failed for Question Generator!
        pause
        exit /b 1
    )
    echo Tagging Question Generator image for Snowflake repository...
    docker tag %QUESTION_GEN_TAG% %IMAGE_REPO_URL%/%QUESTION_GEN_TAG%
    if %errorlevel% neq 0 (
        echo ERROR: Docker tag failed for Question Generator!
        pause
        exit /b 1
    )
    cd ..
) else if "%SERVICE%"=="all" (
    echo.
    echo ============================================================================
    echo Building AI Plugin...
    echo ============================================================================
    cd python_ai_plugin
    docker build -t %AI_PLUGIN_TAG% .
    if %errorlevel% neq 0 (
        echo ERROR: Docker build failed for AI Plugin!
        pause
        exit /b 1
    )
    echo Tagging AI Plugin image for Snowflake repository...
    docker tag %AI_PLUGIN_TAG% %IMAGE_REPO_URL%/%AI_PLUGIN_TAG%
    if %errorlevel% neq 0 (
        echo ERROR: Docker tag failed for AI Plugin!
        pause
        exit /b 1
    )
    cd ..

    echo.
    echo ============================================================================
    echo Building Question Generator...
    echo ============================================================================
    cd python_question_generator
    docker build -t %QUESTION_GEN_TAG% .
    if %errorlevel% neq 0 (
        echo ERROR: Docker build failed for Question Generator!
        pause
        exit /b 1
    )
    echo Tagging Question Generator image for Snowflake repository...
    docker tag %QUESTION_GEN_TAG% %IMAGE_REPO_URL%/%QUESTION_GEN_TAG%
    if %errorlevel% neq 0 (
        echo ERROR: Docker tag failed for Question Generator!
        pause
        exit /b 1
    )
    cd ..
) else (
    echo ERROR: Invalid service specified. Use "all", "ai-plugin", or "question-generator"
    pause
    exit /b 1
)

echo.
echo ============================================================================
echo Logging into Snowflake Docker registry...
echo ============================================================================
echo Note: Using registry URL: %REGISTRY_URL%
echo %SNOWFLAKE_PASSWORD% | docker login %REGISTRY_URL% -u %SNOWFLAKE_USER% --password-stdin
if %errorlevel% neq 0 (
    echo ERROR: Docker login failed!
    echo Please check your Snowflake credentials and network connection.
    pause
    exit /b 1
)

REM Push services based on selection
echo.
echo ============================================================================
echo Pushing images to Snowflake...
echo ============================================================================

if "%SERVICE%"=="ai-plugin" (
    echo.
    echo Pushing AI Plugin to Snowflake...
    docker push %IMAGE_REPO_URL%/%AI_PLUGIN_TAG%
    if %errorlevel% neq 0 (
        echo ERROR: Docker push failed for AI Plugin!
        pause
        exit /b 1
    )
    echo AI Plugin pushed successfully!
) else if "%SERVICE%"=="question-generator" (
    echo.
    echo Pushing Question Generator to Snowflake...
    docker push %IMAGE_REPO_URL%/%QUESTION_GEN_TAG%
    if %errorlevel% neq 0 (
        echo ERROR: Docker push failed for Question Generator!
        pause
        exit /b 1
    )
    echo Question Generator pushed successfully!
) else if "%SERVICE%"=="all" (
    echo.
    echo Pushing AI Plugin to Snowflake...
    docker push %IMAGE_REPO_URL%/%AI_PLUGIN_TAG%
    if %errorlevel% neq 0 (
        echo ERROR: Docker push failed for AI Plugin!
        pause
        exit /b 1
    )
    echo AI Plugin pushed successfully!

    echo.
    echo Pushing Question Generator to Snowflake...
    docker push %IMAGE_REPO_URL%/%QUESTION_GEN_TAG%
    if %errorlevel% neq 0 (
        echo ERROR: Docker push failed for Question Generator!
        pause
        exit /b 1
    )
    echo Question Generator pushed successfully!
)

echo.
echo ============================================================================
echo SUCCESS! Docker images pushed to Snowflake successfully!
echo ============================================================================
echo.
echo NEXT STEPS:
echo 1. Open Snowflake Snowsight in your browser
echo 2. Copy and paste the SQL from the appropriate deployment script:
if "%SERVICE%"=="ai-plugin" (
    echo    - For AI Plugin: snowflake_service_deployment.sql
) else if "%SERVICE%"=="question-generator" (
    echo    - For Question Generator: snowflake_question_generator_deployment.sql
) else if "%SERVICE%"=="all" (
    echo    - For AI Plugin: snowflake_service_deployment.sql
    echo    - For Question Generator: snowflake_question_generator_deployment.sql
)
echo 3. Run the SQL script(s) to create your Python AI service(s)
echo 4. Note down the endpoint URL(s) from the SHOW ENDPOINTS command
echo 5. Install your Moodle plugin and configure it with the endpoint URL(s)
echo.
echo Services built and pushed: %SERVICE%
echo.
echo ============================================================================

pause
