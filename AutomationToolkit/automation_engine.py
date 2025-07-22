"""
Core automation engine for desktop interactions
Handles PyAutoGUI operations with AI vision guidance
"""

import pyautogui
import time
import base64
import io
from PIL import ImageGrab, Image
from vision_analyzer import VisionAnalyzer
from logger_config import setup_logger

class AutomationEngine:
    def __init__(self):
        self.logger = setup_logger(__name__)
        self.vision = VisionAnalyzer()
        self.headless_mode = False
        
        # Setup display environment
        self._setup_display_environment()
        
        # Configure PyAutoGUI
        try:
            pyautogui.FAILSAFE = False  # Disable for headless operation
            pyautogui.PAUSE = 0.5
            # Test if we can access the display
            pyautogui.size()
            self.logger.info("GUI environment detected")
        except Exception as e:
            self.logger.warning(f"GUI environment not available: {e}")
            self.headless_mode = True
        
        self.logger.info(f"Automation engine initialized (headless: {self.headless_mode})")
    
    def _setup_display_environment(self):
        """Setup display environment for automation"""
        import os
        from pathlib import Path
        
        try:
            # Set DISPLAY if not already set
            if 'DISPLAY' not in os.environ:
                os.environ['DISPLAY'] = ':0'
            
            # Create Xauthority file if it doesn't exist
            xauth_path = Path.home() / '.Xauthority'
            if not xauth_path.exists():
                xauth_path.touch()
                self.logger.info(f"Created {xauth_path}")
                
        except Exception as e:
            self.logger.warning(f"Could not setup display environment: {e}")
    
    def take_screenshot(self, save_path=None):
        """Take a screenshot of the desktop"""
        try:
            screenshot = ImageGrab.grab()
            if save_path:
                screenshot.save(save_path)
            return screenshot
        except Exception as e:
            self.logger.error(f"Failed to take screenshot: {e}")
            raise
    
    def screenshot_to_base64(self, screenshot=None):
        """Convert screenshot to base64 string"""
        if screenshot is None:
            screenshot = self.take_screenshot()
        
        buffer = io.BytesIO()
        screenshot.save(buffer, format='PNG')
        return base64.b64encode(buffer.getvalue()).decode()
    
    def find_element_coordinates(self, description, screenshot=None):
        """Use AI vision to find element coordinates on screen"""
        try:
            if screenshot is None:
                screenshot = self.take_screenshot()
            
            screenshot_b64 = self.screenshot_to_base64(screenshot)
            
            prompt = f"""
            Analyze this desktop screenshot and find the element described as: "{description}"
            
            Return the pixel coordinates of the CENTER of the element in JSON format:
            {{"x": coordinate, "y": coordinate, "found": true/false, "confidence": 0.0-1.0}}
            
            If the element is not found or you're not confident, set found to false.
            """
            
            response = self.vision.analyze_screenshot_for_coordinates(screenshot_b64, prompt)
            
            if response.get('found', False):
                self.logger.info(f"Found element '{description}' at ({response['x']}, {response['y']}) with confidence {response['confidence']}")
                return response['x'], response['y']
            else:
                self.logger.warning(f"Element '{description}' not found in screenshot")
                return None, None
                
        except Exception as e:
            self.logger.error(f"Error finding element coordinates: {e}")
            return None, None
    
    def click_element(self, description, max_attempts=3):
        """Find and click an element using AI vision"""
        for attempt in range(max_attempts):
            try:
                self.logger.info(f"Attempting to click '{description}' (attempt {attempt + 1}/{max_attempts})")
                
                x, y = self.find_element_coordinates(description)
                
                if x is not None and y is not None:
                    # Move to element and click
                    pyautogui.moveTo(x, y, duration=0.5)
                    time.sleep(0.2)
                    pyautogui.click()
                    
                    self.logger.info(f"Successfully clicked '{description}' at ({x}, {y})")
                    return True
                else:
                    self.logger.warning(f"Could not find '{description}' on attempt {attempt + 1}")
                    
                # Wait before retry
                if attempt < max_attempts - 1:
                    time.sleep(2)
                    
            except Exception as e:
                self.logger.error(f"Error clicking element on attempt {attempt + 1}: {e}")
                
        self.logger.error(f"Failed to click '{description}' after {max_attempts} attempts")
        return False
    
    def type_text(self, text, delay=0.1):
        """Type text with specified delay between characters"""
        try:
            self.logger.info(f"Typing text: {text[:50]}{'...' if len(text) > 50 else ''}")
            pyautogui.write(text, interval=delay)
            return True
        except Exception as e:
            self.logger.error(f"Error typing text: {e}")
            return False
    
    def press_key(self, key):
        """Press a specific key"""
        try:
            self.logger.info(f"Pressing key: {key}")
            pyautogui.press(key)
            return True
        except Exception as e:
            self.logger.error(f"Error pressing key {key}: {e}")
            return False
    
    def key_combination(self, *keys):
        """Press a combination of keys"""
        try:
            self.logger.info(f"Pressing key combination: {'+'.join(keys)}")
            pyautogui.hotkey(*keys)
            return True
        except Exception as e:
            self.logger.error(f"Error pressing key combination: {e}")
            return False
    
    def wait_for_element(self, description, timeout=30, check_interval=2):
        """Wait for an element to appear on screen"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            self.logger.info(f"Waiting for element '{description}'...")
            
            x, y = self.find_element_coordinates(description)
            if x is not None and y is not None:
                self.logger.info(f"Element '{description}' appeared after {time.time() - start_time:.1f} seconds")
                return True
            
            time.sleep(check_interval)
        
        self.logger.warning(f"Element '{description}' did not appear within {timeout} seconds")
        return False
    
    def verify_screen_state(self, expected_description):
        """Verify that the screen shows expected content"""
        try:
            screenshot = self.take_screenshot()
            screenshot_b64 = self.screenshot_to_base64(screenshot)
            
            prompt = f"""
            Analyze this desktop screenshot and determine if it shows: "{expected_description}"
            
            Return a JSON response with:
            {{"matches": true/false, "confidence": 0.0-1.0, "description": "what you actually see"}}
            """
            
            response = self.vision.analyze_screenshot_general(screenshot_b64, prompt)
            
            self.logger.info(f"Screen verification for '{expected_description}': {response}")
            return response.get('matches', False), response.get('confidence', 0.0)
            
        except Exception as e:
            self.logger.error(f"Error verifying screen state: {e}")
            return False, 0.0
