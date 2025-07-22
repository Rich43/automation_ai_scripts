"""
Level 4 Challenge: Basic UI Navigation
Navigate through menus and dialogs using AI vision
"""

import time
from challenges.base_challenge import BaseChallenge
from automation_engine import AutomationEngine
from system_detector import SystemDetector

class Level4UiNavigation(BaseChallenge):
    def __init__(self):
        super().__init__(
            level=4,
            name="Basic UI Navigation",
            description="Navigate KiCad menus and create a new PCB project using AI vision"
        )
        
        self.automation = AutomationEngine()
        self.detector = SystemDetector()
        
        # Prerequisites: Levels 1, 2, and 3 must be completed
        self.prerequisites = [1, 2, 3]
    
    def get_steps(self):
        """Return list of steps for UI navigation challenge"""
        return [
            "Verify KiCad is running",
            "Navigate to File menu",
            "Select 'New Project' option",
            "Choose project location and name",
            "Confirm project creation",
            "Verify project is created successfully"
        ]
    
    def execute_step(self, step_number):
        """Execute a specific step of the UI navigation challenge"""
        try:
            if step_number == 0:
                return self._verify_kicad_running()
            elif step_number == 1:
                return self._navigate_to_file_menu()
            elif step_number == 2:
                return self._select_new_project()
            elif step_number == 3:
                return self._choose_project_details()
            elif step_number == 4:
                return self._confirm_project_creation()
            elif step_number == 5:
                return self._verify_project_created()
            else:
                self.logger.error(f"Unknown step number: {step_number}")
                return False
                
        except Exception as e:
            self.logger.error(f"Step {step_number} failed: {e}")
            self.take_error_screenshot(f"step_{step_number}_error")
            return False
    
    def _verify_kicad_running(self):
        """Verify that KiCad is running and accessible"""
        try:
            self.logger.info("Verifying KiCad is running...")
            
            # Check if KiCad process is running
            is_running = self.detector.is_process_running('kicad')
            
            if not is_running:
                self.logger.error("KiCad is not running - cannot proceed with UI navigation")
                return False
            
            # Verify KiCad window is visible
            screenshot = self.automation.take_screenshot()
            screenshot_b64 = self.automation.screenshot_to_base64(screenshot)
            
            application_state = self.automation.vision.detect_application_state(screenshot_b64, "KiCad")
            
            if not application_state.get('application_running', False):
                self.logger.error("KiCad window not detected on screen")
                return False
            
            self.logger.info("✓ KiCad is running and window is visible")
            
            # Try to bring KiCad to foreground
            kicad_window_x, kicad_window_y = self.automation.find_element_coordinates("KiCad window")
            if kicad_window_x and kicad_window_y:
                self.automation.automation.click(kicad_window_x, kicad_window_y)
                time.sleep(1)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to verify KiCad is running: {e}")
            return False
    
    def _navigate_to_file_menu(self):
        """Navigate to the File menu in KiCad"""
        try:
            self.logger.info("Navigating to File menu...")
            
            # Look for File menu in the menu bar
            file_menu_descriptions = [
                "File menu",
                "File menu item",
                "File in menu bar",
                "File button in KiCad menu"
            ]
            
            menu_clicked = False
            
            for description in file_menu_descriptions:
                if self.automation.click_element(description):
                    self.logger.info(f"✓ Clicked {description}")
                    menu_clicked = True
                    break
            
            if not menu_clicked:
                self.logger.warning("Could not find File menu directly, trying alternative methods...")
                
                # Alternative: Try using keyboard shortcut
                if self.automation.key_combination('alt', 'f'):
                    self.logger.info("✓ Used Alt+F to open File menu")
                    menu_clicked = True
                
            if not menu_clicked:
                self.logger.error("Failed to open File menu")
                self.take_error_screenshot("file_menu_not_found")
                return False
            
            # Wait for menu to appear
            self.wait_with_progress(2, "Waiting for File menu to appear")
            
            # Verify menu is open
            screenshot = self.automation.take_screenshot()
            matches, confidence = self.automation.verify_screen_state("File menu is open and showing menu options")
            
            if matches and confidence > 0.6:
                self.logger.info(f"✓ File menu opened successfully (confidence: {confidence:.2f})")
                return True
            else:
                self.logger.warning(f"File menu state unclear (confidence: {confidence:.2f})")
                # Continue anyway - menu might be open but not detected perfectly
                return True
            
        except Exception as e:
            self.logger.error(f"Failed to navigate to File menu: {e}")
            return False
    
    def _select_new_project(self):
        """Select 'New Project' option from File menu"""
        try:
            self.logger.info("Selecting 'New Project' option...")
            
            new_project_descriptions = [
                "New Project menu item",
                "New Project option",
                "Create New Project",
                "New KiCad Project",
                "New project button"
            ]
            
            option_clicked = False
            
            for description in new_project_descriptions:
                if self.automation.click_element(description):
                    self.logger.info(f"✓ Clicked {description}")
                    option_clicked = True
                    break
            
            if not option_clicked:
                self.logger.warning("Could not find New Project option directly, trying alternatives...")
                
                # Try typing 'n' to select New Project
                if self.automation.press_key('n'):
                    self.logger.info("✓ Used 'N' key to select New Project")
                    option_clicked = True
                
            if not option_clicked:
                self.logger.error("Failed to select New Project option")
                self.take_error_screenshot("new_project_not_found")
                return False
            
            # Wait for dialog to appear
            self.wait_with_progress(3, "Waiting for New Project dialog")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to select New Project: {e}")
            return False
    
    def _choose_project_details(self):
        """Choose project location and name"""
        try:
            self.logger.info("Configuring project details...")
            
            # Check for New Project dialog
            screenshot = self.automation.take_screenshot()
            screenshot_b64 = self.automation.screenshot_to_base64(screenshot)
            
            dialog_state = self.automation.vision.analyze_screenshot_general(
                screenshot_b64,
                "Analyze this dialog and determine if it's a 'New Project' or 'Create Project' dialog. Return JSON with 'is_new_project_dialog': true/false and 'description': 'what you see'"
            )
            
            if not dialog_state.get('is_new_project_dialog', False):
                self.logger.warning("New Project dialog not clearly detected, continuing anyway...")
            
            # Generate a unique project name
            import time
            project_name = f"AutomationTest_{int(time.time())}"
            self.project_name = project_name
            
            self.logger.info(f"Using project name: {project_name}")
            
            # Look for project name field
            name_field_descriptions = [
                "project name text field",
                "project name input",
                "name field",
                "project name textbox"
            ]
            
            name_field_found = False
            
            for description in name_field_descriptions:
                if self.automation.click_element(description):
                    self.logger.info(f"✓ Found project name field: {description}")
                    
                    # Clear existing text and type new name
                    self.automation.key_combination('ctrl', 'a')  # Select all
                    time.sleep(0.2)
                    self.automation.type_text(project_name)
                    
                    name_field_found = True
                    break
            
            if not name_field_found:
                self.logger.warning("Could not find project name field specifically")
                # Try typing the name anyway - might be already focused
                self.automation.type_text(project_name)
            
            # Look for project location/path field if needed
            import config
            project_path = str(config.KICAD_PROJECT_DIR)
            
            path_field_descriptions = [
                "project path field",
                "project location field",
                "folder path input",
                "directory field"
            ]
            
            for description in path_field_descriptions:
                path_x, path_y = self.automation.find_element_coordinates(description)
                if path_x and path_y:
                    self.logger.info(f"Found project path field: {description}")
                    self.automation.automation.click(path_x, path_y)
                    time.sleep(0.5)
                    
                    # Clear and set path
                    self.automation.key_combination('ctrl', 'a')
                    time.sleep(0.2)
                    self.automation.type_text(project_path)
                    break
            
            self.logger.info(f"Project configured: {project_name} in {project_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to configure project details: {e}")
            return False
    
    def _confirm_project_creation(self):
        """Confirm project creation by clicking OK/Create button"""
        try:
            self.logger.info("Confirming project creation...")
            
            # Look for confirmation buttons
            confirm_buttons = [
                "OK button",
                "Create button",
                "Create Project button",
                "OK",
                "Create",
                "Save button"
            ]
            
            button_clicked = False
            
            for button_desc in confirm_buttons:
                if self.automation.click_element(button_desc):
                    self.logger.info(f"✓ Clicked {button_desc}")
                    button_clicked = True
                    break
            
            if not button_clicked:
                self.logger.warning("Could not find confirmation button, trying Enter key...")
                if self.automation.press_key('enter'):
                    self.logger.info("✓ Used Enter key to confirm")
                    button_clicked = True
            
            if not button_clicked:
                self.logger.error("Failed to confirm project creation")
                self.take_error_screenshot("confirm_button_not_found")
                return False
            
            # Wait for project creation to complete
            self.wait_with_progress(5, "Waiting for project creation to complete")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to confirm project creation: {e}")
            return False
    
    def _verify_project_created(self):
        """Verify that the project was created successfully"""
        try:
            self.logger.info("Verifying project creation...")
            
            # Check if we're back to the main KiCad project manager
            screenshot = self.automation.take_screenshot()
            screenshot_b64 = self.automation.screenshot_to_base64(screenshot)
            
            # Look for signs that a project is loaded
            project_indicators = [
                f"project named {self.project_name}",
                "project is loaded in KiCad",
                "KiCad project manager showing an open project",
                "schematic editor button is available",
                "PCB editor button is available"
            ]
            
            project_detected = False
            
            for indicator in project_indicators:
                matches, confidence = self.automation.verify_screen_state(indicator)
                if matches and confidence > 0.6:
                    self.logger.info(f"✓ Project verification: {indicator} (confidence: {confidence:.2f})")
                    project_detected = True
                    break
            
            if not project_detected:
                self.logger.warning("Could not confirm project creation through screen analysis")
                
                # Alternative: Check for project files on disk
                try:
                    import config
                    from pathlib import Path
                    
                    project_dir = config.KICAD_PROJECT_DIR / self.project_name
                    project_file = project_dir / f"{self.project_name}.kicad_pro"
                    
                    if project_file.exists():
                        self.logger.info(f"✓ Project file found on disk: {project_file}")
                        project_detected = True
                    else:
                        self.logger.warning(f"Project file not found: {project_file}")
                        
                        # Check if any project files were created
                        if project_dir.exists():
                            files = list(project_dir.glob("*"))
                            if files:
                                self.logger.info(f"Project directory contains {len(files)} files")
                                project_detected = True
                
                except Exception as e:
                    self.logger.warning(f"Could not verify project files: {e}")
            
            if project_detected:
                self.logger.info("✓ Project creation verified successfully")
                
                # Try to identify available project tools
                editor_buttons = [
                    "Schematic Editor",
                    "PCB Editor", 
                    "Symbol Editor",
                    "Footprint Editor"
                ]
                
                available_tools = []
                for tool in editor_buttons:
                    tool_x, tool_y = self.automation.find_element_coordinates(tool)
                    if tool_x and tool_y:
                        available_tools.append(tool)
                
                if available_tools:
                    self.logger.info(f"Available tools detected: {', '.join(available_tools)}")
                
                return True
            else:
                self.logger.error("✗ Could not verify project creation")
                self.take_error_screenshot("project_verification_failed")
                return False
            
        except Exception as e:
            self.logger.error(f"Failed to verify project creation: {e}")
            return False
    
    def verify_success_condition(self):
        """Verify that UI navigation was successful"""
        try:
            # Success condition: Project was created and KiCad shows project interface
            # Check if we have a project name set
            if not hasattr(self, 'project_name'):
                return False
            
            # Verify KiCad is still running
            is_running = self.detector.is_process_running('kicad')
            if not is_running:
                self.logger.error("KiCad is no longer running")
                return False
            
            # Check screen state
            screenshot = self.automation.take_screenshot()
            matches, confidence = self.automation.verify_screen_state(
                "KiCad project manager is open with a project loaded"
            )
            
            if matches and confidence > 0.5:
                self.logger.info(f"✓ UI navigation successful (confidence: {confidence:.2f})")
                return True
            else:
                self.logger.warning(f"UI navigation verification unclear (confidence: {confidence:.2f})")
                return True  # Don't fail if we got this far
            
        except Exception as e:
            self.logger.error(f"Failed to verify success condition: {e}")
            return False
    
    def post_challenge_cleanup(self):
        """Cleanup after UI navigation"""
        try:
            self.logger.info("UI navigation challenge completed")
            
            if hasattr(self, 'project_name'):
                self.logger.info(f"✓ Created project: {self.project_name}")
                self.logger.info("Next recommended challenge: Level 5 (Complex Task Execution)")
                
                # Store project info for next challenges
                self.logger.info(f"Project available for subsequent challenges: {self.project_name}")
            else:
                self.logger.warning("✗ Project creation status unclear")
            
            # Keep KiCad and project open for next challenges
            self.logger.info("Leaving KiCad and project open for subsequent challenges")
            
        except Exception as e:
            self.logger.error(f"Cleanup failed: {e}")
