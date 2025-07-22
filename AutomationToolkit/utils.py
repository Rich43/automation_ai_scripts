"""
Utility functions for the Progressive Desktop Automation Challenge System
Common helpers and shared functionality
"""

import os
import time
import json
import hashlib
import subprocess
import platform
from typing import Dict, List, Any, Optional, Union, Tuple
from pathlib import Path
from datetime import datetime, timedelta

from logger_config import setup_logger

logger = setup_logger(__name__)

def get_timestamp() -> float:
    """Get current timestamp"""
    return time.time()

def format_timestamp(timestamp: float, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Format timestamp to human-readable string"""
    return datetime.fromtimestamp(timestamp).strftime(format_str)

def get_relative_time(timestamp: float) -> str:
    """Get relative time string (e.g., '2 minutes ago')"""
    now = datetime.now()
    then = datetime.fromtimestamp(timestamp)
    diff = now - then
    
    if diff.days > 0:
        return f"{diff.days} day{'s' if diff.days != 1 else ''} ago"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    else:
        return f"{diff.seconds} second{'s' if diff.seconds != 1 else ''} ago"

def ensure_directory(path: Union[str, Path]) -> Path:
    """Ensure directory exists, create if it doesn't"""
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path

def safe_filename(filename: str) -> str:
    """Convert string to safe filename"""
    # Remove or replace invalid characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    # Limit length
    if len(filename) > 255:
        filename = filename[:255]
    
    return filename

def generate_unique_id() -> str:
    """Generate unique ID based on timestamp and random data"""
    import uuid
    return str(uuid.uuid4())

def hash_string(text: str) -> str:
    """Generate SHA256 hash of string"""
    return hashlib.sha256(text.encode()).hexdigest()

def load_json_file(file_path: Union[str, Path]) -> Optional[Dict[str, Any]]:
    """Load JSON file safely"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load JSON file {file_path}: {e}")
        return None

def save_json_file(data: Dict[str, Any], file_path: Union[str, Path]) -> bool:
    """Save data to JSON file safely"""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        logger.error(f"Failed to save JSON file {file_path}: {e}")
        return False

def run_command(command: List[str], timeout: int = 30, cwd: Optional[str] = None) -> Dict[str, Any]:
    """
    Run system command and return result
    """
    try:
        logger.debug(f"Running command: {' '.join(command)}")
        
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=cwd
        )
        
        return {
            'success': result.returncode == 0,
            'returncode': result.returncode,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'command': ' '.join(command)
        }
        
    except subprocess.TimeoutExpired:
        logger.error(f"Command timed out after {timeout}s: {' '.join(command)}")
        return {
            'success': False,
            'error': f'Timeout after {timeout}s',
            'command': ' '.join(command)
        }
    except Exception as e:
        logger.error(f"Command failed: {e}")
        return {
            'success': False,
            'error': str(e),
            'command': ' '.join(command)
        }

def get_system_info() -> Dict[str, Any]:
    """Get comprehensive system information"""
    try:
        import psutil
        
        # Basic system info
        system_info = {
            'platform': {
                'system': platform.system(),
                'release': platform.release(),
                'version': platform.version(),
                'machine': platform.machine(),
                'processor': platform.processor(),
                'architecture': platform.architecture(),
                'python_version': platform.python_version()
            },
            'hardware': {
                'cpu_count': os.cpu_count(),
                'cpu_freq': None,
                'memory': None,
                'disk': None
            },
            'performance': {
                'cpu_percent': 0,
                'memory_percent': 0,
                'disk_percent': 0,
                'load_average': None
            }
        }
        
        # CPU information
        try:
            cpu_freq = psutil.cpu_freq()
            if cpu_freq:
                system_info['hardware']['cpu_freq'] = {
                    'current': cpu_freq.current,
                    'min': cpu_freq.min,
                    'max': cpu_freq.max
                }
        except Exception:
            pass
        
        # Memory information
        try:
            memory = psutil.virtual_memory()
            system_info['hardware']['memory'] = {
                'total': memory.total,
                'available': memory.available,
                'used': memory.used,
                'free': memory.free
            }
            system_info['performance']['memory_percent'] = memory.percent
        except Exception:
            pass
        
        # Disk information
        try:
            disk = psutil.disk_usage('/')
            system_info['hardware']['disk'] = {
                'total': disk.total,
                'used': disk.used,
                'free': disk.free
            }
            system_info['performance']['disk_percent'] = (disk.used / disk.total) * 100
        except Exception:
            pass
        
        # Performance metrics
        try:
            system_info['performance']['cpu_percent'] = psutil.cpu_percent(interval=1)
        except Exception:
            pass
        
        try:
            if platform.system() != 'Windows':
                system_info['performance']['load_average'] = os.getloadavg()
        except Exception:
            pass
        
        return system_info
        
    except Exception as e:
        logger.error(f"Failed to get system info: {e}")
        return {'error': str(e)}

def format_bytes(bytes_value: int) -> str:
    """Format bytes to human-readable string"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.1f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.1f} PB"

def format_duration(seconds: float) -> str:
    """Format duration in seconds to human-readable string"""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}h"

def validate_coordinates(x: int, y: int, screen_width: int, screen_height: int) -> bool:
    """Validate if coordinates are within screen bounds"""
    return 0 <= x <= screen_width and 0 <= y <= screen_height

def clamp_coordinates(x: int, y: int, screen_width: int, screen_height: int) -> Tuple[int, int]:
    """Clamp coordinates to screen bounds"""
    x = max(0, min(x, screen_width))
    y = max(0, min(y, screen_height))
    return x, y

