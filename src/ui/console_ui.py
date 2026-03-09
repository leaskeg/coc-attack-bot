import sys
import os
import time
from typing import Optional
from ..bot_controller import BotController
from ..utils.colored_output import ColoredOutput, Fore, Style
from ..utils.sound_notifier import SoundNotifier
from ..utils.progress_tracker import ProgressTracker, CountdownTimer, SpinnerDisplay
from ..utils.screen_utils import print_screen_info

class ConsoleUI:
    
    def __init__(self, bot_controller: BotController):
        self.bot = bot_controller
        self.running = True
        self.sound = SoundNotifier(enabled=self.bot.config.get('display.sound_notifications', True))
        self.use_colors = self.bot.config.get('display.colored_output', True)
        self.use_shortcuts = self.bot.config.get('display.quick_shortcuts', True)
    
    def clear_screen(self) -> None:
        """Clear console screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def run(self) -> None:
        """Main UI loop"""
        self.show_banner()
        
        while self.running:
            try:
                self.clear_screen()
                self.show_menu()
                choice = input("\nEnter your choice: ").strip()
                self.handle_choice(choice)
            except KeyboardInterrupt:
                print("\n\nShutting down...")
                self.running = False
            except EOFError:
                print("\n\nShutting down...")
                self.running = False
            except Exception as e:
                print(f"\nError: {e}")
                input("Press Enter to continue...")
        
        self.bot.shutdown()
    
    def show_banner(self) -> None:
        print("=" * 60)
        print("                    Application")
        print("=" * 60)
    
    def show_menu(self) -> None:
        if self.use_colors:
            ColoredOutput.header("MAIN MENU", width=50)
            ColoredOutput.menu_option("1", "Coordinate Mapping" + (" [C]" if self.use_shortcuts else ""))
            ColoredOutput.menu_option("2", "Session Recording" + (" [R]" if self.use_shortcuts else ""))
            ColoredOutput.menu_option("3", "Session Playback" + (" [P]" if self.use_shortcuts else ""))
            ColoredOutput.menu_option("4", "Automation System" + (" [A]" if self.use_shortcuts else ""))
            ColoredOutput.menu_option("5", "Window Detection" + (" [W]" if self.use_shortcuts else ""))
            ColoredOutput.menu_option("6", "Capture" + (" [S]" if self.use_shortcuts else ""))
            ColoredOutput.menu_option("7", "Settings" + (" [T]" if self.use_shortcuts else ""))
            ColoredOutput.menu_option("8", "Help" + (" [H]" if self.use_shortcuts else ""))
            ColoredOutput.menu_option("9", "Exit" + (" [Q]" if self.use_shortcuts else ""))
            print(f"{Fore.CYAN}{'=' * 50}{Style.RESET_ALL}")
        else:
            print("\n" + "=" * 40)
            print("           MENU")
            print("=" * 40)
            print("1. Coordinate Mapping")
            print("2. Session Recording")
            print("3. Session Playback")
            print("4. Automation System")
            print("5. Window Detection")
            print("6. Capture")
            print("7. Settings")
            print("8. Help")
            print("9. Exit")
            print("=" * 40)
    
    def handle_choice(self, choice: str) -> None:
        """Handle user menu choice"""
        # Normalize shortcuts
        choice = choice.lower()
        
        # Map shortcuts to numbers
        if self.use_shortcuts:
            shortcuts = {
                'c': '1', 'r': '2', 'p': '3', 'a': '4',
                'w': '5', 's': '6', 't': '7', 'h': '8', 'q': '9'
            }
            choice = shortcuts.get(choice, choice)
        
        if choice == '1':
            self.coordinate_mapping_menu()
        elif choice == '2':
            self.attack_recording_menu()
        elif choice == '3':
            self.attack_playback_menu()
        elif choice == '4':
            self.auto_attack_menu()
        elif choice == '5':
            self.game_detection_menu()
        elif choice == '6':
            self.screenshots_menu()
        elif choice == '7':
            self.settings_menu()
        elif choice == '8':
            self.show_help()
        elif choice == '9':
            self.sound.play_stop()
            self.running = False
        else:
            if self.use_colors:
                ColoredOutput.error("Invalid choice. Please try again.")
            else:
                print("Invalid choice. Please try again()")
            input("Press Enter to continue...")

    
    def auto_attack_menu(self) -> None:
        while True:
            self.clear_screen()
            print("\n" + "=" * 40)
            print("      AUTOMATION SYSTEM")
            print("=" * 40)
            
            if self.bot.is_auto_attacking():
                print("Status: RUNNING")
                stats = self.bot.get_auto_attack_stats()
                print(f"Sessions: {stats['total_attacks']} (Success: {stats['success_rate']:.1f}%)")
                print(f"Runtime: {stats['runtime_hours']:.1f} hours")
            else:
                print("Status: STOPPED")
            
            print("=" * 40)
            print("1. Setup Automation")
            print("2. Edit Attack Groups")
            print("3. Remove Attack Groups/Variations")
            print("4. Start Automation")
            print("5. Stop Automation")
            print("6. View Statistics")
            print("7. Configure Required Buttons")
            print("8. Back to main menu")
            print("=" * 40)
            
            choice = input("Enter your choice: ").strip()
            
            if choice == '1':
                self.setup_auto_attack()
            elif choice == '2':
                self.edit_auto_attack_groups()
            elif choice == '3':
                self.remove_auto_attack_groups()
            elif choice == '4':
                self.start_auto_attack()
            elif choice == '5':
                self.stop_auto_attack()
            elif choice == '6':
                self.show_auto_attack_stats()
            elif choice == '7':
                self.configure_auto_attack_buttons()
            elif choice == '8':
                self.clear_screen()
                break
            else:
                print("Invalid choice.")
    
    def setup_auto_attack(self) -> None:
        print("\nSetup Automation with Variations")
        
        sessions = self.bot.list_recorded_attacks()
        if not sessions:
            print("No sessions found")
            return
        
        print("Available sessions:")
        for i, session in enumerate(sessions, 1):
            print(f"  {i}. {session}")
        
        attack_groups = {}
        while True:
            print("\n" + "=" * 40)
            print("Current Groups:")
            if attack_groups:
                for attack_name, variations in attack_groups.items():
                    print(f"  {attack_name}: {variations}")
            else:
                print("  (None configured yet)")
            print("=" * 40)
            
            print("\nOptions:")
            print("1. Add a new group")
            print("2. Finish configuration")
            
            choice = input("Enter your choice: ").strip()
            
            if choice == '1':
                attack_name = input("\nEnter group name (e.g., 'group1'): ").strip()
                if not attack_name:
                    print("Name required")
                    continue
                
                if attack_name not in attack_groups:
                    attack_groups[attack_name] = []
                
                variations = []
                while True:
                    print(f"\nAdding variations to '{attack_name}'")
                    print("Variations:")
                    for i, session in enumerate(sessions, 1):
                        print(f"  {i}. {session}")
                    
                    choice = input("\nEnter session number to add (0 to finish adding variations): ").strip()
                    if choice == '0':
                        break
                    
                    try:
                        session_idx = int(choice) - 1
                        if 0 <= session_idx < len(sessions):
                            session_name = sessions[session_idx]
                            if session_name not in variations:
                                variations.append(session_name)
                                print(f"Added variation: {session_name}")
                            else:
                                print("Variation already added to this group")
                        else:
                            print("Invalid session number")
                    except ValueError:
                        print("Please enter a valid number")
                
                if variations:
                    attack_groups[attack_name] = variations
                    print(f"✅ Attack group '{attack_name}' configured with {len(variations)} variations")
                else:
                    print("No variations added for this group")
            
            elif choice == '2':
                break
            else:
                print("Invalid choice")
        
        if not attack_groups:
            print("No attack groups configured")
            return

        ai_enabled = input("\nEnable AI Analysis for this run? (y/n, default y): ").strip().lower()
        ai_enabled = ai_enabled != 'n'
        self.bot.config.set('ai_analyzer.enabled', ai_enabled)
        
        if ai_enabled:
            api_key = self.bot.config.get('ai_analyzer.google_gemini_api_key', '').strip()
            
            print("\nGoogle Gemini API Key setup:")
            if api_key:
                print(f"Current key: {api_key[:10]}...{api_key[-5:]}")
                use_existing = input("Use this key? (y/n, default y): ").strip().lower()
                if use_existing == 'n':
                    api_key = ""
            
            if not api_key:
                api_key = input("Please enter your Google Gemini API Key: ").strip()
                if not api_key:
                    print("❌ API Key cannot be empty. Disabling AI analysis.")
                    self.bot.config.set('ai_analyzer.enabled', False)
                else:
                    self.bot.config.set('ai_analyzer.google_gemini_api_key', api_key)
                    self.bot.ai_analyzer.api_key = api_key
            else:
                self.bot.ai_analyzer.api_key = api_key
            
            if self.bot.config.get('ai_analyzer.enabled'):
                print("Testing AI Connection...")
                if not self.bot.test_ai_connection():
                    print("❌ AI Connection Failed. Check your API key. Disabling AI for this run.")
                    self.bot.config.set('ai_analyzer.enabled', False)
                else:
                    print("✅ AI Connection Successful.")
        
        print("\nSet minimum loot requirements:")
        try:
            min_gold = int(input(f"Minimum Gold (default {self.bot.config.get('ai_analyzer.min_gold')}): ") or self.bot.config.get('ai_analyzer.min_gold'))
            min_elixir = int(input(f"Minimum Elixir (current: {self.bot.config.get('ai_analyzer.min_elixir')}): ") or self.bot.config.get('ai_analyzer.min_elixir'))
            min_dark_elixir = int(input(f"Minimum Dark Elixir (current: {self.bot.config.get('ai_analyzer.min_dark_elixir')}): ") or self.bot.config.get('ai_analyzer.min_dark_elixir'))
            max_townhall = int(input(f"Maximum Town Hall Level to attack (current: {self.bot.config.get('ai_analyzer.max_townhall_level')}): ") or self.bot.config.get('ai_analyzer.max_townhall_level'))
            self.bot.config.set('ai_analyzer.min_gold', min_gold)
            self.bot.config.set('ai_analyzer.min_elixir', min_elixir)
            self.bot.config.set('ai_analyzer.min_dark_elixir', min_dark_elixir)
            self.bot.config.set('ai_analyzer.max_townhall_level', max_townhall)
        except ValueError:
            print("Invalid input. Using default loot values.")

        self.bot.config.set('auto_attacker.attack_sessions', attack_groups)
        self.bot.auto_attacker.attack_sessions = attack_groups
        self.bot.config.save_config()
        
        print("\n" + "=" * 50)
        print("✅ Auto Attack Configured:")
        for attack_name, variations in attack_groups.items():
            print(f"  {attack_name}:")
            for var in variations:
                print(f"    - {var}")
        print(f"\n  AI Analysis: {'ENABLED' if self.bot.config.get('ai_analyzer.enabled') else 'DISABLED'}")
        if self.bot.config.get('ai_analyzer.enabled'):
            print(f"    Min Gold: {self.bot.config.get('ai_analyzer.min_gold'):,}")
            print(f"    Min Elixir: {self.bot.config.get('ai_analyzer.min_elixir'):,}")
            print(f"    Min Dark Elixir: {self.bot.config.get('ai_analyzer.min_dark_elixir'):,}")
            print(f"    Max Town Hall Level: {self.bot.config.get('ai_analyzer.max_townhall_level')}")
        print("=" * 50)
        print("Ready to start from the Auto Attack menu!")

    def start_auto_attack(self) -> None:
        if self.bot.is_auto_attacking():
            print("Automation is already running!")
            return
        
        is_valid, errors = self.bot.validate_auto_attack_config()
        if not is_valid:
            print("\n" + "=" * 60)
            print("         ❌ CONFIGURATION VALIDATION FAILED")
            print("=" * 60)
            for error in errors:
                print(error)
            print("=" * 60)
            print("\nPlease fix the above issues before starting automation.")
            input("\nPress Enter to continue...")
            return
        
        attack_sessions = self.bot.config.get('auto_attacker.attack_sessions', {})
        
        print("\n" + "=" * 50)
        print("         🚀 STARTING AUTOMATION 🚀")
        print("=" * 50)
        print("Configuration for this run:")
        for attack_name, variations in attack_sessions.items():
            print(f"  {attack_name}:")
            for var in variations:
                print(f"    - {var}")
        print(f"\n  AI Analysis: {'ENABLED' if self.bot.config.get('ai_analyzer.enabled') else 'DISABLED'}")
        if self.bot.config.get('ai_analyzer.enabled'):
            print(f"    Min Gold: {self.bot.config.get('ai_analyzer.min_gold'):,}")
            print(f"    Min Elixir: {self.bot.config.get('ai_analyzer.min_elixir'):,}")
            print(f"    Min Dark: {self.bot.config.get('ai_analyzer.min_dark_elixir'):,}")
            print(f"    Max TH: {self.bot.config.get('ai_analyzer.max_townhall_level')}")
        print("-" * 50)
        
        confirm = input("Confirm and start automation? (y/n): ").strip().lower()
        if confirm == 'y':
            self.bot.start_auto_attack()
            self.sound.play_start()
            if self.use_colors:
                ColoredOutput.success("Automation started successfully!")
            else:
                print("\n✅ Automation started successfully!")
            print("Press Ctrl+Alt+S to stop at any time.")
        else:
            print("Automation cancelled.")

    def stop_auto_attack(self) -> None:
        if not self.bot.is_auto_attacking():
            print("Automation is not running")
            return
        
        print("Stopping automation...")
        self.bot.stop_auto_attack()
        self.sound.play_stop()
        if self.use_colors:
            ColoredOutput.info("Automation stopped")
        else:
            print("Automation stopped")
    
    def show_auto_attack_stats(self) -> None:
        stats = self.bot.get_auto_attack_stats()
        
        print("\n" + "=" * 50)
        print("         AUTOMATION STATISTICS")
        print("=" * 50)
        print(f"Status: {'RUNNING' if stats['is_running'] else 'STOPPED'}")
        print(f"Total Sessions: {stats['total_attacks']}")
        print(f"Successful: {stats['successful_attacks']}")
        print(f"Failed: {stats['failed_attacks']}")
        print(f"Success Rate: {stats['success_rate']:.1f}%")
        print(f"Runtime: {stats['runtime_hours']:.1f} hours")
        print(f"Sessions/Hour: {stats['attacks_per_hour']:.1f}")
        print(f"Last Session: {stats['last_attack']}")
        print(f"Total Variations: {stats.get('total_variations', 0)}")
        print("\nConfigured Groups:")
        attacks = stats.get('configured_attacks', {})
        if attacks:
            for attack_name, variations in attacks.items():
                print(f"  {attack_name}: {len(variations)} variations")
                for var in variations:
                    print(f"    - {var}")
        else:
            print("  (None configured)")
        print("=" * 50)
        
        input("\nPress Enter to continue...")
    
    def configure_auto_attack_buttons(self) -> None:
        """Show required button mappings for auto attack"""
        summary = self.bot.get_validation_summary()
        required_buttons = self.bot.get_required_buttons()
        mapped_coords = self.bot.get_mapped_coordinates()
        
        print("\n" + "=" * 70)
        print("        REQUIRED BUTTON MAPPINGS & PROGRESS")
        print("=" * 70)
        
        mapped_count = len(summary['mapped_buttons'])
        total_count = len(required_buttons)
        progress_pct = (mapped_count / total_count * 100) if total_count > 0 else 0
        
        bar_length = 40
        filled = int(bar_length * progress_pct / 100)
        bar = "█" * filled + "░" * (bar_length - filled)
        print(f"\nProgress: [{bar}] {mapped_count}/{total_count} ({progress_pct:.0f}%)\n")
        
        print("Status:")
        for button_name, description in required_buttons.items():
            status = "✓ MAPPED" if button_name in mapped_coords else "✗ MISSING"
            status_color = "  " if button_name in mapped_coords else "  "
            print(f"{status_color} {button_name:20} | {status:10} | {description}")
        
        print("\n" + "=" * 70)
        
        if summary['missing_buttons']:
            print(f"\n⚠️  {len(summary['missing_buttons'])} buttons still need to be mapped:")
            for btn in summary['missing_buttons']:
                print(f"   - {btn}")
            print("\nTo map missing buttons:")
            print("1. Go to 'Coordinate Mapping' in the main menu")
            print("2. Select 'Start coordinate mapping'")
            print("3. Move mouse to button, press F2, enter button name")
            print("4. Press F3 to save when done")
        else:
            print("\n✅ All required buttons are mapped! Ready for automation.")
        
        input("\nPress Enter to continue...")
    
    def edit_auto_attack_groups(self) -> None:
        """Edit existing attack groups and variations"""
        attack_groups = self.bot.config.get('auto_attacker.attack_sessions', {})
        
        if not attack_groups:
            print("\nNo attack groups configured.")
            input("Press Enter to continue...")
            return
        
        print("\n" + "=" * 50)
        print("         EDIT ATTACK GROUPS")
        print("=" * 50)
        print("Current Groups:")
        group_list = list(attack_groups.keys())
        for i, (attack_name, variations) in enumerate(attack_groups.items(), 1):
            print(f"  {i}. {attack_name}: {len(variations)} variations")
            for var in variations:
                print(f"      - {var}")
        print("=" * 50)
        
        try:
            choice = int(input("\nEnter group number to edit (0 to cancel): ")) - 1
            if choice == -1:
                return
            
            if 0 <= choice < len(group_list):
                group_name = group_list[choice]
                current_variations = attack_groups[group_name]
                
                print(f"\nEditing group: {group_name}")
                print("Options:")
                print("1. Rename group")
                print("2. Add variations to group")
                print("3. Remove variations from group")
                print("4. Cancel")
                
                edit_choice = input("Enter your choice: ").strip()
                
                if edit_choice == '1':
                    new_name = input(f"Enter new name for '{group_name}': ").strip()
                    if new_name and new_name != group_name:
                        if new_name in attack_groups:
                            print(f"❌ Group '{new_name}' already exists")
                        else:
                            attack_groups[new_name] = attack_groups.pop(group_name)
                            self.bot.config.set('auto_attacker.attack_sessions', attack_groups)
                            self.bot.auto_attacker.attack_sessions = attack_groups
                            self.bot.config.save_config()
                            print(f"✅ Renamed group to '{new_name}'")
                    else:
                        print("Invalid name or no change")
                
                elif edit_choice == '2':
                    sessions = self.bot.list_recorded_attacks()
                    if not sessions:
                        print("No recorded sessions available")
                    else:
                        print("\nAvailable sessions:")
                        for i, session in enumerate(sessions, 1):
                            status = "✓" if session in current_variations else " "
                            print(f"  {i}. [{status}] {session}")
                        
                        while True:
                            var_choice = input("\nEnter session number to add (0 to finish): ").strip()
                            if var_choice == '0':
                                break
                            
                            try:
                                var_idx = int(var_choice) - 1
                                if 0 <= var_idx < len(sessions):
                                    session_name = sessions[var_idx]
                                    if session_name not in current_variations:
                                        current_variations.append(session_name)
                                        print(f"✅ Added '{session_name}'")
                                    else:
                                        print(f"'{session_name}' already in group")
                                else:
                                    print("Invalid session number")
                            except ValueError:
                                print("Invalid input")
                        
                        self.bot.config.set('auto_attacker.attack_sessions', attack_groups)
                        self.bot.auto_attacker.attack_sessions = attack_groups
                        self.bot.config.save_config()
                        print(f"✅ Group '{group_name}' updated")
                
                elif edit_choice == '3':
                    if not current_variations:
                        print("No variations to remove")
                    else:
                        print("\nCurrent variations:")
                        for i, var in enumerate(current_variations, 1):
                            print(f"  {i}. {var}")
                        
                        while True:
                            var_choice = input("\nEnter variation number to remove (0 to finish): ").strip()
                            if var_choice == '0':
                                break
                            
                            try:
                                var_idx = int(var_choice) - 1
                                if 0 <= var_idx < len(current_variations):
                                    removed = current_variations.pop(var_idx)
                                    print(f"✅ Removed '{removed}'")
                                    if not current_variations:
                                        print("⚠️  Group is now empty")
                                        break
                                else:
                                    print("Invalid variation number")
                            except ValueError:
                                print("Invalid input")
                        
                        self.bot.config.set('auto_attacker.attack_sessions', attack_groups)
                        self.bot.auto_attacker.attack_sessions = attack_groups
                        self.bot.config.save_config()
                        print(f"✅ Group '{group_name}' updated")
            else:
                print("Invalid selection")
        except ValueError:
            print("Invalid input")
        
        input("\nPress Enter to continue...")
    
    def remove_auto_attack_groups(self) -> None:
        """Remove attack groups or variations"""
        attack_groups = self.bot.config.get('auto_attacker.attack_sessions', {})
        
        if not attack_groups:
            print("\nNo attack groups configured.")
            input("Press Enter to continue...")
            return
        
        print("\n" + "=" * 50)
        print("       REMOVE ATTACK GROUPS/VARIATIONS")
        print("=" * 50)
        print("Current Groups:")
        group_list = list(attack_groups.keys())
        for i, (attack_name, variations) in enumerate(attack_groups.items(), 1):
            print(f"  {i}. {attack_name}: {len(variations)} variations")
            for var in variations:
                print(f"      - {var}")
        print("=" * 50)
        
        print("\nOptions:")
        print("1. Remove entire group")
        print("2. Remove specific variations from a group")
        print("3. Cancel")
        
        choice = input("Enter your choice: ").strip()
        
        if choice == '1':
            try:
                group_idx = int(input("\nEnter group number to remove: ")) - 1
                if 0 <= group_idx < len(group_list):
                    group_name = group_list[group_idx]
                    confirm = input(f"Remove entire group '{group_name}'? (y/n): ").strip().lower()
                    if confirm == 'y':
                        if self.bot.auto_attacker.remove_attack_session(group_name):
                            self.bot.config.save_config()
                            print(f"✅ Removed group '{group_name}'")
                        else:
                            print(f"❌ Failed to remove group")
                else:
                    print("Invalid selection")
            except ValueError:
                print("Invalid input")
        
        elif choice == '2':
            try:
                group_idx = int(input("\nEnter group number: ")) - 1
                if 0 <= group_idx < len(group_list):
                    group_name = group_list[group_idx]
                    variations = attack_groups[group_name]
                    
                    print(f"\nVariations in '{group_name}':")
                    for i, var in enumerate(variations, 1):
                        print(f"  {i}. {var}")
                    
                    var_idx = int(input("\nEnter variation number to remove: ")) - 1
                    if 0 <= var_idx < len(variations):
                        var_name = variations[var_idx]
                        confirm = input(f"Remove variation '{var_name}'? (y/n): ").strip().lower()
                        if confirm == 'y':
                            if self.bot.auto_attacker.remove_attack_session(group_name, var_name):
                                self.bot.config.save_config()
                                print(f"✅ Removed variation '{var_name}'")
                            else:
                                print(f"❌ Failed to remove variation")
                    else:
                        print("Invalid selection")
                else:
                    print("Invalid selection")
            except ValueError:
                print("Invalid input")
        
        input("\nPress Enter to continue...")

    def coordinate_mapping_menu(self) -> None:
        """Coordinate mapping submenu"""
        while True:
            self.clear_screen()
            print("\n" + "=" * 40)
            print("       COORDINATE MAPPING")
            print("=" * 40)
            print("1. Start coordinate mapping")
            print("2. View mapped coordinates")
            print("3. Edit coordinate")
            print("4. Delete coordinate")
            print("5. Export coordinates")
            print("6. Import coordinates")
            print("7. Back to main menu")
            print("=" * 40)
            
            choice = input("Enter your choice: ").strip()
            
            if choice == '1':
                print("\nStarting coordinate mapping mode...")
                print("Follow the on-screen instructions.")
                self.bot.start_coordinate_mapping()
            
            elif choice == '2':
                coords = self.bot.get_mapped_coordinates()
                if coords:
                    print("\n=== MAPPED COORDINATES ===")
                    for i, (name, coord) in enumerate(coords.items(), 1):
                        print(f"  {i}. {name}: ({coord['x']}, {coord['y']})")
                else:
                    print("No coordinates mapped yet.")
                input("\nPress Enter to continue...")
            
            elif choice == '3':
                coords = self.bot.get_mapped_coordinates()
                if not coords:
                    print("No coordinates to edit.")
                    continue
                
                print("\n=== SELECT COORDINATE TO EDIT ===")
                coord_list = list(coords.keys())
                for i, name in enumerate(coord_list, 1):
                    coord = coords[name]
                    print(f"  {i}. {name}: ({coord['x']}, {coord['y']})")
                
                try:
                    idx = int(input("\nEnter coordinate number to edit: ")) - 1
                    if 0 <= idx < len(coord_list):
                        coord_name = coord_list[idx]
                        if self.bot.coordinate_mapper.edit_coordinate(coord_name):
                            self.bot.coordinate_mapper.save_coordinates()
                    else:
                        print("Invalid selection")
                except ValueError:
                    print("Invalid input")
                input("\nPress Enter to continue...")
            
            elif choice == '4':
                coords = self.bot.get_mapped_coordinates()
                if not coords:
                    print("No coordinates to delete.")
                    continue
                
                print("\n=== SELECT COORDINATE TO DELETE ===")
                coord_list = list(coords.keys())
                for i, name in enumerate(coord_list, 1):
                    coord = coords[name]
                    print(f"  {i}. {name}: ({coord['x']}, {coord['y']})")
                
                try:
                    idx = int(input("\nEnter coordinate number to delete: ")) - 1
                    if 0 <= idx < len(coord_list):
                        coord_name = coord_list[idx]
                        confirm = input(f"Delete '{coord_name}'? (y/n): ").strip().lower()
                        if confirm == 'y':
                            if self.bot.coordinate_mapper.remove_coordinate(coord_name):
                                self.bot.coordinate_mapper.save_coordinates()
                                print(f"✅ Deleted '{coord_name}'")
                            else:
                                print(f"❌ Failed to delete '{coord_name}'")
                        else:
                            print("Delete cancelled")
                    else:
                        print("Invalid selection")
                except ValueError:
                    print("Invalid input")
                input("\nPress Enter to continue...")
            
            elif choice == '5':
                filename = input("Enter export filename (without extension): ").strip()
                if filename:
                    filepath = f"coordinates/{filename}.json"
                    self.bot.coordinate_mapper.export_coordinates(filepath)
            
            elif choice == '6':
                filename = input("Enter import filename: ").strip()
                if filename and os.path.exists(filename):
                    merge = input("Merge with existing coordinates? (y/n): ").strip().lower() == 'y'
                    self.bot.coordinate_mapper.import_coordinates(filename, merge)
                else:
                    print("File not found.")
            
            elif choice == '7':
                self.clear_screen()
                break
            else:
                print("Invalid choice.")
    
    def attack_recording_menu(self) -> None:
        while True:
            self.clear_screen()
            print("\n" + "=" * 40)
            print("       SESSION RECORDING")
            print("=" * 40)
            auto_status = "ENABLED" if self.bot.attack_recorder.auto_detect_clicks else "DISABLED"
            print(f"Auto-detection: {auto_status}")
            print("=" * 40)
            print("1. Start new recording")
            print("2. List recordings")
            print("3. View recording info")
            print("4. Rename recording")
            print("5. Delete recording")
            print("6. Toggle auto-detection")
            print("7. Back to main menu")
            print("=" * 40)
            
            choice = input("Enter your choice: ").strip()
            
            if choice == '1':
                session_name = input("Enter session name: ").strip()
                if session_name:
                    self.bot.start_attack_recording(session_name)
                    input("\nPress Enter when recording is complete...")
                    self.bot.stop_attack_recording()
                else:
                    print("Session name required.")
            
            elif choice == '2':
                sessions = self.bot.list_recorded_attacks()
                if sessions:
                    print("\n=== RECORDED SESSIONS ===")
                    for i, session in enumerate(sessions, 1):
                        print(f"  {i}. {session}")
                else:
                    print("No recorded sessions found.")
                input("\nPress Enter to continue...")
            
            elif choice == '3':
                sessions = self.bot.list_recorded_attacks()
                if not sessions:
                    print("No recordings available.")
                    input("Press Enter to continue...")
                    continue
                
                print("\n=== SELECT RECORDING TO VIEW INFO ===")
                for i, session in enumerate(sessions, 1):
                    print(f"  {i}. {session}")
                
                try:
                    idx = int(input("\nEnter recording number (0 to cancel): ")) - 1
                    if idx == -1:
                        continue
                    
                    if 0 <= idx < len(sessions):
                        session_name = sessions[idx]
                        info = self.bot.attack_recorder.get_recording_info(session_name)
                        if info:
                            print(f"\n=== SESSION INFO: {session_name} ===")
                            print(f"Created: {info['created']}")
                            print(f"Duration: {info['duration']:.1f} seconds")
                            print(f"Actions: {info['action_count']}")
                            print("Action types:")
                            for action_type, count in info['action_types'].items():
                                print(f"  {action_type}: {count}")
                        else:
                            print("Session not found.")
                    else:
                        print("Invalid selection")
                except ValueError:
                    print("Invalid input")
                
                input("Press Enter to continue...")
            
            elif choice == '4':
                sessions = self.bot.list_recorded_attacks()
                if not sessions:
                    print("No recordings to rename.")
                    continue
                
                print("\n=== SELECT RECORDING TO RENAME ===")
                for i, session in enumerate(sessions, 1):
                    print(f"  {i}. {session}")
                
                try:
                    idx = int(input("\nEnter recording number to rename: ")) - 1
                    if 0 <= idx < len(sessions):
                        old_name = sessions[idx]
                        new_name = input(f"Enter new name for '{old_name}': ").strip()
                        if new_name:
                            if self.bot.attack_recorder.rename_recording(old_name, new_name):
                                print(f"✅ Renamed '{old_name}' to '{new_name}'")
                            else:
                                print(f"❌ Failed to rename recording")
                        else:
                            print("Name cannot be empty")
                    else:
                        print("Invalid selection")
                except ValueError:
                    print("Invalid input")
                input("\nPress Enter to continue...")
            
            elif choice == '5':
                sessions = self.bot.list_recorded_attacks()
                if not sessions:
                    print("No recordings to delete.")
                    input("Press Enter to continue...")
                    continue
                
                print("\n=== SELECT RECORDING TO DELETE ===")
                for i, session in enumerate(sessions, 1):
                    print(f"  {i}. {session}")
                
                try:
                    idx = int(input("\nEnter recording number to delete (0 to cancel): ")) - 1
                    if idx == -1:
                        continue
                    
                    if 0 <= idx < len(sessions):
                        session_name = sessions[idx]
                        confirm = input(f"Delete '{session_name}'? (y/n): ").strip().lower()
                        if confirm == 'y':
                            if self.bot.attack_recorder.delete_recording(session_name):
                                self.sound.play_success()
                                if self.use_colors:
                                    ColoredOutput.success(f"Deleted '{session_name}'")
                                else:
                                    print(f"✅ Deleted '{session_name}'")
                            else:
                                self.sound.play_error()
                                if self.use_colors:
                                    ColoredOutput.error(f"Failed to delete '{session_name}'")
                                else:
                                    print(f"❌ Failed to delete '{session_name}'")
                        else:
                            print("Delete cancelled")
                    else:
                        print("Invalid selection")
                except ValueError:
                    print("Invalid input")
                
                input("Press Enter to continue...")
            
            elif choice == '6':
                # Toggle auto-detection
                self.bot.attack_recorder.auto_detect_clicks = not self.bot.attack_recorder.auto_detect_clicks
                status = "ENABLED" if self.bot.attack_recorder.auto_detect_clicks else "DISABLED"
                print(f"🖱️ Auto-click detection is now {status}")
                if self.bot.attack_recorder.auto_detect_clicks:
                    print("✅ Clicks will be automatically recorded during sessions")
                    print("💡 If you get unwanted clicks, use F6 for manual mode instead")
                else:
                    print("⚠️ You must use F6 to manually record each click during sessions")
                input("\nPress Enter to continue...")
            
            elif choice == '7':
                self.clear_screen()
                break
            else:
                print("Invalid choice.")
    
    def attack_playback_menu(self) -> None:
        while True:
            self.clear_screen()
            print("\n" + "=" * 40)
            print("       SESSION PLAYBACK")
            print("=" * 40)
            print("1. Play session")
            print("2. Preview recording")
            print("3. Validate recording")
            print("4. Set playback speed")
            print("5. Back to main menu")
            print("=" * 40)
            
            choice = input("Enter your choice: ").strip()
            
            if choice == '1':
                sessions = self.bot.list_recorded_attacks()
                if not sessions:
                    print("No recorded sessions available.")
                    continue
                
                print("\nAvailable sessions:")
                for i, session in enumerate(sessions, 1):
                    print(f"  {i}. {session}")
                
                try:
                    session_idx = int(input("Select session number: ")) - 1
                    if 0 <= session_idx < len(sessions):
                        session_name = sessions[session_idx]
                        speed = float(input("Playback speed (1.0 = normal): ") or "1.0")
                        
                        print(f"\nStarting playback of '{session_name}' at {speed}x speed")
                        print("Make sure COC is visible and in the correct state!")
                        input("Press Enter to begin...")
                        
                        self.bot.attack_player.play_attack(session_name, speed)
                        
                        # Wait for playback to complete
                        while self.bot.attack_player.is_playing:
                            time.sleep(0.5)
                    else:
                        print("Invalid session number.")
                except ValueError:
                    print("Invalid input.")
            
            elif choice == '2':
                sessions = self.bot.list_recorded_attacks()
                if not sessions:
                    print("No recorded sessions available.")
                    input("Press Enter to continue...")
                    continue
                
                print("\nAvailable sessions:")
                for i, session in enumerate(sessions, 1):
                    print(f"  {i}. {session}")
                
                try:
                    session_idx = int(input("\nSelect session number to preview (0 to cancel): ")) - 1
                    if session_idx == -1:
                        continue
                    
                    if 0 <= session_idx < len(sessions):
                        session_name = sessions[session_idx]
                        self.bot.attack_player.preview_recording(session_name)
                    else:
                        print("Invalid session number.")
                except ValueError:
                    print("Invalid input.")
                
                input("\nPress Enter to continue...")
            
            elif choice == '3':
                sessions = self.bot.list_recorded_attacks()
                if not sessions:
                    print("No recorded sessions available.")
                    input("Press Enter to continue...")
                    continue
                
                print("\nAvailable sessions:")
                for i, session in enumerate(sessions, 1):
                    print(f"  {i}. {session}")
                
                try:
                    session_idx = int(input("\nSelect session number to validate (0 to cancel): ")) - 1
                    if session_idx == -1:
                        continue
                    
                    if 0 <= session_idx < len(sessions):
                        session_name = sessions[session_idx]
                        validation = self.bot.attack_player.validate_recording(session_name)
                        print(f"\n=== VALIDATION RESULT ===")
                        print(f"Valid: {validation['valid']}")
                        print(f"Total actions: {validation['total_actions']}")
                        print(f"Duration: {validation['duration']:.1f} seconds")
                        
                        if not validation['valid']:
                            print(f"Error: {validation['error']}")
                            if validation.get('out_of_bounds'):
                                print("Out of bounds actions:")
                                for i, x, y in validation['out_of_bounds'][:5]:
                                    print(f"  Action {i}: ({x}, {y})")
                    else:
                        print("Invalid session number.")
                except ValueError:
                    print("Invalid input.")
                
                input("\nPress Enter to continue...")
            
            elif choice == '4':
                try:
                    speed = float(input("Enter playback speed (0.1 - 5.0): "))
                    self.bot.attack_player.set_playback_speed(speed)
                except ValueError:
                    print("Invalid speed value.")
            
            elif choice == '5':
                self.clear_screen()
                break
            else:
                print("Invalid choice.")
    
    def game_detection_menu(self) -> None:
        """Game detection submenu"""
        print("\n" + "=" * 40)
        print("       GAME DETECTION")
        print("=" * 40)
        
        # Show screen configuration first
        print_screen_info()
        
        print("\nDetecting COC game window...")
        bounds = self.bot.detect_game_window()
        
        if bounds:
            x, y, width, height = bounds
            if self.use_colors:
                ColoredOutput.success("Game window found!")
            else:
                print("Game window found!")
            print(f"Position: ({x}, {y})")
            print(f"Size: {width} x {height}")
            
            # Check which monitor the game is on
            if x >= 1920:
                print(f"ℹ️  Game appears to be on secondary monitor (X > 1920)")
            
            screenshot = input("\nTake screenshot of game window? (y/n): ").strip().lower()
            if screenshot == 'y':
                filepath = self.bot.take_screenshot(bounds)
                print(f"Screenshot saved: {filepath}")
        else:
            if self.use_colors:
                ColoredOutput.error("Game window not found.")
            else:
                print("Game window not found.")
            print("Make sure Clash of Clans is running and visible.")
        
        input("\nPress Enter to continue...")
    
    def screenshots_menu(self) -> None:
        """Screenshots submenu"""
        while True:
            self.clear_screen()
            print("\n" + "=" * 40)
            print("         SCREENSHOTS")
            print("=" * 40)
            print("1. Take full screen screenshot")
            print("2. Take game window screenshot")
            print("3. View screenshots folder")
            print("4. Back to main menu")
            print("=" * 40)
            
            choice = input("Enter your choice: ").strip()
            
            if choice == '1':
                filepath = self.bot.take_screenshot()
                print(f"Screenshot saved: {filepath}")
                input("\nPress Enter to continue...")
            
            elif choice == '2':
                bounds = self.bot.detect_game_window()
                if bounds:
                    filepath = self.bot.take_screenshot(bounds)
                    print(f"Screenshot saved: {filepath}")
                else:
                    print("Game window not found.")
                input("\nPress Enter to continue...")
            
            elif choice == '3':
                screenshots_dir = "screenshots"
                if os.path.exists(screenshots_dir):
                    files = [f for f in os.listdir(screenshots_dir) if f.endswith('.png')]
                    if files:
                        print(f"\nScreenshots in {screenshots_dir}:")
                        for file in sorted(files)[-10:]:  # Show last 10
                            print(f"  {file}")
                        if len(files) > 10:
                            print(f"  ... and {len(files) - 10} more")
                    else:
                        print("No screenshots found.")
                else:
                    print("Screenshots directory not found.")
                input("\nPress Enter to continue...")
            
            elif choice == '4':
                self.clear_screen()
                break
            else:
                print("Invalid choice.")
    
    def settings_menu(self) -> None:
        """Settings submenu"""
        while True:
            self.clear_screen()
            print("\n" + "=" * 60)
            print("                    SETTINGS")
            print("=" * 60)
            
            print("\n📋 AUTOMATION SETTINGS:")
            print(f"  Click Delay: {self.bot.config.get('automation.default_click_delay')}s")
            print(f"  Playback Speed: {self.bot.config.get('automation.default_playback_speed')}x")
            print(f"  Failsafe: {'Enabled' if self.bot.config.get('automation.failsafe_enabled') else 'Disabled'}")
            print(f"  Click Variation: {'Enabled' if self.bot.config.get('automation.enable_click_variation') else 'Disabled'}")
            print(f"  Click Variance: {self.bot.config.get('automation.click_variance_pixels')}px")
            
            print("\n🤖 AUTO ATTACKER SETTINGS:")
            print(f"  Max Search Attempts: {self.bot.config.get('auto_attacker.max_search_attempts')}")
            print(f"  Battle Duration Min: {self.bot.config.get('auto_attacker.battle_duration_min')}s")
            print(f"  Battle Duration Max: {self.bot.config.get('auto_attacker.battle_duration_max')}s")
            print(f"  Base Load Wait: {self.bot.config.get('auto_attacker.base_load_wait')}s")
            
            print("\n🧠 AI ANALYZER SETTINGS:")
            print(f"  AI Enabled: {'Yes' if self.bot.config.get('ai_analyzer.enabled') else 'No'}")
            print(f"  Min Gold: {self.bot.config.get('ai_analyzer.min_gold'):,}")
            print(f"  Min Elixir: {self.bot.config.get('ai_analyzer.min_elixir'):,}")
            print(f"  Min Dark Elixir: {self.bot.config.get('ai_analyzer.min_dark_elixir'):,}")
            print(f"  Max Town Hall: {self.bot.config.get('ai_analyzer.max_townhall_level')}")
            
            print("\n🎨 UI/UX SETTINGS:")
            print(f"  Colored Output: {'Enabled' if self.bot.config.get('display.colored_output') else 'Disabled'}")
            print(f"  Progress Bars: {'Enabled' if self.bot.config.get('display.show_progress_bars') else 'Disabled'}")
            print(f"  Sound Notifications: {'Enabled' if self.bot.config.get('display.sound_notifications') else 'Disabled'}")
            print(f"  Quick Shortcuts: {'Enabled' if self.bot.config.get('display.quick_shortcuts') else 'Disabled'}")
            
            print("\n" + "=" * 60)
            print("1. Edit Automation Settings")
            print("2. Edit Auto Attacker Settings")
            print("3. Edit AI Analyzer Settings")
            print("4. Edit UI/UX Settings")
            print("5. Reset to Defaults")
            print("6. Export Config")
            print("7. Back to main menu")
            print("=" * 60)
            
            choice = input("\nEnter your choice: ").strip()
            
            if choice == '1':
                self._edit_automation_settings()
            elif choice == '2':
                self._edit_auto_attacker_settings()
            elif choice == '3':
                self._edit_ai_analyzer_settings()
            elif choice == '4':
                self._edit_ui_settings()
            elif choice == '5':
                confirm = input("Reset all settings to defaults? (y/n): ").strip().lower()
                if confirm == 'y':
                    self.bot.config.reset_to_defaults()
                    ColoredOutput.success("Settings reset to defaults")
                    input("Press Enter to continue...")
            elif choice == '6':
                filename = input("Enter export filename: ").strip()
                if filename:
                    self.bot.config.export_config(filename)
                    input("Press Enter to continue...")
            elif choice == '7':
                break
            else:
                print("Invalid choice.")
                input("Press Enter to continue...")
    
    def _edit_automation_settings(self) -> None:
        """Edit automation settings"""
        print("\n" + "=" * 50)
        print("       EDIT AUTOMATION SETTINGS")
        print("=" * 50)
        print("1. Click Delay")
        print("2. Playback Speed")
        print("3. Toggle Failsafe")
        print("4. Toggle Click Variation")
        print("5. Click Variance Pixels")
        print("6. Back")
        
        choice = input("\nEnter your choice: ").strip()
        
        if choice == '1':
            try:
                delay = float(input(f"Current: {self.bot.config.get('automation.default_click_delay')}s\nEnter new click delay (0.01-2.0): "))
                if 0.01 <= delay <= 2.0:
                    self.bot.config.set('automation.default_click_delay', delay)
                    self.bot.config.save_config()
                    print(f"✅ Click delay set to {delay}s")
                else:
                    print("❌ Value out of range")
            except ValueError:
                print("❌ Invalid input")
        
        elif choice == '2':
            try:
                speed = float(input(f"Current: {self.bot.config.get('automation.default_playback_speed')}x\nEnter new playback speed (0.1-5.0): "))
                if 0.1 <= speed <= 5.0:
                    self.bot.config.set('automation.default_playback_speed', speed)
                    self.bot.config.save_config()
                    print(f"✅ Playback speed set to {speed}x")
                else:
                    print("❌ Value out of range")
            except ValueError:
                print("❌ Invalid input")
        
        elif choice == '3':
            current = self.bot.config.get('automation.failsafe_enabled')
            self.bot.config.set('automation.failsafe_enabled', not current)
            self.bot.config.save_config()
            print(f"✅ Failsafe {'enabled' if not current else 'disabled'}")
        
        elif choice == '4':
            current = self.bot.config.get('automation.enable_click_variation')
            self.bot.config.set('automation.enable_click_variation', not current)
            self.bot.config.save_config()
            print(f"✅ Click variation {'enabled' if not current else 'disabled'}")
        
        elif choice == '5':
            try:
                pixels = int(input(f"Current: {self.bot.config.get('automation.click_variance_pixels')}px\nEnter new variance (1-20): "))
                if 1 <= pixels <= 20:
                    self.bot.config.set('automation.click_variance_pixels', pixels)
                    self.bot.config.save_config()
                    print(f"✅ Click variance set to {pixels}px")
                else:
                    print("❌ Value out of range")
            except ValueError:
                print("❌ Invalid input")
        
        input("\nPress Enter to continue...")
    
    def _edit_auto_attacker_settings(self) -> None:
        """Edit auto attacker settings"""
        print("\n" + "=" * 50)
        print("      EDIT AUTO ATTACKER SETTINGS")
        print("=" * 50)
        print("1. Max Search Attempts")
        print("2. Battle Duration Min")
        print("3. Battle Duration Max")
        print("4. Base Load Wait")
        print("5. Base Wait After Reject")
        print("6. Attack Button Delay")
        print("7. Back")
        
        choice = input("\nEnter your choice: ").strip()
        
        if choice == '1':
            try:
                attempts = int(input(f"Current: {self.bot.config.get('auto_attacker.max_search_attempts')}\nEnter new max search attempts (1-50): "))
                if 1 <= attempts <= 50:
                    self.bot.config.set('auto_attacker.max_search_attempts', attempts)
                    self.bot.config.save_config()
                    print(f"✅ Max search attempts set to {attempts}")
                else:
                    print("❌ Value out of range")
            except ValueError:
                print("❌ Invalid input")
        
        elif choice == '2':
            try:
                duration = int(input(f"Current: {self.bot.config.get('auto_attacker.battle_duration_min')}s\nEnter new battle duration min (60-300): "))
                if 60 <= duration <= 300:
                    self.bot.config.set('auto_attacker.battle_duration_min', duration)
                    self.bot.config.save_config()
                    print(f"✅ Battle duration min set to {duration}s")
                else:
                    print("❌ Value out of range")
            except ValueError:
                print("❌ Invalid input")
        
        elif choice == '3':
            try:
                duration = int(input(f"Current: {self.bot.config.get('auto_attacker.battle_duration_max')}s\nEnter new battle duration max (60-400): "))
                if 60 <= duration <= 400:
                    self.bot.config.set('auto_attacker.battle_duration_max', duration)
                    self.bot.config.save_config()
                    print(f"✅ Battle duration max set to {duration}s")
                else:
                    print("❌ Value out of range")
            except ValueError:
                print("❌ Invalid input")
        
        elif choice == '4':
            try:
                wait = float(input(f"Current: {self.bot.config.get('auto_attacker.base_load_wait')}s\nEnter new base load wait (1.0-10.0): "))
                if 1.0 <= wait <= 10.0:
                    self.bot.config.set('auto_attacker.base_load_wait', wait)
                    self.bot.config.save_config()
                    print(f"✅ Base load wait set to {wait}s")
                else:
                    print("❌ Value out of range")
            except ValueError:
                print("❌ Invalid input")
        
        elif choice == '5':
            try:
                wait = float(input(f"Current: {self.bot.config.get('auto_attacker.base_wait_after_reject')}s\nEnter new base wait after reject (1.0-10.0): "))
                if 1.0 <= wait <= 10.0:
                    self.bot.config.set('auto_attacker.base_wait_after_reject', wait)
                    self.bot.config.save_config()
                    print(f"✅ Base wait after reject set to {wait}s")
                else:
                    print("❌ Value out of range")
            except ValueError:
                print("❌ Invalid input")
        
        elif choice == '6':
            try:
                delay = float(input(f"Current: {self.bot.config.get('auto_attacker.attack_button_delay')}s\nEnter new attack button delay (0.5-5.0): "))
                if 0.5 <= delay <= 5.0:
                    self.bot.config.set('auto_attacker.attack_button_delay', delay)
                    self.bot.config.save_config()
                    print(f"✅ Attack button delay set to {delay}s")
                else:
                    print("❌ Value out of range")
            except ValueError:
                print("❌ Invalid input")
        
        input("\nPress Enter to continue...")
    
    def _edit_ai_analyzer_settings(self) -> None:
        """Edit AI analyzer settings"""
        print("\n" + "=" * 50)
        print("       EDIT AI ANALYZER SETTINGS")
        print("=" * 50)
        print("1. Toggle AI Analyzer")
        print("2. Set Google Gemini API Key")
        print("3. Min Gold")
        print("4. Min Elixir")
        print("5. Min Dark Elixir")
        print("6. Max Town Hall Level")
        print("7. Back")
        
        choice = input("\nEnter your choice: ").strip()
        
        if choice == '1':
            current = self.bot.config.get('ai_analyzer.enabled')
            self.bot.config.set('ai_analyzer.enabled', not current)
            self.bot.config.save_config()
            print(f"✅ AI Analyzer {'enabled' if not current else 'disabled'}")
        
        elif choice == '2':
            api_key = input("Enter Google Gemini API Key: ").strip()
            if api_key:
                self.bot.config.set('ai_analyzer.google_gemini_api_key', api_key)
                self.bot.config.save_config()
                self.bot.ai_analyzer.api_key = api_key
                print("✅ API Key updated")
            else:
                print("❌ API Key cannot be empty")
        
        elif choice == '3':
            try:
                gold = int(input(f"Current: {self.bot.config.get('ai_analyzer.min_gold'):,}\nEnter new min gold: "))
                if gold >= 0:
                    self.bot.config.set('ai_analyzer.min_gold', gold)
                    self.bot.config.save_config()
                    print(f"✅ Min gold set to {gold:,}")
                else:
                    print("❌ Value must be positive")
            except ValueError:
                print("❌ Invalid input")
        
        elif choice == '4':
            try:
                elixir = int(input(f"Current: {self.bot.config.get('ai_analyzer.min_elixir'):,}\nEnter new min elixir: "))
                if elixir >= 0:
                    self.bot.config.set('ai_analyzer.min_elixir', elixir)
                    self.bot.config.save_config()
                    print(f"✅ Min elixir set to {elixir:,}")
                else:
                    print("❌ Value must be positive")
            except ValueError:
                print("❌ Invalid input")
        
        elif choice == '5':
            try:
                dark = int(input(f"Current: {self.bot.config.get('ai_analyzer.min_dark_elixir'):,}\nEnter new min dark elixir: "))
                if dark >= 0:
                    self.bot.config.set('ai_analyzer.min_dark_elixir', dark)
                    self.bot.config.save_config()
                    print(f"✅ Min dark elixir set to {dark:,}")
                else:
                    print("❌ Value must be positive")
            except ValueError:
                print("❌ Invalid input")
        
        elif choice == '6':
            try:
                th = int(input(f"Current: {self.bot.config.get('ai_analyzer.max_townhall_level')}\nEnter new max town hall level (1-17): "))
                if 1 <= th <= 17:
                    self.bot.config.set('ai_analyzer.max_townhall_level', th)
                    self.bot.config.save_config()
                    print(f"✅ Max town hall level set to {th}")
                else:
                    print("❌ Value out of range")
            except ValueError:
                print("❌ Invalid input")
        
        input("\nPress Enter to continue...")
    
    def _edit_ui_settings(self) -> None:
        """Edit UI/UX settings"""
        print("\n" + "=" * 50)
        print("         EDIT UI/UX SETTINGS")
        print("=" * 50)
        print("1. Toggle Colored Output")
        print("2. Toggle Progress Bars")
        print("3. Toggle Sound Notifications")
        print("4. Toggle Quick Shortcuts")
        print("5. Test Sound Notification")
        print("6. Back")
        
        choice = input("\nEnter your choice: ").strip()
        
        if choice == '1':
            current = self.bot.config.get('display.colored_output')
            self.bot.config.set('display.colored_output', not current)
            self.bot.config.save_config()
            self.use_colors = not current
            status = "enabled" if not current else "disabled"
            ColoredOutput.success(f"Colored output {status}")
            ColoredOutput.info("Restart for full effect")
        
        elif choice == '2':
            current = self.bot.config.get('display.show_progress_bars')
            self.bot.config.set('display.show_progress_bars', not current)
            self.bot.config.save_config()
            status = "enabled" if not current else "disabled"
            ColoredOutput.success(f"Progress bars {status}")
        
        elif choice == '3':
            current = self.bot.config.get('display.sound_notifications')
            self.bot.config.set('display.sound_notifications', not current)
            self.bot.config.save_config()
            self.sound.enabled = not current
            status = "enabled" if not current else "disabled"
            ColoredOutput.success(f"Sound notifications {status}")
            if not current:
                self.sound.play_success()
        
        elif choice == '4':
            current = self.bot.config.get('display.quick_shortcuts')
            self.bot.config.set('display.quick_shortcuts', not current)
            self.bot.config.save_config()
            self.use_shortcuts = not current
            status = "enabled" if not current else "disabled"
            ColoredOutput.success(f"Quick shortcuts {status}")
            if not current:
                ColoredOutput.info("Use letters like [A] for Automation, [C] for Coordinates, etc.")
        
        elif choice == '5':
            print("\n🔊 Testing sound notifications...")
            print("Playing success sound...")
            self.sound.play_success()
            time.sleep(0.5)
            print("Playing error sound...")
            self.sound.play_error()
            time.sleep(0.5)
            print("Playing warning sound...")
            self.sound.play_warning()
            time.sleep(0.5)
            print("Playing notification sound...")
            self.sound.play_notification()
            ColoredOutput.success("Sound test complete!")
        
        input("\nPress Enter to continue...")
    
    def show_help(self) -> None:
        """Display help information"""
        print("\n" + "=" * 60)
        print("                    HELP")
        print("=" * 60)
        print("""
