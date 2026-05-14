import time
import json
from typing import Dict, List, Optional, Tuple
from .core.screen_capture import ScreenCapture
from .core.coordinate_mapper import CoordinateMapper
from .core.attack_recorder import AttackRecorder
from .core.attack_player import AttackPlayer
from .core.auto_attacker import AutoAttacker
from .core.ai_analyzer import AIAnalyzer
from .core.deployment_detector import DeploymentDetector
from .core.resource_reader import ResourceReader
from .core.battle_detector import BattleDetector
from .core.donation_detector import DonationDetector
from .core.window_manager import WindowManager
from .core.safe_click_executor import SafeClickExecutor
from .core.game_state_detector import GameStateDetector
from .core.resource_collector_detector import ResourceCollectorDetector
from .core.emergency_stop import get_emergency_stop_handler
from .utils.config import Config
from .utils.config_validator import ConfigValidator
from .utils.logger import Logger

class BotController:
    
    def __init__(self):
        self.logger = Logger()
        self.config = Config()
        self.screen_capture = ScreenCapture(logger=self.logger)
        self.coordinate_mapper = CoordinateMapper()
        
        self.window_manager = WindowManager(logger=self.logger)
        self.game_state_detector = GameStateDetector(logger=self.logger)
        self.resource_collector_detector = ResourceCollectorDetector(logger=self.logger)
        self.safe_click_executor = SafeClickExecutor(self.window_manager, logger=self.logger)
        self.emergency_stop = get_emergency_stop_handler(logger=self.logger)
        
        self.deployment_detector = DeploymentDetector(logger=self.logger)
        self.resource_reader = ResourceReader(logger=self.logger)
        self.battle_detector = BattleDetector(logger=self.logger, game_state_detector=self.game_state_detector)
        self.donation_detector = DonationDetector(logger=self.logger)
        self.config_validator = ConfigValidator(self.config, self.coordinate_mapper)
        self.attack_recorder = AttackRecorder(logger=self.logger)
        self.attack_player = AttackPlayer(logger=self.logger, window_manager=self.window_manager)
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
            config=self.config,
            deployment_detector=self.deployment_detector
        )
        
        self.is_recording = False
        self.is_playing = False
        self.cached_game_window = None
        self.game_window_cache_time = 0
        
        self.logger.info("Controller initialized with advanced safety and detection systems")
    
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
    
    def get_game_window(self) -> Optional[Tuple[int, int, int, int]]:
        """Get game window bounds (direct, uncached call)"""
        return self.screen_capture.find_game_window()
    
    def start_coordinate_mapping(self) -> None:
        self.logger.info("Starting coordinate mapping")
        mode = self.get_attack_mode()
        if mode == 'legend':
            required_buttons = self.get_required_buttons_legend()
            self.logger.info("Using Legend League button mapping")
        else:
            required_buttons = self.get_required_buttons()
            self.logger.info("Using Farm mode button mapping")
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
    
    def get_attack_mode(self) -> str:
        """Return current attack mode: 'farm' or 'legend'"""
        return self.auto_attacker.get_attack_mode()

    def set_attack_mode(self, mode: str) -> bool:
        """Switch attack mode ('farm' or 'legend')"""
        return self.auto_attacker.set_attack_mode(mode)

    def get_required_buttons(self) -> Dict[str, str]:
        """Get list of required button mappings for automation"""
        return self.auto_attacker.configure_buttons()

    def get_required_buttons_legend(self) -> Dict[str, str]:
        """Get list of required button mappings for Legend League mode"""
        return self.auto_attacker.configure_buttons_legend()
    
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
    
    def read_base_resources(self, game_region: Optional[Tuple[int, int, int, int]] = None) -> Dict:
        """
        Read gold/elixir/dark elixir from current base preview
        
        Returns:
            {'gold': 465369, 'elixir': 482487, 'dark_elixir': 6528, 'confidence': 0.85}
        """
        if not game_region:
            game_region = self.detect_game_window()
        
        if not game_region:
            self.logger.error("Cannot detect game window")
            return {'gold': 0, 'elixir': 0, 'dark_elixir': 0, 'confidence': 0.0}
        
        return self.resource_reader.read_resources_from_search_screen(game_region)
    
    def is_base_worth_attacking(self, resources: Dict, 
                               min_gold: int = 100000,
                               min_elixir: int = 100000,
                               min_dark: int = 1000) -> Tuple[bool, str]:
        """
        Check if base meets attack criteria
        
        Returns:
            (should_attack: bool, reason: str)
        """
        return self.resource_reader.should_attack_base(resources, min_gold, min_elixir, min_dark)
    
    def classify_base(self, resources: Dict) -> str:
        """
        Classify base as 'Dead Base' or other
        
        Returns:
            "Dead Base" or "Not a Dead Base"
        """
        is_dead = self.resource_reader.detect_dead_base(resources)
        return "Dead Base" if is_dead else "Not a Dead Base"
    
    def is_battle_active(self, game_region: Optional[Tuple[int, int, int, int]] = None) -> bool:
        """Check if battle is currently in progress"""
        if not game_region:
            game_region = self.detect_game_window()
        if not game_region:
            return False
        return self.battle_detector.is_battle_in_progress(game_region)
    
    def is_battle_complete(self, game_region: Optional[Tuple[int, int, int, int]] = None) -> bool:
        """Check if battle has ended (victory/defeat screen visible)"""
        if not game_region:
            game_region = self.detect_game_window()
        if not game_region:
            return False
        return self.battle_detector.is_battle_ended(game_region)
    
    def get_battle_status(self, game_region: Optional[Tuple[int, int, int, int]] = None) -> Dict:
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
        if not game_region:
            game_region = self.detect_game_window()
        if not game_region:
            return {'in_battle': False, 'ended': False, 'result': 'error'}
        return self.battle_detector.get_battle_status(game_region)
    
    def wait_for_battle_end(self, timeout: int = 180) -> bool:
        """
        Wait for battle to auto-complete
        
        Args:
            timeout: Max seconds to wait (default: 3 minutes)
        
        Returns:
            True if battle ended, False if timeout
        """
        game_region = self.detect_game_window()
        if not game_region:
            return False
        return self.battle_detector.wait_for_battle_end(game_region, timeout)
    
    def get_available_troops_to_donate(self, game_region: Optional[Tuple[int, int, int, int]] = None) -> List[Tuple[int, int]]:
        """
        Get list of non-greyed troop icons available to donate
        
        Returns:
            List of (x, y) coordinates to click
        """
        try:
            self.logger.debug("[DONATION API] get_available_troops_to_donate() called")
            
            if not game_region:
                self.logger.debug("  → Detecting game window...")
                game_region = self.detect_game_window()
                if not game_region:
                    self.logger.error("[DONATION API] Game window not detected")
                    return []
                self.logger.debug(f"  → Game window detected: {game_region}")
            
            troops = self.donation_detector.get_available_troops(game_region)
            self.logger.info(f"[DONATION API] Retrieved {len(troops)} available troops to donate")
            return troops
        except Exception as e:
            self.logger.error(f"[DONATION API ERROR] Error getting available troops: {e}", exc_info=True)
            return []
    
    def get_available_spells_to_donate(self, game_region: Optional[Tuple[int, int, int, int]] = None) -> List[Tuple[int, int]]:
        """
        Get list of non-greyed spell icons available to donate
        
        Returns:
            List of (x, y) coordinates to click
        """
        try:
            self.logger.debug("[DONATION API] get_available_spells_to_donate() called")
            
            if not game_region:
                self.logger.debug("  → Detecting game window...")
                game_region = self.detect_game_window()
                if not game_region:
                    self.logger.error("[DONATION API] Game window not detected")
                    return []
                self.logger.debug(f"  → Game window detected: {game_region}")
            
            spells = self.donation_detector.get_available_spells(game_region)
            self.logger.info(f"[DONATION API] Retrieved {len(spells)} available spells to donate")
            return spells
        except Exception as e:
            self.logger.error(f"[DONATION API ERROR] Error getting available spells: {e}", exc_info=True)
            return []
    
    def get_donation_requests(self, game_region: Optional[Tuple[int, int, int, int]] = None) -> List[Dict]:
        """
        Get list of clan members requesting donations
        
        Returns:
            List of request dictionaries
        """
        try:
            self.logger.debug("[DONATION API] get_donation_requests() called")
            
            if not game_region:
                self.logger.debug("  → Detecting game window...")
                game_region = self.detect_game_window()
                if not game_region:
                    self.logger.error("[DONATION API] Game window not detected")
                    return []
                self.logger.debug(f"  → Game window detected: {game_region}")
            
            requests = self.donation_detector.detect_donation_requests(game_region)
            self.logger.info(f"[DONATION API] Found {len(requests)} donation requests")
            return requests
        except Exception as e:
            self.logger.error(f"[DONATION API ERROR] Error getting donation requests: {e}", exc_info=True)
            return []
    
    def find_donate_button(self, game_region: Optional[Tuple[int, int, int, int]] = None) -> Optional[Tuple[int, int]]:
        """
        Find the green 'Donate' button using template matching
        
        Returns:
            (x, y) coordinates or None
        """
        try:
            self.logger.debug("[DONATION API] find_donate_button() called")
            
            if not game_region:
                self.logger.debug("  → Detecting game window...")
                game_region = self.detect_game_window()
                if not game_region:
                    self.logger.error("[DONATION API] Game window not detected")
                    return None
                self.logger.debug(f"  → Game window detected: {game_region}")
            
            button = self.donation_detector.find_donate_button_template(game_region, "donate_button_template.png")
            if button:
                self.logger.info(f"[DONATION API] Donate button found at {button}")
            else:
                self.logger.debug("[DONATION API] Donate button not found")
            return button
        except Exception as e:
            self.logger.error(f"[DONATION API ERROR] Error finding donate button: {e}", exc_info=True)
            return None
    
    def is_in_donation_screen(self, game_region: Optional[Tuple[int, int, int, int]] = None) -> bool:
        """Check if donation screen/clan chat is visible"""
        try:
            self.logger.debug("[DONATION API] is_in_donation_screen() called")
            
            if not game_region:
                self.logger.debug("  → Detecting game window...")
                game_region = self.detect_game_window()
                if not game_region:
                    self.logger.error("[DONATION API] Game window not detected")
                    return False
                self.logger.debug(f"  → Game window detected: {game_region}")
            
            in_screen = self.donation_detector.is_in_clan_chat(game_region)
            self.logger.info(f"[DONATION API] In donation screen: {in_screen}")
            return in_screen
        except Exception as e:
            self.logger.error(f"[DONATION API ERROR] Error checking donation screen: {e}", exc_info=True)
            return False
    
    def shutdown(self) -> None:
        self.logger.info("Shutting down")
        if self.is_recording:
            self.stop_attack_recording()
        if self.is_playing:
            self.is_playing = False
        if self.auto_attacker.is_running:
            self.stop_auto_attack() 