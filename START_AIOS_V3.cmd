@echo off
setlocal
cd /d "%~dp0"
where python >nul 2>nul
if errorlevel 1 (
  echo Python was not found. Install Python and reopen this window.
  pause
  exit /b 1
)
if /I "%~1"=="auto" (
  echo AIOS v3 automatic worker enabled. Codex usage may count toward your plan limits.
  echo Open http://127.0.0.1:8765 on this computer.
  python -m factory.console --auto-run
) else (
  echo AIOS v3 safe mode. No AI jobs run automatically.
  echo Open http://127.0.0.1:8765 on this computer.
  python -m factory.console
)
if errorlevel 1 pause
endlocal
