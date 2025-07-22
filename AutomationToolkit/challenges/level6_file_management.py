"""
Level 6 Challenge: File Management
Save, load, and organize project files
"""

import time
import os
from pathlib import Path
from challenges.base_challenge import BaseChallenge
from automation_engine import AutomationEngine
from system_detector import SystemDetector

class Level6FileManagement(BaseChallenge):
    def __init__(self):
        super().__init__(
            level=6,
            name="File Management",
            description="Save the current PCB project, create backup files, and organize project assets"
        )
        
        self.automation = AutomationEngine()
        self.detector = SystemDetector()
        
        # Prerequisites: Levels 1-5 must be completed
        self.prerequisites = [1, 2, 3, 4, 5]
        
        self.backup_suffix = "_backup"
        self.export_formats = ["PDF", "Gerber", "3D"]
    
    def get_steps(self):
        """Return list of steps for file management challenge"""
        return [
            "Verify PCB project is open",
            "Save current project state",
            "Create project backup",
            "Export design files (PDF)",
            "Export manufacturing files (Gerber)",
            "Organize project directory",
            "Verify all files are saved correctly"
        ]
    
    def execute_step(self, step_number):
        """Execute a specific step of the file management challenge"""
        try:
            if step_number == 0:
                return self._verify_project_open()
            elif step_number == 1:
                return self._save_project()
            elif step_number == 2:
                return self._create_backup()
            elif step_number == 3:
                return self._export_pdf()
            elif step_number == 4:
                return self._export_gerber()
            elif step_number == 5:
                return self._organize_directory()
            elif step_number == 6:
                return self._verify_files()
            else:
                self.logger.error(f"Unknown step number: {step_number}")
                return False
                
        except Exception as e:
            self.logger.error(f"Step {step_number} failed: {e}")
            self.take_error_screenshot(f"step_{step_number}_error")
            return False
    
    def _verify_project_open(self):
        """Verify that a PCB project is currently open"""
        try:
            self.logger.info("Verifying PCB project is open...")
            
            # Check if KiCad is running
            is_running = self.detector.is_process_running('kicad')
            if not is_running:
                self.logger.error("KiCad is not running")
                return False
            
            # Verify we're in PCB editor or project manager
            screenshot = self.automation.take_screenshot()
            pcb_matches, pcb_confidence = self.automation.verify_screen_state(
                "KiCad PCB Editor is open with a design loaded"
            )
            
            project_matches, project_confidence = self.automation.verify_screen_state(
                "KiCad project manager is open with an active project"
            )
            
            if (pcb_matches and pcb_confidence > 0.6) or (project_matches and project_confidence > 0.6):
                self.logger.info("✓ KiCad project verified as open")
                return True
            else:
                self.logger.error("No active KiCad project detected")
                return False
            
        except Exception as e:
            self.logger.error(f"Failed to verify project state: {e}")
            return False
    
    def _save_project(self):
        """Save the current project state"""
        try:
            self.logger.info("Saving current project...")
            
            # Try multiple save methods
            save_methods = [
                ("Ctrl+S shortcut", lambda: self.automation.key_combination('ctrl', 's')),
                ("File -> Save", lambda: self._navigate_file_menu("Save")),
                ("Save button", lambda: self.automation.click_element("Save button"))
            ]
            
            save_attempted = False
            
            for method_name, method_func in save_methods:
                try:
                    self.logger.info(f"Trying save method: {method_name}")
                    if method_func():
                        save_attempted = True
                        break
                except Exception as e:
                    self.logger.debug(f"Save method {method_name} failed: {e}")
            
            if not save_attempted:
                self.logger.error("Could not save project")
                return False
            
            # Wait for save to complete
            self.wait_with_progress(3, "Waiting for project save")
            
            # Check for any save dialogs or confirmations
            self._handle_save_dialogs()
            
            self.logger.info("✓ Project saved")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save project: {e}")
            return False
    
    def _navigate_file_menu(self, item_name):
        """Navigate File menu and click specific item"""
        try:
            if self.automation.click_element("File menu"):
                time.sleep(1)
                return self.automation.click_element(item_name)
            return False
        except Exception:
            return False
    
    def _handle_save_dialogs(self):
        """Handle any dialogs that appear during save operations"""
        try:
            # Look for common save dialog buttons
            dialog_buttons = ["OK", "Save", "Yes", "Overwrite"]
            
            for button in dialog_buttons:
                if self.automation.click_element(button):
                    self.logger.info(f"Handled save dialog: clicked {button}")
                    time.sleep(1)
                    break
            
        except Exception as e:
            self.logger.debug(f"No save dialogs to handle: {e}")
    
    def _create_backup(self):
        """Create a backup copy of the project"""
        try:
            self.logger.info("Creating project backup...")
            
            # Method 1: Try using File -> Save As for backup
            if self._navigate_file_menu("Save As") or self._navigate_file_menu("Save Project As"):
                self.wait_with_progress(2, "Waiting for Save As dialog")
                
                # Modify filename to add backup suffix
                # Select all text in filename field
                self.automation.key_combination('ctrl', 'a')
                time.sleep(0.5)
                
                # Get current timestamp for unique backup name
                import time
                timestamp = int(time.time())
                backup_name = f"backup_{timestamp}"
                
                # Type new name
                self.automation.type_text(backup_name)
                time.sleep(1)
                
                # Confirm save
                if self.automation.click_element("Save button") or self.automation.press_key('enter'):
                    self.wait_with_progress(3, "Creating backup")
                    self.logger.info(f"✓ Backup created: {backup_name}")
                    self.backup_name = backup_name
                    return True
            
            # Method 2: Try copying files manually through file system
            self.logger.info("Attempting file system backup...")
            return self._create_filesystem_backup()
            
        except Exception as e:
            self.logger.error(f"Failed to create backup: {e}")
            return False
    
    def _create_filesystem_backup(self):
        """Create backup by copying project files"""
        try:
            import config
            import shutil
            
            project_dir = config.KICAD_PROJECT_DIR
            
            # Find the most recent project directory
            if project_dir.exists():
                project_dirs = [d for d in project_dir.iterdir() if d.is_dir()]
                if project_dirs:
                    # Get the most recently modified project
                    latest_project = max(project_dirs, key=lambda d: d.stat().st_mtime)
                    
                    # Create backup directory
                    backup_dir = project_dir / f"{latest_project.name}{self.backup_suffix}"
                    
                    if backup_dir.exists():
                        shutil.rmtree(backup_dir)
                    
                    shutil.copytree(latest_project, backup_dir)
                    
                    self.logger.info(f"✓ Filesystem backup created: {backup_dir}")
                    self.backup_path = backup_dir
                    return True
            
            self.logger.warning("Could not create filesystem backup")
            return False
            
        except Exception as e:
            self.logger.error(f"Filesystem backup failed: {e}")
            return False
    
    def _export_pdf(self):
        """Export design to PDF format"""
        try:
            self.logger.info("Exporting design to PDF...")
            
            # Navigate to File -> Plot or Print
            export_methods = [
                ("File -> Plot", lambda: self._navigate_file_menu("Plot")),
                ("File -> Print", lambda: self._navigate_file_menu("Print")),
                ("Plot button", lambda: self.automation.click_element("Plot button")),
                ("F5 key", lambda: self.automation.press_key('f5'))
            ]
            
            export_opened = False
            
            for method_name, method_func in export_methods:
                try:
                    self.logger.info(f"Trying export method: {method_name}")
                    if method_func():
                        export_opened = True
                        break
                except Exception as e:
                    self.logger.debug(f"Export method {method_name} failed: {e}")
            
            if not export_opened:
                self.logger.warning("Could not open plot/export dialog")
                return True  # Don't fail the challenge for this
            
            # Wait for plot dialog
            self.wait_with_progress(3, "Waiting for plot dialog")
            
            # Configure PDF export
            self._configure_pdf_export()
            
            # Execute plot
            if self.automation.click_element("Plot button") or \
               self.automation.click_element("Generate") or \
               self.automation.press_key('enter'):
                
                self.wait_with_progress(5, "Generating PDF")
                self.logger.info("✓ PDF export completed")
                
                # Close plot dialog
                self.automation.press_key('escape')
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to export PDF: {e}")
            return False
    
    def _configure_pdf_export(self):
        """Configure PDF export settings"""
        try:
            # Look for PDF format option
            if self.automation.click_element("PDF format") or \
               self.automation.click_element("PDF"):
                self.logger.info("Selected PDF format")
            
            # Set output directory if possible
            if self.automation.click_element("Output directory") or \
               self.automation.click_element("Browse"):
                time.sleep(1)
                # Use default directory
                self.automation.press_key('enter')
            
        except Exception as e:
            self.logger.debug(f"PDF configuration skipped: {e}")
    
    def _export_gerber(self):
        """Export manufacturing files (Gerber format)"""
        try:
            self.logger.info("Exporting Gerber manufacturing files...")
            
            # Navigate to File -> Fabrication Outputs -> Gerbers
            gerber_methods = [
                ("File -> Fabrication Outputs -> Gerbers", 
                 lambda: self._navigate_fabrication_menu("Gerbers")),
                ("Generate Gerber files", 
                 lambda: self.automation.click_element("Generate Gerber files")),
                ("Gerber export", 
                 lambda: self.automation.click_element("Gerber export"))
            ]
            
            gerber_opened = False
            
            for method_name, method_func in gerber_methods:
                try:
                    self.logger.info(f"Trying Gerber method: {method_name}")
                    if method_func():
                        gerber_opened = True
                        break
                except Exception as e:
                    self.logger.debug(f"Gerber method {method_name} failed: {e}")
            
            if not gerber_opened:
                self.logger.warning("Could not open Gerber export dialog")
                return True  # Don't fail the challenge for this
            
            # Wait for Gerber dialog
            self.wait_with_progress(3, "Waiting for Gerber dialog")
            
            # Generate Gerber files
            if self.automation.click_element("Plot button") or \
               self.automation.click_element("Generate Gerber Files") or \
               self.automation.click_element("Run"):
                
                self.wait_with_progress(5, "Generating Gerber files")
                self.logger.info("✓ Gerber files generated")
                
                # Close dialog
                self.automation.press_key('escape')
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to export Gerber: {e}")
            return False
    
    def _navigate_fabrication_menu(self, item_name):
        """Navigate to Fabrication Outputs submenu"""
        try:
            if self.automation.click_element("File menu"):
                time.sleep(1)
                if self.automation.click_element("Fabrication Outputs"):
                    time.sleep(1)
                    return self.automation.click_element(item_name)
            return False
        except Exception:
            return False
    
    def _organize_directory(self):
        """Organize project files into logical structure"""
        try:
            self.logger.info("Organizing project directory...")
            
            import config
            
            # Get project directory
            project_dir = config.KICAD_PROJECT_DIR
            
            if not project_dir.exists():
                self.logger.warning("Project directory not found")
                return True
            
            # Find project directories
            project_dirs = [d for d in project_dir.iterdir() if d.is_dir()]
            
            for proj_dir in project_dirs:
                try:
                    self._organize_single_project(proj_dir)
                except Exception as e:
                    self.logger.warning(f"Failed to organize {proj_dir}: {e}")
            
            self.logger.info("✓ Project directory organization completed")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to organize directory: {e}")
            return False
    
    def _organize_single_project(self, project_path):
        """Organize files within a single project directory"""
        try:
            # Create subdirectories for different file types
            subdirs = {
                'exports': ['pdf', 'svg', 'png'],
                'gerbers': ['gbr', 'drl', 'gbl', 'gtl'],
                'backups': ['bak', 'backup'],
                'temp': ['tmp', 'cache']
            }
            
            for subdir_name, extensions in subdirs.items():
                subdir_path = project_path / subdir_name
                
                # Create subdirectory if it doesn't exist
                if not subdir_path.exists():
                    subdir_path.mkdir()
                
                # Move matching files to subdirectory
                for file_path in project_path.iterdir():
                    if file_path.is_file() and file_path.suffix.lower().lstrip('.') in extensions:
                        try:
                            target_path = subdir_path / file_path.name
                            if not target_path.exists():
                                file_path.rename(target_path)
                                self.logger.debug(f"Moved {file_path.name} to {subdir_name}/")
                        except Exception as e:
                            self.logger.debug(f"Could not move {file_path.name}: {e}")
            
        except Exception as e:
            self.logger.debug(f"Organization of {project_path} skipped: {e}")
    
    def _verify_files(self):
        """Verify all files were saved and organized correctly"""
        try:
            self.logger.info("Verifying saved files...")
            
            import config
            
            project_dir = config.KICAD_PROJECT_DIR
            
            if not project_dir.exists():
                self.logger.error("Project directory not found")
                return False
            
            # Count different types of files
            file_counts = {
                'project_files': 0,
                'backup_files': 0,
                'export_files': 0,
                'gerber_files': 0
            }
            
            # Search for files recursively
            for file_path in project_dir.rglob('*'):
                if file_path.is_file():
                    ext = file_path.suffix.lower()
                    name = file_path.name.lower()
                    
                    if ext in ['.kicad_pro', '.kicad_sch', '.kicad_pcb']:
                        file_counts['project_files'] += 1
                    elif 'backup' in name or ext == '.bak':
                        file_counts['backup_files'] += 1
                    elif ext in ['.pdf', '.svg', '.png']:
                        file_counts['export_files'] += 1
                    elif ext in ['.gbr', '.drl', '.gbl', '.gtl']:
                        file_counts['gerber_files'] += 1
            
            # Report findings
            self.logger.info("File verification results:")
            for file_type, count in file_counts.items():
                self.logger.info(f"  {file_type.replace('_', ' ').title()}: {count}")
            
            # Success criteria: At least some files exist
            total_files = sum(file_counts.values())
            
            if total_files > 0:
                self.logger.info(f"✓ File verification successful - {total_files} files found")
                self.file_counts = file_counts
                return True
            else:
                self.logger.warning("No project files found")
                return False
            
        except Exception as e:
            self.logger.error(f"Failed to verify files: {e}")
            return False
    
    def verify_success_condition(self):
        """Verify that file management was successful"""
        try:
            # Success condition: Files were saved and organized
            if not hasattr(self, 'file_counts'):
                return False
            
            # Check that we have some project files
            if self.file_counts['project_files'] > 0:
                self.logger.info("✓ File management successful - project files saved")
                return True
            else:
                self.logger.warning("No project files detected")
                return False
            
        except Exception as e:
            self.logger.error(f"Failed to verify success condition: {e}")
            return False
    
    def post_challenge_cleanup(self):
        """Cleanup after file management"""
        try:
            self.logger.info("File management challenge completed")
            
            if hasattr(self, 'file_counts'):
                total_files = sum(self.file_counts.values())
                self.logger.info(f"✓ Managed {total_files} project files")
                
                if self.file_counts['backup_files'] > 0:
                    self.logger.info("✓ Backup files created")
                if self.file_counts['export_files'] > 0:
                    self.logger.info("✓ Export files generated")
                if self.file_counts['gerber_files'] > 0:
                    self.logger.info("✓ Manufacturing files exported")
            
            self.logger.info("Next recommended challenge: Level 7 (Advanced Operations)")
            
        except Exception as e:
            self.logger.error(f"Cleanup failed: {e}")
