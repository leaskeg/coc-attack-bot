"""
Screen utilities for multi-monitor support
"""
import pyautogui
from typing import Tuple

try:
    import win32api
    import win32con
    WIN32_AVAILABLE = True
except ImportError:
    WIN32_AVAILABLE = False


def get_virtual_screen_size() -> Tuple[int, int, int, int]:
    """
    Get the virtual screen bounds across all monitors.
    Returns: (min_x, min_y, max_x, max_y)
    
    For multi-monitor setups, coordinates can be negative or extend beyond primary monitor.
    """
    if WIN32_AVAILABLE:
        try:
            # Get virtual screen metrics (includes all monitors)
            left = win32api.GetSystemMetrics(win32con.SM_XVIRTUALSCREEN)
            top = win32api.GetSystemMetrics(win32con.SM_YVIRTUALSCREEN)
            width = win32api.GetSystemMetrics(win32con.SM_CXVIRTUALSCREEN)
            height = win32api.GetSystemMetrics(win32con.SM_CYVIRTUALSCREEN)
            
            return (left, top, left + width, top + height)
        except Exception as e:
            print(f"Warning: Could not get virtual screen size: {e}")
    
    # Fallback to primary monitor only
    screen_width, screen_height = pyautogui.size()
    return (0, 0, screen_width, screen_height)


def get_primary_screen_size() -> Tuple[int, int]:
    """Get primary monitor size"""
    return pyautogui.size()


def is_coordinate_on_screen(x: int, y: int) -> bool:
    """Check if coordinate is within virtual screen bounds"""
    min_x, min_y, max_x, max_y = get_virtual_screen_size()
    return min_x <= x < max_x and min_y <= y < max_y


def get_monitor_info() -> dict:
    """Get information about all monitors"""
    info = {
        'primary': get_primary_screen_size(),
        'virtual_bounds': get_virtual_screen_size(),
        'monitor_count': 1
    }
    
    if WIN32_AVAILABLE:
        try:
            # Count monitors
            def monitor_enum_proc(hMonitor, hdcMonitor, lprcMonitor, dwData):
                monitors = dwData
                monitors.append({
                    'handle': hMonitor,
                    'left': lprcMonitor[0],
                    'top': lprcMonitor[1],
                    'right': lprcMonitor[2],
                    'bottom': lprcMonitor[3],
                    'width': lprcMonitor[2] - lprcMonitor[0],
                    'height': lprcMonitor[3] - lprcMonitor[1]
                })
                return True
            
            monitors = []
            win32api.EnumDisplayMonitors(None, None, monitor_enum_proc, monitors)
            info['monitor_count'] = len(monitors)
            info['monitors'] = monitors
        except Exception:
            pass
    
    return info


def print_screen_info() -> None:
    """Print screen configuration info"""
    info = get_monitor_info()
    
    print("\n" + "=" * 60)
    print("           SCREEN CONFIGURATION")
    print("=" * 60)
    
    primary_w, primary_h = info['primary']
    print(f"Primary Monitor: {primary_w}x{primary_h}")
    
    min_x, min_y, max_x, max_y = info['virtual_bounds']
    print(f"Virtual Screen: ({min_x}, {min_y}) to ({max_x}, {max_y})")
    print(f"Virtual Size: {max_x - min_x}x{max_y - min_y}")
    print(f"Monitor Count: {info['monitor_count']}")
    
    if 'monitors' in info:
        print("\nAll Monitors:")
        for i, mon in enumerate(info['monitors'], 1):
            print(f"  Monitor {i}: {mon['width']}x{mon['height']} at ({mon['left']}, {mon['top']})")
    
    print("=" * 60)
