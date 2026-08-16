@echo off
rem AI neural voice self-test - requires internet
chcp 65001 >nul
"%~dp0python\python.exe" "%~dp0ai_test.py"
echo.
pause
