import pyautogui
from typing import Dict, List, Tuple, Optional
from .window_manager import WindowManager
from .safe_click_executor import SafeClickExecutor
from .game_state_detector import GameStateDetector
from .resource_collector_detector import ResourceCollectorDetector
from .battle_detector import BattleDetector
from .emergency_stop import get_emergency_stop_handler
from ..utils.logger import Logger


class SystemValidator:
    
    def __init__(self, logger: Optional[Logger] = None):
        self.logger = logger or Logger()
        self.validation_results: Dict[str, bool] = {}
        self.errors: List[str] = []
    
    def validate_all_systems(self) -> Dict[str, any]:
        
        results = {
            'overall_success': True,
            'window_manager': self._validate_window_manager(),
            'game_state_detector': self._validate_game_state_detector(),
            'resource_collector_detector': self._validate_resource_collector_detector(),
            'safe_click_executor': self._validate_safe_click_executor(),
            'battle_detector': self._validate_battle_detector(),
            'emergency_stop': self._validate_emergency_stop(),
            'screen_access': self._validate_screen_access(),
            'errors': self.errors
        }
        
        results['overall_success'] = all(v for k, v in results.items() if k != 'errors' and isinstance(v, bool))
        return results
    
    def _validate_window_manager(self) -> bool:
        
        try:
            wm = WindowManager(logger=self.logger)
            bounds = wm.find_and_lock_game_window()
            
            if bounds:
                self.logger.info(f"✓ WindowManager: Game window found {bounds}")
                return True
            else:
                self.errors.append("WindowManager: No game window found")
                self.logger.warning("✗ WindowManager: No game window detected")
                return False
        except Exception as e:
            self.errors.append(f"WindowManager: {str(e)}")
            self.logger.error(f"✗ WindowManager error: {e}")
            return False
    
    def _validate_game_state_detector(self) -> bool:
        
        try:
            gsd = GameStateDetector(logger=self.logger)
            gsd.reset_battle_tracking()
            state = gsd.capture_loot_state()
            
            if state:
                self.logger.info(f"✓ GameStateDetector: Loot state captured (G={state.gold}, E={state.elixir}, DE={state.dark_elixir})")
                return True
            else:
                self.errors.append("GameStateDetector: Could not capture loot state")
                self.logger.warning("✗ GameStateDetector: Failed to capture loot")
                return False
        except Exception as e:
            self.errors.append(f"GameStateDetector: {str(e)}")
            self.logger.error(f"✗ GameStateDetector error: {e}")
            return False
    
    def _validate_resource_collector_detector(self) -> bool:
        
        try:
            rcd = ResourceCollectorDetector(logger=self.logger)
            collectors = rcd.detect_collectors()
            
            self.logger.info(f"✓ ResourceCollectorDetector: Found {len(collectors)} collectors")
            return True
        except Exception as e:
            self.errors.append(f"ResourceCollectorDetector: {str(e)}")
            self.logger.error(f"✗ ResourceCollectorDetector error: {e}")
            return False
    
    def _validate_safe_click_executor(self) -> bool:
        
        try:
            wm = WindowManager(logger=self.logger)
            sce = SafeClickExecutor(wm, logger=self.logger)
            
            self.logger.info(f"✓ SafeClickExecutor: Initialized successfully")
            return True
        except Exception as e:
            self.errors.append(f"SafeClickExecutor: {str(e)}")
            self.logger.error(f"✗ SafeClickExecutor error: {e}")
            return False
    
    def _validate_battle_detector(self) -> bool:
        
        try:
            gsd = GameStateDetector(logger=self.logger)
            bd = BattleDetector(logger=self.logger, game_state_detector=gsd)
            
            self.logger.info(f"✓ BattleDetector: Initialized with GameStateDetector")
            return True
        except Exception as e:
            self.errors.append(f"BattleDetector: {str(e)}")
            self.logger.error(f"✗ BattleDetector error: {e}")
            return False
    
    def _validate_emergency_stop(self) -> bool:
        
        try:
            esh = get_emergency_stop_handler(logger=self.logger)
            esh.start_monitoring()
            
            self.logger.info(f"✓ EmergencyStopHandler: Monitoring active (Ctrl+Alt+S)")
            return True
        except Exception as e:
            self.errors.append(f"EmergencyStopHandler: {str(e)}")
            self.logger.error(f"✗ EmergencyStopHandler error: {e}")
            return False
    
    def _validate_screen_access(self) -> bool:
        
        try:
            screenshot = pyautogui.screenshot()
            width, height = screenshot.size
            
            if width > 0 and height > 0:
                self.logger.info(f"✓ Screen Access: {width}x{height}")
                return True
            else:
                self.errors.append(f"Screen Access: Invalid screen size {width}x{height}")
                self.logger.warning(f"✗ Screen Access: Invalid resolution")
                return False
        except Exception as e:
            self.errors.append(f"Screen Access: {str(e)}")
            self.logger.error(f"✗ Screen Access error: {e}")
            return False
    
    def print_validation_report(self) -> None:
        
        results = self.validate_all_systems()
        
        print("\n" + "=" * 70)
        print("               SYSTEM VALIDATION REPORT")
        print("=" * 70)
        
        for system, result in results.items():
            if system == 'errors':
                continue
            
            status = "✓" if result else "✗"
            print(f"{status} {system:30} {'PASS' if result else 'FAIL'}")
        
        if results['errors']:
            print("\n" + "=" * 70)
            print("ERRORS:")
            for error in results['errors']:
                print(f"  • {error}")
        
        print("\n" + "=" * 70)
        overall = "ALL SYSTEMS OPERATIONAL" if results['overall_success'] else "SOME SYSTEMS FAILED"
        print(f"OVERALL: {overall}")
        print("=" * 70 + "\n")
