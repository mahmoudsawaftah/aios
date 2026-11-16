@echo off
setlocal
cd /d "%~dp0"
title Item Space AI - Live Studio Safe Preview
if "%~1"=="" (
 set "ACTIVE_ROOT=%USERPROFILE%\Documents\aios"
) else (
 set "ACTIVE_ROOT=%~1"
)
echo ============================================================
echo         ITEM SPACE AI / LIVE STUDIO - SAFE PREVIEW
echo ============================================================
echo This runs FROM A SEPARATE CHECKOUT and never starts a worker.
echo Active tasks and approvals are read-only.
echo Active runtime: "%ACTIVE_ROOT%"
echo.
if not exist "%ACTIVE_ROOT%\.factory-runtime\state.sqlite3" (
 echo ERROR: Active AIOS state DB not found.
 goto fail
)
if not exist "factory\readonly_preview.py" (
 echo ERROR: Preview module is missing.
 goto fail
)
where python >nul 2>nul
if errorlevel 1 (
 echo ERROR: Python not found.
 goto fail
)
echo [1/2] Testing isolated UI release candidate...
python -m unittest discover -s tests -p "test_*.py" -v
if errorlevel 1 goto fail
echo.
echo [2/2] Launching read-only Live Studio on http://127.0.0.1:8877
echo Press Ctrl+C to close the preview. This does NOT stop the active worker.
python -m factory.readonly_preview --active-root "%ACTIVE_ROOT%" --port 8877 --open-browser
set "EXIT_CODE=%ERRORLEVEL%"
if not "%EXIT_CODE%"=="0" goto fail
exit /b 0
:fail
echo.
echo PREVIEW NOT STARTED OR STOPPED WITH ERROR. Active work was not modified.
pause
exit /b 1
