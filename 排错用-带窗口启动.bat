@echo off
rem Debug launcher - run with console to show errors
"%~dp0python\python.exe" "%~dp0textreader_app.py"
echo.
echo [exit code] %errorlevel%
echo.
pause
