#!/usr/bin/env python3
"""
Quick Donation System Diagnostic
Run this to quickly verify donation system is working
"""

import sys
import time
from src.bot_controller import BotController
from src.utils.logger import Logger


def print_header(text):
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}")


def main():
    logger = Logger("donation_diagnostic.log")
    
    print_header("DONATION SYSTEM DIAGNOSTIC")
    print("This quick test will verify all donation components are working.\n")
    
    try:
        logger.info("[DIAGNOSTIC] Starting donation system diagnostic")
        controller = BotController()
        
        print("Step 1: Detecting game window...")
        logger.debug("  → Detecting game window")
        game_window = controller.detect_game_window()
        
        if not game_window:
            print("❌ FAILED: Game window not detected")
            print("   Make sure Clash of Clans is running and visible")
            logger.error("[DIAGNOSTIC] Game window not detected")
            return False
        
        x, y, w, h = game_window
        print(f"✓ Game window detected at ({x}, {y}) - {w}x{h}")
        logger.info(f"[DIAGNOSTIC] Game window: ({x}, {y}) {w}x{h}")
        
        print("\nStep 2: Checking clan chat presence...")
        logger.debug("  → Checking if in clan chat")
        in_chat = controller.is_in_donation_screen(game_window)
        if in_chat:
            print("✓ Currently in clan chat/donation screen")
            logger.info("[DIAGNOSTIC] In clan chat")
        else:
            print("⚠ Not currently in clan chat (normal if not in donation screen)")
            logger.info("[DIAGNOSTIC] Not in clan chat")
        
        print("\nStep 3: Scanning for available troops...")
        logger.debug("  → Scanning available troops")
        troops = controller.get_available_troops_to_donate(game_window)
        print(f"✓ Found {len(troops)} available troops")
        if troops:
            for i, (tx, ty) in enumerate(troops[:5], 1):
                print(f"   {i}. Troop at ({tx}, {ty})")
            if len(troops) > 5:
                print(f"   ... and {len(troops) - 5} more")
        logger.info(f"[DIAGNOSTIC] Available troops: {len(troops)}")
        
        print("\nStep 4: Scanning for available spells...")
        logger.debug("  → Scanning available spells")
        spells = controller.get_available_spells_to_donate(game_window)
        print(f"✓ Found {len(spells)} available spells")
        if spells:
            for i, (sx, sy) in enumerate(spells[:5], 1):
                print(f"   {i}. Spell at ({sx}, {sy})")
            if len(spells) > 5:
                print(f"   ... and {len(spells) - 5} more")
        logger.info(f"[DIAGNOSTIC] Available spells: {len(spells)}")
        
        print("\nStep 5: Looking for donate button...")
        logger.debug("  → Looking for donate button")
        button = controller.find_donate_button(game_window)
        if button:
            print(f"✓ Donate button found at {button}")
            logger.info(f"[DIAGNOSTIC] Donate button at {button}")
        else:
            print("⚠ Donate button not found (no pending requests)")
            logger.debug("[DIAGNOSTIC] No donate button")
        
        print("\nStep 6: Checking for donation requests...")
        logger.debug("  → Checking donation requests")
        requests = controller.get_donation_requests(game_window)
        print(f"✓ Found {len(requests)} donation requests")
        if requests:
            for i, req in enumerate(requests[:3], 1):
                member = req.get('member_name', 'Unknown')
                print(f"   {i}. {member}")
            if len(requests) > 3:
                print(f"   ... and {len(requests) - 3} more")
        logger.info(f"[DIAGNOSTIC] Donation requests: {len(requests)}")
        
        print("\n" + "="*60)
        print("✓ DONATION SYSTEM DIAGNOSTIC COMPLETE")
        print("="*60)
        print(f"\nLog file: {logger.get_log_file_path()}\n")
        
        logger.info("[DIAGNOSTIC] All checks completed successfully")
        return True
    
    except KeyboardInterrupt:
        print("\n\n[CANCELLED] Diagnostic interrupted")
        logger.info("[DIAGNOSTIC] Interrupted by user")
        return False
    
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        logger.error(f"[DIAGNOSTIC] Error: {e}", exc_info=True)
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
