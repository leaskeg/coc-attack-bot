from typing import Dict, List, Tuple, Optional, TYPE_CHECKING
import pyautogui
from .screen_utils import get_virtual_screen_size, is_coordinate_on_screen

if TYPE_CHECKING:
    from .config import Config
    from ..core.coordinate_mapper import CoordinateMapper


class ConfigValidator:
    
    REQUIRED_BUTTONS = {
        'attack': 'Main attack button on home screen',
        'find_a_match': 'Find match/search button in attack screen',
        'attack_button_2': 'Green Attack! button on opponent info screen',
        'next_button': 'Next button to skip bases with low loot',
        'return_home': 'Return home button after battle completion',
        'enemy_gold': 'Enemy gold display for loot checking',
        'enemy_elixir': 'Enemy elixir display for loot checking',
        'enemy_dark_elixir': 'Enemy dark elixir display for loot checking'
    }
    
    def __init__(self, config: 'Config', coordinate_mapper: Optional['CoordinateMapper'] = None):
        self.config = config
        self.coordinate_mapper = coordinate_mapper
    
    def validate_auto_attack_config(self) -> Tuple[bool, List[str]]:
        """
        Validate that auto-attack configuration is complete and valid.
        Returns: (is_valid, list_of_errors)
        """
        errors = []
        
        errors.extend(self._validate_required_buttons())
        errors.extend(self._validate_coordinate_bounds())
        errors.extend(self._validate_attack_sessions())
        errors.extend(self._validate_ai_config())
        errors.extend(self._validate_loot_requirements())
        
        return len(errors) == 0, errors
    
    def _validate_coordinate_bounds(self) -> List[str]:
        """Check if all coordinates are within virtual screen bounds (multi-monitor support)"""
        errors = []
        min_x, min_y, max_x, max_y = get_virtual_screen_size()
        primary_w, primary_h = pyautogui.size()
        
        if self.coordinate_mapper:
            mapped_coords = self.coordinate_mapper.get_coordinates()
            out_of_bounds = []
            
            for button_name, coord in mapped_coords.items():
                x, y = coord.get('x', 0), coord.get('y', 0)
                if not is_coordinate_on_screen(x, y):
                    out_of_bounds.append(
                        f"  - {button_name}: ({x}, {y}) - "
                        f"Virtual Screen: ({min_x}, {min_y}) to ({max_x}, {max_y})"
                    )
            
            if out_of_bounds:
                errors.append(f"❌ {len(out_of_bounds)} button(s) are out of virtual screen bounds:")
                errors.extend(out_of_bounds)
                errors.append(f"\nℹ️  Primary monitor: {primary_w}x{primary_h}, Virtual screen: {max_x - min_x}x{max_y - min_y}")
                errors.append(f"ℹ️  Multi-monitor detected. Coordinates can be outside primary monitor.")
        
        return errors
    
    def _validate_loot_requirements(self) -> List[str]:
        """Check if loot requirements are reasonable"""
        errors = []
        
        min_gold = self.config.get('ai_analyzer.min_gold', 300000)
        min_elixir = self.config.get('ai_analyzer.min_elixir', 300000)
        min_dark = self.config.get('ai_analyzer.min_dark_elixir', 2000)
        max_th = self.config.get('ai_analyzer.max_townhall_level', 12)
        
        if not isinstance(min_gold, (int, float)) or min_gold < 0:
            errors.append("❌ min_gold must be a positive number")
        if not isinstance(min_elixir, (int, float)) or min_elixir < 0:
            errors.append("❌ min_elixir must be a positive number")
        if not isinstance(min_dark, (int, float)) or min_dark < 0:
            errors.append("❌ min_dark_elixir must be a positive number")
        if not isinstance(max_th, int) or max_th < 1 or max_th > 18:
            errors.append("❌ max_townhall_level must be between 1 and 18")
        
        return errors
    
    def _validate_required_buttons(self) -> List[str]:
        """Check if all required buttons are mapped"""
        errors = []
        
        if self.coordinate_mapper:
            mapped_coords = self.coordinate_mapper.get_coordinates()
        else:
            return ["❌ Coordinate mapper not initialized."]
        
        if not mapped_coords or not isinstance(mapped_coords, dict):
            return ["❌ No button coordinates found. Map buttons using 'Coordinate Mapping' first."]
        
        missing_buttons = []
        for button_name in self.REQUIRED_BUTTONS.keys():
            if button_name not in mapped_coords:
                missing_buttons.append(f"  - {button_name}: {self.REQUIRED_BUTTONS[button_name]}")
        
        if missing_buttons:
            errors.append(f"❌ Missing {len(missing_buttons)} required button mappings:")
            errors.extend(missing_buttons)
        
        return errors
    
    def _validate_attack_sessions(self) -> List[str]:
        """Check if attack sessions are configured and files exist"""
        import os
        errors = []
        attack_sessions = self.config.get('auto_attacker.attack_sessions', {})
        recordings_dir = self.config.get('directories.recordings', 'recordings')
        
        if not attack_sessions or not any(attack_sessions.values()):
            errors.append("❌ No attack variations configured. Run 'Setup Automation' first.")
            return errors
        
        for attack_name, variations in attack_sessions.items():
            if not variations or not isinstance(variations, list):
                errors.append(f"❌ Attack group '{attack_name}' has no variations")
            else:
                for variation in variations:
                    filepath = os.path.join(recordings_dir, f"{variation}.json")
                    if not os.path.exists(filepath):
                        errors.append(f"❌ Missing session file for '{attack_name}': {variation}.json")
        
        return errors
    
    def _validate_ai_config(self) -> List[str]:
        """Check AI configuration if enabled"""
        errors = []
        ai_enabled = self.config.get('ai_analyzer.enabled', False)
        
        if not ai_enabled:
            return errors
        
        api_key = self.config.get('ai_analyzer.google_gemini_api_key', '').strip()
        if not api_key:
            errors.append("❌ AI Analysis is enabled but no Google Gemini API key is set.")
        
        return errors
    
    def get_missing_buttons(self) -> List[str]:
        """Get list of missing required buttons"""
        if self.coordinate_mapper:
            mapped_coords = self.coordinate_mapper.get_coordinates()
        else:
            return list(self.REQUIRED_BUTTONS.keys())
        
        if not mapped_coords:
            return list(self.REQUIRED_BUTTONS.keys())
        
        return [btn for btn in self.REQUIRED_BUTTONS.keys() if btn not in mapped_coords]
    
    def get_mapped_buttons(self) -> List[str]:
        """Get list of mapped buttons"""
        if self.coordinate_mapper:
            mapped_coords = self.coordinate_mapper.get_coordinates()
        else:
            return []
        
        return list(mapped_coords.keys()) if mapped_coords else []
    
    def get_validation_summary(self) -> Dict:
        """Get a summary of validation status"""
        is_valid, errors = self.validate_auto_attack_config()
        mapped_buttons = self.get_mapped_buttons()
        missing_buttons = self.get_missing_buttons()
        
        return {
            'is_valid': is_valid,
            'errors': errors,
            'mapped_buttons': mapped_buttons,
            'missing_buttons': missing_buttons,
            'progress': f"{len(mapped_buttons)}/{len(self.REQUIRED_BUTTONS)}"
        }
