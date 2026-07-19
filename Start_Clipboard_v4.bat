@echo off
cd /d "%~dp0"
echo Generating Clipboard v4 from Clipboard_v4_Master_Base.xlsx...
py -3 generate.py
if errorlevel 1 python generate.py
if errorlevel 1 (
  echo.
  echo Clipboard generation failed. Review VALIDATION.txt.
  pause
  exit /b 1
)
cd clipboard_generated
start "" http://localhost:8000
py -3 -m http.server 8000
if errorlevel 1 python -m http.server 8000
