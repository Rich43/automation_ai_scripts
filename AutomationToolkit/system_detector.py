"""
System detection utilities for identifying installed software and system capabilities
"""

import os
import platform
import subprocess
import psutil
from pathlib import Path
from logger_config import setup_logger

# Windows registry access (Windows only)
try:
    import winreg
    WINDOWS_REGISTRY_AVAILABLE = True
except ImportError:
    WINDOWS_REGISTRY_AVAILABLE = False

class SystemDetector:
    def __init__(self):
        self.logger = setup_logger(__name__)
        self.platform = platform.system().lower()
        self.logger.info(f"System detector initialized for platform: {self.platform}")
    
    def get_platform(self):
        """Get current platform information"""
        return {
            'system': platform.system(),
            'release': platform.release(),
            'version': platform.version(),
            'machine': platform.machine(),
            'processor': platform.processor()
        }
    
    def get_system_paths(self):
        """Get important system paths"""
        paths = {
            'home': str(Path.home()),
            'temp': os.environ.get('TEMP', '/tmp'),
            'desktop': None,
            'programs': None,
            'downloads': None
        }
        
        if self.platform == 'windows':
            paths.update({
                'desktop': os.path.join(str(Path.home()), 'Desktop'),
                'programs': os.environ.get('PROGRAMFILES', 'C:\\Program Files'),
                'programs_x86': os.environ.get('PROGRAMFILES(X86)', 'C:\\Program Files (x86)'),
                'downloads': os.path.join(str(Path.home()), 'Downloads'),
                'appdata': os.environ.get('APPDATA'),
                'localappdata': os.environ.get('LOCALAPPDATA')
            })
        elif self.platform == 'linux':
            paths.update({
                'desktop': os.path.join(str(Path.home()), 'Desktop'),
                'downloads': os.path.join(str(Path.home()), 'Downloads'),
                'usr_bin': '/usr/bin',
                'usr_local_bin': '/usr/local/bin',
                'opt': '/opt'
            })
        elif self.platform == 'darwin':  # macOS
            paths.update({
                'desktop': os.path.join(str(Path.home()), 'Desktop'),
                'downloads': os.path.join(str(Path.home()), 'Downloads'),
                'applications': '/Applications',
                'usr_bin': '/usr/bin',
                'usr_local_bin': '/usr/local/bin'
            })
        
        return paths
    
    def is_software_installed(self, software_name, executable_name=None):
        """Check if specific software is installed"""
        try:
            if executable_name is None:
                executable_name = software_name.lower()
            
            # Method 1: Check if executable is in PATH
            if self._check_executable_in_path(executable_name):
                self.logger.info(f"{software_name} found in PATH")
                return True, "found_in_path"
            
            # Method 2: Platform-specific checks
            if self.platform == 'windows':
                return self._check_windows_software(software_name, executable_name)
            elif self.platform == 'linux':
                return self._check_linux_software(software_name, executable_name)
            elif self.platform == 'darwin':
                return self._check_macos_software(software_name, executable_name)
            
            return False, "not_found"
            
        except Exception as e:
            self.logger.error(f"Error checking if {software_name} is installed: {e}")
            return False, f"error: {e}"
    
    def _check_executable_in_path(self, executable_name):
        """Check if executable exists in system PATH"""
        try:
            if self.platform == 'windows':
                result = subprocess.run(['where', executable_name], 
                                      capture_output=True, text=True)
            else:
                result = subprocess.run(['which', executable_name], 
                                      capture_output=True, text=True)
            
            return result.returncode == 0
        except Exception:
            return False
    
    def _check_windows_software(self, software_name, executable_name):
        """Windows-specific software detection"""
        methods_checked = []
        
        # Check common installation directories
        common_paths = [
            os.environ.get('PROGRAMFILES', 'C:\\Program Files'),
            os.environ.get('PROGRAMFILES(X86)', 'C:\\Program Files (x86)'),
            os.path.join(str(Path.home()), 'AppData', 'Local'),
            os.path.join(str(Path.home()), 'AppData', 'Roaming')
        ]
        
        for base_path in common_paths:
            if not base_path or not os.path.exists(base_path):
                continue
                
            # Look for software directory
            for item in os.listdir(base_path):
                if software_name.lower() in item.lower():
                    software_path = os.path.join(base_path, item)
                    if os.path.isdir(software_path):
                        # Look for executable
                        for root, dirs, files in os.walk(software_path):
                            for file in files:
                                if file.lower().startswith(executable_name.lower()) and file.lower().endswith('.exe'):
                                    self.logger.info(f"Found {software_name} at {os.path.join(root, file)}")
                                    return True, f"found_in_directory: {os.path.join(root, file)}"
        
        methods_checked.append("directory_search")
        
        # Check Windows registry if available
        if WINDOWS_REGISTRY_AVAILABLE:
            if self._check_windows_registry(software_name):
                return True, "found_in_registry"
            methods_checked.append("registry_search")
        
        return False, f"not_found (checked: {', '.join(methods_checked)})"
    
    def _check_windows_registry(self, software_name):
        """Check Windows registry for installed software"""
        try:
            registry_paths = [
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
                (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall")
            ]
            
            for hkey, subkey in registry_paths:
                try:
                    with winreg.OpenKey(hkey, subkey) as key:
                        for i in range(winreg.QueryInfoKey(key)[0]):
                            try:
                                subkey_name = winreg.EnumKey(key, i)
                                with winreg.OpenKey(key, subkey_name) as subkey_handle:
                                    try:
                                        display_name = winreg.QueryValueEx(subkey_handle, "DisplayName")[0]
                                        if software_name.lower() in display_name.lower():
                                            self.logger.info(f"Found {software_name} in registry: {display_name}")
                                            return True
                                    except FileNotFoundError:
                                        continue
                            except Exception:
                                continue
                except Exception:
                    continue
            
            return False
        except Exception as e:
            self.logger.error(f"Error checking Windows registry: {e}")
            return False
    
    def _check_linux_software(self, software_name, executable_name):
        """Linux-specific software detection"""
        methods_checked = []
        
        # Check package managers
        package_managers = [
            (['dpkg', '-l', software_name], 'dpkg'),
            (['rpm', '-qa', software_name], 'rpm'),
            (['pacman', '-Q', software_name], 'pacman'),
            (['snap', 'list', software_name], 'snap'),
            (['flatpak', 'list', '--app'], 'flatpak')
        ]
        
        for cmd, manager in package_managers:
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                if result.returncode == 0 and software_name.lower() in result.stdout.lower():
                    self.logger.info(f"Found {software_name} via {manager}")
                    return True, f"found_via_{manager}"
                methods_checked.append(manager)
            except Exception:
                continue
        
        # Check common installation directories
        common_paths = ['/usr/bin', '/usr/local/bin', '/opt', f'{str(Path.home())}/.local/bin']
        
        for path in common_paths:
            if os.path.exists(path):
                for item in os.listdir(path):
                    if software_name.lower() in item.lower() or executable_name.lower() in item.lower():
                        full_path = os.path.join(path, item)
                        if os.path.isfile(full_path) and os.access(full_path, os.X_OK):
                            self.logger.info(f"Found {software_name} at {full_path}")
                            return True, f"found_in_directory: {full_path}"
        
        methods_checked.append("directory_search")
        
        return False, f"not_found (checked: {', '.join(methods_checked)})"
    
    def _check_macos_software(self, software_name, executable_name):
        """macOS-specific software detection"""
        methods_checked = []
        
        # Check Applications folder
        apps_path = '/Applications'
        if os.path.exists(apps_path):
            for item in os.listdir(apps_path):
                if software_name.lower() in item.lower() and item.endswith('.app'):
                    self.logger.info(f"Found {software_name} in Applications: {item}")
                    return True, f"found_in_applications: {item}"
            methods_checked.append("applications_folder")
        
        # Check Homebrew
        try:
            result = subprocess.run(['brew', 'list', software_name], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                self.logger.info(f"Found {software_name} via Homebrew")
                return True, "found_via_homebrew"
            methods_checked.append("homebrew")
        except Exception:
            pass
        
        # Check common directories
        common_paths = ['/usr/bin', '/usr/local/bin', '/opt/local/bin']
        
        for path in common_paths:
            if os.path.exists(path):
                for item in os.listdir(path):
                    if software_name.lower() in item.lower() or executable_name.lower() in item.lower():
                        full_path = os.path.join(path, item)
                        if os.path.isfile(full_path) and os.access(full_path, os.X_OK):
                            self.logger.info(f"Found {software_name} at {full_path}")
                            return True, f"found_in_directory: {full_path}"
        
        methods_checked.append("directory_search")
        
        return False, f"not_found (checked: {', '.join(methods_checked)})"
    
    def get_installed_software(self):
        """Get a list of commonly installed software"""
        software_to_check = [
            ('KiCad', 'kicad'),
            ('Git', 'git'),
            ('Python', 'python'),
            ('Node.js', 'node'),
            ('Visual Studio Code', 'code'),
            ('Firefox', 'firefox'),
            ('Chrome', 'chrome'),
            ('VLC', 'vlc'),
            ('7-Zip', '7z'),
            ('Notepad++', 'notepad++')
        ]
        
        installed_software = []
        
        for software_name, executable_name in software_to_check:
            is_installed, details = self.is_software_installed(software_name, executable_name)
            if is_installed:
                installed_software.append({
                    'name': software_name,
                    'executable': executable_name,
                    'details': details
                })
        
        return installed_software
    
    def get_running_processes(self):
        """Get list of currently running processes"""
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'exe']):
                try:
                    processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            return processes
        except Exception as e:
            self.logger.error(f"Error getting running processes: {e}")
            return []
    
    def is_process_running(self, process_name):
        """Check if a specific process is running"""
        try:
            for proc in psutil.process_iter(['name']):
                if proc.info['name'] and process_name.lower() in proc.info['name'].lower():
                    return True
            return False
        except Exception as e:
            self.logger.error(f"Error checking if process {process_name} is running: {e}")
            return False
