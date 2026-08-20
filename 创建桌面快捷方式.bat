@echo off
setlocal
cd /d "%~dp0"
title Create Desktop Shortcut
echo ============================================
echo   Create desktop shortcut for Text Reader
echo ============================================
echo.

powershell -NoProfile -ExecutionPolicy Bypass -Command "$ErrorActionPreference='Stop'; try { $d=(Get-Location).Path; $exe=Join-Path $d 'python\pythonw.exe'; if(-not (Test-Path -LiteralPath $exe)){ throw 'pythonw.exe not found' }; $tgt=Join-Path $d 'textreader_app.py'; $ico=Join-Path $d 'assets\app.ico'; if(-not (Test-Path -LiteralPath $ico)){ $ico=$exe }; $name=[string][char]0x6587+[char]0x5B57+[char]0x6717+[char]0x8BFB+[char]0x5DE5+[char]0x5177; $lnk=Join-Path ([Environment]::GetFolderPath('Desktop')) ($name+'.lnk'); $ws=New-Object -ComObject WScript.Shell; $s=$ws.CreateShortcut($lnk); $s.TargetPath=$exe; $s.Arguments='\"'+$tgt+'\"'; $s.WorkingDirectory=$d; $s.IconLocation=$ico+',0'; $s.Save(); if(Test-Path -LiteralPath $lnk){ Write-Host 'OK'; exit 0 } else { throw 'shortcut file not found after save' } } catch { Write-Host ('ERR: '+$_.Exception.Message); exit 1 }"

if %errorlevel%==0 (
  echo.
  echo   Done! Shortcut created on your desktop.
) else (
  echo.
  echo   FAILED. Please run this script as a normal user
  echo   do NOT use "Run as administrator".
)
echo.
pause
