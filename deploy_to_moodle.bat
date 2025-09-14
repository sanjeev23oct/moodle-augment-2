@echo off
REM Deployment script for AI Question Generator Plugin
REM This script copies the plugin to your local Moodle installation

echo ========================================
echo AI Question Generator Plugin Deployment
echo ========================================
echo.

REM Set paths
set SOURCE_DIR=%~dp0local_ai_question_gen
set MOODLE_DIR=D:\xampp\moodle
set TARGET_DIR=%MOODLE_DIR%\local\ai_question_gen

echo Source Directory: %SOURCE_DIR%
echo Target Directory: %TARGET_DIR%
echo.

REM Check if source directory exists
if not exist "%SOURCE_DIR%" (
    echo ERROR: Source directory not found: %SOURCE_DIR%
    echo Please make sure you're running this script from the correct location.
    pause
    exit /b 1
)

REM Check if Moodle directory exists
if not exist "%MOODLE_DIR%" (
    echo ERROR: Moodle directory not found: %MOODLE_DIR%
    echo Please update the MOODLE_DIR variable in this script to match your installation.
    pause
    exit /b 1
)

REM Create local plugins directory if it doesn't exist
if not exist "%MOODLE_DIR%\local" (
    echo Creating local plugins directory...
    mkdir "%MOODLE_DIR%\local"
)

REM Remove existing plugin if it exists
if exist "%TARGET_DIR%" (
    echo Removing existing plugin installation...
    rmdir /s /q "%TARGET_DIR%"
)

REM Copy plugin files
echo Copying plugin files...
xcopy "%SOURCE_DIR%" "%TARGET_DIR%" /E /I /Y

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo Plugin deployed successfully!
    echo ========================================
    echo.
    echo Next steps:
    echo 1. Open your browser and go to your Moodle site
    echo 2. Login as administrator
    echo 3. Go to Site Administration ^> Notifications
    echo 4. Follow the installation prompts
    echo 5. Configure the plugin settings if needed
    echo.
    echo Plugin location: %TARGET_DIR%
    echo.
) else (
    echo.
    echo ERROR: Failed to copy plugin files.
    echo Please check permissions and try again.
    echo.
)

pause
