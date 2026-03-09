import time
import json
from typing import Dict, List, Optional, Tuple
from .core.screen_capture import ScreenCapture
from .core.coordinate_mapper import CoordinateMapper
from .core.attack_recorder import AttackRecorder
from .core.attack_player import AttackPlayer
from .core.auto_attacker import AutoAttacker
from .core.ai_analyzer import AIAnalyzer
from .utils.config import Config
from .utils.config_validator import ConfigValidator
from .utils.logger import Logger

class BotController:
    
    def __init__(self):
        self.logger = Logger()
        self.config = Config()
        self.screen_capture = ScreenCapture()
        self.coordinate_mapper = CoordinateMapper()
        self.config_validator = ConfigValidator(self.config, self.coordinate_mapper)
        self.attack_recorder = AttackRecorder()
        self.attack_player = AttackPlayer()
        self.ai_analyzer = AIAnalyzer(
            api_key=self.config.get("ai_analyzer.google_gemini_api_key", ""),
            logger=self.logger
        )
        self.auto_attacker = AutoAttacker(
            attack_player=self.attack_player, 
            screen_capture=self.screen_capture, 
            coordinate_mapper=self.coordinate_mapper, 
            logger=self.logger,
            ai_analyzer=self.ai_analyzer,
            config=self.config
        )
        
        self.is_recording = False
        self.is_playing = False
        self.cached_game_window = None
        self.game_window_cache_time = 0
        
        self.logger.info("Controller initialized")
    
    def get_cached_game_window(self, cache_duration: int = 5) -> Optional[Tuple[int, int, int, int]]:
        """Get game window bounds with caching to reduce repeated window detection calls"""
        import time
        current_time = time.time()
        
        if self.cached_game_window and (current_time - self.game_window_cache_time) < cache_duration:
            return self.cached_game_window
        
        bounds = self.screen_capture.find_game_window()
        if bounds:
            self.cached_game_window = bounds
            self.game_window_cache_time = current_time
        
        return bounds
    
    def start_coordinate_mapping(self) -> None:
        self.logger.info("Starting coordinate mapping")
        required_buttons = self.get_required_buttons()
        self.coordinate_mapper.start_mapping(required_buttons)
    
    def start_attack_recording(self, session_name: str) -> None:
        if self.is_recording:
            self.logger.warning("Already recording a session")
            return
            
        self.logger.info(f"Starting recording: {session_name}")
        self.is_recording = True
        self.attack_recorder.start_recording(session_name)
    
    def stop_attack_recording(self) -> None:
        if not self.is_recording:
            self.logger.warning("No recording session active")
            return
            
        self.logger.info("Stopping recording")
        self.is_recording = False
        self.attack_recorder.stop_recording()
    
    def play_attack(self, session_name: str) -> None:
        if self.is_playing:
            self.logger.warning("Already playing a session")
            return
            
        self.logger.info(f"Playing session: {session_name}")
        self.is_playing = True
        try:
            self.attack_player.play_attack(session_name)
        finally:
            self.is_playing = False
    
    def start_auto_attack(self) -> None:
        self.auto_attacker.start_auto_attack()
    
    def stop_auto_attack(self) -> None:
        self.auto_attacker.stop_auto_attack()
    
    def get_auto_attack_stats(self) -> Dict:
        """Get auto attack statistics"""
        return self.auto_attacker.get_stats()
        
    def test_ai_connection(self) -> bool:
        """Test the connection to the Gemini API."""
        return self.ai_analyzer.test_connection()

    def is_auto_attacking(self) -> bool:
        """Check if auto attack is running"""
        return self.auto_attacker.is_running
    
    def get_required_buttons(self) -> Dict[str, str]:
        """Get list of required button mappings for automation"""
        return self.auto_attacker.configure_buttons()
    
    def list_recorded_attacks(self) -> List[str]:
        """Get list of all recorded attack sessions"""
        return self.attack_recorder.list_sessions()
    
    def get_mapped_coordinates(self) -> Dict:
        """Get all mapped button coordinates"""
        return self.coordinate_mapper.get_coordinates()
    
    def save_coordinates(self, name: str, coordinates: Dict) -> None:
        """Save button coordinates mapping"""
        self.coordinate_mapper.save_coordinates(name, coordinates)
    
    def validate_auto_attack_config(self) -> Tuple[bool, List[str]]:
        """Validate auto-attack configuration"""
        return self.config_validator.validate_auto_attack_config()
    
    def get_validation_summary(self) -> Dict:
        """Get validation summary"""
        return self.config_validator.get_validation_summary()
    
    def detect_game_window(self) -> Optional[Tuple[int, int, int, int]]:
        return self.screen_capture.find_game_window()
    
    def take_screenshot(self, region: Optional[Tuple[int, int, int, int]] = None) -> str:
        """Take a screenshot and return the file path"""
        return self.screen_capture.capture_screen(region)
    
    def shutdown(self) -> None:
        self.logger.info("Shutting down")
        if self.is_recording:
            self.stop_attack_recording()
        if self.is_playing:
            self.is_playing = False
        if self.auto_attacker.is_running:
            self.stop_auto_attack() 