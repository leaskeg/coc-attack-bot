import cv2
import numpy as np
from typing import Optional, Tuple, Dict
import pyautogui
from PIL import Image


class ResourceReader:
    """Resource detection via color analysis and screenshot inspection"""
    
    def __init__(self, logger):
        self.logger = logger
        self.last_resources = {'gold': 0, 'elixir': 0, 'dark_elixir': 0}
    
    def read_resources_from_search_screen(self, game_region: Tuple[int, int, int, int]) -> Dict[str, int]:
        """
        Read Gold, Elixir, Dark Elixir from search/base preview screen
        
        Returns:
            {'gold': 465369, 'elixir': 482487, 'dark_elixir': 6528, 'confidence': 0.85}
        """
        try:
            screenshot = pyautogui.screenshot(region=game_region)
            
            resources = {
                'gold': self._extract_gold(screenshot),
                'elixir': self._extract_elixir(screenshot),
                'dark_elixir': self._extract_dark_elixir(screenshot),
                'confidence': 0.75
            }
            
            self.logger.debug(f"Resources detected: Gold={resources['gold']}, Elixir={resources['elixir']}, DE={resources['dark_elixir']}")
            return resources
        
        except Exception as e:
            self.logger.error(f"Error reading resources: {e}")
            return {'gold': 0, 'elixir': 0, 'dark_elixir': 0, 'confidence': 0.0}
    
    def _extract_gold(self, screenshot: Image.Image) -> int:
        """
        Estimate gold based on gold mine color detection
        Note: Accurate OCR requires Tesseract. This is a fallback color-based estimation.
        """
        frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2HSV)
        
        gold_lower = np.array([15, 80, 120])
        gold_upper = np.array([35, 255, 255])
        
        mask = cv2.inRange(frame, gold_lower, gold_upper)
        
        pixel_count = cv2.countNonZero(mask)
        
        estimated_gold = int(pixel_count * 5)
        self.logger.debug(f"Gold estimation: {pixel_count} pixels → {estimated_gold}")
        
        return estimated_gold
    
    def _extract_elixir(self, screenshot: Image.Image) -> int:
        """
        Estimate elixir based on elixir collector color detection
        Note: Accurate OCR requires Tesseract. This is a fallback color-based estimation.
        """
        frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2HSV)
        
        elixir_lower = np.array([120, 80, 120])
        elixir_upper = np.array([160, 255, 255])
        
        mask = cv2.inRange(frame, elixir_lower, elixir_upper)
        
        pixel_count = cv2.countNonZero(mask)
        
        estimated_elixir = int(pixel_count * 5)
        self.logger.debug(f"Elixir estimation: {pixel_count} pixels → {estimated_elixir}")
        
        return estimated_elixir
    
    def _extract_dark_elixir(self, screenshot: Image.Image) -> int:
        """
        Estimate dark elixir based on dark color detection
        Note: Accurate OCR requires Tesseract. This is a fallback color-based estimation.
        """
        frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2HSV)
        
        dark_lower = np.array([0, 0, 0])
        dark_upper = np.array([180, 100, 80])
        
        mask = cv2.inRange(frame, dark_lower, dark_upper)
        
        pixel_count = cv2.countNonZero(mask)
        
        estimated_de = int(pixel_count * 0.5)
        self.logger.debug(f"Dark Elixir estimation: {pixel_count} pixels → {estimated_de}")
        
        return estimated_de
    
    def detect_dead_base(self, resources: Dict[str, int]) -> bool:
        """
        Classify if base is 'dead' based on resource amounts
        Dead base = low defenses, high loot
        
        Simple heuristic: returns True if total resources meet threshold
        """
        total = resources.get('gold', 0) + resources.get('elixir', 0) + (resources.get('dark_elixir', 0) * 10)
        
        return total > 500000
    
    def should_attack_base(self, resources: Dict[str, int], 
                          min_gold: int = 100000,
                          min_elixir: int = 100000, 
                          min_dark: int = 1000) -> Tuple[bool, str]:
        """
        Determine if base meets attack criteria
        
        Returns: (should_attack: bool, reason: str)
        """
        gold = resources.get('gold', 0)
        elixir = resources.get('elixir', 0)
        dark = resources.get('dark_elixir', 0)
        
        if gold < min_gold:
            return False, f"Gold {gold} < {min_gold}"
        if elixir < min_elixir:
            return False, f"Elixir {elixir} < {min_elixir}"
        if dark < min_dark:
            return False, f"Dark Elixir {dark} < {min_dark}"
        
        return True, "Meets all criteria"
