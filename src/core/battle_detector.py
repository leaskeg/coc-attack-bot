import cv2
import numpy as np
from typing import Optional, Tuple, Dict
import pyautogui
from PIL import Image
from .game_state_detector import GameStateDetector


class BattleDetector:
    """Detects battle state and completion"""
    
    def __init__(self, logger, game_state_detector: Optional[GameStateDetector] = None):
        self.logger = logger
        self.game_state_detector = game_state_detector or GameStateDetector(logger=logger)
    
    def is_battle_in_progress(self, game_region: Tuple[int, int, int, int]) -> bool:
        """
        Check if battle is currently active
        
        Detects:
        - Presence of attack UI elements (troop bar visible)
        - Absence of home button (battle overlay active)
        - Game state = battle screen
        
        Returns:
            True if battle is active, False if in menu/home
        """
        try:
            screenshot = pyautogui.screenshot(region=game_region)
            frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            
            if self._detect_troop_bar(frame):
                return True
            
            if not self._detect_home_button(frame):
                return True
            
            return False
        
        except Exception as e:
            self.logger.error(f"Error checking battle state: {e}")
            return False
    
    def is_battle_ended(self, game_region: Tuple[int, int, int, int]) -> bool:
        """
        Check if battle has ended (victory/defeat screen visible)
        
        Detects:
        - Victory screen (green victory text/banner)
        - Defeat screen (red defeat text/banner)
        - Battle results popup
        - Home button re-appearance
        
        Returns:
            True if battle ended, False if still active
        """
        try:
            screenshot = pyautogui.screenshot(region=game_region)
            frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            
            if self._detect_victory_screen(frame):
                self.logger.info("✓ Victory screen detected")
                return True
            
            if self._detect_defeat_screen(frame):
                self.logger.info("✗ Defeat screen detected")
                return True
            
            if self._detect_home_button(frame):
                self.logger.info("🏠 Home button visible - battle ended")
                return True
            
            return False
        
        except Exception as e:
            self.logger.error(f"Error detecting battle end: {e}")
            return False
    
    def get_battle_status(self, game_region: Tuple[int, int, int, int]) -> dict:
        """
        Get detailed battle status
        
        Returns:
            {
                'in_battle': bool,
                'ended': bool,
                'result': 'victory' | 'defeat' | 'in_progress',
                'stars_earned': 0-3,
                'percentage_destroyed': 0-100
            }
        """
        try:
            screenshot = pyautogui.screenshot(region=game_region)
            frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            
            status = {
                'in_battle': self._detect_troop_bar(frame) or not self._detect_home_button(frame),
                'ended': False,
                'result': 'in_progress',
                'stars_earned': 0,
                'percentage_destroyed': 0
            }
            
            # Check for victory
            if self._detect_victory_screen(frame):
                status['ended'] = True
                status['result'] = 'victory'
                status['stars_earned'] = self._detect_stars(frame)
                status['percentage_destroyed'] = self._detect_destruction_percentage(frame)
            
            # Check for defeat
            elif self._detect_defeat_screen(frame):
                status['ended'] = True
                status['result'] = 'defeat'
                status['percentage_destroyed'] = self._detect_destruction_percentage(frame)
            
            return status
        
        except Exception as e:
            self.logger.error(f"Error getting battle status: {e}")
            return {'in_battle': False, 'ended': False, 'result': 'error'}
    
    def _detect_troop_bar(self, frame: np.ndarray) -> bool:
        """Detect if troop deployment bar is visible"""
        try:
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            
            troop_bar_gray_lower = np.array([0, 0, 80])
            troop_bar_gray_upper = np.array([180, 30, 180])
            
            mask = cv2.inRange(hsv, troop_bar_gray_lower, troop_bar_gray_upper)
            
            bottom_section = mask[int(frame.shape[0] * 0.8):, :]
            pixel_count = cv2.countNonZero(bottom_section)
            
            return pixel_count > 1000
        
        except:
            return False
    
    def _detect_home_button(self, frame: np.ndarray) -> bool:
        """Detect if home button is visible (top-left corner UI)"""
        try:
            top_left_region = frame[:int(frame.shape[0] * 0.15), :int(frame.shape[1] * 0.15)]
            
            hsv = cv2.cvtColor(top_left_region, cv2.COLOR_BGR2HSV)
            
            green_lower = np.array([35, 40, 40])
            green_upper = np.array([85, 255, 255])
            
            mask = cv2.inRange(hsv, green_lower, green_upper)
            
            pixel_count = cv2.countNonZero(mask)
            
            return pixel_count > 500
        
        except:
            return False
    
    def _detect_victory_screen(self, frame: np.ndarray) -> bool:
        """Detect victory/success screen (green tones, centered text)"""
        try:
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            
            victory_green_lower = np.array([40, 80, 80])
            victory_green_upper = np.array([90, 255, 255])
            
            mask = cv2.inRange(hsv, victory_green_lower, victory_green_upper)
            
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (10, 10))
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
            
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if len(contours) > 0:
                largest = max(contours, key=cv2.contourArea)
                area = cv2.contourArea(largest)
                
                return area > 50000
            
            return False
        
        except:
            return False
    
    def _detect_defeat_screen(self, frame: np.ndarray) -> bool:
        """Detect defeat screen (red tones, centered text)"""
        try:
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            
            defeat_red_lower = np.array([0, 100, 100])
            defeat_red_upper = np.array([10, 255, 255])
            
            mask = cv2.inRange(hsv, defeat_red_lower, defeat_red_upper)
            
            defeat_red_lower2 = np.array([170, 100, 100])
            defeat_red_upper2 = np.array([180, 255, 255])
            
            mask2 = cv2.inRange(hsv, defeat_red_lower2, defeat_red_upper2)
            mask = cv2.bitwise_or(mask, mask2)
            
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (10, 10))
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
            
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if len(contours) > 0:
                largest = max(contours, key=cv2.contourArea)
                area = cv2.contourArea(largest)
                
                return area > 50000
            
            return False
        
        except:
            return False
    
    def _detect_stars(self, frame: np.ndarray) -> int:
        """Detect number of stars earned (0-3)"""
        try:
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            
            yellow_lower = np.array([15, 100, 100])
            yellow_upper = np.array([35, 255, 255])
            
            mask = cv2.inRange(hsv, yellow_lower, yellow_upper)
            
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            stars = 0
            for contour in contours:
                area = cv2.contourArea(contour)
                if 5000 < area < 50000:
                    stars += 1
            
            return min(stars, 3)
        
        except:
            return 0
    
    def _detect_destruction_percentage(self, frame: np.ndarray) -> int:
        """Estimate destruction percentage from on-screen display"""
        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            center_y = frame.shape[0] // 2
            center_x = frame.shape[1] // 2
            
            roi = gray[center_y - 50:center_y + 50, center_x - 100:center_x + 100]
            
            destroyed_pixels = cv2.countNonZero(cv2.threshold(roi, 200, 255, cv2.THRESH_BINARY)[1])
            total_pixels = roi.shape[0] * roi.shape[1]
            
            percentage = int((destroyed_pixels / total_pixels) * 100)
            return min(max(percentage, 0), 100)
        
        except:
            return 0
    
    def wait_for_battle_end(self, game_region: Tuple[int, int, int, int], 
                           timeout: int = 180, check_interval: float = 0.5) -> bool:
        """
        Wait for battle to end, checking at regular intervals
        
        Args:
            game_region: Game window region
            timeout: Max seconds to wait (default: 3 minutes)
            check_interval: How often to check (default: 0.5s)
        
        Returns:
            True if battle ended within timeout, False if timeout exceeded
        """
        import time
        
        start_time = time.time()
        checks = 0
        
        while time.time() - start_time < timeout:
            checks += 1
            
            status = self.get_battle_status(game_region)
            
            if status['ended']:
                self.logger.info(f"Battle ended after {checks} checks "
                               f"({(time.time() - start_time):.1f}s). "
                               f"Result: {status['result']}")
                return True
            
            if checks % 10 == 0:
                self.logger.debug(f"Battle still in progress... "
                                f"({(time.time() - start_time):.1f}s)")
            
            time.sleep(check_interval)
        
        self.logger.warning(f"Battle did not end within {timeout}s timeout")
        return False
    
    def check_battle_inactivity(self, inactive_threshold: int = 10) -> bool:
        
        return self.game_state_detector.is_battle_inactive()
    
    def monitor_loot_until_inactive(self, game_region: Tuple[int, int, int, int],
                                   inactive_threshold: int = 10,
                                   max_duration: int = 300,
                                   check_interval: float = 0.5) -> Dict:
        
        import time
        
        self.game_state_detector.reset_battle_tracking()
        start_time = time.time()
        checks = 0
        
        while time.time() - start_time < max_duration:
            checks += 1
            
            self.game_state_detector.capture_loot_state()
            
            if self.game_state_detector.is_battle_inactive():
                summary = self.game_state_detector.get_loot_summary()
                self.logger.info(f"Battle inactive (no loot for {inactive_threshold}s). "
                               f"Loot gained: G={summary['total_gained']['gold']}, "
                               f"E={summary['total_gained']['elixir']}, "
                               f"DE={summary['total_gained']['dark_elixir']}")
                return {
                    'inactive': True,
                    'duration': time.time() - start_time,
                    'checks': checks,
                    'summary': summary
                }
            
            if checks % 20 == 0:
                loot = self.game_state_detector.get_current_loot()
                self.logger.debug(f"Battle active. Current loot: G={loot['gold']}, "
                                f"E={loot['elixir']}, DE={loot['dark_elixir']}")
            
            time.sleep(check_interval)
        
        summary = self.game_state_detector.get_loot_summary()
        self.logger.warning(f"Max duration exceeded ({max_duration}s). "
                          f"Loot gained: G={summary['total_gained']['gold']}, "
                          f"E={summary['total_gained']['elixir']}, "
                          f"DE={summary['total_gained']['dark_elixir']}")
        return {
            'inactive': False,
            'duration': time.time() - start_time,
            'checks': checks,
            'summary': summary,
            'timeout': True
        }
    
    def get_game_state_detector(self) -> GameStateDetector:
        
        return self.game_state_detector
