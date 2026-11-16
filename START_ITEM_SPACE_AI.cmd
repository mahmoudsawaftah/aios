@echo off
setlocal
cd /d "%~dp0"
title item space AI - Mission Control
where python >nul 2>nul
if errorlevel 1 (
  echo Python was not found. Please install Python or add it to PATH.
  pause
  exit /b 1
)
echo ========================================
echo          item space AI
echo          MISSION CONTROL
echo ========================================
echo Starting local server and opening browser...
echo Keep this minimized window open while using the app.
echo.
python -m factory.console --open-browser
set "APP_EXIT=%ERRORLEVEL%"
if not "%APP_EXIT%"=="0" (
  echo.
  echo Could not start item space AI. Exit code: %APP_EXIT%
  echo Another program may be using port 8765.
  pause
)
endlocal
