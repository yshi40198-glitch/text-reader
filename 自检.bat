@echo off
rem Self-check launcher - run diagnostics with console
chcp 65001 >nul
"%~dp0python\python.exe" "%~dp0check.py"
echo.
echo [exit code] %errorlevel%
echo.
pause
