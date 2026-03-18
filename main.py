#!/usr/bin/env python3

import sys
import os
import argparse
import time
from src.bot_controller import BotController
from src.ui.console_ui import ConsoleUI
from src.ui.gui import BotGUI
from src.utils.logger import Logger
from src.utils.stats_display import StatsDisplay


def run_headless_auto_attack(controller: BotController, group_name: str = None, show_live_stats: bool = True):
    """Run auto-attack in headless mode without UI"""
    logger = Logger()
    
    is_valid, errors = controller.validate_auto_attack_config()
    if not is_valid:
        print("\n❌ CONFIGURATION VALIDATION FAILED:")
        for error in errors:
            print(error)
        sys.exit(1)
    
    attack_sessions = controller.config.get('auto_attacker.attack_sessions', {})
    
    if group_name:
        if group_name not in attack_sessions:
            print(f"❌ Attack group '{group_name}' not found!")
            print(f"Available groups: {', '.join(attack_sessions.keys())}")
            sys.exit(1)
        selected_group = {group_name: attack_sessions[group_name]}
    else:
        selected_group = attack_sessions
    
    print("\n" + "=" * 60)
    print("         🚀 HEADLESS AUTO-ATTACK MODE 🚀")
    print("=" * 60)
    print(f"Configuration:")
    for attack_name, variations in selected_group.items():
        print(f"  {attack_name}: {len(variations)} variations")
        for var in variations:
            print(f"    - {var}")
    print(f"AI Analysis: {'ENABLED' if controller.config.get('ai_analyzer.enabled') else 'DISABLED'}")
    print("=" * 60)
    print("Starting in 5 seconds... (Press Ctrl+C to cancel)")
    
    try:
        for i in range(5, 0, -1):
            print(f"\r{i}...", end="", flush=True)
            time.sleep(1)
        print("\n")
    except KeyboardInterrupt:
        print("\n\nCancelled.")
        sys.exit(0)
    
    stats_display = None
    if show_live_stats:
        stats_display = StatsDisplay(refresh_interval=15.0)
        stats_display.start(controller.get_auto_attack_stats)
    
    controller.start_auto_attack()
    print("✅ Auto-attack started! Press Ctrl+C to stop.")
    
    try:
        while controller.is_auto_attacking():
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\nStopping auto-attack...")
        controller.stop_auto_attack()
        time.sleep(2)
    finally:
        if stats_display:
            stats_display.stop()
    
    stats = controller.get_auto_attack_stats()
    print("\n" + "=" * 60)
    print("         FINAL STATISTICS")
    print("=" * 60)
    print(f"Total Sessions: {stats['total_attacks']}")
    print(f"Successful: {stats['successful_attacks']}")
    print(f"Failed: {stats['failed_attacks']}")
    print(f"Success Rate: {stats['success_rate']:.1f}%")
    print(f"Runtime: {stats['runtime_hours']:.2f} hours")
    print(f"Attacks/Hour: {stats['attacks_per_hour']:.1f}")
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description="COC Attack Bot - Automated Clash of Clans attack automation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                    # Start interactive UI
  python main.py --auto-attack      # Run auto-attack with all configured groups
  python main.py --auto-attack -g group1  # Run specific attack group
  python main.py --config config.json     # Use custom config file
        """
    )
    
    parser.add_argument(
        '--auto-attack',
        action='store_true',
        help='Run auto-attack in headless mode (no UI)'
    )
    parser.add_argument(
        '--console',
        action='store_true',
        help='Use the legacy console UI instead of the GUI'
    )
    parser.add_argument(
        '-g', '--group',
        type=str,
        default=None,
        help='Specific attack group to run (for headless mode)'
    )
    parser.add_argument(
        '--config',
        type=str,
        default='src/utils/config.py',
        help='Path to config file (default: src/utils/config.py)'
    )
    
    args = parser.parse_args()
    
    try:
        logger = Logger()
        logger.info("Starting application...")
        
        controller = BotController()
        
        if args.auto_attack:
            run_headless_auto_attack(controller, args.group)
        elif args.console:
            ui = ConsoleUI(controller)
            ui.run()
        else:
            gui = BotGUI(controller)
            gui.run()
        
    except KeyboardInterrupt:
        print("\n[INFO] Application stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"[ERROR] Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main() 