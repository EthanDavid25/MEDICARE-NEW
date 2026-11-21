@echo off
setlocal
cd /d "%~dp0.."
echo ========================================================
echo MEDICARE - PyInstaller Windows Standalone Build
echo ========================================================

set PYTHON_EXE=%LOCALAPPDATA%\Programs\Python311\tools\python.exe
if not exist "%PYTHON_EXE%" (
    set PYTHON_EXE=python.exe
)

echo Building MEDICARE executable using PyInstaller...
"%PYTHON_EXE%" -m PyInstaller --clean medicare.spec
if errorlevel 1 (
    echo.
    echo Build failed with error %errorlevel%.
    pause
    exit /b %errorlevel%
)

echo.
echo ========================================================
echo Build complete! Executable is located in dist\MEDICARE\
echo ========================================================
endlocal