import pyautogui
import cv2
import numpy as np
from typing import Dict, Optional, Tuple, List
from PIL import Image
from datetime import datetime, timedelta
from ..utils.logger import Logger


class LootState:
    def __init__(self):
        self.gold = 0
        self.elixir = 0
        self.dark_elixir = 0
        self.timestamp = 0.0
        self.screenshot = None


class GameStateDetector:
    
    def __init__(self, logger: Optional[Logger] = None, inactive_timeout: int = 10):
        self.logger = logger or Logger()
        self.inactive_timeout = inactive_timeout
        self.loot_history: List[LootState] = []
        self.last_loot_state: Optional[LootState] = None
        self.last_state_check_time = 0
        self.battle_start_time = 0
        self.loot_check_interval = 1
        self.gold_color_range = ((180, 180, 50), (220, 220, 120))
        self.elixir_color_range = ((100, 150, 100), (140, 200, 140))
        self.dark_elixir_color_range = ((150, 100, 150), (200, 150, 200))
    
    def reset_battle_tracking(self) -> None:
        
        self.loot_history.clear()
        self.last_loot_state = None
        self.battle_start_time = datetime.now()
    
    def capture_loot_state(self) -> Optional[LootState]:
        
        current_time = datetime.now()
        
        if self.last_loot_state and (current_time - self.last_state_check_time).total_seconds() < self.loot_check_interval:
            return self.last_loot_state
        
        try:
            screenshot = pyautogui.screenshot()
            state = LootState()
            state.screenshot = screenshot
            state.timestamp = (current_time - self.battle_start_time).total_seconds()
            
            gold, elixir, dark = self._extract_loot_from_screenshot(screenshot)
            state.gold = gold
            state.elixir = elixir
            state.dark_elixir = dark
            
            self.loot_history.append(state)
            self.last_loot_state = state
            self.last_state_check_time = current_time
            
            self.logger.debug(f"Loot state captured: G={gold}, E={elixir}, DE={dark} @ {state.timestamp:.1f}s")
            return state
        
        except Exception as e:
            self.logger.error(f"Failed to capture loot state: {e}")
            return None
    
    def get_loot_change(self) -> Dict[str, int]:
        
        if len(self.loot_history) < 2:
            return {'gold': 0, 'elixir': 0, 'dark_elixir': 0}
        
        current = self.loot_history[-1]
        previous = self.loot_history[-2]
        
        return {
            'gold': current.gold - previous.gold,
            'elixir': current.elixir - previous.elixir,
            'dark_elixir': current.dark_elixir - previous.dark_elixir
        }
    
    def has_loot_changed(self, threshold: int = 0) -> bool:
        
        change = self.get_loot_change()
        total_change = abs(change['gold']) + abs(change['elixir']) + abs(change['dark_elixir'])
        return total_change > threshold
    
    def get_inactive_duration(self) -> float:
        
        if not self.loot_history:
            return 0.0
        
        current_time = (datetime.now() - self.battle_start_time).total_seconds()
        
        for i in range(len(self.loot_history) - 1, -1, -1):
            if self.has_loot_changed_since(i):
                return current_time - self.loot_history[i].timestamp
        
        return current_time
    
    def has_loot_changed_since(self, history_index: int, threshold: int = 0) -> bool:
        
        if history_index < 0 or history_index >= len(self.loot_history):
            return False
        
        if history_index == 0:
            return True
        
        current = self.loot_history[-1]
        previous = self.loot_history[history_index]
        
        change_gold = current.gold - previous.gold
        change_elixir = current.elixir - previous.elixir
        change_dark = current.dark_elixir - previous.dark_elixir
        
        total_change = abs(change_gold) + abs(change_elixir) + abs(change_dark)
        return total_change > threshold
    
    def is_battle_inactive(self) -> bool:
        
        inactive_duration = self.get_inactive_duration()
        is_inactive = inactive_duration >= self.inactive_timeout
        
        if is_inactive:
            self.logger.info(f"Battle inactive for {inactive_duration:.1f}s (threshold: {self.inactive_timeout}s)")
        
        return is_inactive
    
    def _extract_loot_from_screenshot(self, screenshot: Image.Image) -> Tuple[int, int, int]:
        
        try:
            frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            height, width = frame.shape[:2]
            
            resource_region_height = int(height * 0.15)
            resource_region = frame[:resource_region_height, :]
            
            gold = self._detect_resource_value(resource_region, self.gold_color_range, 'GOLD')
            elixir = self._detect_resource_value(resource_region, self.elixir_color_range, 'ELIXIR')
            dark_elixir = self._detect_resource_value(resource_region, self.dark_elixir_color_range, 'DARK ELIXIR')
            
            return gold, elixir, dark_elixir
        
        except Exception as e:
            self.logger.error(f"Loot extraction failed: {e}")
            return 0, 0, 0
    
    def _detect_resource_value(self, frame: np.ndarray, color_range: Tuple, resource_name: str) -> int:
        
        lower_color, upper_color = color_range
        lower_hsv = cv2.cvtColor(np.uint8([[lower_color]]), cv2.COLOR_RGB2HSV)[0][0]
        upper_hsv = cv2.cvtColor(np.uint8([[upper_color]]), cv2.COLOR_RGB2HSV)[0][0]
        
        frame_hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(frame_hsv, lower_hsv, upper_hsv)
        
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if contours:
            largest_contour = max(contours, key=cv2.contourArea)
            area = cv2.contourArea(largest_contour)
            return int(area * 10)
        
        return 0
    
    def get_current_loot(self) -> Dict[str, int]:
        
        if not self.last_loot_state:
            self.capture_loot_state()
        
        if not self.last_loot_state:
            return {'gold': 0, 'elixir': 0, 'dark_elixir': 0}
        
        return {
            'gold': self.last_loot_state.gold,
            'elixir': self.last_loot_state.elixir,
            'dark_elixir': self.last_loot_state.dark_elixir
        }
    
    def get_loot_summary(self) -> Dict:
        
        if not self.loot_history:
            return {
                'current': {'gold': 0, 'elixir': 0, 'dark_elixir': 0},
                'total_gained': {'gold': 0, 'elixir': 0, 'dark_elixir': 0},
                'duration': 0,
                'inactive_duration': 0
            }
        
        first_state = self.loot_history[0]
        last_state = self.loot_history[-1]
        
        return {
            'current': self.get_current_loot(),
            'total_gained': {
                'gold': last_state.gold - first_state.gold,
                'elixir': last_state.elixir - first_state.elixir,
                'dark_elixir': last_state.dark_elixir - first_state.dark_elixir
            },
            'duration': last_state.timestamp,
            'inactive_duration': self.get_inactive_duration(),
            'samples': len(self.loot_history)
        }
