import os
import base64
import json
import requests
import time
import re
from typing import Dict, Optional, Tuple
from PIL import Image
import io

class AIAnalyzer:
    
    def __init__(self, api_key: str, logger):
        self.api_key = api_key
        self.logger = logger
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
        
        self.analysis_prompt = """
Analyze this screenshot and provide:
1. Resource amounts - estimate the visible amounts
2. Difficulty assessment (Easy/Medium/Hard)
3. Recommendation (PROCEED or SKIP)

Respond in this exact JSON format:
{
    "resources": {
        "primary": estimated_primary_amount,
        "secondary": estimated_secondary_amount,
        "tertiary": estimated_tertiary_amount
    },
    "difficulty": "Easy/Medium/Hard",
    "recommendation": "PROCEED/SKIP",
    "reasoning": "Brief explanation of decision"
}
"""
    
    def analyze_base(self, screenshot_path: str, min_gold: int = 300000, 
                    min_elixir: int = 300000, min_dark: int = 2000) -> Dict:
        """
        Analyze enemy base screenshot using Google Gemini
        
        Args:
            screenshot_path: Path to screenshot file
            min_gold: Minimum gold requirement
            min_elixir: Minimum elixir requirement  
            min_dark: Minimum dark elixir requirement
            
        Returns:
            Dict with analysis results and attack recommendation
        """
        try:
            self.logger.info(f"🤖 Analyzing base with AI: {screenshot_path}")
            
            # Encode image to base64
            image_data = self._encode_image(screenshot_path)
            if not image_data:
                return self._create_error_response("Failed to encode image")
            
            # Create analysis prompt with requirements
            prompt = self._create_analysis_prompt(min_gold, min_elixir, min_dark)
            
            # Send request to Gemini
            response = self._send_gemini_request(image_data, prompt)
            
            if response:
                self.logger.info(f"✅ AI Analysis: {response['recommendation']} - {response['reasoning']}")
                return response
            else:
                return self._create_error_response("Failed to get AI response")
                
        except Exception as e:
            self.logger.error(f"AI analysis error: {e}")
            return self._create_error_response(f"Analysis error: {e}")
    
    def _encode_image(self, image_path: str) -> Optional[str]:
        """Encode image to base64 for Gemini API"""
        try:
            with open(image_path, 'rb') as image_file:
                img = Image.open(image_file)
                
                max_dimension = 1024
                if img.width > max_dimension or img.height > max_dimension:
                    ratio = min(max_dimension / img.width, max_dimension / img.height)
                    new_width = int(img.width * ratio)
                    new_height = int(img.height * ratio)
                    img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                img_byte_arr = io.BytesIO()
                img.save(img_byte_arr, format='PNG')
                img_byte_arr = img_byte_arr.getvalue()
                
                return base64.b64encode(img_byte_arr).decode('utf-8')
                
        except Exception as e:
            self.logger.error(f"Image encoding error: {e}")
            return None
    
    def _create_analysis_prompt(self, min_gold: int, min_elixir: int, min_dark: int) -> str:
        """Create analysis prompt with current requirements"""
        return f"""
You are an expert Clash of Clans player analyzing enemy bases for attack decisions.

CRITICAL: You must read the EXACT loot numbers displayed in the top-left area of the screen.

Current loot requirements:
- Minimum Gold: {min_gold:,}
- Minimum Elixir: {min_elixir:,}  
- Minimum Dark Elixir: {min_dark:,}

INSTRUCTIONS:
1. Look at the "Available Loot:" section in the top-left corner of the screenshot
2. Read the EXACT numbers next to the gold coin (yellow), elixir drop (pink), and dark elixir drop (black) icons
3. Identify the Town Hall level by looking at the Town Hall building
4. Compare loot numbers to minimum requirements above
5. Make recommendation based on loot AND Town Hall level

LOOT READING RULES:
- Gold is shown next to a yellow coin icon
- Elixir is shown next to a pink/purple drop icon  
- Dark Elixir is shown next to a black drop icon
- Numbers may have spaces (e.g. "123 456" = 123,456)
- Be extremely careful reading the digits

TOWN HALL RULES:
- Identify the Town Hall level by looking at the Town Hall building design
- Compare detected TH level to the maximum allowed (will be enforced by the bot)
- Look at the Town Hall building design to identify the level (currently max is TH18)

DECISION CRITERIA:
- ATTACK only if: ALL loot types meet requirements
- SKIP if: ANY loot type is below requirements
- Do NOT consider base difficulty - focus ONLY on loot amounts and Town Hall level
- Note: The bot will handle Town Hall level filtering based on configured maximum

Examples:
- Gold: 19,015 (need 500,000) → SKIP (loot too low)
- Town Hall 18 with good loot → ATTACK (bot will decide if TH is acceptable)
- Town Hall 15 with good loot → ATTACK (if loot meets requirements)
- Town Hall 12 with good loot → ATTACK (if loot meets requirements)

Respond in this exact JSON format (use ONLY numbers, NO commas or spaces in numbers):
{{
    "loot": {{
        "gold": 0,
        "elixir": 0,
        "dark_elixir": 0
    }},
    "townhall_level": 0,
    "difficulty": "Easy/Medium/Hard",
    "recommendation": "ATTACK/SKIP",
    "reasoning": "Brief explanation"
}}

Replace the 0 values with actual numbers (no commas, no spaces). Example: use 500000 not 500,000
"""
    
    def _send_gemini_request(self, image_data: str, prompt: str) -> Optional[Dict]:
        """Send request to Google Gemini API with retry logic"""
        max_retries = 3
        base_delay = 2
        
        for attempt in range(max_retries):
            try:
                headers = {
                    'Content-Type': 'application/json',
                    'x-goog-api-key': self.api_key,
                }
                
                payload = {
                    "contents": [{
                        "parts": [
                            {"text": prompt},
                            {
                                "inline_data": {
                                    "mime_type": "image/png",
                                    "data": image_data
                                }
                            }
                        ]
                    }],
                    "generationConfig": {
                        "temperature": 0.1,
                        "topK": 1,
                        "topP": 1,
                        "maxOutputTokens": 1024,
                    }
                }
                
                url = self.base_url
                response = requests.post(url, headers=headers, json=payload, timeout=30)
                
                if response.status_code == 200:
                    result = response.json()
                    
                    if 'candidates' in result and len(result['candidates']) > 0:
                        content = result['candidates'][0]['content']['parts'][0]['text']
                        
                        try:
                            content = content.strip()
                            if content.startswith('```json'):
                                content = content[7:]
                            if content.startswith('```'):
                                content = content[3:]
                            if content.endswith('```'):
                                content = content[:-3]
                            content = content.strip()
                            
                            try:
                                analysis = json.loads(content)
                            except json.JSONDecodeError:
                                content = re.sub(r':\s*(\d+),(\d+)', r': \1\2', content)
                                analysis = json.loads(content)
                            
                            return analysis
                            
                        except json.JSONDecodeError as e:
                            self.logger.error(f"Failed to parse AI response: {e}")
                            self.logger.debug(f"Response was: {content}")
                            return None
                    else:
                        self.logger.error("No candidates in response")
                        return None
                
                elif response.status_code in [429, 500, 502, 503, 504]:
                    if attempt < max_retries - 1:
                        wait_time = base_delay * (2 ** attempt)
                        self.logger.warning(f"API error {response.status_code}, retrying in {wait_time}s... (attempt {attempt + 1}/{max_retries})")
                        time.sleep(wait_time)
                        continue
                    else:
                        self.logger.error(f"API error {response.status_code} after retries")
                        return None
                else:
                    self.logger.error(f"API error: {response.status_code}")
                    return None
                    
            except requests.exceptions.Timeout:
                if attempt < max_retries - 1:
                    wait_time = base_delay * (2 ** attempt)
                    self.logger.warning(f"Timeout, retrying in {wait_time}s... (attempt {attempt + 1}/{max_retries})")
                    time.sleep(wait_time)
                    continue
                else:
                    self.logger.error(f"Timeout after retries")
                    return None
                    
            except Exception as e:
                if attempt < max_retries - 1:
                    wait_time = base_delay * (2 ** attempt)
                    self.logger.warning(f"Error: {e}, retrying in {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                else:
                    self.logger.error(f"Request failed: {e}")
                    return None
        
        return None
    
    def _create_error_response(self, error_msg: str) -> Dict:
        """Create error response with SKIP recommendation"""
        return {
            "loot": {"gold": 0, "elixir": 0, "dark_elixir": 0},
            "townhall_level": 0,
            "difficulty": "Unknown",
            "recommendation": "SKIP",
            "reasoning": f"Error: {error_msg}",
            "error": True
        }
    
    def test_connection(self) -> bool:
        """Test connection to Gemini API"""
        try:
            if not self.api_key:
                self.logger.error("❌ API key is empty")
                return False
            
            headers = {
                'Content-Type': 'application/json',
                'x-goog-api-key': self.api_key,
            }
            payload = {
                "contents": [{"parts": [{"text": "Hello, respond with 'OK'"}]}],
                "generationConfig": {"maxOutputTokens": 10}
            }
            
            url = self.base_url
            response = requests.post(url, headers=headers, json=payload, timeout=10)
            
            if response.status_code == 200:
                self.logger.info("✅ Gemini API connection successful")
                return True
            elif response.status_code == 400:
                self.logger.error(f"❌ Gemini API test failed: 400 Bad Request - Check API key format")
                try:
                    error_detail = response.json()
                    self.logger.error(f"   Details: {error_detail}")
                except:
                    pass
                return False
            elif response.status_code == 401:
                self.logger.error(f"❌ Gemini API test failed: 401 Unauthorized - API key may be invalid")
                return False
            elif response.status_code == 403:
                self.logger.error(f"❌ Gemini API test failed: 403 Forbidden - Check API permissions")
                return False
            else:
                self.logger.error(f"❌ Gemini API test failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Gemini API test error: {e}")
            return False