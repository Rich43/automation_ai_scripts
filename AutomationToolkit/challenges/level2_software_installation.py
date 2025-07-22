"""
Level 2 Challenge: Software Installation  
Automatically download and install applications when not found
"""

import time
from challenges.base_challenge import BaseChallenge
from system_detector import SystemDetector
from software_installer import SoftwareInstaller

class Level2SoftwareInstallation(BaseChallenge):
    def __init__(self):
        super().__init__(
            level=2,
            name="Software Installation",
            description="Automatically install KiCad if it's not already present on the system"
        )
        
        self.detector = SystemDetector()
        self.installer = SoftwareInstaller()
        
        # Prerequisites: Level 1 must be completed
        self.prerequisites = [1]
    
    def get_steps(self):
        """Return list of steps for software installation challenge"""
        return [
            "Verify system detection results",
            "Check current KiCad installation status",
            "Prepare installation environment",
            "Install KiCad",
            "Verify successful installation",
            "Test basic KiCad functionality"
        ]
    
    def execute_step(self, step_number):
        """Execute a specific step of the software installation challenge"""
        try:
            if step_number == 0:
                return self._verify_system_detection()
            elif step_number == 1:
                return self._check_kicad_status()
            elif step_number == 2:
                return self._prepare_installation()
            elif step_number == 3:
                return self._install_kicad()
            elif step_number == 4:
                return self._verify_installation()
            elif step_number == 5:
                return self._test_kicad_functionality()
            else:
                self.logger.error(f"Unknown step number: {step_number}")
                return False
                
        except Exception as e:
            self.logger.error(f"Step {step_number} failed: {e}")
            self.take_error_screenshot(f"step_{step_number}_error")
            return False
    
    def _verify_system_detection(self):
        """Verify that system detection was completed successfully"""
        try:
            self.logger.info("Verifying system detection results...")
            
            # Re-run basic system detection to get current state
            platform_info = self.detector.get_platform()
            self.logger.info(f"Platform confirmed: {platform_info['system']} {platform_info['release']}")
            
            # Check if we have necessary permissions for installation
            if platform_info['system'].lower() == 'windows':
                self.logger.info("Windows platform detected - may require administrator privileges")
            elif platform_info['system'].lower() == 'linux':
                self.logger.info("Linux platform detected - may require sudo privileges")
            elif platform_info['system'].lower() == 'darwin':
                self.logger.info("macOS platform detected - may require administrator privileges")
            
            self.platform_info = platform_info
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to verify system detection: {e}")
            return False
    
    def _check_kicad_status(self):
        """Check current KiCad installation status"""
        try:
            self.logger.info("Checking current KiCad installation status...")
            
            is_installed, details = self.detector.is_software_installed('KiCad', 'kicad')
            
            self.logger.info(f"KiCad installation status: {is_installed}")
            self.logger.info(f"Details: {details}")
            
            if is_installed:
                self.logger.warning("KiCad is already installed - installation may not be necessary")
                self.kicad_already_installed = True
            else:
                self.logger.info("KiCad not found - proceeding with installation")
                self.kicad_already_installed = False
            
            self.initial_kicad_status = is_installed
            self.initial_kicad_details = details
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to check KiCad status: {e}")
            return False
    
    def _prepare_installation(self):
        """Prepare the system for software installation"""
        try:
            self.logger.info("Preparing installation environment...")
            
            import config
            
            # Ensure necessary directories exist
            config.ensure_directories()
            
            # Check available disk space
            import shutil
            free_space = shutil.disk_usage(config.TEMP_DIR).free
            free_space_gb = free_space / (1024**3)
            
            self.logger.info(f"Available disk space: {free_space_gb:.2f} GB")
            
            if free_space_gb < 2.0:  # KiCad typically needs ~1GB
                self.logger.warning("Low disk space - installation might fail")
                return False
            
            # Check internet connectivity (basic test)
            try:
                import requests
                response = requests.get("https://www.google.com", timeout=10)
                if response.status_code == 200:
                    self.logger.info("Internet connectivity confirmed")
                else:
                    self.logger.warning("Internet connectivity issues detected")
            except Exception as e:
                self.logger.warning(f"Could not verify internet connectivity: {e}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to prepare installation: {e}")
            return False
    
    def _install_kicad(self):
        """Install KiCad using the software installer"""
        try:
            self.logger.info("Starting KiCad installation...")
            
            if self.kicad_already_installed:
                self.logger.info("KiCad already installed - skipping installation step")
                return True
            
            # Install KiCad
            install_start_time = time.time()
            success, details = self.installer.install_software('kicad')
            install_time = time.time() - install_start_time
            
            self.logger.info(f"Installation completed in {install_time:.1f} seconds")
            self.logger.info(f"Installation result: {success}")
            self.logger.info(f"Installation details: {details}")
            
            if success:
                self.logger.info("✓ KiCad installation successful")
                self.installation_successful = True
                self.installation_details = details
            else:
                self.logger.error(f"✗ KiCad installation failed: {details}")
                self.installation_successful = False
                self.installation_details = details
                
                # Take screenshot of any error dialogs
                self.take_error_screenshot("installation_failed")
                
                return False
            
            # Wait a moment for installation to complete
            self.wait_with_progress(5, "Waiting for installation to finalize")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to install KiCad: {e}")
            self.take_error_screenshot("installation_exception")
            return False
    
    def _verify_installation(self):
        """Verify that KiCad was successfully installed"""
        try:
            self.logger.info("Verifying KiCad installation...")
            
            # Wait a bit for system to register the new installation
            self.wait_with_progress(10, "Waiting for system to register installation")
            
            # Re-check KiCad installation status
            is_installed, details = self.detector.is_software_installed('KiCad', 'kicad')
            
            self.logger.info(f"Post-installation KiCad status: {is_installed}")
            self.logger.info(f"Post-installation details: {details}")
            
            if is_installed:
                self.logger.info("✓ KiCad installation verified successfully")
                self.final_kicad_status = True
                self.final_kicad_details = details
                
                # Compare with initial status
                if not self.initial_kicad_status:
                    self.logger.info("Installation successful - KiCad was not present before and is now installed")
                else:
                    self.logger.info("KiCad was already present and remains installed")
                
                return True
            else:
                self.logger.error("✗ KiCad installation verification failed")
                self.final_kicad_status = False
                self.final_kicad_details = details
                
                # Try to find out what went wrong
                self.logger.error("Installation verification failed - checking for common issues:")
                
                # Check if installation is pending reboot
                if 'windows' in self.platform_info['system'].lower():
                    self.logger.info("Windows installation may require system reboot")
                
                return False
            
        except Exception as e:
            self.logger.error(f"Failed to verify installation: {e}")
            return False
    
    def _test_kicad_functionality(self):
        """Test basic KiCad functionality"""
        try:
            self.logger.info("Testing basic KiCad functionality...")
            
            if not self.final_kicad_status:
                self.logger.error("Cannot test functionality - KiCad not installed")
                return False
            
            # Try to run KiCad with version flag to test if it works
            try:
                import subprocess
                
                # Try different command variations based on platform
                if 'windows' in self.platform_info['system'].lower():
                    cmd = ['kicad', '--version']
                else:
                    cmd = ['kicad', '--version']
                
                self.logger.info(f"Testing KiCad with command: {' '.join(cmd)}")
                
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                
                if result.returncode == 0:
                    self.logger.info("✓ KiCad responds to version command")
                    self.logger.info(f"KiCad version output: {result.stdout.strip()[:100]}")
                    self.kicad_functional = True
                else:
                    self.logger.warning(f"KiCad version command failed: {result.stderr}")
                    self.kicad_functional = False
                    # This might not be critical - some installations don't support --version
                    
            except subprocess.TimeoutExpired:
                self.logger.warning("KiCad version command timed out")
                self.kicad_functional = False
            except FileNotFoundError:
                self.logger.warning("KiCad executable not found in PATH")
                self.kicad_functional = False
            except Exception as e:
                self.logger.warning(f"KiCad functionality test failed: {e}")
                self.kicad_functional = False
            
            # Even if version test fails, consider installation successful if KiCad is detected
            if self.final_kicad_status:
                self.logger.info("Installation verification complete - KiCad is available")
                return True
            else:
                return False
            
        except Exception as e:
            self.logger.error(f"Failed to test KiCad functionality: {e}")
            return False
    
    def verify_success_condition(self):
        """Verify that software installation was successful"""
        try:
            # Success condition: KiCad is now installed (either was already installed or newly installed)
            return hasattr(self, 'final_kicad_status') and self.final_kicad_status
            
        except Exception as e:
            self.logger.error(f"Failed to verify success condition: {e}")
            return False
    
    def post_challenge_cleanup(self):
        """Cleanup after software installation"""
        try:
            self.logger.info("Software installation challenge completed")
            
            # Log final status
            if hasattr(self, 'final_kicad_status') and self.final_kicad_status:
                self.logger.info("✓ KiCad is now available on the system")
                self.logger.info("Next recommended challenge: Level 3 (Application Launch)")
                
                # Log installation summary
                if hasattr(self, 'kicad_already_installed'):
                    if self.kicad_already_installed:
                        self.logger.info("Installation summary: KiCad was already present")
                    else:
                        self.logger.info("Installation summary: KiCad was successfully installed")
            else:
                self.logger.error("✗ KiCad installation failed")
                self.logger.error("Manual installation may be required before proceeding")
            
            # Clean up any temporary files if needed
            # (The installer should handle its own cleanup)
            
        except Exception as e:
            self.logger.error(f"Cleanup failed: {e}")
