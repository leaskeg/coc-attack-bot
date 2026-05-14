import pyautogui
import time
import random
from typing import Optional, Tuple, Callable
from .window_manager import WindowManager
from ..utils.logger import Logger
from ..utils.timing import human_move_duration, pixel_distance


class SafeClickExecutor:
    
    def __init__(self, window_manager: WindowManager, logger: Optional[Logger] = None):
        self.window_manager = window_manager
        self.logger = logger or Logger()
        self.max_retries = 3
        self.click_timeout = 5.0
        self.pre_click_validation = True
        self.post_click_validation = False
    
    def safe_click(self, x: int, y: int, button: str = 'left', clicks: int = 1, 
                   interval: float = 0.1, validate_after: Optional[Callable] = None,
                   click_context: str = "") -> bool:
        
        self.logger.debug(f"[CLICK] Initiating safe click at ({x}, {y}) | Context: {click_context}")
        
        if not self._pre_click_validation(x, y):
            self.logger.warning(f"[CLICK ERROR] Pre-click validation failed at ({x}, {y})")
            return False
        
        try:
            self.logger.debug(f"  → Moving mouse to ({x}, {y})")
            self._human_move_to(x, y)
            
            for click_num in range(clicks):
                self.logger.debug(f"  → Executing click {click_num + 1}/{clicks}")
                pyautogui.mouseDown(x, y, button=button)
                time.sleep(random.uniform(0.06, 0.19))
                pyautogui.mouseUp(button=button)
                
                if clicks > 1:
                    time.sleep(interval)
            
            if self.post_click_validation and validate_after:
                self.logger.debug(f"  → Running post-click validation")
                if not self._post_click_validation(x, y, validate_after):
                    self.logger.warning(f"[CLICK ERROR] Post-click validation failed at ({x}, {y})")
                    return False
            
            self.logger.info(f"[CLICK SUCCESS] Clicked at ({x}, {y}) | {click_context}")
            return True
        
        except Exception as e:
            self.logger.error(f"[CLICK ERROR] Click execution failed at ({x}, {y}): {e}", exc_info=True)
            return False
    
    def safe_drag(self, x1: int, y1: int, x2: int, y2: int, duration: float = 1.0,
                  drag_context: str = "") -> bool:
        
        self.logger.debug(f"[DRAG] Initiating safe drag from ({x1}, {y1}) to ({x2}, {y2}) | Context: {drag_context}")
        
        if not self._pre_click_validation(x1, y1) or not self._pre_click_validation(x2, y2):
            self.logger.warning(f"[DRAG ERROR] Drag validation failed from ({x1}, {y1}) to ({x2}, {y2})")
            return False
        
        try:
            self.logger.debug(f"  → Moving mouse to start position ({x1}, {y1})")
            self._human_move_to(x1, y1)
            
            self.logger.debug(f"  → Mouse down at ({x1}, {y1})")
            pyautogui.mouseDown(x1, y1)
            time.sleep(0.1)
            
            self.logger.debug(f"  → Dragging to ({x2}, {y2}) over {duration:.2f}s")
            pyautogui.moveTo(x2, y2, duration=duration)
            time.sleep(random.uniform(0.05, 0.15))
            
            self.logger.debug(f"  → Mouse up")
            pyautogui.mouseUp()
            
            self.logger.info(f"[DRAG SUCCESS] Drag completed: ({x1}, {y1}) → ({x2}, {y2}) | {drag_context}")
            return True
        
        except Exception as e:
            self.logger.error(f"[DRAG ERROR] Drag execution failed: {e}", exc_info=True)
            return False
    
    def safe_hotkey(self, *keys) -> bool:
        
        try:
            hotkey_str = '+'.join(keys)
            self.logger.debug(f"[HOTKEY] Executing hotkey: {hotkey_str}")
            pyautogui.hotkey(*keys)
            self.logger.info(f"[HOTKEY SUCCESS] {hotkey_str}")
            return True
        except Exception as e:
            self.logger.error(f"[HOTKEY ERROR] Hotkey failed: {e}", exc_info=True)
            return False
    
    def _pre_click_validation(self, x: int, y: int) -> bool:
        
        if not self.window_manager.is_coordinate_in_window(x, y):
            x, y = self.window_manager.constrain_to_window(x, y)
            self.logger.debug(f"[VALIDATION] Coordinate constrained: ({x}, {y})")
        
        if not self.window_manager.is_window_focused():
            self.logger.debug("[VALIDATION] Game window not focused, attempting to focus...")
            self.window_manager.focus_game_window()
        
        if not self.window_manager.window_exists():
            self.logger.warning("[VALIDATION] Game window no longer exists")
            return False
        
        return True
    
    def _post_click_validation(self, x: int, y: int, validator: Callable) -> bool:
        
        self.logger.debug(f"[VALIDATION] Starting post-click validation at ({x}, {y})")
        start_time = time.time()
        attempt = 0
        
        while time.time() - start_time < self.click_timeout:
            attempt += 1
            try:
                if validator():
                    self.logger.debug(f"[VALIDATION] Post-click validation succeeded (attempt {attempt})")
                    return True
            except Exception as e:
                self.logger.debug(f"[VALIDATION] Validation check failed (attempt {attempt}): {e}")
            
            time.sleep(0.2)
        
        elapsed = time.time() - start_time
        self.logger.warning(f"[VALIDATION] Post-click validation timeout after {elapsed:.1f}s ({attempt} attempts)")
        return False
    
    def _human_move_to(self, x: int, y: int) -> None:
        
        cx, cy = pyautogui.position()
        dist = pixel_distance(cx, cy, x, y)
        duration = human_move_duration(dist)
        
        self.logger.debug(f"  → Mouse movement: {dist:.0f}px over {duration:.2f}s")
        
        tweens = [pyautogui.easeOutQuad, pyautogui.easeInOutQuad, pyautogui.linear]
        weights = [0.55, 0.35, 0.10]
        tween = random.choices(tweens, weights=weights, k=1)[0]
        
        if dist > 100 and random.random() < 0.08:
            ox = x + random.randint(-9, 9)
            oy = y + random.randint(-9, 9)
            self.logger.debug(f"    (natural movement via intermediate: ({ox}, {oy}))")
            pyautogui.moveTo(ox, oy, duration=duration * 0.82, tween=tween)
            time.sleep(random.uniform(0.02, 0.06))
            pyautogui.moveTo(x, y, duration=random.uniform(0.04, 0.09),
                           tween=pyautogui.easeOutQuad)
        else:
            pyautogui.moveTo(x, y, duration=duration, tween=tween)
