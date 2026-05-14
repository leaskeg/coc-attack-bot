#!/usr/bin/env python3
"""
Donation Flow Validator
Validates the complete donation flow step-by-step without taking actions
Helps diagnose issues at each stage of the donation process
"""

import sys
import time
from src.bot_controller import BotController
from src.utils.logger import Logger


class DonationFlowValidator:
    def __init__(self):
        self.logger = Logger("donation_flow_validation.log")
        self.controller = BotController()
        self.flow_status = {}
        
        self.logger.info("="*80)
        self.logger.info("DONATION FLOW VALIDATOR STARTED")
        self.logger.info("="*80)
    
    def print_section(self, title: str):
        line = "─" * (len(title) + 4)
        print(f"\n{line}")
        print(f"  {title}")
        print(f"{line}")
    
    def check_stage(self, stage_name: str, check_func) -> bool:
        """Run a check and log results"""
        try:
            result, message = check_func()
            status = "✓" if result else "⚠"
            print(f"{status} {stage_name}: {message}")
            self.logger.info(f"[FLOW] {stage_name}: {'PASS' if result else 'WARN'} - {message}")
            self.flow_status[stage_name] = result
            return result
        except Exception as e:
            print(f"✗ {stage_name}: ERROR - {e}")
            self.logger.error(f"[FLOW] {stage_name}: ERROR - {e}", exc_info=True)
            self.flow_status[stage_name] = False
            return False
    
    def validate_flow(self):
        """Validate the complete donation detection and interaction flow"""
        
        self.print_section("DONATION FLOW VALIDATION")
        print("\nThis validator checks each stage of the donation system")
        print("without actually clicking on anything (dry run mode)\n")
        
        self.logger.info("[FLOW] Starting flow validation...")
        
        game_window = None
        
        def stage_1():
            self.logger.debug("[FLOW-STAGE-1] Detecting game window")
            nonlocal game_window
            game_window = self.controller.detect_game_window()
            if game_window:
                x, y, w, h = game_window
                return True, f"Window at ({x}, {y}) {w}x{h}"
            else:
                return False, "Game window not found"
        
        def stage_2():
            self.logger.debug("[FLOW-STAGE-2] Checking clan chat presence")
            if not game_window:
                return False, "Requires game window"
            
            is_chat = self.controller.is_in_donation_screen(game_window)
            return True, f"In clan chat: {is_chat}"
        
        def stage_3():
            self.logger.debug("[FLOW-STAGE-3] Scanning for available troops")
            if not game_window:
                return False, "Requires game window"
            
            troops = self.controller.get_available_troops_to_donate(game_window)
            return True, f"Found {len(troops)} available troops"
        
        def stage_4():
            self.logger.debug("[FLOW-STAGE-4] Scanning for available spells")
            if not game_window:
                return False, "Requires game window"
            
            spells = self.controller.get_available_spells_to_donate(game_window)
            return True, f"Found {len(spells)} available spells"
        
        def stage_5():
            self.logger.debug("[FLOW-STAGE-5] Detecting donation requests")
            if not game_window:
                return False, "Requires game window"
            
            requests = self.controller.get_donation_requests(game_window)
            return True, f"Found {len(requests)} donation requests"
        
        def stage_6():
            self.logger.debug("[FLOW-STAGE-6] Looking for donate button")
            if not game_window:
                return False, "Requires game window"
            
            button = self.controller.find_donate_button(game_window)
            if button:
                x, y = button
                return True, f"Button at ({x}, {y})"
            else:
                return True, "Button not found (no pending requests is normal)"
        
        def stage_7():
            self.logger.debug("[FLOW-STAGE-7] Checking clan chat button")
            if not game_window:
                return False, "Requires game window"
            
            button = self.controller.donation_detector.find_clan_chat_button(game_window)
            if button:
                x, y = button
                return True, f"Button at ({x}, {y})"
            else:
                return True, "Button not found (may not be visible)"
        
        def stage_8():
            self.logger.debug("[FLOW-STAGE-8] Checking close button")
            if not game_window:
                return False, "Requires game window"
            
            button = self.controller.donation_detector.find_close_button(game_window)
            if button:
                x, y = button
                return True, f"Button at ({x}, {y})"
            else:
                return True, "Button not found (may not be visible)"
        
        def stage_9():
            self.logger.debug("[FLOW-STAGE-9] Creating debug screenshot")
            if not game_window:
                return False, "Requires game window"
            
            path = self.controller.donation_detector.create_debug_screenshot(
                game_window,
                "donation_flow_debug.png"
            )
            if path:
                return True, f"Screenshot: {path}"
            else:
                return False, "Failed to create screenshot"
        
        def stage_10():
            self.logger.debug("[FLOW-STAGE-10] Testing template matching")
            if not game_window:
                return False, "Requires game window"
            
            troops = self.controller.donation_detector.find_troops_by_templates(game_window)
            return True, f"Template match found {len(troops)} troops"
        
        print("\n📋 STAGE VALIDATION\n")
        
        self.check_stage("1. Game Window Detection", stage_1)
        self.check_stage("2. Clan Chat Presence", stage_2)
        self.check_stage("3. Available Troops", stage_3)
        self.check_stage("4. Available Spells", stage_4)
        self.check_stage("5. Donation Requests", stage_5)
        self.check_stage("6. Donate Button", stage_6)
        self.check_stage("7. Clan Chat Button", stage_7)
        self.check_stage("8. Close Button", stage_8)
        self.check_stage("9. Debug Screenshot", stage_9)
        self.check_stage("10. Template Matching", stage_10)
        
        self.print_summary()
    
    def print_summary(self):
        """Print validation summary"""
        self.print_section("VALIDATION SUMMARY")
        
        passed = sum(1 for v in self.flow_status.values() if v)
        total = len(self.flow_status)
        pass_rate = (passed / total * 100) if total > 0 else 0
        
        print(f"\n✓ Passed: {passed}/{total}")
        print(f"✗ Failed: {total - passed}/{total}")
        print(f"📊 Pass Rate: {pass_rate:.0f}%\n")
        
        if pass_rate == 100:
            print("🎉 FLOW IS FULLY OPERATIONAL")
            self.logger.info("[FLOW] All stages passed - system is operational")
            return True
        elif pass_rate >= 80:
            print("⚠️  FLOW HAS MINOR ISSUES (check details above)")
            self.logger.info("[FLOW] Flow operational but with warnings")
            return True
        else:
            print("❌ FLOW HAS CRITICAL ISSUES (see details above)")
            self.logger.error("[FLOW] Flow validation failed")
            return False
    
    def detailed_analysis(self):
        """Show detailed analysis if requested"""
        print("\n" + "="*60)
        print("DETAILED FLOW ANALYSIS")
        print("="*60)
        
        game_window = self.controller.detect_game_window()
        if not game_window:
            print("Cannot perform detailed analysis without game window")
            return
        
        print("\n[DETAILED] Game Window Analysis")
        print(f"  Window bounds: {game_window}")
        x, y, w, h = game_window
        print(f"  Position: ({x}, {y})")
        print(f"  Size: {w}x{h}")
        print(f"  Area: {w*h:,} pixels")
        
        print("\n[DETAILED] Clan Chat Analysis")
        is_chat = self.controller.is_in_donation_screen(game_window)
        print(f"  In clan chat: {is_chat}")
        
        print("\n[DETAILED] Donation Resources")
        troops = self.controller.get_available_troops_to_donate(game_window)
        spells = self.controller.get_available_spells_to_donate(game_window)
        requests = self.controller.get_donation_requests(game_window)
        
        print(f"  Available troops: {len(troops)}")
        if troops:
            for i, (tx, ty) in enumerate(troops[:5], 1):
                print(f"    {i}. ({tx}, {ty})")
            if len(troops) > 5:
                print(f"    ... and {len(troops) - 5} more")
        
        print(f"  Available spells: {len(spells)}")
        if spells:
            for i, (sx, sy) in enumerate(spells[:5], 1):
                print(f"    {i}. ({sx}, {sy})")
            if len(spells) > 5:
                print(f"    ... and {len(spells) - 5} more")
        
        print(f"  Donation requests: {len(requests)}")
        
        print("\n[DETAILED] Button Detection")
        donate_btn = self.controller.find_donate_button(game_window)
        print(f"  Donate button: {donate_btn}")
        
        chat_btn = self.controller.donation_detector.find_clan_chat_button(game_window)
        print(f"  Clan chat button: {chat_btn}")
        
        close_btn = self.controller.donation_detector.find_close_button(game_window)
        print(f"  Close button: {close_btn}")
        
        print("\n" + "="*60)


def main():
    try:
        validator = DonationFlowValidator()
        validator.validate_flow()
        
        if input("\nShow detailed analysis? (y/n): ").lower() == 'y':
            validator.detailed_analysis()
        
        print(f"\nLog saved to: {validator.logger.get_log_file_path()}\n")
        return 0
    
    except KeyboardInterrupt:
        print("\n\n[CANCELLED] Validation interrupted by user")
        return 0
    
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
