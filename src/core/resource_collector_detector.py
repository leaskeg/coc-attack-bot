import cv2
import numpy as np
import pyautogui
from typing import List, Optional, Tuple, Dict
from PIL import Image
from ..utils.logger import Logger


class ResourceCollector:
    def __init__(self, x: int, y: int, resource_type: str, confidence: float):
        self.x = x
        self.y = y
        self.resource_type = resource_type
        self.confidence = confidence
        self.collected = False
        self.collection_time = None


class ResourceCollectorDetector:
    
    def __init__(self, logger: Optional[Logger] = None):
        self.logger = logger or Logger()
        self.collectors: List[ResourceCollector] = []
        self.gold_collector_hsv_range = (
            np.array([15, 100, 100]),
            np.array([35, 255, 255])
        )
        self.elixir_collector_hsv_range = (
            np.array([90, 100, 100]),
            np.array([130, 255, 255])
        )
        self.dark_elixir_collector_hsv_range = (
            np.array([130, 100, 100]),
            np.array([160, 255, 255])
        )
        self.min_collector_size = 20
        self.max_collector_size = 150
    
    def detect_collectors(self, game_region: Optional[Tuple[int, int, int, int]] = None) -> List[ResourceCollector]:
        
        try:
            if game_region:
                screenshot = pyautogui.screenshot(region=game_region)
                region_x, region_y = game_region[0], game_region[1]
            else:
                screenshot = pyautogui.screenshot()
                region_x, region_y = 0, 0
            
            frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2HSV)
            
            collectors = []
            
            gold_collectors = self._find_collectors_by_color(
                frame, self.gold_collector_hsv_range, 'GOLD', region_x, region_y
            )
            collectors.extend(gold_collectors)
            
            elixir_collectors = self._find_collectors_by_color(
                frame, self.elixir_collector_hsv_range, 'ELIXIR', region_x, region_y
            )
            collectors.extend(elixir_collectors)
            
            dark_elixir_collectors = self._find_collectors_by_color(
                frame, self.dark_elixir_collector_hsv_range, 'DARK_ELIXIR', region_x, region_y
            )
            collectors.extend(dark_elixir_collectors)
            
            self.collectors = collectors
            self.logger.info(f"Found {len(collectors)} collectors: "
                           f"Gold={sum(1 for c in collectors if c.resource_type == 'GOLD')}, "
                           f"Elixir={sum(1 for c in collectors if c.resource_type == 'ELIXIR')}, "
                           f"Dark={sum(1 for c in collectors if c.resource_type == 'DARK_ELIXIR')}")
            
            return collectors
        
        except Exception as e:
            self.logger.error(f"Collector detection failed: {e}")
            return []
    
    def get_available_collectors(self) -> List[ResourceCollector]:
        
        return [c for c in self.collectors if not c.collected]
    
    def get_closest_collector(self, current_x: int, current_y: int) -> Optional[ResourceCollector]:
        
        available = self.get_available_collectors()
        if not available:
            return None
        
        closest = min(available, key=lambda c: self._distance(current_x, current_y, c.x, c.y))
        return closest
    
    def mark_collected(self, collector: ResourceCollector) -> None:
        
        collector.collected = True
        collector.collection_time = pyautogui.time.time()
        self.logger.debug(f"Marked collector as collected: {collector.resource_type} @ ({collector.x}, {collector.y})")
    
    def get_collection_sequence(self, start_x: int, start_y: int) -> List[ResourceCollector]:
        
        sequence = []
        current_x, current_y = start_x, start_y
        
        while True:
            closest = self.get_closest_collector(current_x, current_y)
            if not closest:
                break
            
            sequence.append(closest)
            current_x, current_y = closest.x, closest.y
        
        return sequence
    
    def _find_collectors_by_color(self, frame: np.ndarray, hsv_range: Tuple,
                                 resource_type: str, offset_x: int, offset_y: int) -> List[ResourceCollector]:
        
        lower, upper = hsv_range
        mask = cv2.inRange(frame, lower, upper)
        
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        collectors = []
        for contour in contours:
            area = cv2.contourArea(contour)
            
            if area < self.min_collector_size:
                continue
            
            x, y, w, h = cv2.boundingRect(contour)
            size = max(w, h)
            
            if size > self.max_collector_size:
                continue
            
            center_x = x + w // 2 + offset_x
            center_y = y + h // 2 + offset_y
            
            confidence = min(1.0, area / (size * size))
            
            collector = ResourceCollector(center_x, center_y, resource_type, confidence)
            collectors.append(collector)
        
        return collectors
    
    def _distance(self, x1: int, y1: int, x2: int, y2: int) -> float:
        return ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
    
    def visualize_collectors(self, game_region: Optional[Tuple[int, int, int, int]] = None) -> Optional[str]:
        
        try:
            if game_region:
                screenshot = pyautogui.screenshot(region=game_region)
                region_x, region_y = game_region[0], game_region[1]
            else:
                screenshot = pyautogui.screenshot()
                region_x, region_y = 0, 0
            
            frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            
            colors = {'GOLD': (0, 215, 255), 'ELIXIR': (0, 255, 0), 'DARK_ELIXIR': (255, 0, 0)}
            
            for collector in self.collectors:
                color = colors.get(collector.resource_type, (255, 255, 255))
                x = collector.x - region_x
                y = collector.y - region_y
                
                cv2.circle(frame, (x, y), 15, color, 2)
                cv2.putText(frame, collector.resource_type[0], (x - 5, y + 5),
                          cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
            
            filename = f"collectors_visualization_{int(pyautogui.time.time())}.png"
            cv2.imwrite(filename, frame)
            self.logger.info(f"Visualization saved: {filename}")
            return filename
        
        except Exception as e:
            self.logger.error(f"Visualization failed: {e}")
            return None
