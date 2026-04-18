import json
import time
import random
import base64
import pyautogui
import keyboard
import threading
import cv2
import numpy as np
from io import BytesIO
from PIL import Image
from typing import Dict, List, Optional, Tuple
from .attack_recorder import AttackRecorder
from .screen_capture import ScreenCapture
from ..utils.config import Config
from ..utils.logger import Logger
from ..utils.screen_utils import is_coordinate_on_screen, get_virtual_screen_size
from ..utils.timing import human_move_duration, pixel_distance

class AttackPlayer:
    
    def _add_random_delay(self, base_delay: float, variance: float = 0.15) -> float:
        """Add randomness to delay (±variance %)"""
        factor = 1 + random.uniform(-variance, variance)
        return base_delay * factor
    
    def _add_coordinate_variance(self, x: int, y: int, variance_pixels: int = 5) -> Tuple[int, int]:
        """Add randomness to click coordinates (±variance pixels)"""
        offset_x = random.randint(-variance_pixels, variance_pixels)
        offset_y = random.randint(-variance_pixels, variance_pixels)
        return (x + offset_x, y + offset_y)
    
    def _find_troop_in_bar(self, icon_b64: str, confidence: float = 0.7) -> Optional[Tuple[int, int]]:
        """Use template matching to find a troop icon's current position in the troop bar"""
        try:
            icon_bytes = base64.b64decode(icon_b64)
            template_img = Image.open(BytesIO(icon_bytes))
            template = cv2.cvtColor(np.array(template_img), cv2.COLOR_RGB2BGR)

            screen_w, screen_h = pyautogui.size()
            bar_top = int(screen_h * 0.83)
            bar_region = (0, bar_top, screen_w, screen_h - bar_top)
            bar_screenshot = pyautogui.screenshot(region=bar_region)
            haystack = cv2.cvtColor(np.array(bar_screenshot), cv2.COLOR_RGB2BGR)

            result = cv2.matchTemplate(haystack, template, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(result)

            if max_val >= confidence:
                found_x = max_loc[0] + template.shape[1] // 2
                found_y = bar_top + max_loc[1] + template.shape[0] // 2
                return (found_x, found_y)

            return None
        except Exception as e:
            self.logger.error(f"Template matching failed: {e}")
            return None

    def _adjust_coordinates_for_window(self, x: int, y: int, recorded_bounds: Optional[Tuple] = None) -> Tuple[int, int]:
        """Adjust coordinates based on game window position change"""
        if not recorded_bounds:
            return (x, y)
        
        recorded_x, recorded_y, recorded_w, recorded_h = recorded_bounds
        
        current_bounds = self.screen_capture.find_game_window()
        if not current_bounds:
            return (x, y)
        
        current_x, current_y, current_w, current_h = current_bounds
        
        x_offset = current_x - recorded_x
        y_offset = current_y - recorded_y
        
        adjusted_x = x + x_offset
        adjusted_y = y + y_offset
        
        return (adjusted_x, adjusted_y)
    
    def __init__(self, logger: Optional[Logger] = None):
        self.logger = logger or Logger()
        self.attack_recorder = AttackRecorder(logger=self.logger)
        self.screen_capture = ScreenCapture()
        self.config = Config()
        self.is_playing = False
        self.current_playback = None
        self.playback_thread = None
        self.playback_speed = 1.0
        self.enable_click_variation = self.config.get("automation.enable_click_variation", True)
        self.click_variance_pixels = self.config.get("automation.click_variance_pixels", 5)
        
        self.logger.info("Player initialized")
        self.logger.info(f"Variation: {'enabled' if self.enable_click_variation else 'disabled'} (±{self.click_variance_pixels} pixels)")
        print("Controls:")
        print("  F8 - Pause/Resume")
        print("  F9 - Stop")
        print("  ESC - Emergency stop")
    
    def play_attack(self, session_name: str, speed: float = 1.0) -> bool:
        """Play back a recorded attack session"""
        if self.is_playing:
            self.logger.warning("Already playing an attack")
            return False
        
        # Load the recording
        recording = self.attack_recorder.load_recording(session_name)
        if not recording:
            self.logger.error(f"Could not load recording: {session_name}")
            return False
        
        self.current_playback = recording
        self.playback_speed = speed
        self.is_playing = True
        
        self.logger.info(f"=== PLAYING ATTACK SESSION: {session_name} ===")
        self.logger.info(f"Duration: {recording.get('duration', 0):.1f} seconds")
        self.logger.info(f"Actions: {len(recording.get('actions', []))}")
        self.logger.info(f"Speed: {speed}x")
        self.logger.info("Press F8 to pause, F9 to stop, ESC for emergency stop")

        time.sleep(random.uniform(0.4, 0.9))
        
        recorded_bounds = recording.get('game_window_bounds')
        
        self.playback_thread = threading.Thread(
            target=self._playback_loop, 
            args=(recording.get('actions', []), recorded_bounds)
        )
        self.playback_thread.daemon = True
        self.playback_thread.start()
        
        return True
    
    def stop_playback(self) -> None:
        """Stop the current playback"""
        if not self.is_playing:
            self.logger.warning("No playback active")
            return
        
        self.logger.info("Stopping playback")
        self.is_playing = False
        
        if self.playback_thread:
            self.playback_thread.join(timeout=2)
    
    def _playback_loop(self, actions: List[Dict], recorded_bounds: Optional[Tuple] = None) -> None:
        """
        Main playback loop with drift-corrected, human-like timing.

        Core principle: each action has an absolute target fire-time derived from
        its recorded timestamp.  We sleep only for however long remains until that
        target, so mouse-movement and click overhead are automatically absorbed
        rather than stacked on top of the recorded gaps.

        Human-like variance is still applied per-action:
          - Short gaps (<0.4s, burst mode) → ±15% jitter, rare 0.10-0.30s micro-pause
          - Long gaps (≥0.4s)             → ±25% jitter, 20% chance of extra 0.15-0.45s
            pause when exiting a burst
        """
        try:
            schedule_start = time.time()
            total_pause_time = 0.0
            last_timestamp = 0.0
            paused = False
            log_interval = max(1, len(actions) // 10)
            in_burst = False
            BURST_THRESHOLD = 0.40

            for i, action in enumerate(actions):
                if not self.is_playing:
                    break

                if keyboard.is_pressed('esc'):
                    self.logger.warning("Emergency stop activated")
                    break

                if keyboard.is_pressed('f9'):
                    self.logger.info("Playback stopped by user")
                    break

                if keyboard.is_pressed('f8'):
                    paused = not paused
                    self.logger.info(f"Playback {'paused' if paused else 'resumed'}")
                    while keyboard.is_pressed('f8'):
                        time.sleep(0.1)

                if paused:
                    pause_start = time.time()
                    while paused and self.is_playing:
                        time.sleep(0.1)
                        if keyboard.is_pressed('f8'):
                            paused = False
                            total_pause_time += time.time() - pause_start
                            self.logger.info("Playback resumed")
                            while keyboard.is_pressed('f8'):
                                time.sleep(0.1)

                if not self.is_playing:
                    break

                current_timestamp = action.get('timestamp', 0)
                target_elapsed = current_timestamp / self.playback_speed

                if i > 0:
                    raw_gap = (current_timestamp - last_timestamp) / self.playback_speed
                    if raw_gap < BURST_THRESHOLD:
                        in_burst = True
                        variance_offset = raw_gap * random.uniform(-0.15, 0.15)
                        if random.random() < 0.05:
                            variance_offset += random.uniform(0.10, 0.30)
                    else:
                        if in_burst and random.random() < 0.20:
                            variance_offset = random.uniform(0.15, 0.45)
                        else:
                            variance_offset = raw_gap * random.uniform(-0.25, 0.25)
                        in_burst = False
                    target_elapsed += variance_offset

                actual_elapsed = time.time() - schedule_start - total_pause_time
                sleep_needed = target_elapsed - actual_elapsed
                if sleep_needed > 0:
                    time.sleep(sleep_needed)

                self._execute_action(action, recorded_bounds, action_index=i + 1)
                last_timestamp = current_timestamp

                if (i + 1) % log_interval == 0 or i == len(actions) - 1:
                    progress = (i + 1) / len(actions) * 100
                    self.logger.info(f"Playback Progress: {progress:.1f}% ({i + 1}/{len(actions)})")

        except Exception as e:
            self.logger.error(f"Playback error: {e}")

        finally:
            self.is_playing = False
            self.logger.info("Playback completed")
    
    def _human_move_to(self, x: int, y: int, allow_overshoot: bool = True) -> None:
        """
        Move mouse to (x, y) with:
        - Distance-aware speed (Fitts' Law inspired)
        - Random tween curve selection
        - 10% chance of a tiny overshoot + micro-correction for distant targets
        """
        cx, cy = pyautogui.position()
        dist = pixel_distance(cx, cy, x, y)
        duration = human_move_duration(dist)

        tweens = [
            pyautogui.easeOutQuad,
            pyautogui.easeInOutQuad,
            pyautogui.linear,
        ]
        weights = [0.55, 0.35, 0.10]
        tween = random.choices(tweens, weights=weights, k=1)[0]

        if allow_overshoot and dist > 100 and random.random() < 0.10:
            overshoot_x = x + random.randint(-10, 10)
            overshoot_y = y + random.randint(-10, 10)
            pyautogui.moveTo(overshoot_x, overshoot_y,
                             duration=duration * 0.80, tween=tween)
            time.sleep(random.uniform(0.025, 0.07))
            pyautogui.moveTo(x, y,
                             duration=random.uniform(0.04, 0.10),
                             tween=pyautogui.easeOutQuad)
        else:
            pyautogui.moveTo(x, y, duration=duration, tween=tween)

    def _execute_action(self, action: Dict, recorded_bounds: Optional[Tuple] = None, action_index: int = -1) -> None:
        """Execute a single action"""
        action_type = action.get('type', '')
        orig_x = action.get('x', 0)
        orig_y = action.get('y', 0)
        timestamp = action.get('timestamp', 0)
        
        x, y = self._adjust_coordinates_for_window(orig_x, orig_y, recorded_bounds)
        
        label = f"[#{action_index}]" if action_index >= 0 else ""
        
        try:
            if action_type == 'click':
                if action.get('troop_bar_click') and action.get('troop_icon'):
                    matched = self._find_troop_in_bar(action['troop_icon'])
                    if matched:
                        x, y = matched
                        # Move to troop icon before clicking
                        self._human_move_to(x, y)
                        self.logger.debug(f"  CLICK {label} [TROOP MATCHED] t={timestamp:.2f}s  matched=({x}, {y})")
                    else:
                        self.logger.debug(f"  CLICK {label} [TROOP FALLBACK] t={timestamp:.2f}s  using recorded=({x}, {y})")

                if self.enable_click_variation:
                    final_x, final_y = self._add_coordinate_variance(x, y, self.click_variance_pixels)
                else:
                    final_x, final_y = x, y

                self._human_move_to(final_x, final_y)
                self.logger.debug(
                    f"  CLICK {label} t={timestamp:.2f}s  "
                    f"recorded=({orig_x}, {orig_y})  adjusted=({x}, {y})  final=({final_x}, {final_y})"
                )
                pyautogui.mouseDown(final_x, final_y)
                time.sleep(random.uniform(0.06, 0.19))
                pyautogui.mouseUp()
            elif action_type == 'move':
                pass
            elif action_type == 'delay':
                duration = action.get('duration', 1.0) / self.playback_speed
                randomized_duration = self._add_random_delay(duration, variance=0.15)
                self.logger.debug(f"  DELAY {label} t={timestamp:.2f}s  duration={randomized_duration:.2f}s")
                time.sleep(randomized_duration)
            elif action_type == 'drag':
                start_x = action.get('start_x', x)
                start_y = action.get('start_y', y)
                self.logger.debug(f"  DRAG  {label} t={timestamp:.2f}s  from=({start_x}, {start_y})  to=({x}, {y})")
                pyautogui.drag(x - start_x, y - start_y)
        
        except Exception as e:
            self.logger.error(f"Error executing action {action_type} at ({x}, {y}): {e}")
    
    def validate_recording(self, session_name: str) -> Dict[str, any]:
        """Validate a recording before playback (supports multi-monitor)"""
        recording = self.attack_recorder.load_recording(session_name)
        if not recording:
            return {'valid': False, 'error': 'Recording not found'}
        
        actions = recording.get('actions', [])
        if not actions:
            return {'valid': False, 'error': 'No actions in recording'}
        
        # Check virtual screen bounds (multi-monitor support)
        min_x, min_y, max_x, max_y = get_virtual_screen_size()
        out_of_bounds = []
        
        for i, action in enumerate(actions):
            x, y = action.get('x', 0), action.get('y', 0)
            if not is_coordinate_on_screen(x, y):
                out_of_bounds.append((i, x, y))
        
        result = {
            'valid': len(out_of_bounds) == 0,
            'total_actions': len(actions),
            'duration': recording.get('duration', 0),
            'out_of_bounds': out_of_bounds,
            'virtual_screen': f"({min_x}, {min_y}) to ({max_x}, {max_y})"
        }
        
        if out_of_bounds:
            result['error'] = f"{len(out_of_bounds)} actions are out of virtual screen bounds"
        
        return result
    
    def preview_recording(self, session_name: str) -> None:
        """Show a preview of the recording actions"""
        recording = self.attack_recorder.load_recording(session_name)
        if not recording:
            self.logger.error(f"Recording not found: {session_name}")
            return
        
        actions = recording.get('actions', [])
        
        self.logger.info(f"=== RECORDING PREVIEW: {session_name} ===")
        self.logger.info(f"Duration: {recording.get('duration', 0):.1f} seconds")
        print(f"Total actions: {len(actions)}")
        
        # Show action summary
        action_counts = {}
        for action in actions:
            action_type = action.get('type', 'unknown')
            action_counts[action_type] = action_counts.get(action_type, 0) + 1
        
        print("\nAction breakdown:")
        for action_type, count in action_counts.items():
            print(f"  {action_type}: {count}")
        
        # Show first few actions
        print(f"\nFirst 10 actions:")
        for i, action in enumerate(actions[:10]):
            timestamp = action.get('timestamp', 0)
            action_type = action.get('type', 'unknown')
            x, y = action.get('x', 0), action.get('y', 0)
            print(f"  {i+1:2d}. {timestamp:6.1f}s - {action_type} at ({x}, {y})")
        
        if len(actions) > 10:
            print(f"  ... and {len(actions) - 10} more actions")
    
    def set_playback_speed(self, speed: float) -> None:
        """Set the playback speed multiplier"""
        if speed <= 0:
            print("Speed must be positive")
            return
        
        self.playback_speed = speed
        print(f"Playback speed set to {speed}x") 