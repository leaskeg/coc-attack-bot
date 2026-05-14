#!/usr/bin/env python3
"""
Donation-Only Mode
Continuously checks for clan donation requests and auto-donates
Perfect for clan wars and active clan support
"""

import time
import random
import pyautogui
from src.bot_controller import BotController


def donation_only_loop(controller, max_donations: int = 100, cycle_duration: int = 300):
    """
    Donation-only mode: check for requests and donate
    
    Args:
        controller: BotController instance
        max_donations: Max donations to send before stopping
        cycle_duration: Donation check interval in seconds (default: 5 minutes)
    """
    
    game_region = controller.detect_game_window()
    if not game_region:
        print("❌ Game window not detected")
        return
    
    print("=" * 70)
    print("💚 DONATION-ONLY MODE")
    print("=" * 70)
    print(f"Checking for donation requests every {cycle_duration}s")
    print("Will auto-donate all available troops and spells")
    print("=" * 70 + "\n")
    
    donation_count = 0
    start_time = time.time()
    last_check = time.time()
    
    while donation_count < max_donations:
        
        current_time = time.time()
        
        # Check if it's time for next donation cycle
        if current_time - last_check < cycle_duration:
            time.sleep(1)
            continue
        
        last_check = current_time
        
        # ═════════════════════════════════════════════════════════════
        # PHASE 1: CHECK FOR DONATION REQUESTS
        # ═════════════════════════════════════════════════════════════
        
        print(f"[{donation_count + 1}/{max_donations}] Checking for donation requests...")
        
        # Check if in clan chat/donation screen
        if not controller.is_in_donation_screen(game_region):
            print("  → Not in donation screen, skipping cycle")
            time.sleep(2)
            continue
        
        # Get donation requests
        requests = controller.get_donation_requests(game_region)
        
        if not requests:
            print("  → No active donation requests")
            time.sleep(2)
            continue
        
        print(f"  ✓ Found {len(requests)} donation request(s)")
        
        # ═════════════════════════════════════════════════════════════
        # PHASE 2: GET AVAILABLE TROOPS & SPELLS
        # ═════════════════════════════════════════════════════════════
        
        available_troops = controller.get_available_troops_to_donate(game_region)
        available_spells = controller.get_available_spells_to_donate(game_region)
        
        print(f"  → Available: {len(available_troops)} troops, {len(available_spells)} spells")
        
        if not available_troops and not available_spells:
            print("  ⚠ No troops or spells available to donate")
            time.sleep(2)
            continue
        
        # ═════════════════════════════════════════════════════════════
        # PHASE 3: AUTO-DONATE AVAILABLE TROOPS
        # ═════════════════════════════════════════════════════════════
        
        donated_this_cycle = 0
        
        if available_troops:
            print(f"  → Donating {len(available_troops)} troop(s)...")
            
            for troop_pos in available_troops:
                pyautogui.click(troop_pos[0], troop_pos[1])
                
                print(f"     🎖️  Troop donated at {troop_pos}")
                donated_this_cycle += 1
                donation_count += 1
                
                # Random delay between donations (human-like)
                time.sleep(random.uniform(0.3, 0.7))
                
                if donation_count >= max_donations:
                    break
        
        if available_spells and donation_count < max_donations:
            print(f"  → Donating {len(available_spells)} spell(s)...")
            
            for spell_pos in available_spells:
                pyautogui.click(spell_pos[0], spell_pos[1])
                
                print(f"     📜 Spell donated at {spell_pos}")
                donated_this_cycle += 1
                donation_count += 1
                
                # Random delay between donations
                time.sleep(random.uniform(0.3, 0.7))
                
                if donation_count >= max_donations:
                    break
        
        # ═════════════════════════════════════════════════════════════
        # PHASE 4: CLICK DONATE BUTTON
        # ═════════════════════════════════════════════════════════════
        
        if donated_this_cycle > 0:
            donate_button = controller.find_donate_button(game_region)
            
            if donate_button:
                print(f"  → Clicking DONATE button at {donate_button}...")
                pyautogui.click(donate_button[0], donate_button[1])
                time.sleep(0.5)
                
                print(f"  ✓ Successfully donated {donated_this_cycle} item(s)!")
            else:
                print(f"  ⚠ Donate button not found")
        
        # Stats
        elapsed = time.time() - start_time
        print(f"\n  📊 Stats: {donation_count} donations, {elapsed / 60:.1f}m elapsed\n")
    
    # ═════════════════════════════════════════════════════════════
    # SESSION COMPLETE
    # ═════════════════════════════════════════════════════════════
    
    total_time = time.time() - start_time
    
    print("\n" + "=" * 70)
    print("💚 DONATION SESSION COMPLETE")
    print("=" * 70)
    print(f"Total donations: {donation_count}")
    print(f"Total time: {total_time / 60:.1f} minutes")
    print(f"Average per donation: {total_time / max(donation_count, 1):.1f} seconds")
    print(f"Donations per hour: {(donation_count / total_time) * 3600:.0f}")
    print("=" * 70)


