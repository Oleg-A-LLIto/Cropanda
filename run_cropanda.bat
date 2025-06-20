@echo off
echo --- Starting Cropanda Launcher ---

REM Get the directory where this batch file is located
set SCRIPT_DIR=%~dp0
echo Batch file location: %SCRIPT_DIR%

REM Change directory to the script's location (handles spaces in path)
echo Changing directory to project folder...
cd /d "%SCRIPT_DIR%"
if errorlevel 1 (
    echo ERROR: Failed to change directory to %SCRIPT_DIR%
    pause
    exit /b 1
)
echo Current directory: %CD%

REM Define the path to the venv activation script
set VENV_ACTIVATE=venv\Scripts\activate.bat
echo Expected activation script: %CD%\%VENV_ACTIVATE%

REM Check if the activation script exists
if not exist "%VENV_ACTIVATE%" (
    echo ERROR: Virtual environment activation script not found!
    echo Expected it at: %CD%\%VENV_ACTIVATE%
    echo Make sure the 'venv' folder exists in the same directory as this batch file.
    pause
    exit /b 1
)
echo Activation script found.

REM Activate the virtual environment
echo Calling activation script: %VENV_ACTIVATE%
call "%VENV_ACTIVATE%"
if errorlevel 1 (
    echo ERROR: Activation script '%VENV_ACTIVATE%' failed or returned an error.
    echo Look for specific errors above this message. The '. was unexpected' might have occurred here.
    pause
    exit /b 1
)
echo Activation script finished. Environment should be active.

REM Define Python script name
set PYTHON_SCRIPT=cropanda.py
echo Expected Python script: %CD%\%PYTHON_SCRIPT%

REM Check if Python script exists
if not exist "%PYTHON_SCRIPT%" (
    echo ERROR: Python script '%PYTHON_SCRIPT%' not found in %CD%
    pause
    exit /b 1
)
echo Python script found.

REM Verify Python command works in venv
echo Verifying python command in venv...
python --version
if errorlevel 1 (
    echo ERROR: 'python --version' command failed after activation.
    echo This might indicate a problem with the venv activation or PATH setup.
    pause
    exit /b 1
)

REM Run the Python script
echo Launching application: python %PYTHON_SCRIPT%
python "%PYTHON_SCRIPT%"
if errorlevel 1 (
    echo ERROR: Python script '%PYTHON_SCRIPT%' exited with an error.
    pause
    exit /b 1
)

echo.
echo Cropanda application closed normally.
pause
echo --- Cropanda Launcher Finished ---