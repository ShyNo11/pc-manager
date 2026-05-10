@echo off
echo Uninstalling...
reg delete "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v "WindowsUpdateService" /f >nul 2>&1
taskkill /F /IM "WindowsUpdateService.exe" >nul 2>&1
rd /s /q "%APPDATA%\Microsoft\Windows\WindowsUpdateService" >nul 2>&1
echo Uninstallation complete!
pause