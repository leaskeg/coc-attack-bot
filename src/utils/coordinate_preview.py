import threading
import time
import pyautogui
from typing import Dict, Optional, Tuple
from PIL import Image, ImageDraw, ImageFont
import os


class CoordinatePreview:
    
    def __init__(self, mapped_coords: Dict = None, window_title: str = "Clash of Clans"):
        self.mapped_coords = mapped_coords or {}
        self.window_title = window_title
        self.is_running = False
        self.preview_thread = None
        self.position_history = []
        self.max_history = 10
    
    def start(self) -> None:
        """Start the coordinate preview thread"""
        if self.is_running:
            return
        
        self.is_running = True
        self.preview_thread = threading.Thread(target=self._preview_loop, daemon=True)
        self.preview_thread.start()
    
    def stop(self) -> None:
        """Stop the coordinate preview thread"""
        self.is_running = False
        if self.preview_thread:
            self.preview_thread.join(timeout=5)
    
    def update_mapped_coords(self, coords: Dict) -> None:
        """Update the list of mapped coordinates"""
        self.mapped_coords = coords.copy()
    
    def _preview_loop(self) -> None:
        """Main preview loop"""
        try:
            while self.is_running:
                x, y = pyautogui.position()
                self._print_coordinate_info(x, y)
                time.sleep(0.5)
        except Exception as e:
            print(f"[ERROR] Coordinate preview error: {e}")
        finally:
            self.is_running = False
    
    def _print_coordinate_info(self, x: int, y: int) -> None:
        """Print current coordinate information"""
        self.position_history.append((x, y))
        if len(self.position_history) > self.max_history:
            self.position_history.pop(0)
        
        print(f"\r📍 Current Position: ({x:4d}, {y:4d})", end="", flush=True)
        
        if self.mapped_coords:
            nearest = self._find_nearest_coordinate(x, y)
            if nearest:
                name, coord, distance = nearest
                print(f" | Nearest: {name} ({coord['x']}, {coord['y']}) - {distance:.0f}px away", end="", flush=True)
    
    def _find_nearest_coordinate(self, x: int, y: int, max_distance: int = 200) -> Optional[Tuple[str, Dict, int]]:
        """Find the nearest mapped coordinate"""
        nearest = None
        min_distance = max_distance
        
        for name, coord in self.mapped_coords.items():
            distance = ((x - coord['x']) ** 2 + (y - coord['y']) ** 2) ** 0.5
            if distance < min_distance:
                min_distance = distance
                nearest = (name, coord, distance)
        
        return nearest
    
    def get_position_summary(self) -> str:
        """Get a summary of recent positions"""
        if not self.position_history:
            return "No position history"
        
        x_coords = [pos[0] for pos in self.position_history]
        y_coords = [pos[1] for pos in self.position_history]
        
        avg_x = sum(x_coords) / len(x_coords)
        avg_y = sum(y_coords) / len(y_coords)
        
        return f"Average: ({avg_x:.0f}, {avg_y:.0f}) | Current: ({x_coords[-1]}, {y_coords[-1]})"


class OverlayCoordinateDisplay:
    
    """Display coordinates as an overlay on the game window (experimental)"""
    
    def __init__(self, screen_width: int = 1920, screen_height: int = 1080):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.mapped_coords = {}
        self.is_running = False
        self.current_pos = (0, 0)
    
    def _create_overlay_image(self) -> Image:
        """Create an overlay image with coordinate information"""
        img = Image.new('RGBA', (self.screen_width, self.screen_height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        x, y = self.current_pos
        
        try:
            font = ImageFont.truetype("arial.ttf", 20)
            small_font = ImageFont.truetype("arial.ttf", 14)
        except:
            font = ImageFont.load_default()
            small_font = font
        
        draw.ellipse([x-10, y-10, x+10, y+10], outline=(255, 0, 0, 255), width=2)
        draw.line([x-20, y, x+20, y], fill=(255, 0, 0, 200), width=1)
        draw.line([x, y-20, x, y+20], fill=(255, 0, 0, 200), width=1)
        
        text = f"({x}, {y})"
        draw.text((x+15, y-25), text, fill=(255, 255, 255, 255), font=font)
        
        for i, (name, coord) in enumerate(self.mapped_coords.items()):
            cx, cy = coord['x'], coord['y']
            distance = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5
            
            if distance < 300:
                draw.ellipse([cx-5, cy-5, cx+5, cy+5], outline=(0, 255, 0, 200), width=1)
                draw.text((cx+10, cy), f"{name}", fill=(0, 255, 0, 200), font=small_font)
        
        return img


class SimpleCoordinateDisplay:
    
    """Simple console-based coordinate display"""
    
    def __init__(self):
        self.mapped_coords = {}
    
    def display_current_position(self, mapped_coords: Dict = None) -> None:
        """Display current mouse position and nearby coordinates"""
        x, y = pyautogui.position()
        
        print(f"\n📍 CURRENT POSITION: ({x}, {y})")
        
        if mapped_coords:
            print("\n📌 NEARBY MAPPED COORDINATES (within 300px):")
            found = False
            for name, coord in sorted(mapped_coords.items()):
                distance = ((x - coord['x']) ** 2 + (y - coord['y']) ** 2) ** 0.5
                if distance < 300:
                    found = True
                    bar_length = int((300 - distance) / 300 * 20)
                    bar = "█" * bar_length + "░" * (20 - bar_length)
                    print(f"  • {name:20} ({coord['x']:4d}, {coord['y']:4d}) [{bar}] {distance:6.0f}px")
            
            if not found:
                print("  (No mapped coordinates nearby)")
        
        print()
