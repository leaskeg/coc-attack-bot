import json
import os
import time
import pyautogui
import keyboard
from typing import Dict, List, Tuple, Optional
from datetime import datetime
from ..utils.coordinate_preview import SimpleCoordinateDisplay
from ..utils.screen_utils import get_virtual_screen_size, is_coordinate_on_screen

class CoordinateMapper:
    
    def __init__(self):
        self.coordinates_dir = "coordinates"
        self.coordinates_file = os.path.join(self.coordinates_dir, "button_coordinates.json")
        self.coordinates = {}
        self.is_mapping = False
        self.preview_display = SimpleCoordinateDisplay()
        
        # Create coordinates directory
        os.makedirs(self.coordinates_dir, exist_ok=True)
        
        # Load existing coordinates
        self.load_coordinates()
        
        print("Mapper ready")
    
    def load_coordinates(self) -> None:
        """Load coordinates from file"""
        if os.path.exists(self.coordinates_file):
            try:
                with open(self.coordinates_file, 'r') as f:
                    self.coordinates = json.load(f)
                print(f"Loaded {len(self.coordinates)} coordinate mappings")
            except Exception as e:
                print(f"Error loading coordinates: {e}")
                self.coordinates = {}
        else:
            print("No existing coordinates file found")
    
    def save_coordinates(self, name: Optional[str] = None, coords: Optional[Dict] = None) -> None:
        """Save coordinates to file"""
        try:
            if coords:
                # Save specific coordinates
                if name:
                    self.coordinates[name] = coords
                else:
                    self.coordinates.update(coords)
            
            with open(self.coordinates_file, 'w') as f:
                json.dump(self.coordinates, f, indent=2)
            
            print(f"Coordinates saved to {self.coordinates_file}")
            print(f"Total mappings: {len(self.coordinates)}")
        except Exception as e:
            print(f"Error saving coordinates: {e}")
    
    def start_mapping(self, required_buttons: Dict[str, str] = None) -> None:
        """Start interactive coordinate mapping with enhanced UX"""
        if self.is_mapping:
            print("Already in mapping mode")
            return
        
        self.is_mapping = True
        current_session = {}
        
        print("\n" + "=" * 70)
        print("                COORDINATE MAPPING MODE")
        print("=" * 70)
        
        if required_buttons:
            print("\n📋 REQUIRED BUTTONS TO MAP:")
            for btn_name, description in required_buttons.items():
                status = "✓" if btn_name in self.coordinates else "✗"
                print(f"  {status} {btn_name:20} - {description}")
        
        print("\n📌 INSTRUCTIONS:")
        print("  1. Move mouse to a button you want to map")
        print("  2. Press F2 to record the position")
        print("  3. Enter the button name (or exact name from list above)")
        print("  4. Repeat for all buttons")
        print("  5. Press F3 to save all mappings at once")
        print("  6. Press ESC or F1 to exit")
        print("\n" + "=" * 70)
        print("Starting in 3 seconds...")
        time.sleep(3)
        
        try:
            while self.is_mapping:
                if keyboard.is_pressed('esc'):
                    print("\nMapping cancelled")
                    break
                
                if keyboard.is_pressed('f2'):
                    x, y = pyautogui.position()
                    
                    print(f"\n📍 Mouse Position: ({x}, {y})")
                    
                    if self.coordinates:
                        print("\n📌 NEARBY MAPPED COORDINATES (within 200px):")
                        found = False
                        for name, coord in sorted(self.coordinates.items()):
                            distance = ((x - coord['x']) ** 2 + (y - coord['y']) ** 2) ** 0.5
                            if distance < 200:
                                found = True
                                bar_length = int((200 - distance) / 200 * 15)
                                bar = "█" * bar_length + "░" * (15 - bar_length)
                                print(f"    {name:20} ({coord['x']:4d}, {coord['y']:4d}) [{bar}] {distance:6.0f}px")
                        if not found:
                            print("    (No mapped coordinates nearby)")
                    
                    if required_buttons:
                        print("\nSuggested names: " + ", ".join(required_buttons.keys()))
                    
                    button_name = input("\nEnter button name: ").strip()
                    
                    if button_name:
                        current_session[button_name] = {"x": x, "y": y}
                        
                        status = "NEW" if button_name not in self.coordinates else "UPDATED"
                        print(f"✅ [{status}] '{button_name}' at ({x}, {y})")
                        print(f"📊 Session: {len(current_session)} mappings | "
                              f"Total: {len(self.coordinates) + len(current_session)} coordinates")
                        
                        if required_buttons and button_name in required_buttons:
                            print(f"✓ '{button_name}' is a required button")
                    else:
                        print("❌ Button name cannot be empty")
                    
                    while keyboard.is_pressed('f2'):
                        time.sleep(0.1)
                
                if keyboard.is_pressed('f3'):
                    if current_session:
                        self.coordinates.update(current_session)
                        self.save_coordinates()
                        print(f"\n✅ Saved {len(current_session)} mappings")
                        current_session.clear()
                        
                        if required_buttons:
                            mapped = [btn for btn in required_buttons.keys() if btn in self.coordinates]
                            print(f"📊 Progress: {len(mapped)}/{len(required_buttons)} required buttons mapped")
                    else:
                        print("\n⚠️  No mappings in session to save")
                    
                    while keyboard.is_pressed('f3'):
                        time.sleep(0.1)
                
                if keyboard.is_pressed('f1'):
                    print("\nExiting mapping mode")
                    break
                
                time.sleep(0.1)
        
        except KeyboardInterrupt:
            print("\n\nMapping interrupted")
        
        finally:
            self.is_mapping = False
            print("\n" + "=" * 70)
            
            if current_session:
                response = input(f"Save {len(current_session)} unsaved mappings? (y/n): ").strip().lower()
                if response == 'y':
                    self.coordinates.update(current_session)
                    self.save_coordinates()
                    print(f"✅ Saved {len(current_session)} mappings")
                else:
                    print("⚠️  Unsaved mappings discarded")
            
            if required_buttons:
                mapped = [btn for btn in required_buttons.keys() if btn in self.coordinates]
                print(f"\n📊 FINAL PROGRESS: {len(mapped)}/{len(required_buttons)} required buttons")
                
                missing = [btn for btn in required_buttons.keys() if btn not in self.coordinates]
                if missing:
                    print("\n⚠️  Still missing:")
                    for btn in missing:
                        print(f"  - {btn}")
                else:
                    print("\n✅ ALL REQUIRED BUTTONS MAPPED!")
            
            print("=" * 70)
    
    def get_coordinates(self, button_name: Optional[str] = None) -> Dict:
        """Get coordinates for a specific button or all buttons"""
        if button_name:
            return self.coordinates.get(button_name, {})
        return self.coordinates.copy()
    
    def add_coordinate(self, name: str, x: int, y: int) -> None:
        """Add a single coordinate mapping"""
        self.coordinates[name] = {"x": x, "y": y}
        print(f"Added coordinate '{name}' at ({x}, {y})")
    
    def remove_coordinate(self, name: str) -> bool:
        """Remove a coordinate mapping"""
        if name in self.coordinates:
            del self.coordinates[name]
            print(f"Removed coordinate '{name}'")
            return True
        else:
            print(f"Coordinate '{name}' not found")
            return False
    
    def edit_coordinate(self, name: str, x: Optional[int] = None, y: Optional[int] = None) -> bool:
        """Edit an existing coordinate mapping"""
        if name not in self.coordinates:
            print(f"Coordinate '{name}' not found")
            return False
        
        current_x = self.coordinates[name]['x']
        current_y = self.coordinates[name]['y']
        
        # If coordinates provided, use them
        if x is not None and y is not None:
            self.coordinates[name] = {"x": x, "y": y}
            print(f"Updated coordinate '{name}' from ({current_x}, {current_y}) to ({x}, {y})")
            return True
        
        # Interactive edit mode
        print(f"\nCurrent: '{name}' at ({current_x}, {current_y})")
        print("Options:")
        print("1. Use current mouse position")
        print("2. Enter coordinates manually")
        print("3. Cancel")
        
        choice = input("Choose option: ").strip()
        
        if choice == '1':
            x, y = pyautogui.position()
            self.coordinates[name] = {"x": x, "y": y}
            print(f"Updated coordinate '{name}' to ({x}, {y})")
            return True
        
        elif choice == '2':
            try:
                x = int(input("Enter X coordinate: ").strip())
                y = int(input("Enter Y coordinate: ").strip())
                self.coordinates[name] = {"x": x, "y": y}
                print(f"Updated coordinate '{name}' to ({x}, {y})")
                return True
            except ValueError:
                print("Invalid coordinates")
                return False
        
        else:
            print("Edit cancelled")
            return False
    
    def list_coordinates(self) -> None:
        """Print all mapped coordinates"""
        if not self.coordinates:
            print("No coordinates mapped yet")
            return
        
        print("\n=== MAPPED COORDINATES ===")
        for name, coords in self.coordinates.items():
            print(f"  {name}: ({coords['x']}, {coords['y']})")
        print(f"Total: {len(self.coordinates)} mappings")
    
    def validate_coordinates(self) -> Dict[str, bool]:
        """Validate that all coordinates are within virtual screen bounds (multi-monitor support)"""
        min_x, min_y, max_x, max_y = get_virtual_screen_size()
        validation = {}
        
        for name, coords in self.coordinates.items():
            x, y = coords['x'], coords['y']
            is_valid = is_coordinate_on_screen(x, y)
            validation[name] = is_valid
            
            if not is_valid:
                print(f"WARNING: Coordinate '{name}' ({x}, {y}) is outside virtual screen bounds "
                      f"({min_x}, {min_y}) to ({max_x}, {max_y})")
        
        return validation
    
    def export_coordinates(self, filepath: str) -> None:
        """Export coordinates to a custom file"""
        try:
            with open(filepath, 'w') as f:
                json.dump(self.coordinates, f, indent=2)
            print(f"Coordinates exported to {filepath}")
        except Exception as e:
            print(f"Error exporting coordinates: {e}")
    
    def import_coordinates(self, filepath: str, merge: bool = True) -> None:
        """Import coordinates from a file"""
        try:
            with open(filepath, 'r') as f:
                imported_coords = json.load(f)
            
            if merge:
                self.coordinates.update(imported_coords)
                print(f"Merged {len(imported_coords)} coordinates")
            else:
                self.coordinates = imported_coords
                print(f"Replaced with {len(imported_coords)} coordinates")
            
            self.save_coordinates()
        except Exception as e:
            print(f"Error importing coordinates: {e}") 