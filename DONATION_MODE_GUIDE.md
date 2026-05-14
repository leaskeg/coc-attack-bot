# Donation-Only Mode Guide

## Overview

**Donation Mode** allows your bot to automatically support your clan by:
- ✅ Detecting clan members requesting donations
- ✅ Finding available (non-greyed) troop/spell icons  
- ✅ Auto-clicking and donating all available units
- ✅ Running 24/7 to help your clan

---

## How It Works

### Detection System

The bot detects:

1. **Non-Greyed Icons** = Available to donate (colored)
2. **Greyed Icons** = Not available (insufficient troops/spells)
3. **Donate Button** = Green button to submit donations
4. **Donation Requests** = Red request indicators from clan mates

### Icon Detection

```
AVAILABLE (click these):        NOT AVAILABLE (skip these):
┌─────────────────────────┐    ┌─────────────────────────┐
│ 🔴 Barbarian (colored)  │    │ ⚫ Archer (greyed out)   │
│ 🟡 Archer (colored)     │    │ ⚫ Giant (greyed out)    │
│ 🟢 Goblin (colored)     │    │ ⚫ Spell (greyed out)    │
└─────────────────────────┘    └─────────────────────────┘
```

---

## Usage Modes

### Mode 1: Pure Donation Loop
```python
from src.bot_controller import BotController
from DONATION_ONLY_MODE import donation_only_loop

controller = BotController()
donation_only_loop(controller, max_donations=100)
```

**Best for:**
- Clan wars support
- Farming clans
- Co-leaders managing donations
- 24/7 clan support bot

---

### Mode 2: Hybrid (Attack + Donate)
```python
from DONATION_ONLY_MODE import donation_with_attack_combo

donation_with_attack_combo(controller)
```

**Best for:**
- Active players who want personal farming + clan support
- Search for good bases first, donate while waiting
- Balanced offensive/support gameplay

---

### Mode 3: Quick Donation Checks
```python
from DONATION_ONLY_MODE import quick_donation_bot

quick_donation_bot(controller, max_quick_donations=20)
```

**Best for:**
- Background bot running while you play
- 5-second donation check intervals
- Light clan support without affecting your gameplay

---

## Available Methods

### Get Donation Info
```python
# Find what's available to donate
troops = controller.get_available_troops_to_donate()
# → [(523, 340), (612, 280), ...]

spells = controller.get_available_spells_to_donate()
# → [(451, 420), (390, 310), ...]

# Find the donate button
donate_btn = controller.find_donate_button()
# → (600, 400)
```

### Check Status
```python
# Check if in donation screen
if controller.is_in_donation_screen():
    print("In clan chat!")

# Get all requests
requests = controller.get_donation_requests()
# → [{'member_name': '...', 'requested_troops': ['X3', 'X1']}, ...]
```

---

## Configuration

Add to your config.json:

```json
{
  "donation_mode": {
    "enabled": true,
    "check_interval_seconds": 300,
    "max_donations_per_session": 100,
    "donate_troops": true,
    "donate_spells": true,
    "priority": "requests"  // or "available"
  }
}
```

---

## How to Click Available Icons

Since colors vary by game theme, the detector uses **color range detection**:

```python
# Get non-greyed icons
available = controller.get_available_troops_to_donate(game_region)

for x, y in available:
    print(f"Clicking troop at {x}, {y}")
    # TODO: pyautogui.click(x, y)
    # Add your click implementation here
```

### For Each Icon:
1. **Read HSV color** to detect if it's greyed or colored
2. **Filter by contour area** (troops are ~800-8000 pixels)
3. **Get center point** of the icon
4. **Return coordinates** ready to click

---

## Workflow Example

```python
def auto_donate_workflow():
    controller = BotController()
    game_region = controller.detect_game_window()
    
    print("Starting donation mode...")
    
    while True:
        # Step 1: Check if in clan chat
        if not controller.is_in_donation_screen(game_region):
            print("Waiting for clan chat...")
            time.sleep(5)
            continue
        
        # Step 2: Find available items
        troops = controller.get_available_troops_to_donate(game_region)
        spells = controller.get_available_spells_to_donate(game_region)
        
        if not troops and not spells:
            print("Nothing to donate")
            time.sleep(5)
            continue
        
        # Step 3: Click each item
        for x, y in troops:
            pyautogui.click(x, y)
            time.sleep(0.3)
        
        for x, y in spells:
            pyautogui.click(x, y)
            time.sleep(0.3)
        
        # Step 4: Click Donate button
        donate_btn = controller.find_donate_button(game_region)
        if donate_btn:
            pyautogui.click(donate_btn[0], donate_btn[1])
            print(f"✓ Donated {len(troops) + len(spells)} items!")
        
        time.sleep(300)  # Check again in 5 minutes
```

---

## Color Ranges (If You Need to Tweak)

Adjust in `src/core/donation_detector.py`:

### Troop Icons (Colored vs Greyed)
```python
# Colored troops
lower = np.array([hue_min, 80, 100])     # High saturation
upper = np.array([hue_max, 255, 255])

# Greyed troops
lower = np.array([hue_min, 0, 80])       # Low saturation
upper = np.array([hue_max, 50, 200])
```

### Spell Icons
```python
# Gold/yellow spells
lower = np.array([15, 100, 120])
upper = np.array([35, 255, 255])
```

---

## Tips for Success

✅ **Do:**
- Keep bot running 24/7 for active clan support
- Use in clans with frequent donation requests
- Combine with attack mode for balanced gameplay
- Monitor logs to see donation activity

❌ **Don't:**
- Run donation mode if your clan is inactive (wastes energy)
- Donate units you're saving for war (configure carefully)
- Leave greyed-out items expecting them to be donated

---

## Expected Output

```
💚 DONATION-ONLY MODE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[1/100] Checking for donation requests...
  ✓ Found 3 donation requests
  → Available: 8 troops, 2 spells
  → Donating 8 troops...
     🎖️  Troop donated at (523, 340)
     🎖️  Troop donated at (612, 280)
     ...
  → Donating 2 spells...
     📜 Spell donated at (451, 420)
     📜 Spell donated at (390, 310)
  → Clicking DONATE button...
  ✓ Successfully donated 10 items!

📊 Stats: 10 donations, 2.3m elapsed

[2/100] Checking for donation requests...
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| No icons detected | Check game theme/lighting, adjust HSV ranges |
| Greyed icons being clicked | Increase color saturation threshold |
| Donate button not found | Verify green color range, check UI position |
| No requests found | Clan may be inactive, check manually first |

---

## Integration with Attack Mode

You can run both simultaneously:

```python
import threading

def hybrid_bot():
    controller = BotController()
    
    # Attack thread
    attack_thread = threading.Thread(
        target=ultra_fast_attack_loop,
        args=(controller, 100)
    )
    
    # Donation thread
    donation_thread = threading.Thread(
        target=donation_only_loop,
        args=(controller, 1000)
    )
    
    attack_thread.start()
    donation_thread.start()
    
    attack_thread.join()
    donation_thread.join()

if __name__ == "__main__":
    hybrid_bot()
```

This runs **attacks and donations in parallel** for ultimate clan support! 🚀

---

## Next Steps

1. **Implement click function**: Add `pyautogui.click(x, y)` to actual code
2. **Test color detection**: Run with screenshots enabled to verify icon detection
3. **Configure thresholds**: Adjust HSV ranges if colors don't match
4. **Run donation loop**: Start with `donation_only_loop()` in production

Good luck supporting your clan! 💚
