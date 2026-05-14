# Testing Tools - Quick Reference

## 🚀 Quick Start

### Fastest Test (30 seconds)
```bash
python donation_diagnostic.py
```
This will tell you immediately if the donation system is working.

---

### Complete Test (5-10 minutes)
```bash
python donation_test.py
```
Runs all 10 tests with detailed results.

---

### Analyze Logs
```bash
python analyze_donation_logs.py
```
See what happened in detail.

---

## 📊 What Each Tool Does

| Tool | Time | Purpose | Use When |
|------|------|---------|----------|
| `donation_diagnostic.py` | 30s | Quick system check | You want quick feedback |
| `donation_test.py` | 5-10m | Complete validation | Testing new features |
| `analyze_donation_logs.py` | 1m | Understand logs | Debugging issues |

---

## 📝 Log Files

After running tests, check:
- `logs/donation_diagnostic.log` - Quick check results
- `logs/donation_test.log` - Detailed test results
- `logs/app_YYYYMMDD.log` - All activity (main log)

---

## ✅ Success Indicators

**Game Window Detected:** ✓  
**Clan Chat Found:** ✓  
**Troops Scanned:** ✓ (0+ found)  
**Spells Scanned:** ✓ (0+ found)  
**No Errors:** ✓  

---

## ❌ Common Issues

### Issue: "Game window not detected"
**Solution:** Make sure Clash of Clans is running and visible

### Issue: "Not in clan chat"
**Solution:** Navigate to clan chat/donation screen first

### Issue: "No troops found"
**Solution:** You may have insufficient inventory or wrong color detection

### Issue: "Donation button not found"
**Solution:** This is normal if there are no pending requests

---

## 🔍 Understanding the Logs

Look for patterns in `logs/app_YYYYMMDD.log`:

```
✓ SUCCESS: [DONATION] Clan chat presence: YES ✓
✓ SUCCESS: [DONATION] Troop scan result: 2 available troops detected  
✓ SUCCESS: [DONATION] Donate button found at (600, 400)
✗ FAILURE: [DONATION ERROR] Error checking clan chat: ...
```

---

## 🎯 Testing Checklist

Before using donation bot:
- [ ] Run `python donation_diagnostic.py`
- [ ] All checks show ✓
- [ ] Review logs for warnings
- [ ] Open clan chat with pending requests
- [ ] Run again to verify donation button detection

---

## 📖 More Details

See `DONATION_TESTING_GUIDE.md` for:
- Detailed troubleshooting
- Log marker reference
- Performance metrics
- Customization options
- Scheduled testing

---

## Quick Commands

```bash
# Quick 30-second test
python donation_diagnostic.py

# Full test suite
python donation_test.py

# Search logs interactively
python analyze_donation_logs.py interactive

# View latest log
tail -f logs/app_*.log

# Find errors in logs
grep "ERROR\|FAIL" logs/app_*.log
```

---

## Support Workflow

1. **Something not working?**
   ```bash
   python donation_diagnostic.py
   ```

2. **See errors?**
   ```bash
   python analyze_donation_logs.py
   ```

3. **Need details?**
   ```bash
   python donation_test.py
   ```

4. **Still confused?**
   - Check `logs/donation_test.log`
   - Look at `donation_debug_test.png`
   - Review `DONATION_TESTING_GUIDE.md`

---

That's it! Start with `python donation_diagnostic.py` 🎯

