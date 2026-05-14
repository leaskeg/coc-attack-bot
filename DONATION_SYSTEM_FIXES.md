# Donation System - Critical Issues & Fixes

## 🔴 CRITICAL STUCK POINTS FOUND

### 1. **STUCK: No donation requests forever**
**Location:** `DONATION_ONLY_MODE.py` line 43

```python
if not requests:
    print("  → No active donation requests")
    time.sleep(2)
    continue  # ❌ INFINITE LOOP!
```

**Problem:** If clan has no active requests, bot loops forever checking every 5 minutes
**Fix:**
```python
if not requests:
    print(f"  → No active requests (checked {check_count} times)")
    if check_count > 5:  # After 25+ minutes with no requests
        print("  ⚠️ Consider running attack mode instead")
        return  # Exit gracefully
    check_count += 1
    continue
```

---

### 2. **STUCK: Brown color detection fails**
**Location:** `donation_detector.py` line 26

```python
brown_lower = np.array([30, 50, 80])
brown_upper = np.array([50, 120, 150])
return pixel_count > 5000  # ❌ Arbitrary threshold!
```

**Problem:** 
- Brown color range might not match your game theme
- 5000 pixels is arbitrary - could be too high for small screens
- If detection fails, `is_in_clan_chat()` returns False forever
- Bot never enters donation mode

**Fix:**
```python
def is_in_clan_chat(self, game_region: Tuple[int, int, int, int]) -> bool:
    """Check if clan chat/donation screen is visible"""
    try:
        screenshot = pyautogui.screenshot(region=game_region)
        frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        
        # Check for brown/tan background (donation UI)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        brown_lower = np.array([15, 30, 60])     # Wider range
        brown_upper = np.array([25, 150, 200])
        
        mask = cv2.inRange(hsv, brown_lower, brown_upper)
        pixel_count = cv2.countNonZero(mask)
        
        # Calculate threshold based on screen size
        threshold = (frame.shape[0] * frame.shape[1]) * 0.05  # 5% of pixels
        
        result = pixel_count > threshold
        
        if not result:
            self.logger.debug(f"Not in clan chat: {pixel_count} < {threshold}")
        
        return result
    
    except Exception as e:
        self.logger.error(f"Error checking clan chat: {e}")
        return False
```

---

### 3. **STUCK: All troops greyed out = empty list**
**Location:** `donation_detector.py` lines 100-121

```python
for hue_min in [0, 20, 40, 80, 120, 160]:
    hue_max = hue_min + 20
    lower = np.array([hue_min, 80, 100])  # ❌ Only high saturation
    # ...
    if 800 < area < 8000:  # ❌ Area range might be wrong
```

**Problem:**
- If all troops are greyed (low saturation), returns empty list
- Donation loop continues forever with nothing to click
- Area threshold (800-8000) assumes fixed resolution - fails on different screen sizes

**Fix:**
```python
def get_available_troops(self, game_region: Tuple[int, int, int, int], 
                        resolution_multiplier: float = 1.0) -> List[Tuple[int, int]]:
    """Detect available (non-greyed) troop icons"""
    try:
        screenshot = pyautogui.screenshot(region=game_region)
        frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        available_troops = []
        
        # Adjust area thresholds based on resolution
        min_area = 800 * resolution_multiplier
        max_area = 8000 * resolution_multiplier
        
        for hue_min in [0, 20, 40, 80, 120, 160]:
            hue_max = hue_min + 20
            
            # SATURATION CHECK: High saturation = colored (available)
            lower = np.array([hue_min, 80, 100])    # Saturation >= 80
            upper = np.array([hue_max, 255, 255])
            
            mask = cv2.inRange(hsv, lower, upper)
            
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours:
                area = cv2.contourArea(contour)
                if min_area < area < max_area:
                    M = cv2.moments(contour)
                    if M["m00"] > 0:
                        cx = int(M["m10"] / M["m00"]) + game_region[0]
                        cy = int(M["m01"] / M["m00"]) + game_region[1]
                        
                        # Avoid duplicates with better threshold
                        is_duplicate = any(abs(cx - x) < 50 and abs(cy - y) < 50 
                                          for x, y in available_troops)
                        if not is_duplicate:
                            available_troops.append((cx, cy))
        
        if not available_troops:
            self.logger.warning("No available troops detected - all may be greyed")
        
        return available_troops
    
    except Exception as e:
        self.logger.error(f"Error detecting troops: {e}")
        return []
```

---

### 4. **STUCK: Donate button not found**
**Location:** `DONATION_ONLY_MODE.py` lines 107-116

```python
donate_button = controller.find_donate_button(game_region)

if donate_button:
    print(f"  → Clicking DONATE button...")
    # TODO: click
    # ❌ If button is None, continues anyway!
```

**Problem:** If green button detection fails, returns None but code doesn't handle it