def donation_with_attack_combo(controller):
    """
    Hybrid mode: Attack when good bases found, donate when waiting
    Perfect for clan wars + supporting teammates
    """
    
    print("=" * 70)
    print("🔄 HYBRID MODE: ATTACK + DONATIONS")
    print("=" * 70)
    print("Primary: Attack bases when found")
    print("Secondary: Donate when no good bases available")
    print("=" * 70 + "\n")
    
    game_region = controller.detect_game_window()
    if not game_region:
        print("❌ Game window not detected")
        return
    
    attack_count = 0
    donation_count = 0
    search_attempts = 0
    
    while True:
        
        # ─────────────────────────────────────────────────────────
        # PART 1: SEARCH FOR GOOD BASE (max 10 attempts)
        # ─────────────────────────────────────────────────────────
        
        print(f"[Search Phase] Looking for bases... (attempt {search_attempts + 1}/10)")
        
        search_attempts += 1
        
        resources = controller.read_base_resources(game_region)
        should_attack, _ = controller.is_base_worth_attacking(resources)
        
        if should_attack and search_attempts <= 10:
            print(f"✓ Found good base! Gold: {resources['gold']:,}")
            print(f"→ Executing attack...")
            
            # TODO: execute_attack()
            
            attack_count += 1
            search_attempts = 0
            print(f"✓ Attack complete!\n")
            continue
        
        # ─────────────────────────────────────────────────────────
        # PART 2: DONATE WHILE SEARCHING
        # ─────────────────────────────────────────────────────────
        
        if search_attempts > 3:  # After 3 failed searches, try donating
            
            print(f"[Donation Phase] No good base found, checking for donations...")
            
            if controller.is_in_donation_screen(game_region):
                troops = controller.get_available_troops_to_donate(game_region)
                spells = controller.get_available_spells_to_donate(game_region)
                
                if troops or spells:
                    print(f"→ Donating {len(troops)} troops + {len(spells)} spells...")
                    
                    for pos in troops + spells:
                        pyautogui.click(pos[0], pos[1])
                        donation_count += 1
                        time.sleep(0.3)
                    
                    donate_btn = controller.find_donate_button(game_region)
                    if donate_btn:
                        pyautogui.click(donate_btn[0], donate_btn[1])
                        print(f"✓ Donations sent!\n")
            
            # Reset search attempts
            search_attempts = 0
        else:
            # Try next base
            # TODO: click_next_button()
            time.sleep(0.2)
        
        # Stats
        print(f"Session: {attack_count} attacks, {donation_count} donations\n")


def quick_donation_bot(controller, max_quick_donations: int = 20):
    """
    Quick donation mode: 5-second checks for fast clan support
    Best when you're playing casually and want to support clan
    """
    
    print("=" * 70)
    print("⚡ QUICK DONATION MODE (5-second cycles)")
    print("=" * 70)
    
    game_region = controller.detect_game_window()
    if not game_region:
        print("❌ Game window not detected")
        return
    
    donation_count = 0
    
    while donation_count < max_quick_donations:
        
        # Check for donations every 5 seconds
        if not controller.is_in_donation_screen(game_region):
            print(".", end="", flush=True)
            time.sleep(5)
            continue
        
        troops = controller.get_available_troops_to_donate(game_region)
        spells = controller.get_available_spells_to_donate(game_region)
        
        if troops or spells:
            print(f"\n✓ Found {len(troops) + len(spells)} items to donate!")
            
            for pos in troops + spells:
                pyautogui.click(pos[0], pos[1])
                donation_count += 1
                time.sleep(0.2)
            
            donate_btn = controller.find_donate_button(game_region)
            if donate_btn:
                pyautogui.click(donate_btn[0], donate_btn[1])
                print(f"✓ Donated!")
        
        time.sleep(5)
    
    print(f"\n✓ Quick donation session complete! {donation_count} donations sent.")


if __name__ == "__main__":
    controller = BotController()
    
    print("\nDONATION MODE OPTIONS:")
    print("1. donation_only_loop() - Continuous donation checking")
    print("2. donation_with_attack_combo() - Attack + donate hybrid")
    print("3. quick_donation_bot() - 5-second quick donation checks")
    print("\nUncomment your preferred mode below to run:\n")
    
    # Choose your mode:
    # donation_only_loop(controller, max_donations=50)
    # donation_with_attack_combo(controller)
    # quick_donation_bot(controller, max_quick_donations=20)
    
    print("To enable donation mode, set 'donation_mode: true' in config")
