@echo off
chcp 65001 >nul 2>&1
title Backfocus Calculator - Launcher
setlocal EnableDelayedExpansion

echo ============================================
echo   Backfocus Calculator - Auto Launcher
echo ============================================
echo.

:: --- Detect script directory ---
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

:: --- Try to find Python ---
set "PYTHON_CMD="

:: Check if python is in PATH
where python >nul 2>&1
if %ERRORLEVEL% equ 0 (
    :: Verify it's real Python, not the Windows Store stub
    python --version >nul 2>&1
    if %ERRORLEVEL% equ 0 (
        set "PYTHON_CMD=python"
        goto :found_python
    )
)

where python3 >nul 2>&1
if %ERRORLEVEL% equ 0 (
    set "PYTHON_CMD=python3"
    goto :found_python
)

:: Check common installation paths
for %%P in (
    "%LOCALAPPDATA%\Programs\Python\Python313\python.exe"
    "%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
    "%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
    "%LOCALAPPDATA%\Programs\Python\Python310\python.exe"
    "C:\Python313\python.exe"
    "C:\Python312\python.exe"
    "C:\Python311\python.exe"
    "C:\Python310\python.exe"
) do (
    if exist %%P (
        set "PYTHON_CMD=%%~P"
        goto :found_python
    )
)

:: Python not found - offer to install
echo [ERROR] Python was not found on this system.
echo.
echo Python 3.8+ is required to run Backfocus Calculator.
echo.
set /p INSTALL_PYTHON="Download and install Python now? (Y/N): "
if /i "!INSTALL_PYTHON!"=="Y" (
    echo.
    echo Opening Python download page...
    start https://www.python.org/downloads/
    echo.
    echo Please install Python with "Add to PATH" checked.
    echo Then re-run this launcher.
    echo.
    pause
    exit /b 1
)
echo.
echo Please install Python 3.8+ from https://www.python.org/downloads/
echo Make sure to check "Add Python to PATH" during installation.
pause
exit /b 1

:found_python
:: Display Python version
for /f "tokens=*" %%V in ('%PYTHON_CMD% --version 2^>^&1') do set "PY_VERSION=%%V"
echo [OK] Found: %PY_VERSION%

:: --- Check tkinter availability ---
%PYTHON_CMD% -c "import tkinter" >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERROR] tkinter is not available.
    echo Please reinstall Python with "tcl/tk" option enabled.
    pause
    exit /b 1
)
echo [OK] tkinter available

:: --- Create virtual environment if needed ---
if exist "%SCRIPT_DIR%venv\Scripts\python.exe" (
    :: Verify the existing venv actually works (not broken by removed Python)
    "%SCRIPT_DIR%venv\Scripts\python.exe" -c "import sys; sys.exit(0)" >nul 2>&1
    if !ERRORLEVEL! neq 0 (
        echo [!] Broken virtual environment ^(base Python removed^). Recreating...
        rmdir /s /q "%SCRIPT_DIR%venv" >nul 2>&1
    )
)

if not exist "%SCRIPT_DIR%venv" (
    echo.
    echo Creating virtual environment...
    %PYTHON_CMD% -m venv "%SCRIPT_DIR%venv"
    if %ERRORLEVEL% neq 0 (
        echo [WARNING] Could not create venv, running directly...
        goto :run_direct
    )
    echo [OK] Virtual environment created
)

:: --- Activate venv and run ---
if exist "%SCRIPT_DIR%venv\Scripts\python.exe" (
    set "PYTHON_CMD=%SCRIPT_DIR%venv\Scripts\python.exe"
    echo [OK] Using virtual environment
)

:: --- Install dependencies if requirements.txt has content ---
if exist "%SCRIPT_DIR%requirements.txt" (
    "%PYTHON_CMD%" -m pip install -r "%SCRIPT_DIR%requirements.txt" --quiet >nul 2>&1
)

:run_direct
:: --- Launch the application (hide console) ---
echo.
echo Starting Backfocus Calculator...
echo.

:: Try pythonw.exe (GUI, no console) from venv first, then system
set "PYTHONW_CMD="
if exist "%SCRIPT_DIR%venv\Scripts\pythonw.exe" (
    set "PYTHONW_CMD=%SCRIPT_DIR%venv\Scripts\pythonw.exe"
) else (
    where pythonw >nul 2>&1
    if !ERRORLEVEL! equ 0 set "PYTHONW_CMD=pythonw"
)

if defined PYTHONW_CMD (
    start "" "%PYTHONW_CMD%" "%SCRIPT_DIR%backfocus.py"
) else (
    :: Fallback: python.exe — use /b to avoid opening a second console
    start /b "" "%PYTHON_CMD%" "%SCRIPT_DIR%backfocus.py"
)
exit
