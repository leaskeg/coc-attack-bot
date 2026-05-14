import win32gui
import win32con
import win32api
import pyautogui
import time
from typing import Optional, Tuple
from ..utils.logger import Logger


class WindowManager:
    
    def __init__(self, logger: Optional[Logger] = None):
        self.logger = logger or Logger()
        self.game_window_handle = None
        self.game_window_bounds = None
        self.emulator_keywords = ['clash of clans', 'bluestacks', 'nox', 'ldplayer', 'memu', 'gameloop', 'andy']
        self.refresh_interval = 5
        self.last_refresh_time = 0
    
    def find_and_lock_game_window(self, force_refresh: bool = False) -> Optional[Tuple[int, int, int, int]]:
        current_time = time.time()
        if not force_refresh and self.game_window_bounds and (current_time - self.last_refresh_time) < self.refresh_interval:
            return self.game_window_bounds
        
        def enum_windows_callback(hwnd, windows):
            if not win32gui.IsWindowVisible(hwnd):
                return
            
            title = win32gui.GetWindowText(hwnd)
            if not any(keyword.lower() in title.lower() for keyword in self.emulator_keywords):
                return
            
            try:
                rect = win32gui.GetWindowRect(hwnd)
                x, y, right, bottom = rect
                width = right - x
                height = bottom - y
                
                if width > 100 and height > 100:
                    windows.append((hwnd, title, (x, y, width, height)))
            except:
                pass
        
        windows = []
        win32gui.EnumWindows(enum_windows_callback, windows)
        
        if windows:
            hwnd, title, bounds = windows[0]
            self.game_window_handle = hwnd
            self.game_window_bounds = bounds
            self.last_refresh_time = current_time
            
            x, y, w, h = bounds
            self.logger.debug(f"Game window locked: {title} [{x}, {y}, {w}x{h}]")
            return bounds
        
        self.logger.warning("Game window not found")
        return None
    
    def is_window_focused(self) -> bool:
        if not self.game_window_handle:
            return True
        
        try:
            fg_hwnd = win32gui.GetForegroundWindow()
            return fg_hwnd == self.game_window_handle
        except:
            return True
    
    def focus_game_window(self) -> bool:
        if not self.game_window_handle:
            return False
        
        try:
            win32gui.ShowWindow(self.game_window_handle, win32con.SW_NORMAL)
            win32gui.SetForegroundWindow(self.game_window_handle)
            time.sleep(0.3)
            return True
        except Exception as e:
            self.logger.error(f"Failed to focus window: {e}")
            return False
    
    def is_coordinate_in_window(self, x: int, y: int) -> bool:
        if not self.game_window_bounds:
            self.find_and_lock_game_window(force_refresh=True)
        
        if not self.game_window_bounds:
            return False
        
        wx, wy, ww, wh = self.game_window_bounds
        return wx <= x < (wx + ww) and wy <= y < (wy + wh)
    
    def constrain_to_window(self, x: int, y: int) -> Tuple[int, int]:
        if not self.game_window_bounds:
            return (x, y)
        
        wx, wy, ww, wh = self.game_window_bounds
        x = max(wx, min(x, wx + ww - 1))
        y = max(wy, min(y, wy + wh - 1))
        return (x, y)
    
    def convert_to_window_relative(self, x: int, y: int) -> Tuple[int, int]:
        if not self.game_window_bounds:
            return (x, y)
        
        wx, wy, _, _ = self.game_window_bounds
        return (x - wx, y - wy)
    
    def convert_from_window_relative(self, rel_x: int, rel_y: int) -> Tuple[int, int]:
        if not self.game_window_bounds:
            return (rel_x, rel_y)
        
        wx, wy, _, _ = self.game_window_bounds
        return (rel_x + wx, rel_y + wy)
    
    def get_window_center(self) -> Optional[Tuple[int, int]]:
        if not self.game_window_bounds:
            self.find_and_lock_game_window(force_refresh=True)
        
        if not self.game_window_bounds:
            return None
        
        x, y, w, h = self.game_window_bounds
        return (x + w // 2, y + h // 2)
    
    def get_window_bounds(self) -> Optional[Tuple[int, int, int, int]]:
        return self.find_and_lock_game_window()
    
    def window_exists(self) -> bool:
        if not self.game_window_handle:
            return False
        
        try:
            return bool(win32gui.IsWindow(self.game_window_handle))
        except:
            return False