GETTING STARTED:
1. Open Clash of Clans in full screen
2. Use 'Game Detection' to verify the bot can find your game
3. Map button coordinates for your screen resolution
4. Record attack sessions
5. Set up and start auto attack

COORDINATE MAPPING:
- Use F1 to start/stop mapping mode
- Move mouse to buttons and press F2 to record positions
- Press F3 to save coordinates
- ESC to cancel mapping

ATTACK RECORDING:
- Press F5 to start/stop recording
- Press F6 to manually record clicks
- Press F7 to add delays
- All mouse clicks are automatically recorded

ATTACK PLAYBACK:
- Press F8 to pause/resume during playback
- Press F9 to stop playback
- ESC for emergency stop

AUTO ATTACK SYSTEM - EXACT STRATEGY:
1. Click attack button
2. Click find_a_match to search for base  
3. Wait few seconds and take screenshot
4. Check enemy_gold, enemy_elixir, enemy_dark_elixir
5. If loot is good → start attack recording
6. If loot is bad → click next_button to skip
7. After attack starts → wait 3 minutes for battle
8. Click return_home button to go back
9. Repeat continuously
- Emergency stop: Ctrl+Alt+S

REQUIRED BUTTONS FOR AUTO ATTACK:
- attack: Main attack button on home screen
- find_a_match: Search for opponents
- next_button: Skip to next target
- return_home: Return to village after battle
- end_button: End battle button
- loot_1 through loot_8: Army slots (troops/spells for deployment)

OPTIONAL FOR LOOT CHECKING:
- enemy_gold: Enemy's gold display on attack screen
- enemy_elixir: Enemy's elixir display on attack screen
- enemy_dark_elixir: Enemy's dark elixir display on attack screen

TIPS:
- Make sure COC is in the same state when playing back
- Test recordings on practice attacks first
- Use slower speeds (0.5x) for more reliable playback
- Keep your screen resolution consistent
- Always supervise automation

SAFETY:
- Move mouse to top-left corner to trigger failsafe
- Use Ctrl+Alt+S for emergency stop during auto attack
- Always supervise bot operation
- Use at your own risk
        """)
        input("\nPress Enter to continue...") 