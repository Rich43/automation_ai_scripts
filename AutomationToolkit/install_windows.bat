@echo off
echo ===============================================
echo Progressive Desktop Automation Setup (Windows)
echo ===============================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo [1/5] Checking Python version...
python -c "import sys; print(f'Python {sys.version}'); exit(0 if sys.version_info >= (3,8) else 1)"
if errorlevel 1 (
    echo ERROR: Python 3.8 or higher is required
    pause
    exit /b 1
)

echo [2/5] Creating virtual environment...
python -m venv automation_env
if errorlevel 1 (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)

echo [3/5] Activating virtual environment...
call automation_env\Scripts\activate.bat

echo [4/5] Installing required packages...
pip install --upgrade pip
pip install flask openai pillow pyautogui psutil requests

if errorlevel 1 (
    echo ERROR: Failed to install packages
    pause
    exit /b 1
)

echo [5/5] Creating run script...
echo @echo off > run_windows.bat
echo echo Starting Progressive Desktop Automation System... >> run_windows.bat
echo call automation_env\Scripts\activate.bat >> run_windows.bat
echo python app.py >> run_windows.bat
echo pause >> run_windows.bat

echo.
echo ===============================================
echo Setup completed successfully!
echo ===============================================
echo.
echo To start the system:
echo   1. Double-click run_windows.bat
echo   2. Or run: python app.py
echo.
echo The web interface will be available at:
echo   http://localhost:5000
echo.
echo IMPORTANT: Configure your OpenAI API key in Settings
echo Get your API key from: https://platform.openai.com/api-keys
echo.
pause