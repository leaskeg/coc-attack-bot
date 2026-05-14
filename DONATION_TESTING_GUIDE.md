# Donation System Testing & Logging Guide

## Overview

This guide explains how to test the donation system and analyze comprehensive logs to identify any issues or flow problems.

## Enhanced Logging

All donation-related operations now include **detailed logging** with clear markers:

```
[DONATION FLOW] - Main donation detection steps
[DONATION] - Key donation events (troops found, button detected, etc.)
[DONATION ERROR] - Errors during donation detection
[DONATION API] - API calls to donation functions
[CLICK] - Click operations during donation
[WINDOW] - Game window detection
[SCREEN] - Screenshot operations
```

### Log Location

Logs are saved to: `logs/app_YYYYMMDD.log`

All DEBUG, INFO, WARNING, and ERROR messages are recorded with timestamps.

---

## Quick Testing Tools

### 1. **Donation Diagnostic** (Quick 2-minute test)

Runs a quick diagnostic to verify all donation components:

```bash
python donation_diagnostic.py
```

**What it does:**
- ✓ Detects game window
- ✓ Checks clan chat presence
- ✓ Scans available troops
- ✓ Scans available spells
- ✓ Looks for donate button
- ✓ Checks for donation requests

**Output:**
- Console output with ✓/❌ status for each test
- Detailed log file at `logs/donation_diagnostic.log`

---

### 2. **Comprehensive Test Suite** (Complete 5-10 minute test)

Runs all 10 donation tests with detailed results:

```bash
python donation_test.py
```

**Tests:**
1. Game window detection
2. Clan chat presence detection
3. Available troops detection
4. Available spells detection
5. Donation requests detection
6. Donate button detection
7. Clan chat button detection
8. Close button detection
9. Debug screenshot creation
10. Troop template matching

**Output:**
- Console: Final pass/fail summary
- Log: Complete test results at `logs/donation_test.log`
- Screenshot: Debug screenshot at `donation_debug_test.png`

---

### 3. **Log Analyzer** (Analyze existing logs)

Analyzes logs to understand donation flow and identify issues:

```bash
python analyze_donation_logs.py
```

**Features:**
- Summarizes donation detection cycles
- Shows all API calls
- Lists any errors found
- Displays recent donation flows
- Generates statistics

**Interactive Mode:**
```bash
python analyze_donation_logs.py interactive
```

Allows you to:
- Browse through available log files
- Search for specific terms in logs
- Find error patterns

---

## Interpreting Logs

### Successful Donation Detection Flow

```
[DONATION FLOW] Checking clan chat presence in region (100, 200, 800, 600)
  → Screenshot captured: 800x600 pixels
  → Brown HSV range: [5 20 40] to [30 200 220]
  → Brown pixels found: 50000, threshold: 10000.0
[DONATION] Clan chat presence: YES ✓

[DONATION FLOW] Scanning for available troops in region (100, 200, 800, 600)
  → Captured 800x600 image for troop analysis
  → Area thresholds: min=1920, max=9600
  → Hue range 1/6 (0-10): 15 contours found
    ✓ Troop detected at (523, 340) | Area: 3000.0, Aspect: 1.50
    ✓ Troop detected at (612, 280) | Area: 2800.0, Aspect: 1.45
[DONATION] Troop scan result: 2 available troops detected

[DONATION] Donate button found at (600, 400) | Confidence: 0.75
```

### Troubleshooting Issues

#### Issue: "Clan chat button not found"
```
[DONATION] Looking for clan chat button...
[DONATION] Clan chat button not found
```
**Solution:** Make sure you're on the home screen where the clan chat button is visible.

---

#### Issue: "No available troops detected"
```
[DONATION] Troop scan result: 0 available troops detected
[DONATION] No available troops - all may be greyed out or insufficient inventory
```
**Solution:** Check if you have troops available or if the game theme is different (may need HSV range adjustments).

---

#### Issue: "Donate button not found (no pending requests)"
```
[DONATION] Donate button not found on screen - no pending donation requests
```
**Solution:** This is normal! It means there are no donation requests currently. The bot will retry later.

---

#### Issue: API call returns empty results
```
[DONATION API] Retrieved 0 available troops to donate
[DONATION API] In donation screen: False
```
**Solution:** Make sure you've opened the donation screen first.

---

## Testing Workflow

