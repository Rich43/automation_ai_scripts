"""
Configuration management for the Progressive Desktop Automation System
"""
import json
import os
from pathlib import Path
from typing import Dict, Any, Optional

class Config:
    """Configuration manager for the automation system"""
    
    def __init__(self):
        self.config_dir = Path.home() / ".automation_system"
        self.config_file = self.config_dir / "config.json"
        self.ensure_config_dir()
        self.load_config()
    
    def ensure_config_dir(self):
        """Create config directory if it doesn't exist"""
        self.config_dir.mkdir(exist_ok=True)
    
    def load_config(self):
        """Load configuration from file or create default"""
        self.default_config = {
            "openai_api_key": "",
            "automation_speed": 1.0,  # 0.1 (slow) to 3.0 (fast)
            "screenshot_delay": 1.0,  # seconds between screenshots
            "click_delay": 0.5,       # seconds between clicks
            "typing_speed": 0.05,     # seconds between keystrokes
            "max_retries": 3,         # max automation retries
            "log_level": "INFO",      # DEBUG, INFO, WARNING, ERROR
            "auto_save_screenshots": True,
            "screenshot_dir": str(self.config_dir / "screenshots"),
            "error_screenshot_dir": str(self.config_dir / "error_screenshots"),
            "max_screenshot_history": 100,
            "vision_model": "gpt-4o",  # AI model for vision analysis
            "vision_timeout": 30,      # seconds for vision API calls
            "failsafe_enabled": True,  # PyAutoGUI failsafe
            "failsafe_corner": "top-left"  # corner for failsafe
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    loaded_config = json.load(f)
                    # Merge with defaults to handle new config options
                    self.config = {**self.default_config, **loaded_config}
            except (json.JSONDecodeError, IOError):
                self.config = self.default_config.copy()
        else:
            self.config = self.default_config.copy()
        
        self.save_config()
    
    def save_config(self):
        """Save current configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=4)
        except IOError as e:
            print(f"Warning: Could not save config: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any):
        """Set configuration value and save"""
        self.config[key] = value
        self.save_config()
    
    def update(self, updates: Dict[str, Any]):
        """Update multiple configuration values"""
        self.config.update(updates)
        self.save_config()
    
    def reset_to_defaults(self):
        """Reset configuration to defaults"""
        self.config = self.default_config.copy()
        self.save_config()
    
    def get_openai_api_key(self) -> Optional[str]:
        """Get OpenAI API key from config or environment"""
        # First check config file
        api_key = self.get("openai_api_key")
        if api_key:
            return api_key
        
        # Fallback to environment variable
        return os.environ.get("OPENAI_API_KEY")
    
    def validate_config(self) -> list:
        """Validate configuration and return list of issues"""
        issues = []
        
        # Check API key
        if not self.get_openai_api_key():
            issues.append("OpenAI API key not configured")
        
        # Check speed settings
        speed = self.get("automation_speed", 1.0)
        if not isinstance(speed, (int, float)) or speed <= 0 or speed > 10:
            issues.append("Automation speed must be between 0.1 and 10.0")
        
        # Check directories exist
        screenshot_dir = Path(self.get("screenshot_dir"))
        error_dir = Path(self.get("error_screenshot_dir"))
        
        try:
            screenshot_dir.mkdir(parents=True, exist_ok=True)
            error_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            issues.append(f"Cannot create screenshot directories: {e}")
        
        return issues

# Global config instance
config = Config()