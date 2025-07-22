"""
Challenge management system for progressive automation tasks
"""

import importlib
import time
from pathlib import Path
from logger_config import setup_logger

class ChallengeManager:
    def __init__(self):
        self.logger = setup_logger(__name__)
        self.challenges = {}
        self.challenge_logs = []
        self.current_challenge = None
        
        # Load all challenge modules
        self._load_challenges()
        
        self.logger.info(f"Challenge manager initialized with {len(self.challenges)} challenges")
    
    def _load_challenges(self):
        """Dynamically load all challenge modules"""
        challenges_dir = Path("challenges")
        
        for challenge_file in challenges_dir.glob("level*.py"):
            try:
                module_name = f"challenges.{challenge_file.stem}"
                module = importlib.import_module(module_name)
                
                # Get the challenge class (assumes class name matches pattern)
                class_name = ''.join(word.capitalize() for word in challenge_file.stem.split('_'))
                challenge_class = getattr(module, class_name)
                
                # Extract level number from filename
                level = int(challenge_file.stem.split('_')[0].replace('level', ''))
                
                self.challenges[level] = challenge_class()
                self.logger.info(f"Loaded challenge level {level}: {challenge_class.__name__}")
                
            except Exception as e:
                self.logger.error(f"Failed to load challenge {challenge_file}: {e}")
    
    def get_all_challenges(self):
        """Get information about all available challenges"""
        challenge_info = []
        
        for level in sorted(self.challenges.keys()):
            challenge = self.challenges[level]
            info = {
                'level': level,
                'name': challenge.name,
                'description': challenge.description,
                'status': challenge.status,
                'last_run': challenge.last_run,
                'success_count': challenge.success_count,
                'failure_count': challenge.failure_count,
                'prerequisites': challenge.prerequisites
            }
            challenge_info.append(info)
        
        return challenge_info
    
    def get_challenge_status(self, level):
        """Get detailed status of a specific challenge"""
        if level not in self.challenges:
            raise ValueError(f"Challenge level {level} not found")
        
        challenge = self.challenges[level]
        return {
            'level': level,
            'name': challenge.name,
            'status': challenge.status,
            'progress': challenge.progress,
            'current_step': challenge.current_step,
            'total_steps': len(challenge.steps),
            'last_error': challenge.last_error,
            'execution_time': challenge.execution_time
        }
    
    def run_challenge(self, level):
        """Execute a specific challenge"""
        if level not in self.challenges:
            raise ValueError(f"Challenge level {level} not found")
        
        challenge = self.challenges[level]
        self.current_challenge = challenge
        
        try:
            self.logger.info(f"Starting challenge level {level}: {challenge.name}")
            self._log_challenge_event(level, "started", "Challenge execution started")
            
            # Check prerequisites
            if not self._check_prerequisites(level):
                raise Exception("Prerequisites not met for this challenge")
            
            # Execute the challenge
            start_time = time.time()
            success = challenge.execute()
            execution_time = time.time() - start_time
            
            # Update challenge statistics
            challenge.execution_time = execution_time
            challenge.last_run = time.time()
            
            if success:
                challenge.success_count += 1
                challenge.status = "completed"
                self._log_challenge_event(level, "completed", f"Challenge completed successfully in {execution_time:.2f}s")
                self.logger.info(f"Challenge level {level} completed successfully")
            else:
                challenge.failure_count += 1
                challenge.status = "failed"
                self._log_challenge_event(level, "failed", f"Challenge failed after {execution_time:.2f}s")
                self.logger.error(f"Challenge level {level} failed")
            
            return success
            
        except Exception as e:
            challenge.failure_count += 1
            challenge.status = "error"
            challenge.last_error = str(e)
            self._log_challenge_event(level, "error", str(e))
            self.logger.error(f"Challenge level {level} error: {e}")
            raise
        
        finally:
            self.current_challenge = None
    
    def _check_prerequisites(self, level):
        """Check if prerequisites for a challenge are met"""
        challenge = self.challenges[level]
        
        for prereq_level in challenge.prerequisites:
            if prereq_level not in self.challenges:
                self.logger.error(f"Prerequisite level {prereq_level} not found")
                return False
            
            prereq_challenge = self.challenges[prereq_level]
            if prereq_challenge.status != "completed":
                self.logger.error(f"Prerequisite level {prereq_level} not completed")
                return False
        
        return True
    
    def _log_challenge_event(self, level, event_type, message):
        """Log a challenge event"""
        log_entry = {
            'timestamp': time.time(),
            'level': level,
            'event_type': event_type,
            'message': message
        }
        
        self.challenge_logs.append(log_entry)
        
        # Keep only last 1000 log entries
        if len(self.challenge_logs) > 1000:
            self.challenge_logs = self.challenge_logs[-1000:]
    
    def get_recent_logs(self, limit=50):
        """Get recent challenge logs"""
        return self.challenge_logs[-limit:]
    
    def reset_challenge(self, level):
        """Reset a challenge to initial state"""
        if level not in self.challenges:
            raise ValueError(f"Challenge level {level} not found")
        
        challenge = self.challenges[level]
        challenge.reset()
        
        self._log_challenge_event(level, "reset", "Challenge reset to initial state")
        self.logger.info(f"Challenge level {level} reset")
    
    def get_overall_progress(self):
        """Get overall progress across all challenges"""
        total_challenges = len(self.challenges)
        completed_challenges = sum(1 for c in self.challenges.values() if c.status == "completed")
        
        return {
            'total_challenges': total_challenges,
            'completed_challenges': completed_challenges,
            'completion_percentage': (completed_challenges / total_challenges * 100) if total_challenges > 0 else 0,
            'current_level': max([level for level, challenge in self.challenges.items() 
                                if challenge.status == "completed"], default=0) + 1
        }
