import random
import math
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

def human_move_duration(distance_px: float) -> float:
    """
    Return a realistic mouse-movement duration (seconds) for a given pixel distance.

    Loosely inspired by Fitts' Law: further targets take longer, but speed is
    non-linear and has natural jitter.  Values are tuned for a casual gamer
    who knows what they're clicking — fast but not robotic.

    Ranges:
        < 60 px  → micro-adjustment       0.04 – 0.11 s
        < 200 px → within-region tap      0.09 – 0.20 s
        < 450 px → cross-screen half-move 0.16 – 0.32 s
        ≥ 450 px → full-screen sweep      0.25 – 0.50 s
    """
    if distance_px < 60:
        base = random.uniform(0.04, 0.11)
    elif distance_px < 200:
        base = random.uniform(0.09, 0.20)
    elif distance_px < 450:
        base = random.uniform(0.16, 0.32)
    else:
        base = random.uniform(0.25, 0.50)

    jitter = random.gauss(0, 0.025)
    return max(0.035, base + jitter)

def pixel_distance(x1: int, y1: int, x2: int, y2: int) -> float:
    """Euclidean distance between two screen coordinates"""
    return math.hypot(x2 - x1, y2 - y1)
