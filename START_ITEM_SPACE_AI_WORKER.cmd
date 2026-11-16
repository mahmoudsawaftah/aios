@echo off
setlocal
cd /d "%~dp0"
title item space AI - Autonomous Task Worker
where python >nul 2>nul
if errorlevel 1 (
 echo Python missing or not on PATH.
 pause
 exit /b 1
)
echo ========================================
echo          ITEM SPACE AI - WORKER
echo ========================================
echo Automated Codex tasks are enabled until approval gates.
echo Execution counts against your Codex plan limits.
echo GitHub PR publishing and production deployment are NOT enabled.
echo Leave this window running or minimized.
python -m factory.console --auto-run --open-browser
if errorlevel 1 pause
endlocal