### Step 1: Prepare
1. Open Clash of Clans
2. Navigate to clan chat/donation screen
3. Ensure there are pending donation requests (for full test)

### Step 2: Run Quick Diagnostic
```bash
python donation_diagnostic.py
```
This gives you immediate feedback on all systems.

### Step 3: Review Logs
```bash
python analyze_donation_logs.py
```
Check for any warnings or errors in the recent log.

### Step 4: Run Full Test Suite (Optional)
```bash
python donation_test.py
```
For comprehensive validation of all 10 donation features.

### Step 5: Debug with Screenshots
If tests fail, check these files:
- `donation_debug_test.png` - Shows detected items with circles and labels
- `logs/donation_test.log` - Detailed step-by-step logs

---

## Log Markers Reference

| Marker | Meaning | Example |
|--------|---------|---------|
| `[DONATION FLOW]` | Step in donation detection flow | Checking clan chat presence |
| `[DONATION]` | Key result/event | Clan chat presence: YES ✓ |
| `[DONATION ERROR]` | Error occurred | Error detecting available troops |
| `[DONATION API]` | API function called | get_available_troops_to_donate() called |
| `[CLICK]` | Mouse click performed | Clicked at (523, 340) |
| `[CLICK SUCCESS]` | Click succeeded | Clicked troop at (523, 340) |
| `[CLICK ERROR]` | Click failed | Click execution failed |
| `[WINDOW]` | Window detection | Game window found at (0, 0) - 1280x720 |
| `[SCREEN]` | Screenshot operation | Screenshot saved: screenshots/... |
| `[VALIDATION]` | Validation check | Coordinate constrained to window bounds |

---

## Common Tests Checklist

Use this checklist when testing donation system:

- [ ] Game window detected correctly
- [ ] Can detect when in clan chat
- [ ] Can find available troops
- [ ] Can find available spells
- [ ] Can detect donation requests
- [ ] Can find donate button
- [ ] Can find clan chat button
- [ ] Can create debug screenshot
- [ ] Template matching works
- [ ] No errors in logs

---

## Performance Monitoring

### Expected Timing

- Game window detection: < 100ms
- Clan chat check: 200-400ms
- Troop scanning: 300-500ms
- Spell scanning: 200-400ms
- Button detection: 100-200ms
- Debug screenshot: 500-800ms

If times are significantly higher, check:
1. System CPU/RAM usage
2. Game window size (larger = slower processing)
3. Image complexity (more objects = slower detection)

---

## Customization

### Adjust Detection Sensitivity

Edit in `src/core/donation_detector.py`:

```python
# Brown color range (clan chat detection)
brown_lower = np.array([5, 20, 40])
brown_upper = np.array([30, 200, 220])

# Green color range (donate button)
green_lower = np.array([25, 70, 100])
green_upper = np.array([95, 255, 255])

# Yellow color range (spells)
lower = np.array([15, 120, 100])
upper = np.array([30, 255, 255])
```

If detection isn't working:
1. Run test with `--debug` flag to see detailed color analysis
2. Check `donation_debug_test.png` to see what's being detected
3. Adjust HSV ranges based on your game theme

---

## Automated Testing Schedule

For production use, schedule these checks:

```bash
# Run diagnostic every hour
0 * * * * cd /path/to/bot && python donation_diagnostic.py >> logs/hourly_check.log 2>&1

# Run full test daily
0 0 * * * cd /path/to/bot && python donation_test.py >> logs/daily_test.log 2>&1

# Analyze logs daily
0 1 * * * cd /path/to/bot && python analyze_donation_logs.py >> logs/daily_analysis.log 2>&1
```

---

## Support

If tests fail:

1. **Check log files** - Look for [DONATION ERROR] entries
2. **Run diagnostic** - `python donation_diagnostic.py`
3. **Create debug screenshot** - Shows what the system sees
4. **Check game state** - Ensure clan chat is open with pending requests
5. **Verify game window** - Must be visible and focused

---

## Summary

The donation system now includes:

✓ **Comprehensive logging** at every step  
✓ **Quick diagnostic tool** for rapid testing  
✓ **Full test suite** with 10 individual tests  
✓ **Log analyzer** to understand system behavior  
✓ **Debug screenshots** to visualize detections  

**Next steps:**
1. Run `python donation_diagnostic.py` to verify setup
2. Check `logs/` directory for detailed logs
3. Review `DONATION_MODE_GUIDE.md` for usage

