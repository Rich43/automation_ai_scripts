#!/bin/bash

echo "==============================================="
echo "Progressive Desktop Automation Setup (Linux)"
echo "==============================================="
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Install Python 3.8+ using your package manager:"
    echo "  Ubuntu/Debian: sudo apt update && sudo apt install python3 python3-pip python3-venv"
    echo "  CentOS/RHEL: sudo yum install python3 python3-pip"
    echo "  Fedora: sudo dnf install python3 python3-pip"
    echo "  Arch: sudo pacman -S python python-pip"
    exit 1
fi

echo "[1/6] Checking Python version..."
python3 -c "import sys; print(f'Python {sys.version}'); exit(0 if sys.version_info >= (3,8) else 1)"
if [ $? -ne 0 ]; then
    echo "ERROR: Python 3.8 or higher is required"
    exit 1
fi

echo "[2/6] Installing system dependencies..."
# Detect package manager and install dependencies
if command -v apt &> /dev/null; then
    echo "Detected Debian/Ubuntu system"
    sudo apt update
    sudo apt install -y python3-tk python3-dev scrot xvfb xauth
elif command -v yum &> /dev/null; then
    echo "Detected CentOS/RHEL system"
    sudo yum install -y tkinter python3-devel scrot xorg-x11-server-Xvfb xauth
elif command -v dnf &> /dev/null; then
    echo "Detected Fedora system"
    sudo dnf install -y tkinter python3-devel scrot xorg-x11-server-Xvfb xauth
elif command -v pacman &> /dev/null; then
    echo "Detected Arch system"
    sudo pacman -S tk python-pip scrot xorg-server-xvfb xorg-xauth
else
    echo "WARNING: Unknown package manager. You may need to install tkinter, scrot, and xvfb manually"
fi

echo "[3/6] Creating virtual environment..."
python3 -m venv automation_env
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to create virtual environment"
    echo "Try installing python3-venv: sudo apt install python3-venv"
    exit 1
fi

echo "[4/6] Activating virtual environment..."
source automation_env/bin/activate

echo "[5/6] Installing Python packages..."
pip install --upgrade pip
pip install flask openai pillow pyautogui psutil requests

if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install packages"
    exit 1
fi

echo "[6/6] Creating run script..."
cat > run_linux.sh << 'EOF'
#!/bin/bash
echo "Starting Progressive Desktop Automation System..."
cd "$(dirname "$0")"
source automation_env/bin/activate
python3 app.py
EOF

chmod +x run_linux.sh

echo
echo "==============================================="
echo "Setup completed successfully!"
echo "==============================================="
echo
echo "To start the system:"
echo "  1. Run: ./run_linux.sh"
echo "  2. Or: source automation_env/bin/activate && python3 app.py"
echo
echo "The web interface will be available at:"
echo "  http://localhost:5000"
echo
echo "IMPORTANT: Configure your OpenAI API key in Settings"
echo "Get your API key from: https://platform.openai.com/api-keys"
echo
echo "For GUI automation to work properly:"
echo "  - Make sure you're running in a desktop environment"
echo "  - The system needs to control mouse and keyboard"
echo "  - Some automation features may require running with sudo"
echo