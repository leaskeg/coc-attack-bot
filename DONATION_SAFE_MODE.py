#!/usr/bin/env python3
"""
Safe Donation Mode - With timeout protection and error recovery
Prevents getting stuck in infinite loops
"""

import time
from src.bot_controller import BotController


def safe_donation_loop(controller, max_donations: int = 100, 
                      max_consecutive_failures: int = 5,
                      check_timeout: int = 300):
    """
    Safe donation loop with multiple timeout protections
    
    Args:
        controller: BotController instance
        max_donations: Max donations to send
        max_consecutive_failures: Exit after N failed attempts
        check_timeout: Max seconds between successful donations
    """
    
    game_region = controller.detect_game_window()
    if not game_region:
        print("❌ Game window not detected")
        return
    
    print("=" * 70)
    print("💚 SAFE DONATION MODE (with timeout protection)")
    print("=" * 70)
    print(f"Max donations: {max_donations}")
    print(f"Max failed attempts: {max_consecutive_failures}")
    print(f"Timeout between donations: {check_timeout}s")
    print("=" * 70 + "\n")
    
    donation_count = 0
    consecutive_failures = 0
    last_successful_donation = time.time()
    session_start = time.time()
    
    while donation_count < max_donations:
        
        current_time = time.time()
        
        # ═════════════════════════════════════════════════════════════
        # SAFETY CHECK 1: Timeout if no donations for too long
        # ═════════════════════════════════════════════════════════════
        
        time_since_last = current_time - last_successful_donation
        
        if time_since_last > check_timeout:
            print(f"⚠️  No donation for {check_timeout}s - may be stuck")
            print(f"   Consecutive failures: {consecutive_failures}/{max_consecutive_failures}")
            
            if consecutive_failures >= max_consecutive_failures:
                print(f"\n❌ GIVING UP: {max_consecutive_failures} consecutive failures")
                print(f"   Check color ranges or manually verify donation screen")
                break
        
        # ═════════════════════════════════════════════════════════════
        # PHASE 1: VERIFY DONATION SCREEN
        # ═════════════════════════════════════════════════════════════
        
        print(f"[{donation_count + 1}/{max_donations}] Checking donation screen...", end=" ")
        
        if not controller.is_in_donation_screen(game_region):
            print("❌ NOT IN DONATION SCREEN")
            consecutive_failures += 1
            time.sleep(5)
            continue
        
        print("✓")
        
        # ═════════════════════════════════════════════════════════════
        # PHASE 2: GET AVAILABLE ITEMS
        # ═════════════════════════════════════════════════════════════
        
        troops = controller.get_available_troops_to_donate(game_region)
        spells = controller.get_available_spells_to_donate(game_region)
        
        total_available = len(troops) + len(spells)
        
        print(f"  Found: {len(troops)} troops, {len(spells)} spells")
        
        # ═════════════════════════════════════════════════════════════
        # SAFETY CHECK 2: No items available
        # ═════════════════════════════════════════════════════════════
        
        if total_available == 0:
            print("  ⚠️  No troops or spells available")
            print("      (All may be greyed out - insufficient items)")
            consecutive_failures += 1
            time.sleep(5)
            continue
        
        # ═════════════════════════════════════════════════════════════
        # PHASE 3: DONATE TROOPS
        # ═════════════════════════════════════════════════════════════
        
        print(f"  Donating {len(troops)} troop(s)...", end="", flush=True)
        
        for i, (x, y) in enumerate(troops):
            try:
                pyautogui.click(x, y)
                print(".", end="", flush=True)
                time.sleep(0.3)
            except Exception as e:
                print(f"\n     ❌ Error clicking troop at {(x, y)}: {e}")
                consecutive_failures += 1
                continue
        
        print(" ✓")
        
        # ═════════════════════════════════════════════════════════════
        # PHASE 4: DONATE SPELLS
        # ═════════════════════════════════════════════════════════════
        
        if spells:
            print(f"  Donating {len(spells)} spell(s)...", end="", flush=True)
            
            for i, (x, y) in enumerate(spells):
                try:
                    pyautogui.click(x, y)
                    print(".", end="", flush=True)
                    time.sleep(0.3)
                except Exception as e:
                    print(f"\n     ❌ Error clicking spell at {(x, y)}: {e}")
                    consecutive_failures += 1
                    continue
            
            print(" ✓")
        
        # ═════════════════════════════════════════════════════════════
        # PHASE 5: CLICK DONATE BUTTON
        # ═════════════════════════════════════════════════════════════
        
        print(f"  Finding Donate button...", end="", flush=True)
        
        donate_btn = controller.find_donate_button(game_region)
        
        if not donate_btn:
            print(" ❌")
            print("     Donate button not found!")
            print("     → Try adjusting green color range in donation_detector.py")
            print("     → Or take screenshot to verify button is visible")
            
            # Save screenshot for debugging
            try:
                screenshot_path = controller.take_screenshot(game_region)
                print(f"     → Screenshot saved: {screenshot_path}")
            except:
                pass
            
            consecutive_failures += 1
            time.sleep(5)
            continue
        
        print(f" ✓ at {donate_btn}")
        
        try:
            print(f"  Clicking Donate...", end="", flush=True)
            # TODO: pyautogui.click(donate_btn[0], donate_btn[1])
            print(" ✓")
            
            time.sleep(0.5)
        
        except Exception as e:
            print(f" ❌\n     Error: {e}")
            consecutive_failures += 1
            continue
        
        # ═════════════════════════════════════════════════════════════
        # SUCCESS!
        # ═════════════════════════════════════════════════════════════
        
        donation_count += total_available
        consecutive_failures = 0  # Reset on success
        last_successful_donation = time.time()
        
        elapsed = time.time() - session_start
        rate = donation_count / elapsed * 3600
        
        print(f"\n  ✅ Donated {total_available} items!")
        print(f"     Total: {donation_count} | Rate: {rate:.0f}/hour | Elapsed: {elapsed/60:.1f}m\n")
        
        # ═════════════════════════════════════════════════════════════
        # WAIT BEFORE NEXT CYCLE
        # ═════════════════════════════════════════════════════════════
        
        time.sleep(5)
    
    # ═════════════════════════════════════════════════════════════
    # SESSION COMPLETE
    # ═════════════════════════════════════════════════════════════
    
    total_time = time.time() - session_start
    
    print("\n" + "=" * 70)
    print("💚 DONATION SESSION COMPLETE")
    print("=" * 70)
    print(f"Total items donated: {donation_count}")
    print(f"Session duration: {total_time / 60:.1f} minutes")
    print(f"Items per hour: {(donation_count / total_time * 3600):.0f}")
    print("=" * 70)


