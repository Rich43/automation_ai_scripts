# Progressive Desktop Automation System - Deployment Guide

## Quick Start - Get This Running on Your PC

### 1. Download the Code
```bash
git clone https://github.com/yourusername/progressive-desktop-automation
cd progressive-desktop-automation
```

### 2. Install Requirements
Install the Python dependencies using the provided file:
```bash
pip install -r setup_requirements.txt
```
Alternatively, run the platform-specific install script to automatically set up
a virtual environment and create a convenient `run_*.{bat,sh}` launcher:
`install_windows.bat`, `install_mac.sh`, or `install_linux.sh`.

### 3. Configure OpenAI API Key
Launch the application and open the **Settings** dialog. Paste your key there to
enable OpenAI features. The old `.env` file approach is no longer required.

### 4. Run the System
```bash
python app.py
```

Then open your browser to: `http://localhost:5000`

## What This System Does

### Automatic Software Installation & Circuit Creation
- **Detects** if KiCad is installed on your system
- **Automatically installs** KiCad if needed (Windows/Mac/Linux)
- **Creates circuits** using AI vision to control KiCad
- **Generates** complete PCB files ready for manufacturing

### 7 Progressive Challenge Levels
1. **System Detection** - Scans your computer for installed software
2. **Software Installation** - Auto-installs KiCad and dependencies
3. **Application Launch** - Opens KiCad using AI vision
4. **UI Navigation** - Navigates KiCad interface intelligently
5. **Complex Tasks** - Creates schematic diagrams
6. **File Management** - Manages project files and exports
7. **Advanced Operations** - Generates PCB layouts and manufacturing files

## Example Circuit Created
The system automatically creates a **CR2032 + Switch + LED circuit**:
- CR2032 3V battery holder
- Momentary push button switch
- 5mm LED (any color)
- 330Ω current-limiting resistor
- Complete PCB layout with proper routing

## Files Generated
- `cr2032_led_circuit.sch` - KiCad schematic
- `cr2032_led_circuit.kicad_pcb` - PCB layout
- `cr2032_led_circuit.pro` - Project file
- Manufacturing files (Gerber format)

## Time Savings
- **Manual work**: 45-60 minutes
- **Automated time**: 5-10 minutes
- **Time savings**: 85%
- **Accuracy**: Eliminates human errors

## Requirements
- Python 3.8+
- OpenAI API key
- Internet connection
- Windows, Mac, or Linux desktop

## Supported Software
The system can be extended to automate:
- KiCad (PCB design)
- Eagle CAD
- Fusion 360
- SolidWorks
- And any desktop application

## Getting OpenAI API Key
1. Go to https://platform.openai.com/
2. Create an account or sign in
3. Navigate to the **API Keys** section
4. Create a new secret key
5. Paste the key into the application's **Settings** dialog

## Troubleshooting
- Make sure you have a graphical desktop environment
- Ensure OpenAI API key has sufficient credits
- Check that your system allows GUI automation
- For Linux: Install `xvfb` for headless operation

## License
MIT License - Feel free to use and modify for your projects!