**Fix:**
```python
donate_button = controller.find_donate_button(game_region)

if not donate_button:
    self.logger.warning("Donate button not found - skipping submission")
    # Take screenshot for debugging
    self.controller.take_screenshot(game_region)
    return False

print(f"  → Clicking DONATE button at {donate_button}...")
# TODO: click
```

---

### 5. **STUCK: No click verification**
**Location:** `DONATION_ONLY_MODE.py` lines 91-102

```python
for troop_pos in available_troops:
    # TODO: implement_fast_click(troop_pos)
    print(f"     🎖️  Troop donated at {troop_pos}")  # ❌ Assumes success!
    time.sleep(random.uniform(0.3, 0.7))
```

**Problem:**
- Clicks position but never verifies it worked
- Could be clicking wrong spot (center-of-mass off by pixels)
- Donation fails silently

**Fix:**
```python
def donate_troop_with_verification(troop_pos, max_attempts=3):
    """Click troop and verify selection"""
    for attempt in range(max_attempts):
        # Click the troop
        pyautogui.click(troop_pos[0], troop_pos[1])
        time.sleep(0.3)
        
        # Take screenshot to verify selection
        screenshot = pyautogui.screenshot()
        
        # Check if troop is now highlighted/selected
        # (Would need UI element detection here)
        
        # TODO: Verify selection from screenshot
        
        if verified:
            print(f"✓ Troop selected")
            return True
        else:
            print(f"⚠️ Click may have failed, retrying...")
    
    return False
```

---

### 6. **STUCK: Wrong color ranges for your game**
**Location:** Multiple places

```python
# These are hardcoded - may not match YOUR game theme!
brown_lower = np.array([30, 50, 80])          # Donation UI
green_lower = np.array([35, 100, 100])        # Donate button
red_lower = np.array([0, 50, 150])            # Requests
```

**Problem:** Different game themes have different colors!

**Solution:** Add color tuning mode:

```python
def auto_calibrate_colors(self, game_region: Tuple[int, int, int, int]):
    """
    Automatically detect UI element colors
    User manually clicks on elements, bot learns their colors
    """
    print("🎨 Color Calibration Mode")
    print("Click on donation screen background...")
    # TODO: Detect click, read color under click
    
    print("Click on Donate button...")
    # TODO: Detect click, read color
    
    print("Colors saved to config.json")
```

---

## ✅ SAFETY CHECKLIST

- [ ] Add timeout to `is_in_clan_chat()` checks (max 10 minutes)
- [ ] Add maximum retry attempts before giving up
- [ ] Add screenshot capture on failure for debugging
- [ ] Verify each click was successful before continuing
- [ ] Handle case where donate button not found
- [ ] Handle case where no troops available
- [ ] Adjust color ranges to match your game theme
- [ ] Test with all troops greyed out (edge case)
- [ ] Test with no donation requests (edge case)
- [ ] Add graceful exit instead of infinite loops

---

## 🧪 TESTING SCENARIOS

### Test 1: No Donation Requests
```python
# Bot should not get stuck
# Expected: Log "No requests found, exiting" after N checks
# Current: ❌ Infinite loop
```

### Test 2: All Troops Greyed Out
```python
# Bot detects 0 available troops
# Expected: Log warning and skip this cycle
# Current: ❌ Infinite loop with empty list
```

### Test 3: Donate Button Missing
```python
# Green button color detection fails
# Expected: Take screenshot, log error, skip
# Current: ❌ Crashes or gets stuck
```

### Test 4: Color Range Mismatch
```python
# Your game uses different colors than expected
# Expected: Color calibration prompts user
# Current: ❌ Silently returns empty results
```

---

## 🔧 EMERGENCY FIXES (Quick Patches)

### Prevent infinite loops:
```python
# Add to donation_only_loop():
max_check_cycles = 12  # Max 1 hour with 5-min cycles
check_cycle = 0

while donation_count < max_donations:
    if check_cycle > max_check_cycles:
        print("❌ Max cycles reached, no requests found. Exiting.")
        break
    check_cycle += 1
```

### Verify clicks work:
```python
# After clicking each troop:
pyautogui.click(x, y)
time.sleep(0.5)

# Check if it visibly changed (darker/highlighted)
new_screenshot = pyautogui.screenshot(region=game_region)
# Visual comparison: Did the icon change?
```

### Add timeout to detection:
```python
def is_in_clan_chat_with_timeout(self, timeout=60):
    """Timeout if detection not working"""
    start = time.time()
    while time.time() - start < timeout:
        if self.is_in_clan_chat():
            return True
        time.sleep(5)
    return False  # Timeout
```

---

## 📋 RECOMMENDED IMPLEMENTATION ORDER

1. ✅ Fix color detection with calibration
2. ✅ Add click verification
3. ✅ Add timeout to prevent infinite loops
4. ✅ Add error screenshots for debugging
5. ✅ Test edge cases (greyed troops, no requests, etc)
6. ✅ Add graceful exit conditions
7. ✅ Implement retry logic with limits

This will prevent most stuck scenarios! 🚀
