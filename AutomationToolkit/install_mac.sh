#!/bin/bash

echo "==============================================="
echo "Progressive Desktop Automation Setup (macOS)"
echo "==============================================="
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Install Python 3.8+ using one of these methods:"
    echo "  1. Download from https://python.org"
    echo "  2. Using Homebrew: brew install python"
    echo "  3. Using MacPorts: sudo port install python310"
    exit 1
fi

echo "[1/5] Checking Python version..."
python3 -c "import sys; print(f'Python {sys.version}'); exit(0 if sys.version_info >= (3,8) else 1)"
if [ $? -ne 0 ]; then
    echo "ERROR: Python 3.8 or higher is required"
    exit 1
fi

echo "[2/5] Checking macOS accessibility permissions..."
echo "IMPORTANT: macOS requires accessibility permissions for GUI automation"
echo "When prompted, please allow Terminal (or your terminal app) to control your computer"
echo "You may need to go to System Preferences > Security & Privacy > Privacy > Accessibility"
echo

# Check if Homebrew is available for installing dependencies
if command -v brew &> /dev/null; then
    echo "[3/5] Installing system dependencies via Homebrew..."
    brew install python-tk
else
    echo "[3/5] Skipping system dependencies (Homebrew not found)"
    echo "Note: Some features may require tkinter. Install with: brew install python-tk"
fi

echo "[4/5] Creating virtual environment..."
python3 -m venv automation_env
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to create virtual environment"
    exit 1
fi

echo "[5/5] Activating virtual environment and installing packages..."
source automation_env/bin/activate
pip install --upgrade pip
pip install flask openai pillow pyautogui psutil requests

if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install packages"
    exit 1
fi

echo "[6/6] Creating run script..."
cat > run_mac.sh << 'EOF'
#!/bin/bash
echo "Starting Progressive Desktop Automation System..."
cd "$(dirname "$0")"
source automation_env/bin/activate
python3 app.py
EOF

chmod +x run_mac.sh

echo
echo "==============================================="
echo "Setup completed successfully!"
echo "==============================================="
echo
echo "To start the system:"
echo "  1. Run: ./run_mac.sh"
echo "  2. Or: source automation_env/bin/activate && python3 app.py"
echo
echo "The web interface will be available at:"
echo "  http://localhost:5000"
echo
echo "IMPORTANT MACOS SETUP STEPS:"
echo "1. Configure your OpenAI API key in Settings"
echo "   Get your API key from: https://platform.openai.com/api-keys"
echo
echo "2. Enable accessibility permissions:"
echo "   - Go to System Preferences > Security & Privacy > Privacy"
echo "   - Click on 'Accessibility' in the left sidebar"
echo "   - Add Terminal (or your terminal app) to the list"
echo "   - Check the box to enable it"
echo
echo "3. For screen capture permissions:"
echo "   - Go to System Preferences > Security & Privacy > Privacy"
echo "   - Click on 'Screen Recording' in the left sidebar"
echo "   - Add Terminal (or your terminal app) to the list"
echo
echo "Without these permissions, GUI automation will not work!"
echo