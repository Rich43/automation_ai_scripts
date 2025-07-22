"""
Main Challenge System Coordinator
Orchestrates the execution of progressive automation challenges
"""

import threading
import time
import queue
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

from challenge_manager import ChallengeManager
from automation_engine import AutomationEngine
from system_detector import SystemDetector
from logger_config import setup_logger

class ChallengeSystemState(Enum):
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPING = "stopping"
    ERROR = "error"

@dataclass
class SystemEvent:
    event_type: str
    timestamp: float
    data: Dict[str, Any]
    level: Optional[int] = None

class ChallengeSystem:
    """
    Main coordinator for the progressive automation challenge system
    Manages challenge execution, state, and provides unified interface
    """
    
    def __init__(self):
        self.logger = setup_logger(__name__)
        
        # Core components
        self.challenge_manager = ChallengeManager()
        self.automation_engine = AutomationEngine()
        self.system_detector = SystemDetector()
        
        # System state
        self.state = ChallengeSystemState.IDLE
        self.current_challenge_level = None
        self.execution_thread = None
        self.event_queue = queue.Queue()
        self.system_metrics = {}
        
        # Execution control
        self.stop_requested = False
        self.pause_requested = False
        
        # Event listeners
        self.event_listeners = []
        
        self.logger.info("Challenge system initialized")
    
    def start_challenge_sequence(self, start_level: int = 1, end_level: int = 7) -> bool:
        """Start executing challenges sequentially from start_level to end_level"""
        try:
            if self.state != ChallengeSystemState.IDLE:
                self.logger.error(f"Cannot start challenges - system is {self.state.value}")
                return False
            
            self.logger.info(f"Starting challenge sequence: levels {start_level} to {end_level}")
            
            # Reset state
            self.stop_requested = False
            self.pause_requested = False
            
            # Start execution thread
            self.execution_thread = threading.Thread(
                target=self._execute_challenge_sequence,
                args=(start_level, end_level),
                daemon=True
            )
            self.execution_thread.start()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start challenge sequence: {e}")
            return False
    
    def start_single_challenge(self, level: int) -> bool:
        """Start a single challenge"""
        try:
            if self.state not in [ChallengeSystemState.IDLE, ChallengeSystemState.ERROR]:
                self.logger.error(f"Cannot start challenge - system is {self.state.value}")
                return False
            
            self.logger.info(f"Starting single challenge: level {level}")
            
            # Reset state
            self.stop_requested = False
            self.pause_requested = False
            
            # Start execution thread
            self.execution_thread = threading.Thread(
                target=self._execute_single_challenge,
                args=(level,),
                daemon=True
            )
            self.execution_thread.start()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start challenge {level}: {e}")
            return False
    
    def stop_execution(self) -> bool:
        """Stop current challenge execution"""
        try:
            if self.state in [ChallengeSystemState.IDLE, ChallengeSystemState.STOPPING]:
                return True
            
            self.logger.info("Stopping challenge execution")
            self.stop_requested = True
            self.state = ChallengeSystemState.STOPPING
            
            # Wait for execution thread to finish
            if self.execution_thread and self.execution_thread.is_alive():
                self.execution_thread.join(timeout=10)
            
            self.state = ChallengeSystemState.IDLE
            self.current_challenge_level = None
            
            self._emit_event("execution_stopped", {"reason": "user_requested"})
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to stop execution: {e}")
            return False
    
    def pause_execution(self) -> bool:
        """Pause current challenge execution"""
        try:
            if self.state != ChallengeSystemState.RUNNING:
                return False
            
            self.logger.info("Pausing challenge execution")
            self.pause_requested = True
            self.state = ChallengeSystemState.PAUSED
            
            self._emit_event("execution_paused", {})
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to pause execution: {e}")
            return False
    
    def resume_execution(self) -> bool:
        """Resume paused challenge execution"""
        try:
            if self.state != ChallengeSystemState.PAUSED:
                return False
            
            self.logger.info("Resuming challenge execution")
            self.pause_requested = False
            self.state = ChallengeSystemState.RUNNING
            
            self._emit_event("execution_resumed", {})
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to resume execution: {e}")
            return False
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        try:
            # Get challenge progress
            challenges = self.challenge_manager.get_all_challenges()
            overall_progress = self.challenge_manager.get_overall_progress()
            
            # Get system information
            platform_info = self.system_detector.get_platform()
            installed_software = self.system_detector.get_installed_software()
            
            # Current challenge status
            current_challenge_status = None
            if self.current_challenge_level:
                current_challenge_status = self.challenge_manager.get_challenge_status(
                    self.current_challenge_level
                )
            
            return {
                "state": self.state.value,
                "current_challenge_level": self.current_challenge_level,
                "current_challenge_status": current_challenge_status,
                "challenges": challenges,
                "overall_progress": overall_progress,
                "platform_info": platform_info,
                "installed_software": installed_software,
                "system_metrics": self.system_metrics,
                "recent_events": self._get_recent_events(10)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get system status: {e}")
            return {
                "state": "error",
                "error": str(e)
            }
    
    def add_event_listener(self, callback):
        """Add an event listener for system events"""
        self.event_listeners.append(callback)
    
    def remove_event_listener(self, callback):
        """Remove an event listener"""
        if callback in self.event_listeners:
            self.event_listeners.remove(callback)
    
    def _execute_challenge_sequence(self, start_level: int, end_level: int):
        """Execute challenge sequence in background thread"""
        try:
            self.state = ChallengeSystemState.RUNNING
            self._emit_event("sequence_started", {
                "start_level": start_level,
                "end_level": end_level
            })
            
            for level in range(start_level, end_level + 1):
                if self.stop_requested:
                    self.logger.info("Challenge sequence stopped by user")
                    break
                
                # Handle pause
                while self.pause_requested and not self.stop_requested:
                    time.sleep(1)
                
                if self.stop_requested:
                    break
                
                # Execute challenge
                success = self._execute_challenge_with_monitoring(level)
                
                if not success:
                    self.logger.error(f"Challenge {level} failed - stopping sequence")
                    self.state = ChallengeSystemState.ERROR
                    self._emit_event("sequence_failed", {
                        "failed_level": level,
                        "reason": "challenge_failed"
                    })
                    return
                
                # Brief pause between challenges
                if level < end_level:
                    time.sleep(2)
            
            if not self.stop_requested:
                self.logger.info("Challenge sequence completed successfully")
                self._emit_event("sequence_completed", {
                    "start_level": start_level,
                    "end_level": end_level
                })
            
            self.state = ChallengeSystemState.IDLE
            self.current_challenge_level = None
            
        except Exception as e:
            self.logger.error(f"Challenge sequence execution failed: {e}")
            self.state = ChallengeSystemState.ERROR
            self._emit_event("sequence_error", {"error": str(e)})
    
    def _execute_single_challenge(self, level: int):
        """Execute a single challenge in background thread"""
        try:
            self.state = ChallengeSystemState.RUNNING
            self._emit_event("challenge_started", {"level": level})
            
            success = self._execute_challenge_with_monitoring(level)
            
            if success:
                self.logger.info(f"Challenge {level} completed successfully")
                self._emit_event("challenge_completed", {"level": level})
            else:
                self.logger.error(f"Challenge {level} failed")
                self.state = ChallengeSystemState.ERROR
                self._emit_event("challenge_failed", {"level": level})
                return
            
            self.state = ChallengeSystemState.IDLE
            self.current_challenge_level = None
            
        except Exception as e:
            self.logger.error(f"Single challenge execution failed: {e}")
            self.state = ChallengeSystemState.ERROR
            self._emit_event("challenge_error", {"level": level, "error": str(e)})
    
    def _execute_challenge_with_monitoring(self, level: int) -> bool:
        """Execute a challenge with system monitoring"""
        try:
            self.current_challenge_level = level
            
            # Pre-execution monitoring
            self._update_system_metrics()
            
            # Execute challenge
            start_time = time.time()
            success = self.challenge_manager.run_challenge(level)
            execution_time = time.time() - start_time
            
            # Post-execution monitoring
            self._update_system_metrics()
            
            # Log execution metrics
            self.logger.info(f"Challenge {level} execution time: {execution_time:.2f}s")
            
            self._emit_event("challenge_metrics", {
                "level": level,
                "execution_time": execution_time,
                "success": success,
                "system_metrics": self.system_metrics.copy()
            })
            
            return success
            
        except Exception as e:
            self.logger.error(f"Challenge {level} execution failed: {e}")
            return False
    
    def _update_system_metrics(self):
        """Update system performance metrics"""
        try:
            import psutil
            
            # CPU and memory usage
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            
            # Disk usage
            disk = psutil.disk_usage('/')
            
            # Process information
            processes = len(psutil.pids())
            
            self.system_metrics.update({
                "timestamp": time.time(),
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_available_gb": memory.available / (1024**3),
                "disk_percent": (disk.used / disk.total) * 100,
                "disk_free_gb": disk.free / (1024**3),
                "process_count": processes
            })
            
        except Exception as e:
            self.logger.debug(f"Failed to update system metrics: {e}")
    
    def _emit_event(self, event_type: str, data: Dict[str, Any]):
        """Emit a system event to all listeners"""
        try:
            event = SystemEvent(
                event_type=event_type,
                timestamp=time.time(),
                data=data,
                level=self.current_challenge_level
            )
            
            # Add to event queue
            self.event_queue.put(event)
            
            # Notify listeners
            for listener in self.event_listeners:
                try:
                    listener(event)
                except Exception as e:
                    self.logger.error(f"Event listener failed: {e}")
            
        except Exception as e:
            self.logger.error(f"Failed to emit event: {e}")
    
    def _get_recent_events(self, count: int) -> List[Dict[str, Any]]:
        """Get recent events from the queue"""
        events = []
        temp_events = []
        
        # Get events from queue
        while not self.event_queue.empty() and len(events) < count:
            try:
                event = self.event_queue.get_nowait()
                events.append({
                    "event_type": event.event_type,
                    "timestamp": event.timestamp,
                    "data": event.data,
                    "level": event.level
                })
                temp_events.append(event)
            except queue.Empty:
                break
        
        # Put events back in queue (keep recent events)
        for event in temp_events:
            try:
                self.event_queue.put_nowait(event)
            except queue.Full:
                break
        
        # Return most recent events first
        return list(reversed(events))
    
    def get_challenge_logs(self, level: Optional[int] = None, count: int = 50) -> List[Dict[str, Any]]:
        """Get logs for a specific challenge or all challenges"""
        try:
            if level is not None:
                # Get logs for specific challenge
                return self.challenge_manager.get_recent_logs(count)
            else:
                # Get all recent logs
                return self.challenge_manager.get_recent_logs(count)
                
        except Exception as e:
            self.logger.error(f"Failed to get challenge logs: {e}")
            return []
    
    def reset_challenge(self, level: int) -> bool:
        """Reset a specific challenge to initial state"""
        try:
            if self.state == ChallengeSystemState.RUNNING and self.current_challenge_level == level:
                self.logger.error(f"Cannot reset challenge {level} - it is currently running")
                return False
            
            self.challenge_manager.reset_challenge(level)
            self._emit_event("challenge_reset", {"level": level})
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to reset challenge {level}: {e}")
            return False
    
    def shutdown(self):
        """Shutdown the challenge system gracefully"""
        try:
            self.logger.info("Shutting down challenge system...")
            
            # Stop any running execution
            self.stop_execution()
            
            # Clear event listeners
            self.event_listeners.clear()
            
            # Clear event queue
            while not self.event_queue.empty():
                try:
                    self.event_queue.get_nowait()
                except queue.Empty:
                    break
            
            self.logger.info("Challenge system shutdown complete")
            
        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")

