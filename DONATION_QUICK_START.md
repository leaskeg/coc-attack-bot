# Donation Testing - Quick Start (2 Minutes)

## 🎯 Get Started Now

### Step 1: Make Sure Clash of Clans is Running
Open the game and navigate to your clan chat.

### Step 2: Run the Quick Test
```bash
python donation_diagnostic.py
```

This takes **30 seconds** and checks if everything works.

### Step 3: Check Results

**Good result:**
```
✓ Game window detected at (0, 0) - 1280x720
✓ Found 5 available troops
✓ Found 2 available spells
✓ Donate button found at (600, 400)
```

**Problem result:**
```
❌ FAILED: Game window not detected
   Make sure Clash of Clans is running and visible
```

---

## 📋 What Each Result Means

| Status | Meaning | Solution |
|--------|---------|----------|
| ✓ All checks pass | System working | You're good to go! |
| ✓ but "0 troops found" | No troops available | Normal if inventory is empty |
| ✗ Game window error | Game not running/visible | Open Clash of Clans |
| ✗ Clan chat error | Not in donation screen | Navigate to clan chat |
| ✗ Button not found | No donation requests | Wait for requests to come in |

---

## 🔍 Need More Details?

### See What Happened
```bash
cat logs/donation_diagnostic.log
```

### Full Test (10 minutes)
```bash
python donation_test.py
```

### Analyze All Logs
```bash
python analyze_donation_logs.py
```

---

## 📊 Testing Tools Available

| Tool | Time | Purpose |
|------|------|---------|
| `donation_diagnostic.py` | 30s | Quick system check ✓ |
| `donation_test.py` | 5m | Complete validation |
| `donation_flow_validator.py` | 2m | Flow step validation |
| `analyze_donation_logs.py` | 1m | Log analysis |

---

## ✅ You're Ready If

- [ ] Game window detected
- [ ] Clan chat found
- [ ] Troops can be scanned
- [ ] Spells can be scanned
- [ ] No errors in log

---

## ❌ Common Issues

### "Game window not found"
→ Make sure Clash of Clans is open and visible

### "Not in clan chat"
→ Navigate to clan chat first

### "0 available troops"
→ May have insufficient inventory or wrong game theme

### "Donate button not found"
→ Normal! Appears only when there are pending donation requests

---

## 📝 Log Files

All results saved to: `logs/donation_diagnostic.log`

View latest activity:
```bash
tail -100 logs/donation_diagnostic.log
```

---

## 🚀 Next Steps

1. **Just want quick check?**
   ```bash
   python donation_diagnostic.py
   ```

2. **Want comprehensive test?**
   ```bash
   python donation_test.py
   ```

3. **Something not working?**
   ```bash
   python analyze_donation_logs.py interactive
   ```

4. **Need detailed flow validation?**
   ```bash
   python donation_flow_validator.py
   ```

---

## 📖 More Information

- **Testing Guide:** `DONATION_TESTING_GUIDE.md`
- **Full Reference:** `TESTING_README.md`
- **Enhancement Details:** `LOGGING_ENHANCEMENTS_SUMMARY.md`

---

## That's It!

**Start with:** `python donation_diagnostic.py` 🎯

It'll tell you in 30 seconds if donation system is working.

