"""
Progressive Desktop Automation Challenge System
Main Flask application for the web interface
"""

from flask import Flask, render_template, jsonify, request
import threading
import time
from challenge_manager import ChallengeManager
from logger_config import setup_logger
from config import config

app = Flask(__name__)
logger = setup_logger(__name__)

# Initialize challenge manager
challenge_manager = ChallengeManager()

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')

@app.route('/api/challenges')
def get_challenges():
    """Get all available challenges and their status"""
    try:
        challenges = challenge_manager.get_all_challenges()
        return jsonify({
            'success': True,
            'challenges': challenges
        })
    except Exception as e:
        logger.error(f"Error getting challenges: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/challenge/<int:level>/start', methods=['POST'])
def start_challenge(level):
    """Start a specific challenge level"""
    try:
        # Run challenge in background thread to avoid blocking
        def run_challenge():
            challenge_manager.run_challenge(level)
        
        thread = threading.Thread(target=run_challenge)
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'success': True,
            'message': f'Started challenge level {level}'
        })
    except Exception as e:
        logger.error(f"Error starting challenge {level}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/challenge/<int:level>/status')
def get_challenge_status(level):
    """Get the current status of a challenge"""
    try:
        status = challenge_manager.get_challenge_status(level)
        return jsonify({
            'success': True,
            'status': status
        })
    except Exception as e:
        logger.error(f"Error getting challenge status {level}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/logs')
def get_logs():
    """Get recent automation logs"""
    try:
        logs = challenge_manager.get_recent_logs()
        return jsonify({
            'success': True,
            'logs': logs
        })
    except Exception as e:
        logger.error(f"Error getting logs: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/system/screenshot')
def get_screenshot():
    """Get current desktop screenshot for debugging"""
    try:
        from PIL import ImageGrab
        import base64
        import io
        
        # Take screenshot
        screenshot = ImageGrab.grab()
        
        # Convert to base64
        buffer = io.BytesIO()
        screenshot.save(buffer, format='PNG')
        screenshot_b64 = base64.b64encode(buffer.getvalue()).decode()
        
        return jsonify({
            'success': True,
            'screenshot': f'data:image/png;base64,{screenshot_b64}'
        })
    except Exception as e:
        logger.error(f"Error taking screenshot: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/system/info')
def get_system_info():
    """Get system information"""
    try:
        from system_detector import SystemDetector
        detector = SystemDetector()
        
        info = {
            'platform': detector.get_platform(),
            'installed_software': detector.get_installed_software(),
            'system_paths': detector.get_system_paths()
        }
        
        return jsonify({
            'success': True,
            'system_info': info
        })
    except Exception as e:
        logger.error(f"Error getting system info: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/config')
def get_config():
    """Get current configuration"""
    try:
        # Return config without sensitive API key (only first 8 chars)
        config_data = config.config.copy()
        api_key = config_data.get('openai_api_key', '')
        if api_key:
            config_data['openai_api_key'] = api_key[:8] + '...' if len(api_key) > 8 else api_key
        
        return jsonify(config_data)
    except Exception as e:
        logger.error(f"Error getting config: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/config', methods=['POST'])
def save_config():
    """Save configuration"""
    try:
        data = request.json
        if not data:
            return jsonify({
                'success': False,
                'error': 'No configuration data provided'
            }), 400
        
        # Validate configuration
        issues = []
        
        # Validate API key format
        if 'openai_api_key' in data:
            api_key = data['openai_api_key']
            if api_key and not api_key.startswith('sk-'):
                issues.append('OpenAI API key must start with "sk-"')
        
        # Validate numeric ranges
        speed = data.get('automation_speed', 1.0)
        if not isinstance(speed, (int, float)) or speed < 0.1 or speed > 10:
            issues.append('Automation speed must be between 0.1 and 10.0')
        
        if issues:
            return jsonify({
                'success': False,
                'error': 'Validation failed: ' + '; '.join(issues)
            }), 400
        
        # Update configuration
        config.update(data)
        
        return jsonify({
            'success': True,
            'message': 'Configuration saved successfully'
        })
    except Exception as e:
        logger.error(f"Error saving config: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/config/reset', methods=['POST'])
def reset_config():
    """Reset configuration to defaults"""
    try:
        config.reset_to_defaults()
        return jsonify({
            'success': True,
            'message': 'Configuration reset to defaults'
        })
    except Exception as e:
        logger.error(f"Error resetting config: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/config/validate')
def validate_config():
    """Validate current configuration"""
    try:
        issues = config.validate_config()
        return jsonify({
            'success': True,
            'valid': len(issues) == 0,
            'issues': issues
        })
    except Exception as e:
        logger.error(f"Error validating config: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    logger.info("Starting Progressive Desktop Automation Challenge System")
    app.run(host='0.0.0.0', port=5000, debug=True)