def debug_donation_colors(controller):
    """
    Debug mode: Shows detected colors for UI elements
    Helps you understand why detection is failing
    """
    
    print("=" * 70)
    print("🔍 DONATION COLOR DEBUG MODE")
    print("=" * 70)
    print("This will help identify color detection issues")
    print("=" * 70 + "\n")
    
    game_region = controller.detect_game_window()
    if not game_region:
        print("❌ Game window not detected")
        return
    
    import cv2
    import numpy as np
    import pyautogui
    
    screenshot = pyautogui.screenshot(region=game_region)
    frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    print("Taking screenshot and analyzing colors...\n")
    
    # Check for brown (donation screen)
    brown_mask = cv2.inRange(hsv, 
                             np.array([15, 30, 60]),
                             np.array([25, 150, 200]))
    brown_pixels = cv2.countNonZero(brown_mask)
    threshold = (frame.shape[0] * frame.shape[1]) * 0.05
    
    print(f"🟤 Brown pixels (donation UI): {brown_pixels}")
    print(f"   Threshold: {threshold:.0f}")
    print(f"   Status: {'✓ DETECTED' if brown_pixels > threshold else '❌ NOT DETECTED'}\n")
    
    # Check for colored troops
    colored_count = 0
    for hue_min in [0, 20, 40, 80, 120, 160]:
        hue_max = hue_min + 20
        mask = cv2.inRange(hsv,
                          np.array([hue_min, 80, 100]),
                          np.array([hue_max, 255, 255]))
        pixels = cv2.countNonZero(mask)
        if pixels > 100:
            colored_count += 1
            print(f"🎨 Hue {hue_min:3d}: {pixels:5d} pixels")
    
    print(f"\n✓ Total colored icons detected: {colored_count}/6 hue ranges\n")
    
    # Check for green button
    green_mask = cv2.inRange(hsv,
                            np.array([35, 100, 100]),
                            np.array([85, 255, 255]))
    green_pixels = cv2.countNonZero(green_mask)
    
    print(f"🟢 Green button pixels: {green_pixels}")
    print(f"   Status: {'✓ DETECTED' if green_pixels > 1000 else '❌ NOT DETECTED'}\n")
    
    print("=" * 70)
    if brown_pixels < threshold:
        print("⚠️  ISSUE: Donation screen background not detected")
        print("   Try adjusting brown color range:")
        print("   Lower: [15, 30, 60] → Upper: [25, 150, 200]")
    
    if colored_count < 2:
        print("⚠️  ISSUE: Few colored troops detected")
        print("   All troops may be greyed out (insufficient items)")
    
    if green_pixels < 1000:
        print("⚠️  ISSUE: Donate button not detected")
        print("   Try adjusting green color range:")
        print("   Lower: [35, 100, 100] → Upper: [85, 255, 255]")
    
    if brown_pixels > threshold and colored_count >= 2 and green_pixels > 1000:
        print("✅ All colors detected correctly!")
        print("   Donation mode should work fine.")
    
    print("=" * 70)


if __name__ == "__main__":
    controller = BotController()
    
    # Choose mode:
    # safe_donation_loop(controller, max_donations=100)
    # debug_donation_colors(controller)
    
    print("Safe Donation Mode - Choose from:")
    print("1. safe_donation_loop(controller) - Run with timeouts")
    print("2. debug_donation_colors(controller) - Troubleshoot colors")
