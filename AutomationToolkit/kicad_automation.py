"""
Specialized KiCad automation functions
Provides high-level KiCad-specific automation capabilities
"""

import time
import os
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path

from automation_engine import AutomationEngine
from ai_vision import AIVision
from logger_config import setup_logger

class KiCadComponent:
    """Represents a KiCad component/symbol"""
    def __init__(self, reference: str, component_type: str, value: str = "", footprint: str = ""):
        self.reference = reference
        self.component_type = component_type
        self.value = value
        self.footprint = footprint
        self.position = None  # (x, y) coordinates
        self.rotation = 0
        
    def __str__(self):
        return f"{self.reference} ({self.component_type}): {self.value}"

class KiCadProject:
    """Represents a KiCad project"""
    def __init__(self, name: str, path: Path):
        self.name = name
        self.path = path
        self.components = []
        self.nets = []
        self.created = False
        
    def add_component(self, component: KiCadComponent):
        self.components.append(component)

class KiCadAutomation:
    """
    High-level KiCad automation system
    Provides specialized functions for KiCad PCB design workflows
    """
    
    def __init__(self):
        self.logger = setup_logger(__name__)
        self.automation = AutomationEngine()
        self.ai_vision = AIVision()
        
        # KiCad state tracking
        self.current_project = None
        self.kicad_running = False
        self.current_editor = None  # 'schematic', 'pcb', 'symbol', 'footprint'
        
        # Common KiCad UI elements
        self.ui_elements = {
            'file_menu': 'File menu',
            'tools_menu': 'Tools menu',
            'view_menu': 'View menu',
            'schematic_editor_btn': 'Schematic Editor button',
            'pcb_editor_btn': 'PCB Editor button',
            'symbol_editor_btn': 'Symbol Editor button',
            'footprint_editor_btn': 'Footprint Editor button',
            'add_symbol_btn': 'Add Symbol button',
            'add_wire_btn': 'Add Wire button',
            'run_erc_btn': 'Electrical Rules Check button',
            'run_drc_btn': 'Design Rules Check button',
            'plot_btn': 'Plot button',
            'gerber_btn': 'Generate Gerber files button'
        }
        
        self.logger.info("KiCad automation system initialized")
    
    def detect_kicad_state(self) -> Dict[str, Any]:
        """
        Detect current KiCad application state
        """
        try:
            screenshot = self.automation.take_screenshot()
            screenshot_b64 = self.automation.screenshot_to_base64(screenshot)
            
            # Use AI vision to detect KiCad state
            ui_state = self.ai_vision.analyze_desktop_state(screenshot_b64)
            
            # Determine if KiCad is running and which editor is active
            kicad_detected = False
            current_editor = None
            
            if 'kicad' in ui_state.application_name.lower():
                kicad_detected = True
                
                # Determine active editor based on window title and UI elements
                title_lower = ui_state.window_title.lower()
                if 'schematic' in title_lower:
                    current_editor = 'schematic'
                elif 'pcb' in title_lower or 'board' in title_lower:
                    current_editor = 'pcb'
                elif 'symbol' in title_lower:
                    current_editor = 'symbol'
                elif 'footprint' in title_lower:
                    current_editor = 'footprint'
                else:
                    current_editor = 'project_manager'
            
            self.kicad_running = kicad_detected
            self.current_editor = current_editor
            
            return {
                'kicad_running': kicad_detected,
                'current_editor': current_editor,
                'window_title': ui_state.window_title,
                'elements_detected': len(ui_state.elements),
                'dialog_present': ui_state.dialog_present,
                'error_present': ui_state.error_present,
                'confidence': ui_state.confidence
            }
            
        except Exception as e:
            self.logger.error(f"Failed to detect KiCad state: {e}")
            return {'kicad_running': False, 'current_editor': None}
    
    def create_new_project(self, project_name: str, project_path: Path) -> bool:
        """
        Create a new KiCad project
        """
        try:
            self.logger.info(f"Creating new KiCad project: {project_name}")
            
            # Ensure KiCad is running
            if not self.kicad_running:
                self.logger.error("KiCad is not running")
                return False
            
            # Navigate to File -> New Project
            if not self.automation.click_element(self.ui_elements['file_menu']):
                self.logger.error("Could not open File menu")
                return False
            
            time.sleep(1)
            
            if not self.automation.click_element("New Project"):
                self.logger.error("Could not find New Project option")
                return False
            
            time.sleep(2)
            
            # Handle New Project dialog
            success = self._handle_new_project_dialog(project_name, project_path)
            
            if success:
                self.current_project = KiCadProject(project_name, project_path)
                self.current_project.created = True
                self.logger.info(f"Project {project_name} created successfully")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to create project: {e}")
            return False
    
    def _handle_new_project_dialog(self, project_name: str, project_path: Path) -> bool:
        """Handle the New Project dialog"""
        try:
            # Take screenshot to analyze dialog
            screenshot = self.automation.take_screenshot()
            screenshot_b64 = self.automation.screenshot_to_base64(screenshot)
            
            # Use AI to identify form fields
            form_analysis = self.ai_vision.analyze_form_fields(screenshot_b64)
            
            # Find and fill project name field
            name_field = None
            path_field = None
            
            for field in form_analysis.get('form_fields', []):
                if 'name' in field.get('label', '').lower():
                    name_field = field
                elif 'path' in field.get('label', '').lower() or 'location' in field.get('label', '').lower():
                    path_field = field
            
            # Fill project name
            if name_field:
                self.automation.automation.click(name_field['x'], name_field['y'])
                time.sleep(0.5)
                self.automation.key_combination('ctrl', 'a')
                self.automation.type_text(project_name)
            else:
                # Fallback: just type the name
                self.automation.type_text(project_name)
            
            # Fill project path if field found
            if path_field:
                self.automation.automation.click(path_field['x'], path_field['y'])
                time.sleep(0.5)
                self.automation.key_combination('ctrl', 'a')
                self.automation.type_text(str(project_path))
            
            # Click OK/Create button
            if self.automation.click_element("OK") or \
               self.automation.click_element("Create") or \
               self.automation.press_key('enter'):
                time.sleep(3)
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to handle new project dialog: {e}")
            return False
    
    def open_schematic_editor(self) -> bool:
        """
        Open the schematic editor
        """
        try:
            self.logger.info("Opening schematic editor")
            
            if self.current_editor == 'schematic':
                self.logger.info("Schematic editor already open")
                return True
            
            # Click schematic editor button
            if self.automation.click_element(self.ui_elements['schematic_editor_btn']):
                time.sleep(3)
                
                # Verify schematic editor opened
                state = self.detect_kicad_state()
                if state.get('current_editor') == 'schematic':
                    self.current_editor = 'schematic'
                    return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to open schematic editor: {e}")
            return False
    
    def add_component_to_schematic(self, component: KiCadComponent, position: Tuple[int, int] = None) -> bool:
        """
        Add a component to the schematic
        """
        try:
            self.logger.info(f"Adding component {component.reference} to schematic")
            
            if self.current_editor != 'schematic':
                if not self.open_schematic_editor():
                    return False
            
            # Click Add Symbol button or use shortcut
            if not (self.automation.click_element(self.ui_elements['add_symbol_btn']) or 
                   self.automation.press_key('a')):
                self.logger.error("Could not activate Add Symbol tool")
                return False
            
            time.sleep(1)
            
            # Search for component
            search_terms = [component.component_type, component.value]
            for term in search_terms:
                if term:
                    self.automation.type_text(term)
                    time.sleep(1)
                    
                    # Check if component found
                    screenshot = self.automation.take_screenshot()
                    screenshot_b64 = self.automation.screenshot_to_base64(screenshot)
                    
                    # Use AI to check if search results are visible
                    ui_state = self.ai_vision.analyze_desktop_state(screenshot_b64)
                    
                    # Look for selectable components
                    found_component = False
                    for element in ui_state.elements:
                        if element.clickable and component.component_type.lower() in element.description.lower():
                            self.automation.automation.click(element.x, element.y)
                            found_component = True
                            break
                    
                    if found_component or self.automation.press_key('enter'):
                        break
                    
                    # Clear search and try next term
                    self.automation.key_combination('ctrl', 'a')
            
            time.sleep(1)
            
            # Place component on schematic
            if position:
                x, y = position
            else:
                # Default position or find empty area
                x, y = self._find_empty_schematic_area()
            
            self.automation.automation.click(x, y)
            time.sleep(0.5)
            
            # Confirm placement
            self.automation.press_key('escape')
            
            # Update component position
            component.position = (x, y)
            
            # Add to project if we have one
            if self.current_project:
                self.current_project.add_component(component)
            
            self.logger.info(f"Component {component.reference} added successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to add component: {e}")
            return False
    
    def _find_empty_schematic_area(self) -> Tuple[int, int]:
        """Find an empty area on the schematic canvas"""
        try:
            screenshot = self.automation.take_screenshot()
            width, height = screenshot.size
            
            # Start from center and look for empty space
            base_x = width // 2
            base_y = height // 2
            
            # Simple grid-based placement
            grid_size = 100
            for i in range(10):  # Try up to 10 positions
                x = base_x + (i % 3) * grid_size
                y = base_y + (i // 3) * grid_size
                
                # Make sure coordinates are within bounds
                if x < width - 50 and y < height - 50:
                    return x, y
            
            # Fallback to center
            return base_x, base_y
            
        except Exception:
            # Ultimate fallback
            return 400, 300
    
    def add_wire_connection(self, start_component: str, end_component: str) -> bool:
        """
        Add a wire connection between two components
        """
        try:
            self.logger.info(f"Adding wire from {start_component} to {end_component}")
            
            if self.current_editor != 'schematic':
                if not self.open_schematic_editor():
                    return False
            
            # Activate wire tool
            if not (self.automation.click_element(self.ui_elements['add_wire_btn']) or 
                   self.automation.press_key('w')):
                self.logger.error("Could not activate wire tool")
                return False
            
            time.sleep(1)
            
            # Find components on schematic using AI vision
            screenshot = self.automation.take_screenshot()
            screenshot_b64 = self.automation.screenshot_to_base64(screenshot)
            
            start_pos = self._find_component_pin(screenshot_b64, start_component)
            end_pos = self._find_component_pin(screenshot_b64, end_component)
            
            if not start_pos or not end_pos:
                self.logger.error("Could not locate component pins for wiring")
                return False
            
            # Draw wire
            self.automation.automation.click(start_pos[0], start_pos[1])
            time.sleep(0.5)
            self.automation.automation.click(end_pos[0], end_pos[1])
            time.sleep(0.5)
            
            # Finish wiring
            self.automation.press_key('escape')
            
            self.logger.info(f"Wire connection added from {start_component} to {end_component}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to add wire connection: {e}")
            return False
    
    def _find_component_pin(self, screenshot_b64: str, component_ref: str) -> Optional[Tuple[int, int]]:
        """Find a component pin for wiring"""
        try:
            element = self.ai_vision.find_element_smart(
                screenshot_b64,
                f"pin or connection point of component {component_ref}",
                "pin"
            )
            
            if element and element.confidence > 0.5:
                return (element.x, element.y)
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to find component pin: {e}")
            return None
    
    def run_electrical_rules_check(self) -> Dict[str, Any]:
        """
        Run Electrical Rules Check (ERC) on the schematic
        """
        try:
            self.logger.info("Running Electrical Rules Check")
            
            if self.current_editor != 'schematic':
                if not self.open_schematic_editor():
                    return {'success': False, 'error': 'Could not open schematic editor'}
            
            # Run ERC
            if not (self.automation.click_element(self.ui_elements['run_erc_btn']) or 
                   self.automation.press_key('f8')):
                # Try via Tools menu
                if self.automation.click_element(self.ui_elements['tools_menu']):
                    time.sleep(1)
                    if not self.automation.click_element("Electrical Rules Checker"):
                        return {'success': False, 'error': 'Could not run ERC'}
                else:
                    return {'success': False, 'error': 'Could not access ERC'}
            
            time.sleep(3)
            
            # Analyze ERC results
            screenshot = self.automation.take_screenshot()
            screenshot_b64 = self.automation.screenshot_to_base64(screenshot)
            
            # Extract ERC results using AI vision
            erc_results = self._analyze_erc_results(screenshot_b64)
            
            # Close ERC dialog
            self.automation.press_key('escape')
            
            return erc_results
            
        except Exception as e:
            self.logger.error(f"Failed to run ERC: {e}")
            return {'success': False, 'error': str(e)}
    
    def _analyze_erc_results(self, screenshot_b64: str) -> Dict[str, Any]:
        """Analyze ERC results from screenshot"""
        try:
            text_content = self.ai_vision.extract_text_content(screenshot_b64)
            
            errors = []
            warnings = []
            
            for text_elem in text_content.get('text_elements', []):
                text = text_elem.get('text', '').lower()
                if 'error' in text:
                    errors.append(text_elem.get('text', ''))
                elif 'warning' in text:
                    warnings.append(text_elem.get('text', ''))
            
            return {
                'success': True,
                'errors': errors,
                'warnings': warnings,
                'error_count': len(errors),
                'warning_count': len(warnings),
                'passed': len(errors) == 0
            }
            
        except Exception as e:
            self.logger.error(f"Failed to analyze ERC results: {e}")
            return {'success': False, 'error': str(e)}
    
    def open_pcb_editor(self) -> bool:
        """
        Open the PCB editor
        """
        try:
            self.logger.info("Opening PCB editor")
            
            if self.current_editor == 'pcb':
                self.logger.info("PCB editor already open")
                return True
            
            # Update PCB from schematic first if we're in schematic editor
            if self.current_editor == 'schematic':
                if not self._update_pcb_from_schematic():
                    self.logger.warning("Could not update PCB from schematic")
            
            # Click PCB editor button
            if self.automation.click_element(self.ui_elements['pcb_editor_btn']):
                time.sleep(3)
                
                # Verify PCB editor opened
                state = self.detect_kicad_state()
                if state.get('current_editor') == 'pcb':
                    self.current_editor = 'pcb'
                    return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to open PCB editor: {e}")
            return False
    
    def _update_pcb_from_schematic(self) -> bool:
        """Update PCB from schematic"""
        try:
            # Try Tools -> Update PCB from Schematic
            if self.automation.click_element(self.ui_elements['tools_menu']):
                time.sleep(1)
                if self.automation.click_element("Update PCB from Schematic"):
                    time.sleep(2)
                    
                    # Handle update dialog
                    if self.automation.click_element("Update PCB") or \
                       self.automation.press_key('enter'):
                        time.sleep(2)
                        return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to update PCB: {e}")
            return False
    
    def auto_place_components(self) -> bool:
        """
        Automatically place components on PCB
        """
        try:
            self.logger.info("Auto-placing components on PCB")
            
            if self.current_editor != 'pcb':
                if not self.open_pcb_editor():
                    return False
            
            # Try auto-placement
            if self.automation.click_element(self.ui_elements['tools_menu']):
                time.sleep(1)
                if self.automation.click_element("Auto Place Footprints") or \
                   self.automation.click_element("Arrange Footprints"):
                    time.sleep(3)
                    return True
            
            # Manual arrangement fallback
            self.logger.info("Auto-placement not available, components may need manual positioning")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to auto-place components: {e}")
            return False
    
    def auto_route_traces(self) -> bool:
        """
        Automatically route traces on PCB
        """
        try:
            self.logger.info("Auto-routing PCB traces")
            
            if self.current_editor != 'pcb':
                if not self.open_pcb_editor():
                    return False
            
            # Try auto-routing
            routing_options = [
                "Auto Route",
                "Route -> Auto Route All",
                "Tools -> Auto Route"
            ]
            
            for option in routing_options:
                if "Route" in option:
                    if self.automation.click_element("Route"):
                        time.sleep(1)
                        if self.automation.click_element("Auto Route All"):
                            time.sleep(5)  # Auto-routing takes time
                            return True
                elif "Tools" in option:
                    if self.automation.click_element(self.ui_elements['tools_menu']):
                        time.sleep(1)
                        if self.automation.click_element("Auto Route"):
                            time.sleep(5)
                            return True
                else:
                    if self.automation.click_element(option):
                        time.sleep(5)
                        return True
            
            self.logger.warning("Auto-routing not available or failed")
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to auto-route traces: {e}")
            return False
    
    def export_gerber_files(self, output_dir: Path) -> bool:
        """
        Export Gerber manufacturing files
        """
        try:
            self.logger.info(f"Exporting Gerber files to {output_dir}")
            
            if self.current_editor != 'pcb':
                if not self.open_pcb_editor():
                    return False
            
            # Navigate to File -> Fabrication Outputs -> Gerbers
            if not self.automation.click_element(self.ui_elements['file_menu']):
                return False
            
            time.sleep(1)
            
            if not self.automation.click_element("Fabrication Outputs"):
                return False
            
            time.sleep(1)
            
            if not self.automation.click_element("Gerbers"):
                return False
            
            time.sleep(2)
            
            # Set output directory if dialog allows
            if str(output_dir) != ".":
                # Try to set output directory
                if self.automation.click_element("Output directory"):
                    time.sleep(1)
                    self.automation.key_combination('ctrl', 'a')
                    self.automation.type_text(str(output_dir))
            
            # Generate Gerber files
            if self.automation.click_element("Plot") or \
               self.automation.click_element("Generate Gerber Files"):
                time.sleep(3)
                
                # Close dialog
                self.automation.press_key('escape')
                
                self.logger.info("Gerber files exported successfully")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to export Gerber files: {e}")
            return False
    
    def save_project(self) -> bool:
        """
        Save the current KiCad project
        """
        try:
            self.logger.info("Saving KiCad project")
            
            # Use Ctrl+S shortcut
            if self.automation.key_combination('ctrl', 's'):
                time.sleep(2)
                
                # Handle any save dialogs
                if self.automation.click_element("Save") or \
                   self.automation.press_key('enter'):
                    time.sleep(1)
                
                self.logger.info("Project saved successfully")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to save project: {e}")
            return False
    
    def get_project_status(self) -> Dict[str, Any]:
        """
        Get current project status and statistics
        """
        try:
            status = {
                'project_name': self.current_project.name if self.current_project else None,
                'project_path': str(self.current_project.path) if self.current_project else None,
                'component_count': len(self.current_project.components) if self.current_project else 0,
                'kicad_running': self.kicad_running,
                'current_editor': self.current_editor,
                'project_created': self.current_project.created if self.current_project else False
            }
            
            if self.current_project:
                status['components'] = [str(comp) for comp in self.current_project.components]
            
            return status
            
        except Exception as e:
            self.logger.error(f"Failed to get project status: {e}")
            return {'error': str(e)}

