"""
AI Vision analyzer using OpenAI's GPT-4o for screenshot analysis
"""

import json
import os
from openai import OpenAI
from logger_config import setup_logger

class VisionAnalyzer:
    def __init__(self):
        self.logger = setup_logger(__name__)
        
        # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
        # do not change this unless explicitly requested by the user
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = "gpt-4o"
        
        self.logger.info("Vision analyzer initialized with GPT-4o")
    
    def analyze_screenshot_for_coordinates(self, screenshot_b64, prompt):
        """Analyze screenshot to find specific element coordinates"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/png;base64,{screenshot_b64}"}
                            }
                        ]
                    }
                ],
                response_format={"type": "json_object"},
                max_tokens=500
            )
            
            result = json.loads(response.choices[0].message.content)
            self.logger.debug(f"Vision API coordinate response: {result}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error analyzing screenshot for coordinates: {e}")
            return {"found": False, "confidence": 0.0}
    
    def analyze_screenshot_general(self, screenshot_b64, prompt):
        """General screenshot analysis"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/png;base64,{screenshot_b64}"}
                            }
                        ]
                    }
                ],
                response_format={"type": "json_object"},
                max_tokens=1000
            )
            
            result = json.loads(response.choices[0].message.content)
            self.logger.debug(f"Vision API general response: {result}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error in general screenshot analysis: {e}")
            return {"error": str(e)}
    
    def identify_ui_elements(self, screenshot_b64):
        """Identify all interactive UI elements in a screenshot"""
        prompt = """
        Analyze this desktop screenshot and identify all interactive UI elements.
        
        Return a JSON array of elements with this structure:
        {
            "elements": [
                {
                    "type": "button|menu|textbox|window|icon",
                    "description": "descriptive text",
                    "x": center_x_coordinate,
                    "y": center_y_coordinate,
                    "confidence": 0.0-1.0
                }
            ]
        }
        
        Focus on clearly visible and clickable elements.
        """
        
        return self.analyze_screenshot_general(screenshot_b64, prompt)
    
    def detect_application_state(self, screenshot_b64, application_name):
        """Detect if a specific application is running and its state"""
        prompt = f"""
        Analyze this desktop screenshot to detect the state of {application_name}.
        
        Return JSON with:
        {{
            "application_running": true/false,
            "application_state": "loading|main_window|dialog|minimized|not_found",
            "window_title": "detected window title if any",
            "confidence": 0.0-1.0,
            "description": "what you see related to this application"
        }}
        """
        
        return self.analyze_screenshot_general(screenshot_b64, prompt)
    
    def guide_navigation_step(self, screenshot_b64, goal):
        """Provide guidance for the next navigation step to reach a goal"""
        prompt = f"""
        Analyze this desktop screenshot and provide guidance for the next step to accomplish: "{goal}"
        
        Return JSON with:
        {{
            "next_action": "click|type|key_press|wait",
            "target_description": "description of what to interact with",
            "action_details": "specific text to type or key to press if applicable",
            "confidence": 0.0-1.0,
            "reasoning": "explanation of why this action is recommended"
        }}
        """
        
        return self.analyze_screenshot_general(screenshot_b64, prompt)
