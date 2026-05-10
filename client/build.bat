@echo off
cd /d "%~dp0"
pip install -r requirements.txt
pyinstaller --onefile --noconsole --name "WindowsUpdateService" --icon NONE main.py
echo.
echo Build complete! EXE file: dist\WindowsUpdateService.exe
pause