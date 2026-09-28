@echo off
title Building CollegeLab AI Agent Executable
cd /d "%~dp0"
echo ========================================================
echo   CollegeLab AI Agent - Windows Executable Builder
echo ========================================================
echo.
echo Installing requirements...
python -m pip install -r requirements.txt
echo.
echo Compiling CollegeLabAI.exe with PyInstaller...
python build_exe.py
echo.
echo Build process finished. Check dist\CollegeLabAI.exe
pause