def retry_with_backoff(func, max_attempts: int = 3, base_delay: float = 1.0, 
                      backoff_factor: float = 2.0, exceptions: Tuple = (Exception,)):
    """
    Retry function with exponential backoff
    """
    def wrapper(*args, **kwargs):
        last_exception = None
        
        for attempt in range(max_attempts):
            try:
                return func(*args, **kwargs)
            except exceptions as e:
                last_exception = e
                
                if attempt == max_attempts - 1:
                    # Last attempt, raise the exception
                    raise last_exception
                
                # Calculate delay with exponential backoff
                delay = base_delay * (backoff_factor ** attempt)
                logger.debug(f"Attempt {attempt + 1} failed, retrying in {delay:.1f}s: {e}")
                time.sleep(delay)
        
        # Should never reach here, but just in case
        raise last_exception
    
    return wrapper

def timeout_handler(timeout_seconds: int):
    """
    Decorator to add timeout to function calls
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            import signal
            
            def timeout_signal_handler(signum, frame):
                raise TimeoutError(f"Function {func.__name__} timed out after {timeout_seconds}s")
            
            # Set timeout signal (Unix only)
            if platform.system() != 'Windows':
                old_handler = signal.signal(signal.SIGALRM, timeout_signal_handler)
                signal.alarm(timeout_seconds)
            
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                if platform.system() != 'Windows':
                    signal.alarm(0)  # Cancel the alarm
                    signal.signal(signal.SIGALRM, old_handler)
        
        return wrapper
    return decorator

def debounce(wait_time: float):
    """
    Debounce decorator - only execute function if it hasn't been called in wait_time seconds
    """
    def decorator(func):
        last_called = [0.0]
        
        def wrapper(*args, **kwargs):
            now = time.time()
            if now - last_called[0] >= wait_time:
                last_called[0] = now
                return func(*args, **kwargs)
            else:
                logger.debug(f"Function {func.__name__} debounced")
                return None
        
        return wrapper
    return decorator

def find_available_port(start_port: int = 5000, max_attempts: int = 100) -> int:
    """Find an available port starting from start_port"""
    import socket
    
    for port in range(start_port, start_port + max_attempts):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('localhost', port))
            sock.close()
            
            if result != 0:  # Port is available
                return port
        except Exception:
            continue
    
    raise RuntimeError(f"No available port found in range {start_port}-{start_port + max_attempts}")

def sanitize_log_message(message: str) -> str:
    """Sanitize log message to prevent injection attacks"""
    # Remove control characters and limit length
    sanitized = ''.join(char for char in message if char.isprintable() or char.isspace())
    return sanitized[:1000]  # Limit to 1000 characters

def create_backup_filename(original_path: Union[str, Path], suffix: str = "backup") -> Path:
    """Create backup filename with timestamp"""
    original_path = Path(original_path)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    name_parts = [original_path.stem, suffix, timestamp]
    backup_name = "_".join(name_parts) + original_path.suffix
    
    return original_path.parent / backup_name

def check_internet_connectivity(host: str = "8.8.8.8", port: int = 53, timeout: int = 3) -> bool:
    """Check if internet connectivity is available"""
    import socket
    
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except Exception:
        return False

def get_process_by_name(process_name: str) -> List[Dict[str, Any]]:
    """Get processes by name"""
    try:
        import psutil
        
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'exe', 'create_time', 'memory_info']):
            try:
                if process_name.lower() in proc.info['name'].lower():
                    processes.append({
                        'pid': proc.info['pid'],
                        'name': proc.info['name'],
                        'exe': proc.info['exe'],
                        'create_time': proc.info['create_time'],
                        'memory_mb': proc.info['memory_info'].rss / 1024 / 1024 if proc.info['memory_info'] else 0
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        return processes
        
    except Exception as e:
        logger.error(f"Failed to get processes by name: {e}")
        return []

def kill_process_tree(pid: int, timeout: int = 5) -> bool:
    """Kill process and all its children"""
    try:
        import psutil
        
        parent = psutil.Process(pid)
        children = parent.children(recursive=True)
        
        # Terminate children first
        for child in children:
            try:
                child.terminate()
            except psutil.NoSuchProcess:
                pass
        
        # Terminate parent
        parent.terminate()
        
        # Wait for processes to terminate
        gone, alive = psutil.wait_procs(children + [parent], timeout=timeout)
        
        # Force kill any remaining processes
        for proc in alive:
            try:
                proc.kill()
            except psutil.NoSuchProcess:
                pass
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to kill process tree {pid}: {e}")
        return False

class PerformanceMonitor:
    """Simple performance monitoring utility"""
    
    def __init__(self):
        self.start_time = None
        self.checkpoints = []
    
    def start(self):
        """Start performance monitoring"""
        self.start_time = time.time()
        self.checkpoints = []
    
    def checkpoint(self, name: str):
        """Add a performance checkpoint"""
        if self.start_time is None:
            self.start()
        
        current_time = time.time()
        elapsed = current_time - self.start_time
        
        self.checkpoints.append({
            'name': name,
            'timestamp': current_time,
            'elapsed': elapsed
        })
    
    def finish(self) -> Dict[str, Any]:
        """Finish monitoring and return results"""
        if self.start_time is None:
            return {'error': 'Monitoring not started'}
        
        total_time = time.time() - self.start_time
        
        return {
            'total_time': total_time,
            'checkpoints': self.checkpoints,
            'checkpoint_count': len(self.checkpoints)
        }

# Global performance monitor instance
perf_monitor = PerformanceMonitor()

