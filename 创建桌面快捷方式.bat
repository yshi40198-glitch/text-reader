@echo off
chcp 65001 >nul
title Create Desktop Shortcut
cd /d "%~dp0"
echo 正在创建桌面快捷方式...

powershell -NoProfile -ExecutionPolicy Bypass -Command "$ErrorActionPreference='Stop'; $d=Get-Location; $exe=Join-Path $d 'python\pythonw.exe'; $tgt=Join-Path $d 'textreader_app.py'; $ico=Join-Path $d 'assets\app.ico'; if(-not (Test-Path $ico)){ $ico=$exe }; $name=[string][char]0x6587+[char]0x5B57+[char]0x6717+[char]0x8BFB+[char]0x5DE5+[char]0x5177; $lnk=Join-Path ([Environment]::GetFolderPath('Desktop')) ($name+'.lnk'); $ws=New-Object -ComObject WScript.Shell; $s=$ws.CreateShortcut($lnk); $s.TargetPath=$exe; $s.Arguments='\"'+$tgt+'\"'; $s.WorkingDirectory=$d; $s.IconLocation=$ico+',0'; $s.Description='文字朗读工具 n2.4'; $s.Save(); if(Test-Path $lnk){Write-Host 'OK'; exit 0}else{Write-Host 'FAIL'; exit 1}"

if %errorlevel%==0 (
  echo.
  echo  完成！桌面上已出现「文字朗读工具」金色羽毛图标。
  echo  以后双击它就能直接打开软件。
) else (
  echo.
  echo  创建失败。请用普通用户账户运行本脚本，或把软件放到桌面再试。
)
echo.
pause
