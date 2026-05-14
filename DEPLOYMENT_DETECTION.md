# Deployment Detection System

## Overview

The bot can now **automatically detect** red lines (defensive structures) and collectors on the game board, then calculate optimal deployment zones near them.

## How It Works

### 1. **Red Lines Detection (Defenses)**
- **Color Range**: Detects pixels in the red/pink color spectrum (BGR: 0-50, 80-200, 150-255)
- **Method**: Contour detection with morphological closing to fill gaps
- **Result**: Identifies locations of all defensive structures on the board
- **Deployment Zones**: Calculates 8 deployment points around each defense (45° intervals at ~80px distance)

### 2. **Collector Detection (Gold/Elixir)**
- **Gold Collectors**: Yellow/gold color detection (HSV hue 15-35)
- **Elixir Collectors**: Purple/magenta color detection (HSV hue 120-160)
- **Method**: Color range filtering + contour analysis
- **Result**: Finds all resource-generating buildings
- **Deployment Zones**: Calculates 6 deployment points around each collector (60° intervals at ~60px distance)

### 3. **Deployment Zone Calculation**
Once collectors/defenses are found:
1. Creates virtual circles around each structure
2. Samples points at regular angle intervals
3. Filters out invalid zones (too close to edges)
4. Returns list of recommended deployment coordinates

## Configuration in GUI

### Strategy Settings Tab → **Attack Strategy Settings**

```
Deploy near red lines (defenses):  ✓ ENABLED
Deploy near collectors:             ✓ ENABLED
```

**Enable/disable these toggles to control deployment strategy:**
- ✓ **Both ON**: Mix deployment between defenses and collectors
- ✓ **Defenses only**: Prioritize taking out defensive structures first
- ✓ **Collectors only**: Focus on raiding resources
- ☐ **Both OFF**: Manual deployment (no auto-detection)

## Usage in Code

### Basic Detection
```python
from src.bot_controller import BotController

controller = BotController()
game_region = controller.detect_game_window()

# Get deployment zones based on strategy settings
zones = controller.auto_attacker.find_deployment_zones(game_region)
print(f"Found {len(zones)} deployment zones")
# Output: [(523, 340), (612, 280), (451, 420), ...]
```

### Smart Deployment (Avoid Previous Spots)
```python
previous_deployments = [(523, 340), (612, 280)]

# Select next deployment point avoiding previous ones
next_point = controller.auto_attacker.select_deployment_point(zones, previous_deployments)
print(f"Deploying troops at: {next_point}")
```

### Direct Detector Usage
```python
from src.core.deployment_detector import DeploymentDetector
from src.utils.logger import Logger

detector = DeploymentDetector(logger=Logger())

# Get only defense zones
defense_zones = detector.get_deployment_zones_near_defenses(game_region, deploy_distance=80)

# Get only collector zones
collector_zones = detector.get_deployment_zones_near_collectors(game_region, deploy_distance=60)

# Get raw color-detected positions
red_positions = detector.get_red_lines_zones(game_region)
gold_positions = detector.get_collector_zones(game_region, "gold")
elixir_positions = detector.get_collector_zones(game_region, "elixir")
```

## Color Detection Fine-Tuning

If detection isn't working well for your game version, adjust color ranges in `src/core/deployment_detector.py`:

```python
class DeploymentDetector:
    # Red lines (defenses) - BGR format
    self.RED_LINE_LOWER = np.array([0, 80, 150])    # Adjust these
    self.RED_LINE_UPPER = np.array([50, 200, 255])  # For your game colors
    
    # Gold collectors - HSV format
    # For gold: increase hue upper range if too yellow/orange
    
    # Elixir collectors - HSV format
    # For elixir: adjust saturation if color varies
```

## Performance Notes

- **Detection Speed**: ~200-500ms per analysis (depends on image size)
- **CPU Usage**: Moderate (OpenCV contour detection)
- **Recommended**: Use every 2-3 troops, not on every single deployment
- **Fallback**: If detection fails, uses default grid-based zones

## Debugging

Enable debug logging to see detection results:

```python
controller.logger.info("Red line zones detected at: %s" % defense_zones)
controller.logger.info("Collector zones detected at: %s" % collector_zones)
```

Check `logs/` directory for detailed debug information.

## Limitations

1. **Lighting Dependent**: Bright/dark game themes may affect color detection
2. **Resolution Sensitive**: Designed for 480p+ game windows
3. **Crowded Bases**: May have difficulty in very dense defense clusters
4. **Partial Walls**: Pink walls can be detected as defenses (filter by area size helps)

## Future Improvements

- [ ] Machine Learning model for structure recognition
- [ ] Adaptive color detection based on game theme
- [ ] Heat map generation showing safest deployment zones
- [ ] Integration with AI Analyzer for strategy optimization
