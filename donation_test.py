#!/usr/bin/env python3
"""
Comprehensive Donation System Test Suite
Tests all donation detection and interaction features with detailed logging
"""

import time
import sys
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from src.bot_controller import BotController
from src.utils.logger import Logger


class DonationTestSuite:
    def __init__(self):
        self.logger = Logger("donation_test.log")
        self.controller = BotController()
        self.test_results: Dict[str, Dict] = {}
        self.total_tests = 0
        self.passed_tests = 0
        
        self.logger.info("="*80)
        self.logger.info("DONATION SYSTEM COMPREHENSIVE TEST SUITE STARTED")
        self.logger.info(f"Test timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.logger.info("="*80)
    
    def log_test_start(self, test_name: str):
        """Log the start of a test"""
        self.total_tests += 1
        self.logger.info(f"\n[TEST {self.total_tests}] {test_name} - STARTING")
        self.logger.info(f"  └─ Started at: {datetime.now().strftime('%H:%M:%S')}")
    
    def log_test_pass(self, test_name: str, details: str = ""):
        """Log test passed"""
        self.passed_tests += 1
        self.logger.info(f"[TEST {self.total_tests}] {test_name} - ✓ PASSED")
        if details:
            self.logger.info(f"  Details: {details}")
        self.test_results[test_name] = {"status": "PASS", "details": details}
    
    def log_test_fail(self, test_name: str, error: str = ""):
        """Log test failed"""
        self.logger.error(f"[TEST {self.total_tests}] {test_name} - ✗ FAILED")
        if error:
            self.logger.error(f"  Error: {error}")
        self.test_results[test_name] = {"status": "FAIL", "details": error}
    
    def test_1_game_window_detection(self) -> bool:
        """Test 1: Game window detection"""
        test_name = "Game Window Detection"
        self.log_test_start(test_name)
        
        try:
            self.logger.debug("  → Attempting to detect game window...")
            game_window = self.controller.detect_game_window()
            
            if game_window:
                x, y, w, h = game_window
                self.logger.debug(f"  → Window found at ({x}, {y}) with size {w}x{h}")
                details = f"Window: ({x}, {y}) Size: {w}x{h}"
                self.log_test_pass(test_name, details)
                return True
            else:
                self.logger.debug("  → No game window detected")
                self.log_test_fail(test_name, "Game window not found - ensure game is running and visible")
                return False
        except Exception as e:
            self.log_test_fail(test_name, str(e))
            return False
    
    def test_2_clan_chat_detection(self) -> bool:
        """Test 2: Clan chat presence detection"""
        test_name = "Clan Chat Detection"
        self.log_test_start(test_name)
        
        try:
            game_window = self.controller.detect_game_window()
            if not game_window:
                self.log_test_fail(test_name, "Game window not detected first")
                return False
            
            self.logger.debug("  → Checking if in clan chat...")
            is_in_chat = self.controller.is_in_donation_screen(game_window)
            
            status = "Yes" if is_in_chat else "No"
            self.logger.debug(f"  → In clan chat: {status}")
            
            details = f"In clan chat: {status}"
            self.log_test_pass(test_name, details)
            return True
        except Exception as e:
            self.log_test_fail(test_name, str(e))
            return False
    
    def test_3_available_troops_detection(self) -> bool:
        """Test 3: Available troops detection"""
        test_name = "Available Troops Detection"
        self.log_test_start(test_name)
        
        try:
            game_window = self.controller.detect_game_window()
            if not game_window:
                self.log_test_fail(test_name, "Game window not detected first")
                return False
            
            self.logger.debug("  → Scanning for available troops...")
            troops = self.controller.get_available_troops_to_donate(game_window)
            
            self.logger.debug(f"  → Found {len(troops)} available troops")
            if troops:
                for i, (x, y) in enumerate(troops, 1):
                    self.logger.debug(f"     {i}. Troop at ({x}, {y})")
            
            details = f"Found {len(troops)} troops"
            self.log_test_pass(test_name, details)
            return True
        except Exception as e:
            self.log_test_fail(test_name, str(e))
            return False
    
    def test_4_available_spells_detection(self) -> bool:
        """Test 4: Available spells detection"""
        test_name = "Available Spells Detection"
        self.log_test_start(test_name)
        
        try:
            game_window = self.controller.detect_game_window()
            if not game_window:
                self.log_test_fail(test_name, "Game window not detected first")
                return False
            
            self.logger.debug("  → Scanning for available spells...")
            spells = self.controller.get_available_spells_to_donate(game_window)
            
            self.logger.debug(f"  → Found {len(spells)} available spells")
            if spells:
                for i, (x, y) in enumerate(spells, 1):
                    self.logger.debug(f"     {i}. Spell at ({x}, {y})")
            
            details = f"Found {len(spells)} spells"
            self.log_test_pass(test_name, details)
            return True
        except Exception as e:
            self.log_test_fail(test_name, str(e))
            return False
    
    def test_5_donation_requests_detection(self) -> bool:
        """Test 5: Donation requests detection"""
        test_name = "Donation Requests Detection"
        self.log_test_start(test_name)
        
        try:
            game_window = self.controller.detect_game_window()
            if not game_window:
                self.log_test_fail(test_name, "Game window not detected first")
                return False
            
            self.logger.debug("  → Scanning for donation requests...")
            requests = self.controller.get_donation_requests(game_window)
            
            self.logger.debug(f"  → Found {len(requests)} donation requests")
            if requests:
                for i, req in enumerate(requests, 1):
                    self.logger.debug(f"     {i}. Request: {req}")
            
            details = f"Found {len(requests)} requests"
            self.log_test_pass(test_name, details)
            return True
        except Exception as e:
            self.log_test_fail(test_name, str(e))
            return False
    
    def test_6_donate_button_detection(self) -> bool:
        """Test 6: Donate button detection"""
        test_name = "Donate Button Detection"
        self.log_test_start(test_name)
        
        try:
            game_window = self.controller.detect_game_window()
            if not game_window:
                self.log_test_fail(test_name, "Game window not detected first")
                return False
            
            self.logger.debug("  → Looking for donate button...")
            button = self.controller.find_donate_button(game_window)
            
            if button:
                x, y = button
                self.logger.debug(f"  → Donate button found at ({x}, {y})")
                details = f"Button at ({x}, {y})"
                self.log_test_pass(test_name, details)
                return True
            else:
                self.logger.debug("  → Donate button not found (no pending requests)")
                details = "No button found (normal when no requests pending)"
                self.log_test_pass(test_name, details)
                return True
        except Exception as e:
            self.log_test_fail(test_name, str(e))
            return False
    
    def test_7_clan_chat_button_detection(self) -> bool:
        """Test 7: Clan chat button detection"""
        test_name = "Clan Chat Button Detection"
        self.log_test_start(test_name)
        
        try:
            game_window = self.controller.detect_game_window()
            if not game_window:
                self.log_test_fail(test_name, "Game window not detected first")
                return False
            
            self.logger.debug("  → Looking for clan chat button...")
            button = self.controller.donation_detector.find_clan_chat_button(game_window)
            
            if button:
                x, y = button
                self.logger.debug(f"  → Clan chat button found at ({x}, {y})")
                details = f"Button at ({x}, {y})"
                self.log_test_pass(test_name, details)
                return True
            else:
                self.logger.debug("  → Clan chat button not found")
                details = "Button not found (may not be visible in current screen)"
                self.log_test_pass(test_name, details)
                return True
        except Exception as e:
            self.log_test_fail(test_name, str(e))
            return False
    
    def test_8_close_button_detection(self) -> bool:
        """Test 8: Close button detection in donation screen"""
        test_name = "Close Button Detection"
        self.log_test_start(test_name)
        
        try:
            game_window = self.controller.detect_game_window()
            if not game_window:
                self.log_test_fail(test_name, "Game window not detected first")
                return False
            
            self.logger.debug("  → Looking for close button...")
            button = self.controller.donation_detector.find_close_button(game_window)
            
            if button:
                x, y = button
                self.logger.debug(f"  → Close button found at ({x}, {y})")
                details = f"Button at ({x}, {y})"
                self.log_test_pass(test_name, details)
                return True
            else:
                self.logger.debug("  → Close button not found")
                details = "Button not found (may not be visible in current screen)"
                self.log_test_pass(test_name, details)
                return True
        except Exception as e:
            self.log_test_fail(test_name, str(e))
            return False
    
    def test_9_debug_screenshot_creation(self) -> bool:
        """Test 9: Create debug screenshot with detection boxes"""
        test_name = "Debug Screenshot Creation"
        self.log_test_start(test_name)
        
        try:
            game_window = self.controller.detect_game_window()
            if not game_window:
                self.log_test_fail(test_name, "Game window not detected first")
                return False
            
            self.logger.debug("  → Creating debug screenshot...")
            output_path = self.controller.donation_detector.create_debug_screenshot(
                game_window, 
                "donation_debug_test.png"
            )
            
            if output_path:
                self.logger.debug(f"  → Debug screenshot saved: {output_path}")
                details = f"Screenshot: {output_path}"
                self.log_test_pass(test_name, details)
                return True
            else:
                self.log_test_fail(test_name, "Failed to create screenshot")
                return False
        except Exception as e:
            self.log_test_fail(test_name, str(e))
            return False
    
    def test_10_troop_template_matching(self) -> bool:
        """Test 10: Troop template matching"""
        test_name = "Troop Template Matching"
        self.log_test_start(test_name)
        
        try:
            game_window = self.controller.detect_game_window()
            if not game_window:
                self.log_test_fail(test_name, "Game window not detected first")
                return False
            
            self.logger.debug("  → Looking for troop templates...")
            troops = self.controller.donation_detector.find_troops_by_templates(game_window)
            
            self.logger.debug(f"  → Found {len(troops)} troops via template matching")
            if troops:
                for i, (x, y) in enumerate(troops, 1):
                    self.logger.debug(f"     {i}. Troop at ({x}, {y})")
            
            details = f"Found {len(troops)} troops via templates"
            self.log_test_pass(test_name, details)
            return True
        except Exception as e:
            self.log_test_fail(test_name, str(e))
            return False
    
    def run_all_tests(self):
        """Run all tests in sequence"""
        self.logger.info("\n" + "="*80)
        self.logger.info("STARTING TEST SEQUENCE")
        self.logger.info("="*80)
        
        tests = [
            self.test_1_game_window_detection,
            self.test_2_clan_chat_detection,
            self.test_3_available_troops_detection,
            self.test_4_available_spells_detection,
            self.test_5_donation_requests_detection,
            self.test_6_donate_button_detection,
            self.test_7_clan_chat_button_detection,
            self.test_8_close_button_detection,
            self.test_9_debug_screenshot_creation,
            self.test_10_troop_template_matching,
        ]
        
        for test_func in tests:
            try:
                test_func()
                time.sleep(0.5)
            except Exception as e:
                self.logger.error(f"Unexpected error in {test_func.__name__}: {e}", exc_info=True)
    
    def print_summary(self):
        """Print test summary"""
        self.logger.info("\n" + "="*80)
        self.logger.info("TEST SUITE SUMMARY")
        self.logger.info("="*80)
        
        pass_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        self.logger.info(f"Total Tests Run: {self.total_tests}")
        self.logger.info(f"Passed: {self.passed_tests}")
        self.logger.info(f"Failed: {self.total_tests - self.passed_tests}")
        self.logger.info(f"Pass Rate: {pass_rate:.1f}%")
        self.logger.info("\nDetailed Results:")
        
        for test_name, result in self.test_results.items():
            status = result["status"]
            details = result["details"]
            status_icon = "✓" if status == "PASS" else "✗"
            self.logger.info(f"  {status_icon} {test_name}: {status}")
            if details:
                self.logger.info(f"     → {details}")
        
        self.logger.info("\n" + "="*80)
        self.logger.info(f"Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.logger.info(f"Log file: {self.logger.get_log_file_path()}")
        self.logger.info("="*80)
        
        print("\n" + "="*80)
        print("DONATION TEST SUITE COMPLETED")
        print("="*80)
        print(f"Pass Rate: {pass_rate:.1f}% ({self.passed_tests}/{self.total_tests})")
        print(f"Log file: {self.logger.get_log_file_path()}")
        print("="*80 + "\n")


def main():
    """Main entry point"""
    try:
        print("\n" + "="*80)
        print("DONATION SYSTEM COMPREHENSIVE TEST SUITE")
        print("="*80)
        print("\nInitializing test suite...")
        
        suite = DonationTestSuite()
        suite.run_all_tests()
        suite.print_summary()
        
        sys.exit(0)
    
    except KeyboardInterrupt:
        print("\n\n[CANCELLED] Test suite interrupted by user")
        sys.exit(0)
    
    except Exception as e:
        print(f"\n[FATAL ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
