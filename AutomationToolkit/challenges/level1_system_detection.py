"""
Level 1 Challenge: System Detection
Check if applications are installed by searching system paths and registries
"""

from challenges.base_challenge import BaseChallenge
from system_detector import SystemDetector

class Level1SystemDetection(BaseChallenge):
    def __init__(self):
        super().__init__(
            level=1,
            name="System Detection",
            description="Detect if KiCad and other essential software are installed on the system"
        )
        
        self.detector = SystemDetector()
        self.required_software = [
            ('KiCad', 'kicad'),
            ('Git', 'git'),
            ('Python', 'python')
        ]
        
        # No prerequisites for level 1
        self.prerequisites = []
    
    def get_steps(self):
        """Return list of steps for system detection challenge"""
        return [
            "Initialize system detector",
            "Get platform information",
            "Check system paths",
            "Detect installed software",
            "Verify KiCad installation",
            "Generate detection report"
        ]
    
    def execute_step(self, step_number):
        """Execute a specific step of the system detection challenge"""
        try:
            if step_number == 0:
                return self._initialize_detector()
            elif step_number == 1:
                return self._get_platform_info()
            elif step_number == 2:
                return self._check_system_paths()
            elif step_number == 3:
                return self._detect_installed_software()
            elif step_number == 4:
                return self._verify_kicad_installation()
            elif step_number == 5:
                return self._generate_detection_report()
            else:
                self.logger.error(f"Unknown step number: {step_number}")
                return False
                
        except Exception as e:
            self.logger.error(f"Step {step_number} failed: {e}")
            return False
    
    def _initialize_detector(self):
        """Initialize system detector"""
        try:
            self.logger.info("Initializing system detector...")
            
            # Test basic detector functionality
            platform_info = self.detector.get_platform()
            self.logger.info(f"Detected platform: {platform_info['system']} {platform_info['release']}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize detector: {e}")
            return False
    
    def _get_platform_info(self):
        """Get detailed platform information"""
        try:
            self.logger.info("Gathering platform information...")
            
            platform_info = self.detector.get_platform()
            
            self.logger.info(f"System: {platform_info['system']}")
            self.logger.info(f"Release: {platform_info['release']}")
            self.logger.info(f"Version: {platform_info['version']}")
            self.logger.info(f"Machine: {platform_info['machine']}")
            
            # Store platform info for later use
            self.platform_info = platform_info
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to get platform info: {e}")
            return False
    
    def _check_system_paths(self):
        """Check important system paths"""
        try:
            self.logger.info("Checking system paths...")
            
            system_paths = self.detector.get_system_paths()
            
            important_paths = ['home', 'temp', 'desktop', 'programs', 'downloads']
            
            for path_name in important_paths:
                if path_name in system_paths:
                    path_value = system_paths[path_name]
                    if path_value:
                        import os
                        exists = os.path.exists(path_value)
                        self.logger.info(f"{path_name.capitalize()} path: {path_value} (exists: {exists})")
                    else:
                        self.logger.warning(f"{path_name.capitalize()} path not defined")
                else:
                    self.logger.warning(f"{path_name.capitalize()} path not available on this platform")
            
            # Store paths for later use
            self.system_paths = system_paths
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to check system paths: {e}")
            return False
    
    def _detect_installed_software(self):
        """Detect commonly installed software"""
        try:
            self.logger.info("Detecting installed software...")
            
            installed_software = self.detector.get_installed_software()
            
            self.logger.info(f"Found {len(installed_software)} installed applications:")
            
            for software in installed_software:
                self.logger.info(f"  - {software['name']}: {software['details']}")
            
            # Store detected software for later use
            self.installed_software = installed_software
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to detect installed software: {e}")
            return False
    
    def _verify_kicad_installation(self):
        """Specifically verify KiCad installation"""
        try:
            self.logger.info("Verifying KiCad installation...")
            
            is_installed, details = self.detector.is_software_installed('KiCad', 'kicad')
            
            if is_installed:
                self.logger.info(f"✓ KiCad is installed: {details}")
                self.kicad_installed = True
                self.kicad_details = details
            else:
                self.logger.warning(f"✗ KiCad is not installed: {details}")
                self.kicad_installed = False
                self.kicad_details = details
            
            # Also check if KiCad process is currently running
            is_running = self.detector.is_process_running('kicad')
            self.logger.info(f"KiCad currently running: {is_running}")
            self.kicad_running = is_running
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to verify KiCad installation: {e}")
            return False
    
    def _generate_detection_report(self):
        """Generate comprehensive detection report"""
        try:
            self.logger.info("Generating detection report...")
            
            report = {
                'platform': self.platform_info,
                'system_paths': self.system_paths,
                'installed_software': self.installed_software,
                'kicad_status': {
                    'installed': self.kicad_installed,
                    'details': self.kicad_details,
                    'running': self.kicad_running
                },
                'challenge_result': 'SUCCESS' if self.kicad_installed else 'NEEDS_INSTALLATION'
            }
            
            # Store report for other challenges to use
            self.detection_report = report
            
            self.logger.info("=== SYSTEM DETECTION REPORT ===")
            self.logger.info(f"Platform: {report['platform']['system']} {report['platform']['release']}")
            self.logger.info(f"Total software detected: {len(report['installed_software'])}")
            self.logger.info(f"KiCad installed: {report['kicad_status']['installed']}")
            self.logger.info(f"Challenge result: {report['challenge_result']}")
            
            if not self.kicad_installed:
                self.logger.warning("KiCad not found - Level 2 (Software Installation) will be required")
            else:
                self.logger.info("KiCad detected - can proceed to Level 3 (Application Launch)")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to generate detection report: {e}")
            return False
    
    def verify_success_condition(self):
        """Verify that system detection was successful"""
        try:
            # Success condition: We successfully detected the system state
            # Whether KiCad is installed or not, the detection itself should succeed
            return hasattr(self, 'detection_report') and self.detection_report is not None
            
        except Exception as e:
            self.logger.error(f"Failed to verify success condition: {e}")
            return False
    
    def post_challenge_cleanup(self):
        """Cleanup after system detection"""
        try:
            self.logger.info("System detection completed - no cleanup required")
            
            # Log summary for next challenges
            if hasattr(self, 'kicad_installed'):
                if self.kicad_installed:
                    self.logger.info("Next recommended challenge: Level 3 (Application Launch)")
                else:
                    self.logger.info("Next recommended challenge: Level 2 (Software Installation)")
            
        except Exception as e:
            self.logger.error(f"Cleanup failed: {e}")
