"""
Advanced AI Vision capabilities for desktop automation
Extends the basic vision analyzer with specialized automation functions
"""

import json
import time
import base64
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass

from vision_analyzer import VisionAnalyzer
from logger_config import setup_logger

@dataclass
class DetectedElement:
    element_type: str
    description: str
    x: int
    y: int
    width: int
    height: int
    confidence: float
    clickable: bool
    text_content: Optional[str] = None

@dataclass
class UIState:
    window_title: str
    application_name: str
    elements: List[DetectedElement]
    dialog_present: bool
    error_present: bool
    state_description: str
    confidence: float

class AIVision:
    """
    Advanced AI vision system for intelligent desktop automation
    Provides higher-level vision capabilities for automation tasks
    """
    
    def __init__(self):
        self.logger = setup_logger(__name__)
        self.vision_analyzer = VisionAnalyzer()
        
        # Cache for frequent operations
        self.element_cache = {}
        self.cache_ttl = 5  # seconds
        
        self.logger.info("AI Vision system initialized")
    
    def analyze_desktop_state(self, screenshot_b64: str) -> UIState:
        """
        Comprehensive analysis of current desktop state
        """
        try:
            prompt = """
            Analyze this desktop screenshot comprehensively and provide a detailed UI state analysis.
            
            Return JSON with:
            {
                "window_title": "main window title if visible",
                "application_name": "primary application name",
                "elements": [
                    {
                        "element_type": "button|menu|window|dialog|textbox|icon|label",
                        "description": "clear description of the element",
                        "x": center_x_coordinate,
                        "y": center_y_coordinate,
                        "width": estimated_width,
                        "height": estimated_height,
                        "confidence": 0.0-1.0,
                        "clickable": true/false,
                        "text_content": "visible text if any"
                    }
                ],
                "dialog_present": true/false,
                "error_present": true/false,
                "state_description": "overall description of what's visible",
                "confidence": 0.0-1.0
            }
            
            Focus on interactive elements and provide accurate coordinates.
            """
            
            response = self.vision_analyzer.analyze_screenshot_general(screenshot_b64, prompt)
            
            # Parse response into UIState object
            elements = []
            for elem_data in response.get('elements', []):
                element = DetectedElement(
                    element_type=elem_data.get('element_type', 'unknown'),
                    description=elem_data.get('description', ''),
                    x=elem_data.get('x', 0),
                    y=elem_data.get('y', 0),
                    width=elem_data.get('width', 0),
                    height=elem_data.get('height', 0),
                    confidence=elem_data.get('confidence', 0.0),
                    clickable=elem_data.get('clickable', False),
                    text_content=elem_data.get('text_content')
                )
                elements.append(element)
            
            ui_state = UIState(
                window_title=response.get('window_title', ''),
                application_name=response.get('application_name', ''),
                elements=elements,
                dialog_present=response.get('dialog_present', False),
                error_present=response.get('error_present', False),
                state_description=response.get('state_description', ''),
                confidence=response.get('confidence', 0.0)
            )
            
            self.logger.debug(f"Desktop state analyzed: {ui_state.application_name}, {len(ui_state.elements)} elements")
            return ui_state
            
        except Exception as e:
            self.logger.error(f"Failed to analyze desktop state: {e}")
            return UIState("", "", [], False, False, "Analysis failed", 0.0)
    
    def find_element_smart(self, screenshot_b64: str, element_description: str, 
                          element_type: Optional[str] = None) -> Optional[DetectedElement]:
        """
        Smart element detection with caching and confidence scoring
        """
        try:
            cache_key = f"{element_description}_{element_type}_{hash(screenshot_b64[:100])}"
            
            # Check cache
            if cache_key in self.element_cache:
                cached_result, timestamp = self.element_cache[cache_key]
                if time.time() - timestamp < self.cache_ttl:
                    return cached_result
            
            type_filter = f" of type '{element_type}'" if element_type else ""
            
            prompt = f"""
            Find the UI element described as: "{element_description}"{type_filter}
            
            Return JSON with:
            {{
                "found": true/false,
                "element": {{
                    "element_type": "detected type",
                    "description": "what you found",
                    "x": center_x_coordinate,
                    "y": center_y_coordinate,
                    "width": estimated_width,
                    "height": estimated_height,
                    "confidence": 0.0-1.0,
                    "clickable": true/false,
                    "text_content": "visible text if any"
                }},
                "reasoning": "why you think this is the correct element",
                "alternatives": ["other possible matches if any"]
            }}
            
            Be precise with coordinates and only return high-confidence matches.
            """
            
            response = self.vision_analyzer.analyze_screenshot_general(screenshot_b64, prompt)
            
            if response.get('found', False):
                elem_data = response.get('element', {})
                element = DetectedElement(
                    element_type=elem_data.get('element_type', 'unknown'),
                    description=elem_data.get('description', element_description),
                    x=elem_data.get('x', 0),
                    y=elem_data.get('y', 0),
                    width=elem_data.get('width', 0),
                    height=elem_data.get('height', 0),
                    confidence=elem_data.get('confidence', 0.0),
                    clickable=elem_data.get('clickable', True),
                    text_content=elem_data.get('text_content')
                )
                
                # Cache the result
                self.element_cache[cache_key] = (element, time.time())
                
                self.logger.debug(f"Found element '{element_description}' at ({element.x}, {element.y}) with confidence {element.confidence}")
                return element
            else:
                # Cache negative result
                self.element_cache[cache_key] = (None, time.time())
                self.logger.debug(f"Element '{element_description}' not found")
                return None
                
        except Exception as e:
            self.logger.error(f"Smart element detection failed: {e}")
            return None
    
    def detect_application_errors(self, screenshot_b64: str) -> Dict[str, Any]:
        """
        Detect error conditions, dialogs, and problematic states
        """
        try:
            prompt = """
            Analyze this screenshot for error conditions, problems, or unexpected states.
            
            Return JSON with:
            {
                "has_error": true/false,
                "error_type": "dialog|crash|hang|permission|network|file|unknown",
                "error_message": "visible error text if any",
                "severity": "low|medium|high|critical",
                "suggested_action": "ok|cancel|retry|close|restart|ignore",
                "dialog_buttons": ["list of visible dialog buttons"],
                "recovery_possible": true/false,
                "confidence": 0.0-1.0,
                "description": "detailed description of the error state"
            }
            
            Look for error dialogs, crash reports, unresponsive applications, permission requests, etc.
            """
            
            response = self.vision_analyzer.analyze_screenshot_general(screenshot_b64, prompt)
            
            if response.get('has_error', False):
                self.logger.warning(f"Error detected: {response.get('error_type', 'unknown')} - {response.get('description', '')}")
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error detection failed: {e}")
            return {"has_error": False, "confidence": 0.0}
    
    def guide_next_action(self, screenshot_b64: str, goal: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Provide intelligent guidance for the next automation action
        """
        try:
            context_info = ""
            if context:
                context_info = f"\nContext: {json.dumps(context, indent=2)}"
            
            prompt = f"""
            Analyze this screenshot and provide guidance for achieving the goal: "{goal}"
            {context_info}
            
            Return JSON with:
            {{
                "action_type": "click|type|key_press|scroll|wait|navigate",
                "target_element": "description of element to interact with",
                "target_coordinates": {{"x": coordinate, "y": coordinate}},
                "action_details": "specific text to type or key to press",
                "reasoning": "why this action is recommended",
                "confidence": 0.0-1.0,
                "estimated_success": 0.0-1.0,
                "alternative_actions": [
                    {{"action": "alternative approach", "confidence": 0.0-1.0}}
                ],
                "warnings": ["potential issues or risks"],
                "prerequisites": ["conditions that should be met first"]
            }}
            
            Consider the current state and provide the most logical next step.
            """
            
            response = self.vision_analyzer.analyze_screenshot_general(screenshot_b64, prompt)
            
            action_type = response.get('action_type', 'wait')
            confidence = response.get('confidence', 0.0)
            
            self.logger.info(f"Guided action: {action_type} (confidence: {confidence:.2f})")
            
            return response
            
        except Exception as e:
            self.logger.error(f"Action guidance failed: {e}")
            return {
                "action_type": "wait",
                "reasoning": f"Error in guidance: {e}",
                "confidence": 0.0
            }
    
    def verify_action_result(self, before_screenshot_b64: str, after_screenshot_b64: str, 
                           intended_action: str) -> Dict[str, Any]:
        """
        Verify if an action had the intended effect by comparing before/after screenshots
        """
        try:
            prompt = f"""
            Compare these before and after screenshots to verify if the intended action succeeded.
            Intended action: "{intended_action}"
            
            Return JSON with:
            {{
                "action_succeeded": true/false,
                "changes_detected": true/false,
                "change_description": "what changed between the screenshots",
                "success_indicators": ["signs that action worked"],
                "failure_indicators": ["signs that action failed"],
                "confidence": 0.0-1.0,
                "needs_retry": true/false,
                "suggested_next_action": "what to do next"
            }}
            
            Look for visual changes that indicate the action was successful.
            """
            
            # For now, analyze the after screenshot (multi-image comparison would need special handling)
            response = self.vision_analyzer.analyze_screenshot_general(after_screenshot_b64, prompt)
            
            success = response.get('action_succeeded', False)
            confidence = response.get('confidence', 0.0)
            
            self.logger.info(f"Action verification: {success} (confidence: {confidence:.2f})")
            
            return response
            
        except Exception as e:
            self.logger.error(f"Action verification failed: {e}")
            return {
                "action_succeeded": False,
                "confidence": 0.0,
                "suggested_next_action": "retry"
            }
    
    def extract_text_content(self, screenshot_b64: str, region: Optional[Tuple[int, int, int, int]] = None) -> Dict[str, Any]:
        """
        Extract and structure text content from screenshot
        """
        try:
            region_info = ""
            if region:
                x, y, width, height = region
                region_info = f"\nFocus on the region from ({x}, {y}) with size {width}x{height}"
            
            prompt = f"""
            Extract and analyze all visible text content from this screenshot.
            {region_info}
            
            Return JSON with:
            {{
                "text_elements": [
                    {{
                        "text": "extracted text",
                        "x": approximate_x_coordinate,
                        "y": approximate_y_coordinate,
                        "font_size": "small|medium|large",
                        "element_type": "title|button|label|menu|input|error|info",
                        "confidence": 0.0-1.0
                    }}
                ],
                "structured_content": {{
                    "titles": ["main titles/headings"],
                    "buttons": ["button labels"],
                    "labels": ["form labels"],
                    "errors": ["error messages"],
                    "info": ["informational text"]
                }},
                "overall_confidence": 0.0-1.0
            }}
            
            Be thorough in extracting all readable text.
            """
            
            response = self.vision_analyzer.analyze_screenshot_general(screenshot_b64, prompt)
            
            text_count = len(response.get('text_elements', []))
            self.logger.debug(f"Extracted {text_count} text elements")
            
            return response
            
        except Exception as e:
            self.logger.error(f"Text extraction failed: {e}")
            return {"text_elements": [], "structured_content": {}, "overall_confidence": 0.0}
    
    def detect_loading_states(self, screenshot_b64: str) -> Dict[str, Any]:
        """
        Detect loading indicators, progress bars, and wait states
        """
        try:
            prompt = """
            Analyze this screenshot for loading indicators and wait states.
            
            Return JSON with:
            {
                "is_loading": true/false,
                "loading_indicators": [
                    {
                        "type": "spinner|progress_bar|throbber|dialog|text",
                        "description": "what loading indicator is visible",
                        "progress_percent": 0-100,
                        "x": coordinate,
                        "y": coordinate
                    }
                ],
                "estimated_completion_time": "seconds estimate or 'unknown'",
                "can_interact": true/false,
                "loading_text": "any visible loading message",
                "confidence": 0.0-1.0
            }
            
            Look for spinners, progress bars, "Loading..." text, disabled interfaces, etc.
            """
            
            response = self.vision_analyzer.analyze_screenshot_general(screenshot_b64, prompt)
            
            is_loading = response.get('is_loading', False)
            if is_loading:
                self.logger.debug("Loading state detected")
            
            return response
            
        except Exception as e:
            self.logger.error(f"Loading state detection failed: {e}")
            return {"is_loading": False, "confidence": 0.0}
    
    def analyze_form_fields(self, screenshot_b64: str) -> Dict[str, Any]:
        """
        Analyze and identify form fields and their states
        """
        try:
            prompt = """
            Identify and analyze all form fields in this screenshot.
            
            Return JSON with:
            {
                "form_fields": [
                    {
                        "field_type": "textbox|dropdown|checkbox|radio|button|file",
                        "label": "field label if visible",
                        "placeholder": "placeholder text if any",
                        "current_value": "current content if visible",
                        "required": true/false,
                        "enabled": true/false,
                        "x": center_x_coordinate,
                        "y": center_y_coordinate,
                        "width": estimated_width,
                        "height": estimated_height
                    }
                ],
                "form_state": "empty|partially_filled|complete|invalid",
                "submit_button": {"x": coord, "y": coord, "enabled": true/false},
                "validation_errors": ["visible error messages"],
                "confidence": 0.0-1.0
            }
            
            Focus on interactive form elements and their current states.
            """
            
            response = self.vision_analyzer.analyze_screenshot_general(screenshot_b64, prompt)
            
            field_count = len(response.get('form_fields', []))
            self.logger.debug(f"Analyzed {field_count} form fields")
            
            return response
            
        except Exception as e:
            self.logger.error(f"Form analysis failed: {e}")
            return {"form_fields": [], "confidence": 0.0}
    
    def clear_cache(self):
        """Clear the element detection cache"""
        self.element_cache.clear()
        self.logger.debug("Vision cache cleared")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics"""
        return {
            "cache_size": len(self.element_cache),
            "cache_ttl": self.cache_ttl
        }

