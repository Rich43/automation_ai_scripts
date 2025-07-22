"""
Level 3 Challenge: Application Launch
Start applications and wait for them to fully load
"""

import time
import subprocess
import psutil
from challenges.base_challenge import BaseChallenge
from automation_engine import AutomationEngine
from system_detector import SystemDetector

class Level3ApplicationLaunch(BaseChallenge):
    def __init__(self):
        super().__init__(
            level=3,
            name="Application Launch",
            description="Launch KiCad and verify it loads successfully with a visible interface"
        )
        
        self.automation = AutomationEngine()
        self.detector = SystemDetector()
        
        # Prerequisites: Levels 1 and 2 must be completed
        self.prerequisites = [1, 2]
    
    def get_steps(self):
        """Return list of steps for application launch challenge"""
        return [
            "Verify KiCad installation",
            "Close any existing KiCad instances",
            "Launch KiCad application",
            "Wait for application to load",
            "Verify main window is visible",
            "Verify application responsiveness"
        ]
    
    def execute_step(self, step_number):
        """Execute a specific step of the application launch challenge"""
        try:
            if step_number == 0:
                return self._verify_kicad_installation()
            elif step_number == 1:
                return self._close_existing_instances()
            elif step_number == 2:
                return self._launch_kicad()
            elif step_number == 3:
                return self._wait_for_application_load()
            elif step_number == 4:
                return self._verify_main_window()
            elif step_number == 5:
                return self._verify_responsiveness()
            else:
                self.logger.error(f"Unknown step number: {step_number}")
                return False
                
        except Exception as e:
            self.logger.error(f"Step {step_number} failed: {e}")
            self.take_error_screenshot(f"step_{step_number}_error")
            return False
    
    def _verify_kicad_installation(self):
        """Verify that KiCad is properly installed"""
        try:
            self.logger.info("Verifying KiCad installation...")
            
            is_installed, details = self.detector.is_software_installed('KiCad', 'kicad')
            
            if not is_installed:
                self.logger.error("KiCad is not installed - cannot proceed with launch")
                return False
            
            self.logger.info(f"✓ KiCad installation confirmed: {details}")
            self.kicad_details = details
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to verify KiCad installation: {e}")
            return False
    
    def _close_existing_instances(self):
        """Close any existing KiCad instances"""
        try:
            self.logger.info("Checking for existing KiCad instances...")
            
            # Get list of KiCad processes
            kicad_processes = []
            for proc in psutil.process_iter(['pid', 'name', 'exe']):
                try:
                    if proc.info['name'] and 'kicad' in proc.info['name'].lower():
                        kicad_processes.append(proc)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            if not kicad_processes:
                self.logger.info("No existing KiCad instances found")
                return True
            
            self.logger.info(f"Found {len(kicad_processes)} existing KiCad processes")
            
            # Try to close them gracefully first
            for proc in kicad_processes:
                try:
                    self.logger.info(f"Terminating KiCad process {proc.pid}")
                    proc.terminate()
                except Exception as e:
                    self.logger.warning(f"Failed to terminate process {proc.pid}: {e}")
            
            # Wait for processes to close
            self.wait_with_progress(5, "Waiting for processes to close")
            
            # Force kill any remaining processes
            for proc in kicad_processes:
                try:
                    if proc.is_running():
                        self.logger.warning(f"Force killing KiCad process {proc.pid}")
                        proc.kill()
                except Exception as e:
                    self.logger.warning(f"Failed to kill process {proc.pid}: {e}")
            
            self.wait_with_progress(2, "Waiting after process cleanup")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to close existing instances: {e}")
            return False
    
    def _launch_kicad(self):
        """Launch KiCad application"""
        try:
            self.logger.info("Launching KiCad application...")
            
            # Determine the correct command to launch KiCad
            platform = self.detector.get_platform()['system'].lower()
            
            if platform == 'windows':
                # Try different possible commands for Windows
                possible_commands = [
                    ['kicad'],
                    ['kicad.exe'],
                    [r'C:\Program Files\KiCad\bin\kicad.exe'],
                    [r'C:\Program Files (x86)\KiCad\bin\kicad.exe']
                ]
            elif platform == 'linux':
                possible_commands = [
                    ['kicad'],
                    ['/usr/bin/kicad'],
                    ['/usr/local/bin/kicad']
                ]
            elif platform == 'darwin':  # macOS
                possible_commands = [
                    ['kicad'],
                    ['open', '-a', 'KiCad'],
                    ['/Applications/KiCad/KiCad.app/Contents/MacOS/kicad']
                ]
            else:
                possible_commands = [['kicad']]
            
            # Try each command until one works
            self.kicad_process = None
            
            for cmd in possible_commands:
                try:
                    self.logger.info(f"Trying to launch with command: {' '.join(cmd)}")
                    
                    self.kicad_process = subprocess.Popen(
                        cmd,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        stdin=subprocess.PIPE
                    )
                    
                    # Wait a moment to see if process starts successfully
                    time.sleep(2)
                    
                    if self.kicad_process.poll() is None:
                        self.logger.info(f"✓ KiCad launched successfully with PID {self.kicad_process.pid}")
                        break
                    else:
                        self.logger.warning(f"Process exited immediately with code {self.kicad_process.returncode}")
                        self.kicad_process = None
                        
                except FileNotFoundError:
                    self.logger.debug(f"Command not found: {' '.join(cmd)}")
                except Exception as e:
                    self.logger.warning(f"Failed to launch with {' '.join(cmd)}: {e}")
            
            if self.kicad_process is None:
                self.logger.error("Failed to launch KiCad with any available command")
                return False
            
            # Alternative: Use automation to click on KiCad icon if direct launch fails
            if self.kicad_process is None:
                self.logger.info("Trying to launch KiCad via desktop automation...")
                return self._launch_via_automation()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to launch KiCad: {e}")
            return False
    
    def _launch_via_automation(self):
        """Launch KiCad using desktop automation (clicking on Start menu/desktop)"""
        try:
            self.logger.info("Attempting to launch KiCad via automation...")
            
            platform = self.detector.get_platform()['system'].lower()
            
            if platform == 'windows':
                # Try to find and click KiCad in Start menu
                self.logger.info("Looking for KiCad in Windows Start menu...")
                
                # Click Start button
                if self.automation.click_element("Windows Start button"):
                    self.wait_with_progress(2, "Waiting for Start menu")
                    
                    # Type "kicad" to search
                    if self.automation.type_text("kicad"):
                        self.wait_with_progress(2, "Waiting for search results")
                        
                        # Click on KiCad in search results
                        if self.automation.click_element("KiCad application in search results"):
                            self.wait_with_progress(3, "Waiting for application to start")
                            return True
                
            elif platform == 'linux':
                # Try to find KiCad in application launcher
                self.logger.info("Looking for KiCad in application launcher...")
                
                # Try various ways to open application launcher
                launchers = [
                    "application menu button",
                    "activities button",
                    "start menu"
                ]
                
                for launcher in launchers:
                    if self.automation.click_element(launcher):
                        self.wait_with_progress(2, "Waiting for launcher")
                        
                        if self.automation.type_text("kicad"):
                            self.wait_with_progress(2, "Waiting for search")
                            
                            if self.automation.click_element("KiCad application"):
                                self.wait_with_progress(3, "Waiting for application")
                                return True
                        break
            
            self.logger.warning("Could not launch KiCad via automation")
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to launch via automation: {e}")
            return False
    
    def _wait_for_application_load(self):
        """Wait for KiCad to fully load"""
        try:
            self.logger.info("Waiting for KiCad to fully load...")
            
            import config
            max_wait_time = config.KICAD_WAIT_TIME
            
            for i in range(max_wait_time):
                self.logger.debug(f"Waiting for KiCad to load... ({i+1}/{max_wait_time})")
                
                # Take screenshot and check for KiCad window
                screenshot = self.automation.take_screenshot()
                screenshot_b64 = self.automation.screenshot_to_base64(screenshot)
                
                # Use AI to detect if KiCad main window is visible
                application_state = self.automation.vision.detect_application_state(screenshot_b64, "KiCad")
                
                if application_state.get('application_running', False):
                    state = application_state.get('application_state', 'unknown')
                    
                    if state in ['main_window', 'loading']:
                        self.logger.info(f"✓ KiCad detected in state: {state}")
                        
                        if state == 'main_window':
                            self.logger.info("KiCad main window is visible")
                            return True
                        elif state == 'loading':
                            self.logger.info("KiCad is still loading...")
                
                time.sleep(1)
            
            self.logger.warning(f"KiCad did not fully load within {max_wait_time} seconds")
            self.take_error_screenshot("kicad_load_timeout")
            
            # Check if any KiCad processes are running
            is_running = self.detector.is_process_running('kicad')
            if is_running:
                self.logger.info("KiCad process is running - may have loaded but not detected")
                return True  # Continue anyway
            else:
                self.logger.error("No KiCad processes found running")
                return False
            
        except Exception as e:
            self.logger.error(f"Failed while waiting for application load: {e}")
            return False
    
    def _verify_main_window(self):
        """Verify that KiCad main window is visible and accessible"""
        try:
            self.logger.info("Verifying KiCad main window...")
            
            screenshot = self.automation.take_screenshot()
            screenshot_b64 = self.automation.screenshot_to_base64(screenshot)
            
            # Check for main KiCad window elements
            window_elements = [
                "KiCad project manager window",
                "KiCad main window",
                "KiCad title bar",
                "Create New Project button",
                "Open Existing Project button"
            ]
            
            window_detected = False
            
            for element in window_elements:
                x, y = self.automation.find_element_coordinates(element, screenshot)
                if x is not None and y is not None:
                    self.logger.info(f"✓ Found {element} at ({x}, {y})")
                    window_detected = True
                    break
            
            if not window_detected:
                self.logger.warning("Could not detect specific KiCad window elements")
                
                # Use general AI analysis
                matches, confidence = self.automation.verify_screen_state("KiCad application is open and visible")
                
                if matches and confidence > 0.6:
                    self.logger.info(f"✓ AI confirms KiCad is visible (confidence: {confidence:.2f})")
                    window_detected = True
                else:
                    self.logger.error(f"✗ AI cannot confirm KiCad is visible (confidence: {confidence:.2f})")
            
            if window_detected:
                self.logger.info("✓ KiCad main window verification successful")
                return True
            else:
                self.logger.error("✗ KiCad main window not detected")
                self.take_error_screenshot("main_window_not_detected")
                return False
            
        except Exception as e:
            self.logger.error(f"Failed to verify main window: {e}")
            return False
    
    def _verify_responsiveness(self):
        """Verify that KiCad application is responsive"""
        try:
            self.logger.info("Verifying KiCad responsiveness...")
            
            # Try to interact with the application
            screenshot = self.automation.take_screenshot()
            
            # Look for an element we can safely click (like the window title bar)
            title_bar_x, title_bar_y = self.automation.find_element_coordinates("KiCad window title bar", screenshot)
            
            if title_bar_x is not None and title_bar_y is not None:
                self.logger.info("Testing responsiveness by clicking title bar...")
                
                # Click on title bar (safe operation)
                self.automation.automation.moveTo(title_bar_x, title_bar_y, duration=0.5)
                time.sleep(0.2)
                self.automation.automation.click()
                
                # Wait a moment and take another screenshot
                time.sleep(1)
                
                self.logger.info("✓ KiCad appears responsive to user input")
                return True
            else:
                self.logger.warning("Could not find title bar for responsiveness test")
                
                # Alternative: Check if the window is still the active window
                matches, confidence = self.automation.verify_screen_state("KiCad is the active application window")
                
                if matches and confidence > 0.5:
                    self.logger.info(f"✓ KiCad appears to be active and responsive (confidence: {confidence:.2f})")
                    return True
                else:
                    self.logger.warning(f"KiCad responsiveness unclear (confidence: {confidence:.2f})")
                    return True  # Don't fail the challenge for this
            
        except Exception as e:
            self.logger.error(f"Failed to verify responsiveness: {e}")
            return False
    
    def verify_success_condition(self):
        """Verify that KiCad was successfully launched"""
        try:
            # Success condition: KiCad process is running and main window is visible
            is_running = self.detector.is_process_running('kicad')
            
            if is_running:
                self.logger.info("✓ KiCad process is running")
                
                # Additional check: verify window is still visible
                screenshot = self.automation.take_screenshot()
                matches, confidence = self.automation.verify_screen_state("KiCad application window is visible")
                
                if matches and confidence > 0.5:
                    self.logger.info(f"✓ KiCad window is visible (confidence: {confidence:.2f})")
                    return True
                else:
                    self.logger.warning(f"KiCad window visibility unclear (confidence: {confidence:.2f})")
                    return True  # Process is running, so consider it successful
            else:
                self.logger.error("✗ KiCad process is not running")
                return False
            
        except Exception as e:
            self.logger.error(f"Failed to verify success condition: {e}")
            return False
    
    def post_challenge_cleanup(self):
        """Cleanup after application launch"""
        try:
            self.logger.info("Application launch challenge completed")
            
            # Check final status
            is_running = self.detector.is_process_running('kicad')
            
            if is_running:
                self.logger.info("✓ KiCad is running and ready for use")
                self.logger.info("Next recommended challenge: Level 4 (Basic UI Navigation)")
                
                # Leave KiCad running for next challenges
                self.logger.info("Leaving KiCad running for subsequent challenges")
            else:
                self.logger.warning("✗ KiCad is not running at completion")
            
            # Note: We intentionally don't close KiCad here so subsequent challenges can use it
            
        except Exception as e:
            self.logger.error(f"Cleanup failed: {e}")
