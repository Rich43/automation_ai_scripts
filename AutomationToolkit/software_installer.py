"""
Automated software installation system
Handles downloading and installing applications when not found
"""

import os
import subprocess
import requests
import tempfile
import time
from pathlib import Path
from urllib.parse import urlparse
from logger_config import setup_logger

class SoftwareInstaller:
    def __init__(self):
        self.logger = setup_logger(__name__)
        self.platform = os.name
        
        # Software download URLs and installation info
        self.software_catalog = {
            'kicad': {
                'windows': {
                    'url': 'https://kicad.org/download/windows/',
                    'installer_pattern': 'kicad-*-x86_64.exe',
                    'silent_args': ['/S'],
                    'check_process': 'kicad.exe'
                },
                'linux': {
                    'ubuntu_ppa': 'ppa:kicad/kicad-7.0-releases',
                    'apt_package': 'kicad',
                    'flatpak_id': 'org.kicad.KiCad',
                    'check_process': 'kicad'
                },
                'darwin': {
                    'homebrew_cask': 'kicad',
                    'dmg_url': 'https://kicad.org/download/macos/',
                    'check_process': 'kicad'
                }
            },
            'git': {
                'windows': {
                    'url': 'https://git-scm.com/download/win',
                    'installer_pattern': 'Git-*-64-bit.exe',
                    'silent_args': ['/VERYSILENT', '/NORESTART'],
                    'check_process': 'git.exe'
                },
                'linux': {
                    'apt_package': 'git',
                    'yum_package': 'git',
                    'check_process': 'git'
                },
                'darwin': {
                    'homebrew_formula': 'git',
                    'check_process': 'git'
                }
            }
        }
        
        self.logger.info("Software installer initialized")
    
    def install_software(self, software_name, force_reinstall=False):
        """Install software if not already installed"""
        try:
            from system_detector import SystemDetector
            detector = SystemDetector()
            
            # Check if already installed (unless force reinstall)
            if not force_reinstall:
                is_installed, details = detector.is_software_installed(software_name)
                if is_installed:
                    self.logger.info(f"{software_name} is already installed: {details}")
                    return True, f"Already installed: {details}"
            
            # Get software configuration
            if software_name.lower() not in self.software_catalog:
                raise ValueError(f"Installation configuration for {software_name} not found")
            
            software_config = self.software_catalog[software_name.lower()]
            platform_key = self._get_platform_key()
            
            if platform_key not in software_config:
                raise ValueError(f"{software_name} installation not supported on {platform_key}")
            
            config = software_config[platform_key]
            
            self.logger.info(f"Starting installation of {software_name} on {platform_key}")
            
            # Platform-specific installation
            if platform_key == 'windows':
                return self._install_windows(software_name, config)
            elif platform_key == 'linux':
                return self._install_linux(software_name, config)
            elif platform_key == 'darwin':
                return self._install_macos(software_name, config)
            else:
                raise ValueError(f"Unsupported platform: {platform_key}")
                
        except Exception as e:
            self.logger.error(f"Failed to install {software_name}: {e}")
            return False, str(e)
    
    def _get_platform_key(self):
        """Get platform key for software catalog"""
        import platform
        system = platform.system().lower()
        
        if system == 'windows':
            return 'windows'
        elif system == 'linux':
            return 'linux'
        elif system == 'darwin':
            return 'darwin'
        else:
            return system
    
    def _install_windows(self, software_name, config):
        """Install software on Windows"""
        try:
            # Method 1: Try direct installer download
            if 'url' in config:
                installer_path = self._download_installer(software_name, config['url'])
                if installer_path:
                    return self._run_windows_installer(installer_path, config.get('silent_args', []))
            
            # Method 2: Try chocolatey if available
            if self._is_chocolatey_available():
                return self._install_via_chocolatey(software_name)
            
            # Method 3: Try winget if available
            if self._is_winget_available():
                return self._install_via_winget(software_name)
            
            return False, "No suitable installation method found for Windows"
            
        except Exception as e:
            return False, f"Windows installation failed: {e}"
    
    def _install_linux(self, software_name, config):
        """Install software on Linux"""
        try:
            # Method 1: Try apt (Ubuntu/Debian)
            if 'apt_package' in config and self._is_command_available('apt'):
                return self._install_via_apt(config['apt_package'])
            
            # Method 2: Try yum/dnf (RedHat/CentOS/Fedora)
            if 'yum_package' in config and (self._is_command_available('yum') or self._is_command_available('dnf')):
                return self._install_via_yum(config['yum_package'])
            
            # Method 3: Try flatpak
            if 'flatpak_id' in config and self._is_command_available('flatpak'):
                return self._install_via_flatpak(config['flatpak_id'])
            
            # Method 4: Try snap
            if 'snap_package' in config and self._is_command_available('snap'):
                return self._install_via_snap(config['snap_package'])
            
            return False, "No suitable package manager found for Linux"
            
        except Exception as e:
            return False, f"Linux installation failed: {e}"
    
    def _install_macos(self, software_name, config):
        """Install software on macOS"""
        try:
            # Method 1: Try Homebrew
            if 'homebrew_formula' in config and self._is_command_available('brew'):
                return self._install_via_brew(config['homebrew_formula'], formula=True)
            
            if 'homebrew_cask' in config and self._is_command_available('brew'):
                return self._install_via_brew(config['homebrew_cask'], formula=False)
            
            # Method 2: Try direct DMG download
            if 'dmg_url' in config:
                return self._install_macos_dmg(software_name, config['dmg_url'])
            
            return False, "No suitable installation method found for macOS"
            
        except Exception as e:
            return False, f"macOS installation failed: {e}"
    
    def _download_installer(self, software_name, url):
        """Download installer from URL"""
        try:
            # For now, return None as we can't download actual installers
            # In a real implementation, this would download the installer
            self.logger.info(f"Would download installer for {software_name} from {url}")
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to download installer: {e}")
            return None
    
    def _run_windows_installer(self, installer_path, silent_args):
        """Run Windows installer with silent arguments"""
        try:
            cmd = [installer_path] + silent_args
            self.logger.info(f"Running installer: {' '.join(cmd)}")
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                self.logger.info("Windows installer completed successfully")
                return True, "Installation completed"
            else:
                self.logger.error(f"Windows installer failed: {result.stderr}")
                return False, f"Installer failed: {result.stderr}"
                
        except Exception as e:
            return False, f"Failed to run installer: {e}"
    
    def _is_command_available(self, command):
        """Check if a command is available in system PATH"""
        try:
            subprocess.run([command, '--version'], capture_output=True, timeout=5)
            return True
        except Exception:
            return False
    
    def _is_chocolatey_available(self):
        """Check if Chocolatey is available on Windows"""
        return self._is_command_available('choco')
    
    def _is_winget_available(self):
        """Check if winget is available on Windows"""
        return self._is_command_available('winget')
    
    def _install_via_chocolatey(self, software_name):
        """Install software via Chocolatey"""
        try:
            cmd = ['choco', 'install', software_name, '-y']
            self.logger.info(f"Installing via Chocolatey: {' '.join(cmd)}")
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            
            if result.returncode == 0:
                return True, "Installed via Chocolatey"
            else:
                return False, f"Chocolatey installation failed: {result.stderr}"
                
        except Exception as e:
            return False, f"Chocolatey installation error: {e}"
    
    def _install_via_winget(self, software_name):
        """Install software via winget"""
        try:
            cmd = ['winget', 'install', software_name, '--silent']
            self.logger.info(f"Installing via winget: {' '.join(cmd)}")
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            
            if result.returncode == 0:
                return True, "Installed via winget"
            else:
                return False, f"winget installation failed: {result.stderr}"
                
        except Exception as e:
            return False, f"winget installation error: {e}"
    
    def _install_via_apt(self, package_name):
        """Install software via apt (Ubuntu/Debian)"""
        try:
            # Update package list first
            subprocess.run(['sudo', 'apt', 'update'], capture_output=True, timeout=120)
            
            # Install package
            cmd = ['sudo', 'apt', 'install', '-y', package_name]
            self.logger.info(f"Installing via apt: {' '.join(cmd)}")
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            
            if result.returncode == 0:
                return True, "Installed via apt"
            else:
                return False, f"apt installation failed: {result.stderr}"
                
        except Exception as e:
            return False, f"apt installation error: {e}"
    
    def _install_via_yum(self, package_name):
        """Install software via yum/dnf (RedHat/CentOS/Fedora)"""
        try:
            # Try dnf first, then yum
            package_manager = 'dnf' if self._is_command_available('dnf') else 'yum'
            
            cmd = ['sudo', package_manager, 'install', '-y', package_name]
            self.logger.info(f"Installing via {package_manager}: {' '.join(cmd)}")
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            
            if result.returncode == 0:
                return True, f"Installed via {package_manager}"
            else:
                return False, f"{package_manager} installation failed: {result.stderr}"
                
        except Exception as e:
            return False, f"{package_manager} installation error: {e}"
    
    def _install_via_flatpak(self, flatpak_id):
        """Install software via Flatpak"""
        try:
            cmd = ['flatpak', 'install', '-y', 'flathub', flatpak_id]
            self.logger.info(f"Installing via Flatpak: {' '.join(cmd)}")
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            
            if result.returncode == 0:
                return True, "Installed via Flatpak"
            else:
                return False, f"Flatpak installation failed: {result.stderr}"
                
        except Exception as e:
            return False, f"Flatpak installation error: {e}"
    
    def _install_via_snap(self, package_name):
        """Install software via Snap"""
        try:
            cmd = ['sudo', 'snap', 'install', package_name]
            self.logger.info(f"Installing via Snap: {' '.join(cmd)}")
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            
            if result.returncode == 0:
                return True, "Installed via Snap"
            else:
                return False, f"Snap installation failed: {result.stderr}"
                
        except Exception as e:
            return False, f"Snap installation error: {e}"
    
    def _install_via_brew(self, package_name, formula=True):
        """Install software via Homebrew"""
        try:
            if formula:
                cmd = ['brew', 'install', package_name]
            else:
                cmd = ['brew', 'install', '--cask', package_name]
            
            self.logger.info(f"Installing via Homebrew: {' '.join(cmd)}")
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            
            if result.returncode == 0:
                return True, "Installed via Homebrew"
            else:
                return False, f"Homebrew installation failed: {result.stderr}"
                
        except Exception as e:
            return False, f"Homebrew installation error: {e}"
    
    def _install_macos_dmg(self, software_name, dmg_url):
        """Install software from DMG on macOS"""
        try:
            # This would require downloading and mounting DMG
            # For now, just return a placeholder
            self.logger.info(f"Would install {software_name} from DMG: {dmg_url}")
            return False, "DMG installation not implemented"
            
        except Exception as e:
            return False, f"DMG installation error: {e}"
