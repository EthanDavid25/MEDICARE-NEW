@echo off
setlocal
cd /d "%~dp0.."
echo =======================================================
echo MEDICARE - Medical Symptoms Triage Advisor (Offline)
echo Cross-Platform Desktop & Mobile Engine
echo =======================================================

set PYTHON_EXE=%LOCALAPPDATA%\Programs\Python311\tools\python.exe
if not exist "%PYTHON_EXE%" (
    set PYTHON_EXE=python.exe
)

echo Starting MEDICARE...
"%PYTHON_EXE%" main.py
if errorlevel 1 (
    echo.
    echo Application exited with error code %errorlevel%.
    pause
)
endlocal