import random
from typing import Tuple

def add_random_delay(base_delay: float, variance: float = 0.15) -> float:
    """Add randomness to delay (±variance %)"""
    factor = 1 + random.uniform(-variance, variance)
    return base_delay * factor

def add_coordinate_variance(x: int, y: int, variance_pixels: int = 5) -> Tuple[int, int]:
    """Add randomness to click coordinates (±variance pixels)"""
    offset_x = random.randint(-variance_pixels, variance_pixels)
    offset_y = random.randint(-variance_pixels, variance_pixels)
    return (x + offset_x, y + offset_y)

def add_human_like_hesitation(threshold: float = 0.1) -> None:
    """Occasional human-like pauses"""
    import time
    if random.random() < threshold:
        time.sleep(random.uniform(0.5, 2.0))

def get_varied_delay_range(min_delay: float, max_delay: float, variance: float = 0.2) -> float:
    """Get a random delay within min/max range with variance"""
    base_delay = random.uniform(min_delay, max_delay)
    return add_random_delay(base_delay, variance)
