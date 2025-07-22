"""
Base challenge class that all automation challenges inherit from
"""

import time
import traceback
from abc import ABC, abstractmethod
from logger_config import setup_logger

class BaseChallenge(ABC):
    def __init__(self, level, name, description):
        self.level = level
        self.name = name
        self.description = description
        self.logger = setup_logger(f"Challenge{level}")
        
        # Challenge state
        self.status = "not_started"  # not_started, running, completed, failed, error
        self.progress = 0.0  # 0.0 to 1.0
        self.current_step = 0
        self.steps = []
        
        # Statistics
        self.success_count = 0
        self.failure_count = 0
        self.last_run = None
        self.execution_time = 0
        self.last_error = None
        
        # Prerequisites (other challenge levels that must be completed first)
        self.prerequisites = []
        
        self.logger.info(f"Initialized challenge: {self.name}")
    
    @abstractmethod
    def get_steps(self):
        """Return list of steps required for this challenge"""
        pass
    
    @abstractmethod
    def execute_step(self, step_number):
        """Execute a specific step of the challenge"""
        pass
    
    def execute(self):
        """Execute the complete challenge"""
        try:
            self.status = "running"
            self.progress = 0.0
            self.current_step = 0
            self.last_error = None
            
            self.steps = self.get_steps()
            total_steps = len(self.steps)
            
            self.logger.info(f"Starting challenge '{self.name}' with {total_steps} steps")
            
            # Execute pre-challenge setup
            if not self.pre_challenge_setup():
                raise Exception("Pre-challenge setup failed")
            
            # Execute each step
            for step_num in range(total_steps):
                self.current_step = step_num + 1
                step_description = self.steps[step_num]
                
                self.logger.info(f"Executing step {self.current_step}/{total_steps}: {step_description}")
                
                try:
                    success = self.execute_step(step_num)
                    if not success:
                        raise Exception(f"Step {self.current_step} failed: {step_description}")
                    
                    # Update progress
                    self.progress = self.current_step / total_steps
                    self.logger.info(f"Step {self.current_step} completed successfully")
                    
                except Exception as e:
                    self.logger.error(f"Step {self.current_step} failed: {e}")
                    raise
            
            # Execute post-challenge cleanup
            self.post_challenge_cleanup()
            
            self.status = "completed"
            self.progress = 1.0
            self.logger.info(f"Challenge '{self.name}' completed successfully")
            
            return True
            
        except Exception as e:
            self.status = "failed"
            self.last_error = str(e)
            self.logger.error(f"Challenge '{self.name}' failed: {e}")
            self.logger.debug(f"Challenge error traceback: {traceback.format_exc()}")
            
            # Try to cleanup even if challenge failed
            try:
                self.post_challenge_cleanup()
            except Exception as cleanup_error:
                self.logger.error(f"Cleanup failed: {cleanup_error}")
            
            return False
    
    def pre_challenge_setup(self):
        """Setup required before challenge execution"""
        try:
            self.logger.info("Performing pre-challenge setup")
            return True
        except Exception as e:
            self.logger.error(f"Pre-challenge setup failed: {e}")
            return False
    
    def post_challenge_cleanup(self):
        """Cleanup after challenge execution"""
        try:
            self.logger.info("Performing post-challenge cleanup")
        except Exception as e:
            self.logger.error(f"Post-challenge cleanup failed: {e}")
    
    def reset(self):
        """Reset challenge to initial state"""
        self.status = "not_started"
        self.progress = 0.0
        self.current_step = 0
        self.last_error = None
        self.logger.info(f"Challenge '{self.name}' reset to initial state")
    
    def validate_prerequisites(self):
        """Validate that all prerequisites are met"""
        # This will be checked by the challenge manager
        return True
    
    def take_error_screenshot(self, description="error"):
        """Take a screenshot for debugging purposes"""
        try:
            from PIL import ImageGrab
            from pathlib import Path
            import config
            
            timestamp = int(time.time())
            filename = f"challenge_{self.level}_{description}_{timestamp}.png"
            filepath = config.ERROR_SCREENSHOT_DIR / filename
            
            screenshot = ImageGrab.grab()
            screenshot.save(filepath)
            
            self.logger.info(f"Error screenshot saved: {filepath}")
            return str(filepath)
            
        except Exception as e:
            self.logger.error(f"Failed to take error screenshot: {e}")
            return None
    
    def wait_with_progress(self, seconds, description="Waiting"):
        """Wait with progress updates"""
        self.logger.info(f"{description} for {seconds} seconds...")
        
        for i in range(seconds):
            time.sleep(1)
            if i % 5 == 0:  # Log every 5 seconds
                remaining = seconds - i - 1
                self.logger.debug(f"{description}: {remaining} seconds remaining")
    
    def verify_success_condition(self):
        """Verify that the challenge was completed successfully"""
        # Override in subclasses for specific verification
        return True
    
    def get_status_dict(self):
        """Get challenge status as dictionary"""
        return {
            'level': self.level,
            'name': self.name,
            'description': self.description,
            'status': self.status,
            'progress': self.progress,
            'current_step': self.current_step,
            'total_steps': len(self.steps),
            'success_count': self.success_count,
            'failure_count': self.failure_count,
            'last_run': self.last_run,
            'execution_time': self.execution_time,
            'last_error': self.last_error,
            'prerequisites': self.prerequisites
        }
