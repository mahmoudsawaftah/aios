@echo off
setlocal
cd /d "%~dp0"
title Item Space AI v3.1 - Setup and Verification
echo.
echo ==================================================
echo          ITEM SPACE AI v3.1 - SAFE SETUP
echo ==================================================
where python >nul 2>nul
if errorlevel 1 goto fail
where git >nul 2>nul
if errorlevel 1 goto fail
where codex >nul 2>nul
if errorlevel 1 (
 echo Codex CLI not found. Install it and sign in, then retry.
 goto fail
)
echo [1/4] Python regression tests...
python -m unittest discover -s tests -p "test_*.py" -v
if errorlevel 1 goto fail
echo [2/4] Legacy control audit...
python scripts\audit_legacy_projects.py .
if errorlevel 1 goto fail
echo [3/4] Registering MCP for Codex CLI / IDE...
powershell -NoProfile -ExecutionPolicy RemoteSigned -File "%~dp0INSTALL_CODEX_BRIDGE.ps1"
if errorlevel 1 goto fail
echo [4/4] Creating Item Space AI desktop shortcut with opt-in Codex worker...
powershell -NoProfile -ExecutionPolicy RemoteSigned -File "%~dp0INSTALL_ITEM_SPACE_AI.ps1" -EnableWorker
if errorlevel 1 goto fail
echo.
echo SETUP COMPLETED. Restart the Codex extension in Antigravity.
echo To run: double-click the Item Space AI desktop shortcut.
echo Keep the app window open while Codex is executing tasks.
echo Build and release still require owner review.
pause
exit /b 0
:fail
echo.
echo SETUP NOT COMPLETE. Review the error above. No deployment was performed.
pause
exit /b 1
