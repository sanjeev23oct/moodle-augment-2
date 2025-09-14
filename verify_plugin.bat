@echo off
REM Verification script for AI Question Generator Plugin
REM This script checks if all required files are present

echo ========================================
echo AI Question Generator Plugin Verification
echo ========================================
echo.

set PLUGIN_DIR=%~dp0local_ai_question_gen

echo Checking plugin structure in: %PLUGIN_DIR%
echo.

REM Core files
echo Checking core files...
if exist "%PLUGIN_DIR%\version.php" (echo ✓ version.php) else (echo ✗ version.php - MISSING)
if exist "%PLUGIN_DIR%\lib.php" (echo ✓ lib.php) else (echo ✗ lib.php - MISSING)
if exist "%PLUGIN_DIR%\index.php" (echo ✓ index.php) else (echo ✗ index.php - MISSING)
if exist "%PLUGIN_DIR%\settings.php" (echo ✓ settings.php) else (echo ✗ settings.php - MISSING)
if exist "%PLUGIN_DIR%\README.md" (echo ✓ README.md) else (echo ✗ README.md - MISSING)
if exist "%PLUGIN_DIR%\styles.css" (echo ✓ styles.css) else (echo ✗ styles.css - MISSING)

echo.
echo Checking database files...
if exist "%PLUGIN_DIR%\db\install.xml" (echo ✓ db/install.xml) else (echo ✗ db/install.xml - MISSING)
if exist "%PLUGIN_DIR%\db\access.php" (echo ✓ db/access.php) else (echo ✗ db/access.php - MISSING)
if exist "%PLUGIN_DIR%\db\upgrade.php" (echo ✓ db/upgrade.php) else (echo ✗ db/upgrade.php - MISSING)

echo.
echo Checking language files...
if exist "%PLUGIN_DIR%\lang\en\local_ai_question_gen.php" (echo ✓ lang/en/local_ai_question_gen.php) else (echo ✗ lang/en/local_ai_question_gen.php - MISSING)

echo.
echo Checking classes...
if exist "%PLUGIN_DIR%\classes\ai\ai_provider_interface.php" (echo ✓ classes/ai/ai_provider_interface.php) else (echo ✗ classes/ai/ai_provider_interface.php - MISSING)
if exist "%PLUGIN_DIR%\classes\service\question_generator.php" (echo ✓ classes/service/question_generator.php) else (echo ✗ classes/service/question_generator.php - MISSING)
if exist "%PLUGIN_DIR%\classes\manager\session_manager.php" (echo ✓ classes/manager/session_manager.php) else (echo ✗ classes/manager/session_manager.php - MISSING)
if exist "%PLUGIN_DIR%\classes\manager\question_manager.php" (echo ✓ classes/manager/question_manager.php) else (echo ✗ classes/manager/question_manager.php - MISSING)

echo.
echo Checking templates...
if exist "%PLUGIN_DIR%\templates\main_interface.mustache" (echo ✓ templates/main_interface.mustache) else (echo ✗ templates/main_interface.mustache - MISSING)
if exist "%PLUGIN_DIR%\templates\question_item.mustache" (echo ✓ templates/question_item.mustache) else (echo ✗ templates/question_item.mustache - MISSING)

echo.
echo Checking JavaScript...
if exist "%PLUGIN_DIR%\amd\src\question_generator.js" (echo ✓ amd/src/question_generator.js) else (echo ✗ amd/src/question_generator.js - MISSING)

echo.
echo Checking AJAX endpoints...
if exist "%PLUGIN_DIR%\ajax\generate_questions.php" (echo ✓ ajax/generate_questions.php) else (echo ✗ ajax/generate_questions.php - MISSING)

echo.
echo ========================================
echo Verification complete!
echo ========================================
echo.
echo If all files show ✓, your plugin is ready for deployment.
echo If any files show ✗, please check the file structure.
echo.

pause
