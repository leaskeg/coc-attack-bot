import cv2
import numpy as np
from typing import List, Tuple, Optional
from PIL import Image
import pyautogui


class DeploymentDetector:
    """Detects deployment zones based on game board analysis"""
    
    def __init__(self, logger):
        self.logger = logger
        
        self.RED_LINE_LOWER = np.array([0, 80, 150])
        self.RED_LINE_UPPER = np.array([50, 200, 255])
        
        self.GOLD_COLLECTOR_LOWER = np.array([0, 100, 150])
        self.GOLD_COLLECTOR_UPPER = np.array([50, 180, 255])
        
        self.ELIXIR_COLLECTOR_LOWER = np.array([60, 50, 50])
        self.ELIXIR_COLLECTOR_UPPER = np.array([120, 150, 150])
    
    def get_red_lines_zones(self, region: Tuple[int, int, int, int]) -> List[Tuple[int, int]]:
        """
        Detect red lines (defenses) on game board within region
        Returns list of (x, y) points where red lines are detected
        """
        try:
            screenshot = pyautogui.screenshot(region=region)
            frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2HSV)
            
            mask = cv2.inRange(frame, self.RED_LINE_LOWER, self.RED_LINE_UPPER)
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
            
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            red_line_points = []
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > 50:
                    M = cv2.moments(contour)
                    if M["m00"] > 0:
                        cx = int(M["m10"] / M["m00"]) + region[0]
                        cy = int(M["m01"] / M["m00"]) + region[1]
                        red_line_points.append((cx, cy))
            
            self.logger.debug(f"Detected {len(red_line_points)} red line zones")
            return red_line_points
        
        except Exception as e:
            self.logger.error(f"Error detecting red lines: {e}")
            return []
    
    def get_collector_zones(self, region: Tuple[int, int, int, int], collector_type: str = "gold") -> List[Tuple[int, int]]:
        """
        Detect collectors (gold/elixir) on game board
        
        Args:
            region: Screen region to analyze
            collector_type: "gold" or "elixir"
            
        Returns:
            List of (x, y) points where collectors are detected
        """
        try:
            screenshot = pyautogui.screenshot(region=region)
            frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2HSV)
            
            if collector_type == "gold":
                lower = np.array([15, 100, 100])
                upper = np.array([35, 255, 255])
            elif collector_type == "elixir":
                lower = np.array([120, 100, 100])
                upper = np.array([160, 255, 255])
            else:
                return []
            
            mask = cv2.inRange(frame, lower, upper)
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
            
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            collector_points = []
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > 100:
                    M = cv2.moments(contour)
                    if M["m00"] > 0:
                        cx = int(M["m10"] / M["m00"]) + region[0]
                        cy = int(M["m01"] / M["m00"]) + region[1]
                        collector_points.append((cx, cy))
            
            self.logger.debug(f"Detected {len(collector_points)} {collector_type} collectors")
            return collector_points
        
        except Exception as e:
            self.logger.error(f"Error detecting {collector_type} collectors: {e}")
            return []
    
    def get_deployment_zones_near_defenses(self, game_region: Tuple[int, int, int, int], 
                                          deploy_distance: int = 80) -> List[Tuple[int, int]]:
        """
        Calculate deployment zones near red lines (defenses)
        
        Args:
            game_region: Game board region
            deploy_distance: Distance (pixels) from defenses to deploy near
            
        Returns:
            List of recommended deployment coordinates
        """
        red_zones = self.get_red_lines_zones(game_region)
        
        if not red_zones:
            self.logger.warning("No red lines (defenses) detected - using fallback zones")
            return self._get_fallback_deployment_zones(game_region)
        
        deployment_zones = []
        for rx, ry in red_zones:
            for angle in range(0, 360, 45):
                rad = np.radians(angle)
                dx = int(deploy_distance * np.cos(rad))
                dy = int(deploy_distance * np.sin(rad))
                
                new_x = rx + dx
                new_y = ry + dy
                
                if self._is_valid_deployment_zone(new_x, new_y, game_region):
                    deployment_zones.append((new_x, new_y))
        
        self.logger.info(f"Calculated {len(deployment_zones)} deployment zones near defenses")
        return deployment_zones
    
    def get_deployment_zones_near_collectors(self, game_region: Tuple[int, int, int, int],
                                           deploy_distance: int = 60) -> List[Tuple[int, int]]:
        """
        Calculate deployment zones near collectors (gold/elixir)
        
        Args:
            game_region: Game board region
            deploy_distance: Distance (pixels) from collectors to deploy near
            
        Returns:
            List of recommended deployment coordinates
        """
        gold_zones = self.get_collector_zones(game_region, "gold")
        elixir_zones = self.get_collector_zones(game_region, "elixir")
        collector_zones = gold_zones + elixir_zones
        
        if not collector_zones:
            self.logger.warning("No collectors detected - using fallback zones")
            return self._get_fallback_deployment_zones(game_region)
        
        deployment_zones = []
        for cx, cy in collector_zones:
            for angle in range(0, 360, 60):
                rad = np.radians(angle)
                dx = int(deploy_distance * np.cos(rad))
                dy = int(deploy_distance * np.sin(rad))
                
                new_x = cx + dx
                new_y = cy + dy
                
                if self._is_valid_deployment_zone(new_x, new_y, game_region):
                    deployment_zones.append((new_x, new_y))
        
        self.logger.info(f"Calculated {len(deployment_zones)} deployment zones near collectors")
        return deployment_zones
    
    def _is_valid_deployment_zone(self, x: int, y: int, game_region: Tuple[int, int, int, int]) -> bool:
        """Check if coordinates are within valid deployment area"""
        x_min, y_min, width, height = game_region
        x_max = x_min + width
        y_max = y_min + height
        
        padding = 50
        return (x_min + padding < x < x_max - padding and 
                y_min + padding < y < y_max - padding)
    
    def _get_fallback_deployment_zones(self, game_region: Tuple[int, int, int, int]) -> List[Tuple[int, int]]:
        """Provide default deployment zones if detection fails"""
        x, y, w, h = game_region
        center_x, center_y = x + w // 2, y + h // 2
        
        zones = [
            (x + w // 4, y + h // 4),
            (x + 3 * w // 4, y + h // 4),
            (x + w // 4, y + 3 * h // 4),
            (x + 3 * w // 4, y + 3 * h // 4),
        ]
        
        self.logger.info("Using fallback deployment zones")
        return zones
    
    def get_best_deployment_point(self, zones: List[Tuple[int, int]], 
                                 avoid_points: Optional[List[Tuple[int, int]]] = None,
                                 min_distance: int = 40) -> Optional[Tuple[int, int]]:
        """
        Select best deployment point from list, avoiding previous deployments
        
        Args:
            zones: List of candidate deployment zones
            avoid_points: Points to avoid (previous deployments)
            min_distance: Minimum distance from avoid_points
            
        Returns:
            Best deployment coordinate or None
        """
        if not zones:
            return None
        
        if avoid_points is None:
            avoid_points = []
        
        for zone_x, zone_y in zones:
            valid = True
            for avoid_x, avoid_y in avoid_points:
                distance = np.sqrt((zone_x - avoid_x)**2 + (zone_y - avoid_y)**2)
                if distance < min_distance:
                    valid = False
                    break
            
            if valid:
                return (zone_x, zone_y)
        
        return zones[0] if zones else None
