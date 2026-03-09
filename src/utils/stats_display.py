import os
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, Optional


class StatsDisplay:
    
    def __init__(self, refresh_interval: float = 10.0):
        self.refresh_interval = refresh_interval
        self.display_thread = None
        self.is_running = False
        self.last_stats = {}
        self.lock = threading.Lock()
    
    def start(self, stats_getter) -> None:
        """Start the stats display thread"""
        if self.is_running:
            return
        
        self.is_running = True
        self.stats_getter = stats_getter
        self.display_thread = threading.Thread(target=self._display_loop, daemon=True)
        self.display_thread.start()
    
    def stop(self) -> None:
        """Stop the stats display thread"""
        self.is_running = False
        if self.display_thread:
            self.display_thread.join(timeout=5)
    
    def _display_loop(self) -> None:
        """Main display loop"""
        try:
            while self.is_running:
                try:
                    stats = self.stats_getter()
                    with self.lock:
                        self.last_stats = stats
                    
                    self._print_stats(stats)
                    
                except Exception as e:
                    print(f"[ERROR] Stats display error: {e}")
                
                time.sleep(self.refresh_interval)
        
        except Exception as e:
            print(f"[ERROR] Fatal stats display error: {e}")
        finally:
            self.is_running = False
    
    def _print_stats(self, stats: Dict) -> None:
        """Print stats in a formatted way"""
        clear_screen()
        
        print("\n" + "=" * 70)
        print("                    LIVE AUTO-ATTACK STATISTICS")
        print("=" * 70)
        
        if stats.get('is_running'):
            status = "🟢 RUNNING"
        else:
            status = "🔴 STOPPED"
        
        print(f"\n📊 Status: {status}")
        print(f"⏱️  Runtime: {stats.get('runtime_hours', 0):.2f} hours")
        
        print("\n📈 Attack Statistics:")
        print(f"  Total Attacks: {stats.get('total_attacks', 0)}")
        print(f"  ✅ Successful: {stats.get('successful_attacks', 0)}")
        print(f"  ❌ Failed: {stats.get('failed_attacks', 0)}")
        
        success_rate = stats.get('success_rate', 0)
        bar_length = 30
        filled = int(bar_length * success_rate / 100)
        bar = "█" * filled + "░" * (bar_length - filled)
        print(f"  Success Rate: [{bar}] {success_rate:.1f}%")
        
        print(f"\n⚡ Performance:")
        print(f"  Attacks/Hour: {stats.get('attacks_per_hour', 0):.1f}")
        print(f"  Last Attack: {stats.get('last_attack', 'N/A')}")
        
        configured_attacks = stats.get('configured_attacks', {})
        if configured_attacks:
            print(f"\n🎯 Configured Attack Groups ({len(configured_attacks)} total):")
            for attack_name, variations in configured_attacks.items():
                print(f"  • {attack_name}: {len(variations)} variations")
        
        print("\n" + "=" * 70)
        print("Press Ctrl+C to stop automation")
        print("=" * 70 + "\n")
    
    def get_last_stats(self) -> Dict:
        """Get the last displayed stats"""
        with self.lock:
            return self.last_stats.copy()


def clear_screen() -> None:
    """Clear the console screen"""
    os.system('cls' if os.name == 'nt' else 'clear')


class SimpleStatsDisplay:
    """Simple single-line stats display without thread"""
    
    @staticmethod
    def print_inline_stats(stats: Dict) -> str:
        """Return inline stats string for single-line display"""
        total = stats.get('total_attacks', 0)
        success = stats.get('successful_attacks', 0)
        failed = stats.get('failed_attacks', 0)
        success_rate = stats.get('success_rate', 0)
        runtime = stats.get('runtime_hours', 0)
        attacks_per_hour = stats.get('attacks_per_hour', 0)
        
        return (
            f"[{total:3d}] ✅{success:3d} ❌{failed:3d} | "
            f"Rate: {success_rate:5.1f}% | "
            f"⏱️ {runtime:6.2f}h | "
            f"⚡ {attacks_per_hour:5.1f}/h"
        )
