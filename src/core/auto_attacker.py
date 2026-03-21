import time
import random
import threading
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import pyautogui
import keyboard

from .attack_player import AttackPlayer
from .screen_capture import ScreenCapture
from .coordinate_mapper import CoordinateMapper
from .ai_analyzer import AIAnalyzer
from ..utils.logger import Logger
from ..utils.config import Config
from ..utils.timing import add_random_delay, add_coordinate_variance, add_human_like_hesitation, get_varied_delay_range

class AutoAttacker:
    
    def __init__(self, attack_player: AttackPlayer, screen_capture: ScreenCapture, 
                 coordinate_mapper: CoordinateMapper, logger: Logger, ai_analyzer: AIAnalyzer, config: Config):
        self.attack_player = attack_player
        self.screen_capture = screen_capture
        self.coordinate_mapper = coordinate_mapper
        self.logger = logger
        self.ai_analyzer = ai_analyzer
        self.config = config
        
        self.is_running = False
        self.auto_thread = None
        self.state_lock = threading.Lock()
        self.stats = {
            'total_attacks': 0,
            'successful_attacks': 0,
            'failed_attacks': 0,
            'start_time': None,
            'last_attack_time': None
        }
        
        self.attack_sessions = self.config.get('auto_attacker.attack_sessions', {})
        self.max_search_attempts = self.config.get('auto_attacker.max_search_attempts', 10)
        
        self.logger.info("Auto Attacker initialized")
        self.logger.info("Emergency stop: Ctrl+Alt+S")
    
    def _verify_click_position(self, x: int, y: int) -> Tuple[int, int]:
        """Verify click position is within screen bounds"""
        screen_width, screen_height = pyautogui.size()
        x = max(0, min(x, screen_width - 1))
        y = max(0, min(y, screen_height - 1))
        return (x, y)
    
    def _click_with_jitter(self, x: int, y: int, jitter_pixels: int = 5) -> None:
        """Click with slight human-like jitter"""
        adjusted_x, adjusted_y = add_coordinate_variance(x, y, jitter_pixels)
        adjusted_x, adjusted_y = self._verify_click_position(adjusted_x, adjusted_y)
        pyautogui.click(adjusted_x, adjusted_y)
    
    def add_attack_session(self, attack_name: str, variation_name: str) -> bool:
        """Add an attack variation to a group"""
        sessions = self.config.get('auto_attacker.attack_sessions', {})
        
        if attack_name not in sessions:
            sessions[attack_name] = []
        
        if variation_name not in sessions[attack_name]:
            sessions[attack_name].append(variation_name)
            self.config.set('auto_attacker.attack_sessions', sessions)
            self.attack_sessions = sessions
            self.logger.info(f"Added variation '{variation_name}' to attack '{attack_name}'")
            return True
        return False
    
    def remove_attack_session(self, attack_name: str, variation_name: str = None) -> bool:
        """Remove an attack variation or entire attack group"""
        sessions = self.config.get('auto_attacker.attack_sessions', {})
        
        if attack_name not in sessions:
            self.logger.warning(f"Attack group '{attack_name}' not found")
            return False
        
        if variation_name is None:
            del sessions[attack_name]
            self.logger.info(f"Removed entire attack group: '{attack_name}'")
        else:
            if variation_name in sessions[attack_name]:
                sessions[attack_name].remove(variation_name)
                if not sessions[attack_name]:
                    del sessions[attack_name]
                    self.logger.info(f"Removed variation '{variation_name}' from '{attack_name}' (group now empty)")
                else:
                    self.logger.info(f"Removed variation '{variation_name}' from '{attack_name}'")
            else:
                self.logger.warning(f"Variation '{variation_name}' not found in '{attack_name}'")
                return False
        
        self.config.set('auto_attacker.attack_sessions', sessions)
        self.attack_sessions = sessions
        return True
    
    def start_auto_attack(self) -> None:
        """Start the automated attack system"""
        with self.state_lock:
            if self.is_running:
                self.logger.warning("Auto attacker already running")
                return
            
            if not self.attack_sessions or not any(self.attack_sessions.values()):
                self.logger.error("No attack variations configured. Please add at least one attack group with variations.")
                return
            
            self.is_running = True
            self.stats['start_time'] = datetime.now()
        
        self.auto_thread = threading.Thread(target=self._auto_attack_loop)
        self.auto_thread.daemon = True
        self.auto_thread.start()
        
        self.logger.info("Auto attacker started")
    
    def stop_auto_attack(self) -> None:
        """Stop the automated attack system"""
        with self.state_lock:
            if not self.is_running:
                return
            self.is_running = False
        
        self.logger.info("Auto attacker stopping...")
        self.attack_player.stop_playback()
        
        if self.auto_thread and self.auto_thread.is_alive():
            self.auto_thread.join(timeout=5)
        
        self.logger.info("Auto attacker stopped")
    
    def _click_at(self, x: int, y: int, jitter_pixels: int = 5) -> None:
        """Perform a human-like click with jitter and variable down-time"""
        adjusted_x, adjusted_y = add_coordinate_variance(x, y, jitter_pixels)
        adjusted_x, adjusted_y = self._verify_click_position(adjusted_x, adjusted_y)
        
        # Randomize duration between mouse down and up
        press_duration = random.uniform(0.08, 0.22)
        pyautogui.mouseDown(adjusted_x, adjusted_y)
        time.sleep(press_duration)
        pyautogui.mouseUp()

    def _park_mouse(self) -> None:
        """Move mouse to a 'neutral' zone (edges or off-window) to simulate human waiting"""
        screen_w, screen_h = pyautogui.size()
        
        # Choose a random edge or corner
        destinations = [
            (screen_w - 50, screen_h // 2),  # Right edge
            (50, screen_h // 2),            # Left edge
            (screen_w // 2, 50),            # Top edge
            (screen_w - 50, screen_h - 50)   # Bottom right corner
        ]
        
        dest_x, dest_y = random.choice(destinations)
        
        # Move with a slow, relaxed speed
        move_duration = random.uniform(0.4, 1.2)
        pyautogui.moveTo(dest_x, dest_y, duration=move_duration, tween=pyautogui.easeInOutQuad)
        
        # Occasional micro-movement while parked
        if random.random() < 0.4:
            time.sleep(random.uniform(0.5, 2.0))
            pyautogui.moveRel(random.randint(-10, 10), random.randint(-10, 10), duration=0.3)

    def _auto_attack_loop(self) -> None:
        """Main automation loop"""
        try:
            while self.is_running:
                # Check emergency stop
                if keyboard.is_pressed('ctrl+alt+s'):
                    self.logger.warning("Emergency stop activated!")
                    break
                
                self.logger.info("🎯 Starting new attack cycle...")
                
                # Execute attack sequence
                if self._execute_attack_sequence():
                    self.stats['successful_attacks'] += 1
                    self.logger.info("✅ Attack sequence completed successfully")
                else:
                    self.stats['failed_attacks'] += 1
                    self.logger.warning("❌ Attack sequence failed")
                
                self.stats['total_attacks'] += 1
                self.stats['last_attack_time'] = datetime.now()
                
                # Cleanup old screenshots every 10 attacks
                if self.stats['total_attacks'] % 10 == 0:
                    self.screen_capture.cleanup_old_screenshots(max_age_hours=24)
                
                # Check for a 'Long Break' (simulating human getting distracted or tired)
                # Chance: 15% every attack after the 3rd
                if self.is_running and self.stats['total_attacks'] > 3 and random.random() < 0.15:
                    long_break = random.uniform(180, 480) # 3 to 8 minutes
                    self.logger.info(f"☕ Taking a long break (simulating human)... {long_break/60:.1f} minutes")
                    self._park_mouse()
                    time.sleep(long_break)
                    
                # Short break between attacks (more variable)
                if self.is_running:
                    next_min = self.config.get('auto_attacker.next_attempt_delay', 10)
                    next_max = self.config.get('auto_attacker.next_attempt_delay_max', 35)
                    randomized_delay = get_varied_delay_range(next_min, next_max, variance=0.4)
                    self.logger.info(f"⏳ Waiting {randomized_delay:.1f} seconds before next attack...")
                    # Park mouse during shorter wait too
                    if randomized_delay > 15:
                        self._park_mouse()
                    time.sleep(randomized_delay)
                    add_human_like_hesitation(threshold=0.2)
                    
        except Exception as e:
            self.logger.error(f"Auto attack loop error: {e}")
        finally:
            self.is_running = False
    
    def _zoom_out(self) -> None:
        """Force zoom out to ensure full base visibility"""
        self.logger.info("🔍 Zooming out for maximum visibility...")
        
        # Method 1: Ctrl + Mouse Wheel Down (Common for emulators)
        pyautogui.keyDown('ctrl')
        for _ in range(10):
            pyautogui.scroll(-500)
            time.sleep(0.05)
        pyautogui.keyUp('ctrl')
        
        # Method 2: Pressing '-' key (Fallback for some emulators)
        for _ in range(5):
            pyautogui.press('-')
            time.sleep(0.1)
        
        time.sleep(0.5)

    def _execute_attack_sequence(self) -> bool:
        """Execute the complete attack sequence following your exact process"""
        try:
            # Ensure we are not stuck in any previous menus or popups
            self._escape_menu()
            
            # Zoom out before starting to see the whole base
            self._zoom_out()
            
            coords = self.coordinate_mapper.get_coordinates()
            
            if 'attack' not in coords:
                self.logger.error("Attack button not mapped")
                return False
            
            attack_button_delay = self.config.get('auto_attacker.attack_button_delay', 2.0)
            battle_min = self.config.get('auto_attacker.battle_duration_min', 160)
            battle_max = self.config.get('auto_attacker.battle_duration_max', 200)
            
            attack_coord = coords['attack']
            x, y = attack_coord['x'], attack_coord['y']
            self.logger.info(f"1️⃣ Clicking attack button at ({x}, {y})")
            add_human_like_hesitation(threshold=0.15)
            self._click_at(x, y, jitter_pixels=6)
            time.sleep(add_random_delay(attack_button_delay, variance=0.5))
            
            if not self._find_good_loot_target():
                self.logger.warning("Could not find good loot target")
                return False

            if not self.is_running:
                self.logger.info("Stopped before attack could begin")
                return False

            session_name = self._get_next_attack_session()
            self.logger.info(f"🎯 Starting attack with session: {session_name}")
            
            if not self.attack_player.play_attack(session_name, speed=1.0):
                self.logger.error("Failed to start attack recording")
                return False
            
            self.logger.info("✅ Attack recording started - troops deploying...")
            base_wait = get_varied_delay_range(battle_min, battle_max, variance=0.15)
            self.logger.info(f"⏳ Waiting {base_wait/60:.1f} minutes for battle completion...")
            time.sleep(base_wait)
            
            self._return_home()
            return True
            
        except Exception as e:
            self.logger.error(f"Attack sequence failed: {e}")
            return False
    
    def _find_good_loot_target(self, retry_after_end_button: bool = True) -> bool:
        """Find target with good loot following exact process"""
        coords = self.coordinate_mapper.get_coordinates()
        
        if 'find_a_match' not in coords:
            self.logger.error("find_a_match button not mapped")
            return False
        
        if 'attack_button_2' not in coords:
            self.logger.error("attack_button_2 (opponent attack button) not mapped")
            return False
        
        if 'next_button' not in coords:
            self.logger.error("next_button not mapped")
            return False
        
        use_ai = self.config.get('ai_analyzer.enabled', False)
        self.logger.info(f"AI Analysis is {'ENABLED' if use_ai else 'DISABLED'}.")
        
        search_attempts = 0
        max_attempts = self.max_search_attempts
        base_info_wait = self.config.get('auto_attacker.base_info_display_wait', 3.0)
        base_load_wait = self.config.get('auto_attacker.base_load_wait', 3.5)
        search_variance = self.config.get('auto_attacker.search_delay_variance', 0.35)
        load_variance = self.config.get('auto_attacker.base_load_variance', 0.35)
        patience_factor = self.config.get('auto_attacker.patience_fatigue_factor', 0.3)
        reject_wait = self.config.get('auto_attacker.base_wait_after_reject', 3.5)
        cooldown_wait = 1.5
        in_matchmaking = False

        while search_attempts < max_attempts and self.is_running:
            search_attempts += 1
            patience_fatigue = (search_attempts / max_attempts) * patience_factor

            if not in_matchmaking:
                find_coord = coords['find_a_match']
                x, y = find_coord['x'], find_coord['y']
                self.logger.info(f"2️⃣ Clicking find_a_match at ({x}, {y}) - Attempt {search_attempts}/{max_attempts}")
                self._click_at(x, y, jitter_pixels=8)
                add_human_like_hesitation(threshold=0.15)

                wait_time = add_random_delay(base_info_wait, variance=search_variance)
                self.logger.info(f"3️⃣ Waiting {wait_time:.1f} seconds for My Army screen...")
                time.sleep(wait_time)

                attack_2_coord = coords['attack_button_2']
                x, y = attack_2_coord['x'], attack_2_coord['y']
                self.logger.info(f"3️⃣ Clicking attack_button_2 at ({x}, {y}) to enter matchmaking...")
                self._click_at(x, y, jitter_pixels=8)
                add_human_like_hesitation(threshold=0.12)

                wait_time = add_random_delay(base_load_wait, variance=load_variance)
                self.logger.info(f"4️⃣ Waiting {wait_time:.1f} seconds for base to load...")
                time.sleep(wait_time)

                in_matchmaking = True
            else:
                wait_time = add_random_delay(base_load_wait, variance=load_variance)
                self.logger.info(f"4️⃣ Waiting {wait_time:.1f} seconds for next base to load...")
                time.sleep(wait_time)

            screenshot_path = self.screen_capture.capture_game_screen()
            if not screenshot_path:
                self.logger.warning("Could not take screenshot, skipping base...")
                continue

            decision_to_attack = False
            if use_ai:
                self.logger.info("5️⃣ Checking enemy loot with AI...")
                decision_to_attack, analysis = self._check_loot_with_ai(screenshot_path)
                
                # Check if AI detected a menu or popup instead of a base
                if analysis and self._is_menu_detected(analysis):
                    self.logger.warning("⚠️ Menu or popup detected (e.g. Season Pass)! Attempting to escape...")
                    self._escape_menu()
                    in_matchmaking = False  # Need to restart from home screen/attack menu
                    continue
            else:
                self.logger.info("5️⃣ Performing simple loot check (AI Disabled)...")
                decision_to_attack = self._check_loot()

            if random.random() < patience_fatigue:
                self.logger.info("Taking this base (getting impatient)...")
                decision_to_attack = True

            if decision_to_attack:
                self.logger.info("✅ Base is good! Proceeding with attack...")
                return True

            self.logger.info("❌ Base not suitable. Clicking next...")
            next_coord = coords['next_button']
            x, y = next_coord['x'], next_coord['y']
            add_human_like_hesitation(threshold=0.2)
            self._click_at(x, y, jitter_pixels=6)
            time.sleep(add_random_delay(reject_wait, variance=0.4))
            time.sleep(cooldown_wait)
        
        self.logger.warning(f"Could not find good loot after {max_attempts} attempts")
        
        if retry_after_end_button:
            self.logger.info("🔄 No good bases found - clicking end button to restart search...")
            self._click_end_button_and_retry()
            self.logger.info("🔄 Retrying base search after end button...")
            return self._find_good_loot_target(retry_after_end_button=False)
        
        return False
    
    def _check_loot_with_ai(self, screenshot_path: str) -> Tuple[bool, Optional[Dict]]:
        """Analyze the base with Gemini and decide whether to attack."""
        if not self.is_running:
            return False, None

        min_gold = int(self.config.get('ai_analyzer.min_gold', 300000) or 300000)
        min_elixir = int(self.config.get('ai_analyzer.min_elixir', 300000) or 300000)
        min_dark = int(self.config.get('ai_analyzer.min_dark_elixir', 2000) or 2000)
        max_th = int(self.config.get('ai_analyzer.max_townhall_level', 12) or 12)

        analysis = self.ai_analyzer.analyze_base(screenshot_path, min_gold, min_elixir, min_dark)

        if analysis.get("error"):
            self.logger.error(f"AI analysis failed: {analysis['reasoning']}")
            self.logger.warning("⚠️ Fallback: Attacking base due to AI error (Fail-Open strategy)")
            return True, analysis

        loot = analysis.get("loot", {})
        extracted_gold = int(loot.get("gold", 0) or 0)
        extracted_elixir = int(loot.get("elixir", 0) or 0)
        extracted_dark = int(loot.get("dark_elixir", 0) or 0)
        townhall_level = int(analysis.get("townhall_level", 0) or 0)
        
        self.logger.info(f"🔍 AI Extracted Loot: Gold={extracted_gold:,}, Elixir={extracted_elixir:,}, Dark={extracted_dark:,}")
        self.logger.info(f"🏰 Town Hall Level: {townhall_level}")
        self.logger.info(f"📋 Requirements: Gold={min_gold:,}, Elixir={min_elixir:,}, Dark={min_dark:,}, Max TH={max_th}")
        
        gold_ok = extracted_gold >= min_gold
        elixir_ok = extracted_elixir >= min_elixir
        dark_ok = extracted_dark >= min_dark
        th_ok = townhall_level <= max_th
        
        self.logger.info(f"✅/❌ Meets Requirements: Gold={gold_ok}, Elixir={elixir_ok}, Dark={dark_ok}, TH_Level={th_ok}")
        
        if townhall_level > max_th:
            self.logger.info(f"❌ Overriding AI: Town Hall {townhall_level} is too strong (max allowed: {max_th})")
            return False, analysis
        
        if not (gold_ok and elixir_ok and dark_ok):
            self.logger.info(f"❌ Loot requirements not met: Gold{' ' if gold_ok else ' NOT '}OK, Elixir{' ' if elixir_ok else ' NOT '}OK, Dark{' ' if dark_ok else ' NOT '}OK")
            return False, analysis

        recommendation = analysis.get("recommendation", "SKIP").upper()
        if recommendation != "ATTACK":
            self.logger.info(f"❌ AI recommends SKIP: {analysis.get('reasoning', 'No reason provided')}")
            return False, analysis
        
        self.logger.info(f"✅ AI recommends ATTACK!")
        return True, analysis

    def _check_loot(self) -> bool:
        """Check if enemy base has good loot"""
        coords = self.coordinate_mapper.get_coordinates()
        min_gold = int(self.config.get('ai_analyzer.min_gold', 300000) or 300000)
        min_elixir = int(self.config.get('ai_analyzer.min_elixir', 300000) or 300000)
        min_dark = int(self.config.get('ai_analyzer.min_dark_elixir', 5000) or 5000)
        
        loot_checks = {
            'gold': ('enemy_gold', min_gold),
            'elixir': ('enemy_elixir', min_elixir),
            'dark': ('enemy_dark_elixir', min_dark)
        }
        
        good_loot_count = 0
        
        for loot_name, (coord_name, min_value) in loot_checks.items():
            if coord_name in coords:
                coord = coords[coord_name]
                self.logger.info(f"Checking {loot_name} at ({coord['x']}, {coord['y']})")
                has_good_loot = True
                
                if has_good_loot:
                    good_loot_count += 1
                    self.logger.info(f"✅ {loot_name.capitalize()}: Good")
                else:
                    self.logger.info(f"❌ {loot_name.capitalize()}: Too low")
        
        is_good = good_loot_count >= 2
        self.logger.info(f"{'✅' if is_good else '❌'} Loot check {'PASSED' if is_good else 'FAILED'} - {good_loot_count}/3 loot types are good")
        return is_good
    
    def _click_end_button_and_retry(self) -> None:
        """Click end button when Town Hall is not detected and retry"""
        coords = self.coordinate_mapper.get_coordinates()
        
        if 'end_button' in coords:
            end_coord = coords['end_button']
            x, y = end_coord['x'], end_coord['y']
            x, y = self._verify_click_position(x, y)
            self.logger.info(f"🔄 Clicking end_button at ({x}, {y})")
            if random.random() < 0.15:
                self._click_with_jitter(x, y, jitter_pixels=5)
            else:
                pyautogui.click(x, y)
            time.sleep(add_random_delay(3.5, variance=0.35))
        else:
            self.logger.warning("end_button not mapped - cannot retry automatically")
    
    def _return_home(self) -> None:
        """Return to home base after battle completion"""
        coords = self.coordinate_mapper.get_coordinates()
        
        self.logger.info("🏠 Returning to home base...")
        
        if 'return_home' in coords:
            add_human_like_hesitation(threshold=0.25)
            home_coord = coords['return_home']
            x, y = home_coord['x'], home_coord['y']
            self.logger.info(f"Clicking return_home at ({x}, {y})")
            self._click_at(x, y, jitter_pixels=5)
            return_wait = self.config.get('auto_attacker.return_home_wait', 5.5)
            time.sleep(add_random_delay(return_wait, variance=0.4))
        else:
            self.logger.warning("return_home button not mapped")
    
    def _is_menu_detected(self, analysis: Dict) -> bool:
        """Check if AI detected a menu or popup instead of a base"""
        reasoning = analysis.get("reasoning", "").lower()
        if not reasoning:
            return False
            
        menu_keywords = ["menu", "screen", "rewards", "pass", "task", "card", "event", "shop", "not an enemy base", "not a base"]
        return any(keyword in reasoning for keyword in menu_keywords)

    def _escape_menu(self) -> None:
        """Try multiple ways to escape a menu or popup"""
        coords = self.coordinate_mapper.get_coordinates()
        
        # 1. Press ESC key (common for 'Back' or 'Close' in emulators)
        self.logger.info("⌨️ Pressing ESC to close menu...")
        pyautogui.press('esc')
        time.sleep(1.0)
        
        # 2. Click 'close_menu' if mapped (top-right X)
        if 'close_menu' in coords:
            cm = coords['close_menu']
            x, y = self._verify_click_position(cm['x'], cm['y'])
            self.logger.info(f"🖱️ Clicking close_menu at ({x}, {y})")
            pyautogui.click(x, y)
            time.sleep(1.5)
            
        # 3. Final safety ESC
        pyautogui.press('esc')
        time.sleep(1.0)

    def _get_next_attack_session(self) -> str:
        """Get a random attack variation from all configured attacks"""
        if not self.attack_sessions:
            return ""
        
        all_variations = []
        for variations in self.attack_sessions.values():
            all_variations.extend(variations)
        
        if not all_variations:
            return ""
        
        return random.choice(all_variations)
    
    def get_stats(self) -> Dict:
        """Get automation statistics"""
        if self.stats['start_time']:
            runtime = datetime.now() - self.stats['start_time']
            runtime_hours = runtime.total_seconds() / 3600
        else:
            runtime_hours = 0
        
        total_variations = sum(len(v) for v in self.attack_sessions.values())
        
        return {
            'is_running': self.is_running,
            'total_attacks': self.stats['total_attacks'],
            'successful_attacks': self.stats['successful_attacks'],
            'failed_attacks': self.stats['failed_attacks'],
            'success_rate': (self.stats['successful_attacks'] / max(self.stats['total_attacks'], 1)) * 100,
            'runtime_hours': runtime_hours,
            'attacks_per_hour': self.stats['total_attacks'] / max(runtime_hours, 1),
            'last_attack': self.stats['last_attack_time'].strftime("%H:%M:%S") if self.stats['last_attack_time'] else "None",
            'configured_attacks': self.attack_sessions.copy(),
            'total_variations': total_variations
        }
    
    def update_loot_requirements(self, min_gold: int = None, min_elixir: int = None, min_dark_elixir: int = None):
        """Update minimum loot requirements"""
        if min_gold is not None:
            self.config.set('ai_analyzer.min_gold', min_gold)
        if min_elixir is not None:
            self.config.set('ai_analyzer.min_elixir', min_elixir)
        if min_dark_elixir is not None:
            self.config.set('ai_analyzer.min_dark_elixir', min_dark_elixir)
        
        self.logger.info(f"Updated loot requirements: Gold={self.config.get('ai_analyzer.min_gold', 300000) or 300000}, Elixir={self.config.get('ai_analyzer.min_elixir', 300000) or 300000}, Dark={self.config.get('ai_analyzer.min_dark_elixir', 2000) or 2000}")
    
    def configure_buttons(self) -> Dict[str, str]:
        """Get list of required button mappings for the simplified automation"""
        return {
            'attack': 'Main attack button on home screen',
            'find_a_match': 'Find match/search button in attack screen',
            'attack_button_2': 'Green Attack! button on opponent info screen (to view full base)',
            'next_button': 'Next button to skip bases with low loot',
            'return_home': 'Return home button after battle completion',
            'close_menu': 'Close/X button to exit accidentally opened menus (top right)',
            'end_button': 'End/Cancel search button (usually bottom right during search)',
            'enemy_gold': 'Enemy gold display for loot checking',
            'enemy_elixir': 'Enemy elixir display for loot checking',
            'enemy_dark_elixir': 'Enemy dark elixir display for loot checking'
        }
    
 