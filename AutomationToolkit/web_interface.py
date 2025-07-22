"""
Web interface for the Progressive Desktop Automation Challenge System
Provides Flask-based web dashboard for monitoring and controlling challenges
"""

from flask import Flask, render_template, jsonify, request, send_from_directory
import threading
import time
import os
from pathlib import Path

from challenge_system import ChallengeSystem, SystemEvent
from logger_config import setup_logger

class WebInterface:
    """
    Flask web interface for the automation challenge system
    """
    
    def __init__(self, challenge_system: ChallengeSystem):
        self.logger = setup_logger(__name__)
        self.challenge_system = challenge_system
        
        # Initialize Flask app
        self.app = Flask(__name__)
        self.app.secret_key = os.urandom(24)
        
        # Add event listener to challenge system
        self.challenge_system.add_event_listener(self._handle_system_event)
        
        # Setup routes
        self._setup_routes()
        
        # Track connected clients for real-time updates
        self.connected_clients = set()
        
        self.logger.info("Web interface initialized")
    
    def _setup_routes(self):
        """Setup Flask routes"""
        
        @self.app.route('/')
        def index():
            """Main dashboard page"""
            try:
                return render_template('index.html')
            except Exception as e:
                self.logger.error(f"Error rendering index page: {e}")
                return f"Error loading dashboard: {e}", 500
        
        @self.app.route('/api/status')
        def get_system_status():
            """Get comprehensive system status"""
            try:
                status = self.challenge_system.get_system_status()
                return jsonify({
                    'success': True,
                    'status': status,
                    'timestamp': time.time()
                })
            except Exception as e:
                self.logger.error(f"Error getting system status: {e}")
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500
        
        @self.app.route('/api/challenges')
        def get_challenges():
            """Get all challenges and their status"""
            try:
                status = self.challenge_system.get_system_status()
                challenges = status.get('challenges', [])
                
                return jsonify({
                    'success': True,
                    'challenges': challenges,
                    'overall_progress': status.get('overall_progress', {}),
                    'timestamp': time.time()
                })
            except Exception as e:
                self.logger.error(f"Error getting challenges: {e}")
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500
        
        @self.app.route('/api/challenge/<int:level>/start', methods=['POST'])
        def start_challenge(level):
            """Start a specific challenge"""
            try:
                success = self.challenge_system.start_single_challenge(level)
                
                if success:
                    return jsonify({
                        'success': True,
                        'message': f'Challenge {level} started successfully',
                        'timestamp': time.time()
                    })
                else:
                    return jsonify({
                        'success': False,
                        'error': f'Failed to start challenge {level}'
                    }), 400
                    
            except Exception as e:
                self.logger.error(f"Error starting challenge {level}: {e}")
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500
        
        @self.app.route('/api/challenge/<int:level>/status')
        def get_challenge_status(level):
            """Get detailed status of a specific challenge"""
            try:
                status = self.challenge_system.get_system_status()
                challenges = status.get('challenges', [])
                
                challenge_status = None
                for challenge in challenges:
                    if challenge.get('level') == level:
                        challenge_status = challenge
                        break
                
                if challenge_status:
                    return jsonify({
                        'success': True,
                        'status': challenge_status,
                        'timestamp': time.time()
                    })
                else:
                    return jsonify({
                        'success': False,
                        'error': f'Challenge {level} not found'
                    }), 404
                    
            except Exception as e:
                self.logger.error(f"Error getting challenge {level} status: {e}")
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500
        
        @self.app.route('/api/challenge/<int:level>/reset', methods=['POST'])
        def reset_challenge(level):
            """Reset a specific challenge"""
            try:
                success = self.challenge_system.reset_challenge(level)
                
                if success:
                    return jsonify({
                        'success': True,
                        'message': f'Challenge {level} reset successfully',
                        'timestamp': time.time()
                    })
                else:
                    return jsonify({
                        'success': False,
                        'error': f'Failed to reset challenge {level}'
                    }), 400
                    
            except Exception as e:
                self.logger.error(f"Error resetting challenge {level}: {e}")
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500
        
        @self.app.route('/api/sequence/start', methods=['POST'])
        def start_challenge_sequence():
            """Start challenge sequence"""
            try:
                data = request.get_json() or {}
                start_level = data.get('start_level', 1)
                end_level = data.get('end_level', 7)
                
                success = self.challenge_system.start_challenge_sequence(start_level, end_level)
                
                if success:
                    return jsonify({
                        'success': True,
                        'message': f'Challenge sequence {start_level}-{end_level} started',
                        'timestamp': time.time()
                    })
                else:
                    return jsonify({
                        'success': False,
                        'error': 'Failed to start challenge sequence'
                    }), 400
                    
            except Exception as e:
                self.logger.error(f"Error starting challenge sequence: {e}")
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500
        
        @self.app.route('/api/execution/stop', methods=['POST'])
        def stop_execution():
            """Stop current challenge execution"""
            try:
                success = self.challenge_system.stop_execution()
                
                if success:
                    return jsonify({
                        'success': True,
                        'message': 'Execution stopped successfully',
                        'timestamp': time.time()
                    })
                else:
                    return jsonify({
                        'success': False,
                        'error': 'Failed to stop execution'
                    }), 400
                    
            except Exception as e:
                self.logger.error(f"Error stopping execution: {e}")
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500
        
        @self.app.route('/api/execution/pause', methods=['POST'])
        def pause_execution():
            """Pause current challenge execution"""
            try:
                success = self.challenge_system.pause_execution()
                
                if success:
                    return jsonify({
                        'success': True,
                        'message': 'Execution paused successfully',
                        'timestamp': time.time()
                    })
                else:
                    return jsonify({
                        'success': False,
                        'error': 'Failed to pause execution'
                    }), 400
                    
            except Exception as e:
                self.logger.error(f"Error pausing execution: {e}")
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500
        
        @self.app.route('/api/execution/resume', methods=['POST'])
        def resume_execution():
            """Resume paused challenge execution"""
            try:
                success = self.challenge_system.resume_execution()
                
                if success:
                    return jsonify({
                        'success': True,
                        'message': 'Execution resumed successfully',
                        'timestamp': time.time()
                    })
                else:
                    return jsonify({
                        'success': False,
                        'error': 'Failed to resume execution'
                    }), 400
                    
            except Exception as e:
                self.logger.error(f"Error resuming execution: {e}")
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500
        
        @self.app.route('/api/logs')
        def get_logs():
            """Get recent automation logs"""
            try:
                level = request.args.get('level', type=int)
                count = request.args.get('count', 50, type=int)
                
                logs = self.challenge_system.get_challenge_logs(level, count)
                
                return jsonify({
                    'success': True,
                    'logs': logs,
                    'timestamp': time.time()
                })
                
            except Exception as e:
                self.logger.error(f"Error getting logs: {e}")
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500
        
        @self.app.route('/api/system/screenshot')
        def get_screenshot():
            """Get current desktop screenshot"""
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
                    'screenshot': f'data:image/png;base64,{screenshot_b64}',
                    'timestamp': time.time()
                })
                
            except Exception as e:
                self.logger.error(f"Error taking screenshot: {e}")
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500
        
        @self.app.route('/api/system/info')
        def get_system_info():
            """Get system information"""
            try:
                status = self.challenge_system.get_system_status()
                
                system_info = {
                    'platform': status.get('platform_info', {}),
                    'installed_software': status.get('installed_software', []),
                    'system_metrics': status.get('system_metrics', {}),
                    'state': status.get('state', 'unknown')
                }
                
                return jsonify({
                    'success': True,
                    'system_info': system_info,
                    'timestamp': time.time()
                })
                
            except Exception as e:
                self.logger.error(f"Error getting system info: {e}")
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500
        
        @self.app.route('/api/events')
        def get_recent_events():
            """Get recent system events"""
            try:
                count = request.args.get('count', 20, type=int)
                status = self.challenge_system.get_system_status()
                events = status.get('recent_events', [])[-count:]
                
                return jsonify({
                    'success': True,
                    'events': events,
                    'timestamp': time.time()
                })
                
            except Exception as e:
                self.logger.error(f"Error getting events: {e}")
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500
        
        @self.app.route('/api/health')
        def health_check():
            """Health check endpoint"""
            try:
                return jsonify({
                    'success': True,
                    'status': 'healthy',
                    'timestamp': time.time(),
                    'version': '1.0.0'
                })
            except Exception as e:
                return jsonify({
                    'success': False,
                    'status': 'unhealthy',
                    'error': str(e)
                }), 500
        
        # Static file serving
        @self.app.route('/favicon.ico')
        def favicon():
            return send_from_directory(
                os.path.join(self.app.root_path, 'static'),
                'favicon.ico',
                mimetype='image/vnd.microsoft.icon'
            )
        
        # Error handlers
        @self.app.errorhandler(404)
        def not_found(error):
            return jsonify({
                'success': False,
                'error': 'Endpoint not found'
            }), 404
        
        @self.app.errorhandler(500)
        def internal_error(error):
            return jsonify({
                'success': False,
                'error': 'Internal server error'
            }), 500
    
    def _handle_system_event(self, event: SystemEvent):
        """Handle system events for real-time updates"""
        try:
            # Log important events
            if event.event_type in ['challenge_started', 'challenge_completed', 'challenge_failed']:
                self.logger.info(f"System event: {event.event_type} - Level {event.level}")
            
            # Here you could implement WebSocket or SSE for real-time updates
            # For now, we just log the event
            
        except Exception as e:
            self.logger.error(f"Error handling system event: {e}")
    
    def run(self, host='0.0.0.0', port=5000, debug=False):
        """Run the Flask web interface"""
        try:
            self.logger.info(f"Starting web interface on {host}:{port}")
            
            # Configure Flask logging
            if not debug:
                import logging
                log = logging.getLogger('werkzeug')
                log.setLevel(logging.WARNING)
            
            # Run Flask app
            self.app.run(
                host=host,
                port=port,
                debug=debug,
                threaded=True,
                use_reloader=False  # Disable reloader to avoid issues with threading
            )
            
        except Exception as e:
            self.logger.error(f"Failed to start web interface: {e}")
            raise
    
    def run_threaded(self, host='0.0.0.0', port=5000, debug=False):
        """Run the web interface in a separate thread"""
        try:
            web_thread = threading.Thread(
                target=self.run,
                args=(host, port, debug),
                daemon=True
            )
            web_thread.start()
            
            self.logger.info(f"Web interface started in background thread on {host}:{port}")
            return web_thread
            
        except Exception as e:
            self.logger.error(f"Failed to start web interface thread: {e}")
            raise
    
    def shutdown(self):
        """Shutdown the web interface gracefully"""
        try:
            # Remove event listener
            self.challenge_system.remove_event_listener(self._handle_system_event)
            
            # Clear connected clients
            self.connected_clients.clear()
            
            self.logger.info("Web interface shutdown complete")
            
        except Exception as e:
            self.logger.error(f"Error during web interface shutdown: {e}")

