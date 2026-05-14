import cv2
import numpy as np
from typing import Optional, Tuple, List, Dict
import pyautogui
from PIL import Image


class DonationDetector:
    """Detects donation requests and available troops/spells"""
    
    def __init__(self, logger):
        self.logger = logger
    
    def is_in_clan_chat(self, game_region: Tuple[int, int, int, int]) -> bool:
        """Check if clan chat/donation screen is visible"""
        try:
            self.logger.debug(f"[DONATION FLOW] Checking clan chat presence in region {game_region}")
            
            screenshot = pyautogui.screenshot(region=game_region)
            frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            self.logger.debug(f"  → Screenshot captured: {frame.shape[0]}x{frame.shape[1]} pixels")
            
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            
            brown_lower = np.array([5, 20, 40])
            brown_upper = np.array([30, 200, 220])
            self.logger.debug(f"  → Brown HSV range: {brown_lower} to {brown_upper}")
            
            mask = cv2.inRange(hsv, brown_lower, brown_upper)
            pixel_count = cv2.countNonZero(mask)
            
            threshold = (frame.shape[0] * frame.shape[1]) * 0.02
            self.logger.debug(f"  → Brown pixels found: {pixel_count}, threshold: {threshold:.0f}")
            
            result = pixel_count > threshold
            self.logger.info(f"[DONATION] Clan chat presence: {'YES ✓' if result else 'NO ✗'}")
            
            return result
        
        except Exception as e:
            self.logger.error(f"[DONATION ERROR] Error checking clan chat: {e}", exc_info=True)
            return False
    
    def find_clan_chat_button(self, game_region: Tuple[int, int, int, int]) -> Optional[Tuple[int, int]]:
        """
        Find the clan chat button/icon to open clan chat
        
        Returns:
            (x, y) coordinates of clan chat button, or None if not found
        """
        try:
            screenshot = pyautogui.screenshot(region=game_region)
            frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            
            gray_lower = np.array([0, 0, 80])
            gray_upper = np.array([180, 50, 200])
            
            mask = cv2.inRange(hsv, gray_lower, gray_upper)
            
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            screen_area = frame.shape[0] * frame.shape[1]
            min_area = max(500, int(screen_area * 0.0005))
            max_area = min(5000, int(screen_area * 0.01))
            
            for contour in contours:
                area = cv2.contourArea(contour)
                if min_area < area < max_area:
                    M = cv2.moments(contour)
                    if M["m00"] > 0:
                        cx = int(M["m10"] / M["m00"]) + game_region[0]
                        cy = int(M["m01"] / M["m00"]) + game_region[1]
                        self.logger.info(f"Clan chat button found at ({cx}, {cy})")
                        return (cx, cy)
            
            self.logger.warning("Clan chat button not found")
            return None
        
        except Exception as e:
            self.logger.error(f"Error finding clan chat button: {e}")
            return None
    
    def find_close_button(self, game_region: Tuple[int, int, int, int]) -> Optional[Tuple[int, int]]:
        """
        Find the close/X button on clan chat screen
        
        Returns:
            (x, y) coordinates of close button, or None if not found
        """
        try:
            screenshot = pyautogui.screenshot(region=game_region)
            frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            
            red_lower_1 = np.array([0, 100, 100])
            red_upper_1 = np.array([10, 255, 255])
            red_lower_2 = np.array([170, 100, 100])
            red_upper_2 = np.array([180, 255, 255])
            
            mask1 = cv2.inRange(hsv, red_lower_1, red_upper_1)
            mask2 = cv2.inRange(hsv, red_lower_2, red_upper_2)
            mask = cv2.bitwise_or(mask1, mask2)
            
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours:
                area = cv2.contourArea(contour)
                if 100 < area < 5000:
                    M = cv2.moments(contour)
                    if M["m00"] > 0:
                        cx = int(M["m10"] / M["m00"]) + game_region[0]
                        cy = int(M["m01"] / M["m00"]) + game_region[1]
                        self.logger.info(f"Close button found at ({cx}, {cy})")
                        return (cx, cy)
            
            self.logger.warning("Close button not found")
            return None
        
        except Exception as e:
            self.logger.error(f"Error finding close button: {e}")
            return None
    
    def detect_donation_requests(self, game_region: Tuple[int, int, int, int]) -> List[Dict]:
        """
        Check if there are any donation requests visible (simplified check)
        Just indicates whether requests exist, not individual requests
        
        Returns:
            List with single dict if requests found, empty list otherwise
        """
        try:
            if self.is_in_clan_chat(game_region):
                return [{'has_request': True, 'position': (0, 0)}]
            return []
        
        except Exception as e:
            self.logger.error(f"Error detecting requests: {e}")
            return []
    
    def get_available_troops(self, game_region: Tuple[int, int, int, int]) -> List[Tuple[int, int]]:
        """
        Detect available (non-greyed) troop icons in donation screen
        
        Greyed icons = unavailable (insufficient troops)
        Colored icons = available for donation
        
        Returns:
            List of (x, y) coordinates of clickable troop icons
        """
        try:
            self.logger.debug(f"[DONATION FLOW] Scanning for available troops in region {game_region}")
            
            screenshot = pyautogui.screenshot(region=game_region)
            frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            self.logger.debug(f"  → Captured {frame.shape[0]}x{frame.shape[1]} image for troop analysis")
            
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            
            screen_area = frame.shape[0] * frame.shape[1]
            min_area = int(screen_area * 0.003)
            max_area = int(screen_area * 0.015)
            self.logger.debug(f"  → Area thresholds: min={min_area}, max={max_area}")
            
            available_troops = []
            hue_ranges = [(0, 10), (15, 35), (40, 80), (85, 105), (115, 135), (150, 180)]
            
            for hue_idx, (hue_min, hue_max) in enumerate(hue_ranges, 1):
                lower = np.array([hue_min, 100, 80])
                upper = np.array([hue_max, 255, 255])
                
                mask = cv2.inRange(hsv, lower, upper)
                kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
                mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
                
                contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                self.logger.debug(f"  → Hue range {hue_idx}/6 ({hue_min}-{hue_max}): {len(contours)} contours found")
                
                for contour in contours:
                    area = cv2.contourArea(contour)
                    if min_area < area < max_area:
                        x, y, w, h = cv2.boundingRect(contour)
                        aspect = float(w) / h if h > 0 else 0
                        if 0.5 < aspect < 2.0:
                            M = cv2.moments(contour)
                            if M["m00"] > 0:
                                cx = int(M["m10"] / M["m00"]) + game_region[0]
                                cy = int(M["m01"] / M["m00"]) + game_region[1]
                                
                                is_duplicate = any(abs(cx - x) < 60 and abs(cy - y) < 60 
                                                  for x, y in available_troops)
                                if not is_duplicate:
                                    available_troops.append((cx, cy))
                                    self.logger.debug(f"    ✓ Troop detected at ({cx}, {cy}) | Area: {area:.0f}, Aspect: {aspect:.2f}")
            
            self.logger.info(f"[DONATION] Troop scan result: {len(available_troops)} available troops detected")
            if not available_troops:
                self.logger.warning("[DONATION] No available troops - all may be greyed out or insufficient inventory")
            else:
                for idx, (tx, ty) in enumerate(available_troops, 1):
                    self.logger.debug(f"  Troop {idx}: ({tx}, {ty})")
            
            return available_troops
        
        except Exception as e:
            self.logger.error(f"[DONATION ERROR] Error detecting available troops: {e}", exc_info=True)
            return []
    
    def get_available_spells(self, game_region: Tuple[int, int, int, int]) -> List[Tuple[int, int]]:
        """
        Detect available (non-greyed) spell icons in donation screen
        
        Returns:
            List of (x, y) coordinates of clickable spell icons
        """
        try:
            self.logger.debug(f"[DONATION FLOW] Scanning for available spells in region {game_region}")
            
            screenshot = pyautogui.screenshot(region=game_region)
            frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            self.logger.debug(f"  → Captured {frame.shape[0]}x{frame.shape[1]} image for spell analysis")
            
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            
            screen_area = frame.shape[0] * frame.shape[1]
            min_area = int(screen_area * 0.004)
            max_area = int(screen_area * 0.018)
            self.logger.debug(f"  → Spell area thresholds: min={min_area}, max={max_area}")
            
            available_spells = []
            
            lower = np.array([15, 120, 100])
            upper = np.array([30, 255, 255])
            self.logger.debug(f"  → Gold/Yellow HSV range: {lower} to {upper}")
            
            mask = cv2.inRange(hsv, lower, upper)
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
            
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            self.logger.debug(f"  → Found {len(contours)} spell contours")
            
            for contour in contours:
                area = cv2.contourArea(contour)
                if min_area < area < max_area:
                    x, y, w, h = cv2.boundingRect(contour)
                    aspect = float(w) / h if h > 0 else 0
                    if 0.6 < aspect < 1.8:
                        M = cv2.moments(contour)
                        if M["m00"] > 0:
                            cx = int(M["m10"] / M["m00"]) + game_region[0]
                            cy = int(M["m01"] / M["m00"]) + game_region[1]
                            available_spells.append((cx, cy))
                            self.logger.debug(f"    ✓ Spell detected at ({cx}, {cy}) | Area: {area:.0f}, Aspect: {aspect:.2f}")
            
            self.logger.info(f"[DONATION] Spell scan result: {len(available_spells)} available spells detected")
            if available_spells:
                for idx, (sx, sy) in enumerate(available_spells, 1):
                    self.logger.debug(f"  Spell {idx}: ({sx}, {sy})")
            
            return available_spells
        
        except Exception as e:
            self.logger.error(f"[DONATION ERROR] Error detecting available spells: {e}", exc_info=True)
            return []
    
    def is_donate_button_visible(self, game_region: Tuple[int, int, int, int]) -> Optional[Tuple[int, int]]:
        """
        Detect green "Donate" button - matches bright lime green rectangular button
        
        Returns:
            (x, y) coordinates of donate button center, or None if not found
        """
        try:
            self.logger.debug(f"[DONATION FLOW] Looking for DONATE button in region {game_region}")
            
            screenshot = pyautogui.screenshot(region=game_region)
            frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            self.logger.debug(f"  → Captured {frame.shape[0]}x{frame.shape[1]} image for button detection")
            
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            
            green_lower = np.array([25, 70, 100])
            green_upper = np.array([95, 255, 255])
            self.logger.debug(f"  → Green HSV range: {green_lower} to {green_upper}")
            
            mask = cv2.inRange(hsv, green_lower, green_upper)
            
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
            
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            self.logger.debug(f"  → Found {len(contours)} green contours")
            
            screen_area = frame.shape[0] * frame.shape[1]
            
            best_match = None
            best_score = 0
            
            for idx, contour in enumerate(contours, 1):
                area = cv2.contourArea(contour)
                
                if area < screen_area * 0.003 or area > screen_area * 0.15:
                    continue
                
                x, y, w, h = cv2.boundingRect(contour)
                
                if w < 20 or h < 10:
                    continue
                
                aspect = float(w) / h if h > 0 else 0
                
                if aspect < 1.5:
                    continue
                
                circularity = 4 * np.pi * area / (cv2.arcLength(contour, True) ** 2) if cv2.arcLength(contour, True) > 0 else 0
                
                score = area * aspect
                self.logger.debug(f"    Contour {idx}: Area={area:.0f}, Aspect={aspect:.2f}, Score={score:.0f}")
                
                if score > best_score:
                    best_match = (x, y, w, h)
                    best_score = score
            
            if best_match:
                x, y, w, h = best_match
                cx = x + w // 2 + game_region[0]
                cy = y + h // 2 + game_region[1]
                self.logger.info(f"[DONATION] Donate button found at ({cx}, {cy}) | Best score: {best_score:.0f}")
                return (cx, cy)
            
            self.logger.debug("[DONATION] Donate button not found on screen - no pending donation requests")
            return None
        
        except Exception as e:
            self.logger.error(f"[DONATION ERROR] Error detecting donate button: {e}", exc_info=True)
            return None
    
    def find_donate_button_template(self, game_region: Tuple[int, int, int, int], 
                                    template_path: str = "donate_button_template.png") -> Optional[Tuple[int, int]]:
        """
        Find donate button using template matching against a saved button image
        
        Args:
            game_region: Game window bounds (x, y, w, h)
            template_path: Path to donate button template image
        
        Returns:
            (x, y) coordinates of button center, or None if not found
        """
        try:
            import os
            
            self.logger.debug(f"[DONATION FLOW] Template matching for donate button using: {template_path}")
            
            if not os.path.exists(template_path):
                self.logger.warning(f"[DONATION] Template file not found: {template_path} (falling back to color detection)")
                return self.is_donate_button_visible(game_region)
            
            self.logger.debug(f"  → Template file exists: {template_path}")
            
            screenshot = pyautogui.screenshot(region=game_region)
            frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            self.logger.debug(f"  → Screenshot: {frame.shape[0]}x{frame.shape[1]}")
            
            template = cv2.imread(template_path)
            if template is None:
                self.logger.error(f"[DONATION] Failed to load template: {template_path}")
                return None
            
            self.logger.debug(f"  → Template size: {template.shape[0]}x{template.shape[1]}")
            
            result = cv2.matchTemplate(frame, template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            
            confidence_threshold = 0.55
            
            self.logger.info(f"[DONATION] Template match confidence: {max_val:.3f} (threshold: {confidence_threshold})")
            
            if max_val < confidence_threshold:
                self.logger.debug(f"[DONATION] Template match confidence too low: {max_val:.3f} < {confidence_threshold} (no donation requests)")
                return None
            
            x, y = max_loc
            th, tw = template.shape[:2]
            cx = x + tw // 2 + game_region[0]
            cy = y + th // 2 + game_region[1]
            
            self.logger.info(f"[DONATION] Donate button found via template at ({cx}, {cy}) | Confidence: {max_val:.3f}")
            return (cx, cy)
        
        except Exception as e:
            self.logger.error(f"[DONATION ERROR] Error in template matching: {e}", exc_info=True)
            return None
    
    def find_troops_by_templates(self, game_region: Tuple[int, int, int, int],
                                template_dir: str = "troop_templates",
                                confidence: float = 0.65) -> List[Tuple[int, int]]:
        """
        Find available (colored) troops by matching template images.
        Place colored troop icon PNGs in template_dir/.
        Greyed-out troops won't match colored templates.

        Returns:
            List of (x, y) screen coordinates for each matched troop.
        """
        import os
        try:
            if not os.path.isdir(template_dir):
                self.logger.warning(f"Template dir not found: {template_dir}")
                return []

            templates = [
                f for f in os.listdir(template_dir)
                if f.lower().endswith((".png", ".jpg", ".jpeg"))
            ]
            if not templates:
                self.logger.warning(f"No template images found in {template_dir}")
                return []

            screenshot = pyautogui.screenshot(region=game_region)
            frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

            found = []
            for tpl_file in templates:
                tpl_path = os.path.join(template_dir, tpl_file)
                tpl = cv2.imread(tpl_path)
                if tpl is None:
                    self.logger.warning(f"Failed to load template: {tpl_file}")
                    continue

                if tpl.shape[0] > frame.shape[0] or tpl.shape[1] > frame.shape[1]:
                    self.logger.warning(f"Template {tpl_file} larger than scan region, skipping")
                    continue

                result = cv2.matchTemplate(frame, tpl, cv2.TM_CCOEFF_NORMED)
                locs = np.where(result >= confidence)

                th, tw = tpl.shape[:2]
                for pt in zip(*locs[::-1]):
                    cx = pt[0] + tw // 2 + game_region[0]
                    cy = pt[1] + th // 2 + game_region[1]
                    is_duplicate = any(abs(cx - ex) < 50 and abs(cy - ey) < 50 for ex, ey in found)
                    if not is_duplicate:
                        is_greyed = self._is_pixel_greyed_out(screenshot, pt[0], pt[1], tw, th)
                        if not is_greyed:
                            found.append((cx, cy))
                            self.logger.debug(f"Matched {tpl_file} at ({cx}, {cy})")
                        else:
                            self.logger.debug(f"Skipped greyed-out match at ({cx}, {cy})")

            self.logger.info(f"Template matching found {len(found)} available troops")
            return found

        except Exception as e:
            self.logger.error(f"Error in find_troops_by_templates: {e}")
            return []
    
    def _is_pixel_greyed_out(self, screenshot, x: int, y: int, w: int, h: int) -> bool:
        """
        Check if a pixel region is greyed out (desaturated).
        Greyed-out icons have low saturation in HSV.
        
        Returns:
            True if greyed out, False if colored
        """
        try:
            frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            
            x1, x2 = max(0, x - w // 2), min(hsv.shape[1], x + w // 2)
            y1, y2 = max(0, y - h // 2), min(hsv.shape[0], y + h // 2)
            
            roi = hsv[y1:y2, x1:x2]
            if roi.size == 0:
                return False
            
            avg_saturation = np.mean(roi[:, :, 1])
            
            is_greyed = avg_saturation < 50
            self.logger.debug(f"    Saturation check at ({x}, {y}): {avg_saturation:.1f} → {'GREYED' if is_greyed else 'COLORED'}")
            return is_greyed
        except Exception as e:
            self.logger.warning(f"Error checking pixel greyness: {e}")
            return False
    
    def find_confirm_donate_button(self, game_region: Tuple[int, int, int, int]) -> Optional[Tuple[int, int]]:
        """
        Find the green "Donate" button in the troop selection popup.
        This is the confirmation button that sends the selected troops.
        
        Returns:
            (x, y) coordinates of button center, or None if not found
        """
        try:
            self.logger.debug(f"[DONATION FLOW] Looking for CONFIRM DONATE button in region {game_region}")
            
            screenshot = pyautogui.screenshot(region=game_region)
            frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            self.logger.debug(f"  → Captured {frame.shape[0]}x{frame.shape[1]} image for button detection")
            
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            
            green_lower = np.array([25, 70, 100])
            green_upper = np.array([95, 255, 255])
            
            mask = cv2.inRange(hsv, green_lower, green_upper)
            
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
            
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            self.logger.debug(f"  → Found {len(contours)} green contours")
            
            screen_area = frame.shape[0] * frame.shape[1]
            
            best_match = None
            best_score = 0
            
            for idx, contour in enumerate(contours, 1):
                area = cv2.contourArea(contour)
                
                if area < screen_area * 0.003 or area > screen_area * 0.15:
                    continue
                
                x, y, w, h = cv2.boundingRect(contour)
                
                if w < 20 or h < 10:
                    continue
                
                aspect = float(w) / h if h > 0 else 0
                
                if aspect < 1.5:
                    continue
                
                score = area * aspect
                self.logger.debug(f"    Contour {idx}: Area={area:.0f}, Aspect={aspect:.2f}, Score={score:.0f}")
                
                if score > best_score:
                    best_match = (x, y, w, h)
                    best_score = score
            
            if best_match:
                x, y, w, h = best_match
                cx = x + w // 2 + game_region[0]
                cy = y + h // 2 + game_region[1]
                self.logger.info(f"[DONATION] Confirm Donate button found at ({cx}, {cy})")
                return (cx, cy)
            
            self.logger.debug("[DONATION] Confirm Donate button not found")
            return None
        
        except Exception as e:
            self.logger.error(f"[DONATION ERROR] Error detecting confirm donate button: {e}", exc_info=True)
            return None
    
    def verify_donation_completed(self, game_region: Tuple[int, int, int, int]) -> bool:
        """
        Verify that the donation popup is closed/gone (indicating donation succeeded).
        Checks if donation button is no longer visible.
        
        Returns:
            True if popup is closed (donation succeeded), False if still visible
        """
        try:
            donate_btn = self.find_donate_button_template(game_region, "donate_button_template.png")
            is_closed = donate_btn is None
            
            if is_closed:
                self.logger.info("[DONATION] Donation popup closed - donation likely succeeded ✓")
            else:
                self.logger.warning("[DONATION] Donation popup still visible - donation may have failed")
            
            return is_closed
        
        except Exception as e:
            self.logger.error(f"[DONATION ERROR] Error verifying donation: {e}")
            return False

    def can_donate_more_troops(self, game_region: Tuple[int, int, int, int], 
                              max_troops: int = 55) -> int:
        """
        Read 'Donate Troops: X/55' counter and return remaining capacity
        
        Returns:
            Number of troops that can still be donated (0-55)
        """
        try:
            available = self.get_available_troops(game_region)
            remaining_capacity = max_troops - len(available)
            
            self.logger.debug(f"Troop donation capacity: {remaining_capacity}/{max_troops}")
            return max(0, remaining_capacity)
        
        except:
            return 0
    
    def can_donate_more_spells(self, game_region: Tuple[int, int, int, int], 
                              max_spells: int = 3) -> int:
        """
        Read 'Donate Spells: X/3' counter and return remaining capacity
        
        Returns:
            Number of spells that can still be donated (0-3)
        """
        try:
            available = self.get_available_spells(game_region)
            remaining_capacity = max_spells - len(available)
            
            self.logger.debug(f"Spell donation capacity: {remaining_capacity}/{max_spells}")
            return max(0, remaining_capacity)
        
        except:
            return 0
    
    def create_debug_screenshot(self, game_region: Tuple[int, int, int, int], output_path: str = "donation_debug.png") -> str:
        """
        Create a debug screenshot with circles around detected items
        
        Returns:
            Path to the saved debug screenshot
        """
        try:
            screenshot = pyautogui.screenshot(region=game_region)
            frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            
            troops = self.get_available_troops(game_region)
            spells = self.get_available_spells(game_region)
            donate_btn = self.is_donate_button_visible(game_region)
            
            for tx, ty in troops:
                rx = tx - game_region[0]
                ry = ty - game_region[1]
                if 0 <= rx < frame.shape[1] and 0 <= ry < frame.shape[0]:
                    cv2.circle(frame, (rx, ry), 20, (0, 255, 0), 3)
                    cv2.putText(frame, "T", (rx - 8, ry + 8), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            for sx, sy in spells:
                rx = sx - game_region[0]
                ry = sy - game_region[1]
                if 0 <= rx < frame.shape[1] and 0 <= ry < frame.shape[0]:
                    cv2.circle(frame, (rx, ry), 20, (255, 255, 0), 3)
                    cv2.putText(frame, "S", (rx - 8, ry + 8), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
            
            if donate_btn:
                rx = donate_btn[0] - game_region[0]
                ry = donate_btn[1] - game_region[1]
                if 0 <= rx < frame.shape[1] and 0 <= ry < frame.shape[0]:
                    cv2.circle(frame, (rx, ry), 25, (0, 165, 255), 4)
                    cv2.putText(frame, "D", (rx - 10, ry + 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 165, 255), 3)
            
            cv2.imwrite(output_path, frame)
            self.logger.info(f"Debug screenshot saved to {output_path}")
            return output_path
        
        except Exception as e:
            self.logger.error(f"Error creating debug screenshot: {e}")
            return ""
