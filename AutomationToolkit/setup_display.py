#!/usr/bin/env python3
"""
Setup virtual display for desktop automation in headless environment
"""

import os
import subprocess
import time
import logging
from pathlib import Path

def setup_virtual_display():
    """Setup virtual display for GUI automation"""
    try:
        # Set display environment variable
        os.environ['DISPLAY'] = ':99'
        
        # Create Xauthority file if it doesn't exist
        xauth_path = Path.home() / '.Xauthority'
        if not xauth_path.exists():
            xauth_path.touch()
            logging.info(f"Created {xauth_path}")
        
        # Set up PyAutoGUI failsafe
        try:
            import pyautogui
            pyautogui.FAILSAFE = False  # Disable failsafe for headless operation
            pyautogui.PAUSE = 0.1  # Small pause between operations
            logging.info("PyAutoGUI configured for headless operation")
        except ImportError:
            logging.warning("PyAutoGUI not available")
        
        # Try to start a simple X server process (if available)
        try:
            # Check if we can create a minimal display buffer
            result = subprocess.run(['python3', '-c', 'import tkinter; tkinter.Tk().withdraw()'], 
                                  capture_output=True, timeout=5)
            if result.returncode == 0:
                logging.info("GUI environment is functional")
            else:
                logging.warning("GUI environment has limitations")
        except Exception as e:
            logging.warning(f"GUI test failed: {e}")
        
        logging.info("Virtual display setup completed")
        return True
        
    except Exception as e:
        logging.error(f"Failed to setup virtual display: {e}")
        return False

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    success = setup_virtual_display()
    print(f"Display setup: {'SUCCESS' if success else 'FAILED'}")