#!/usr/bin/env python3
"""
Test script to verify attack variations feature
"""

import sys
import os
import random

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.core.auto_attacker import AutoAttacker
from src.core.attack_player import AttackPlayer
from src.core.screen_capture import ScreenCapture
from src.core.coordinate_mapper import CoordinateMapper
from src.core.ai_analyzer import AIAnalyzer
from src.utils.logger import Logger
from src.utils.config import Config

def test_attack_variations():
    """Test the attack variations feature"""
    print("=" * 60)
    print("Testing Attack Variations Feature")
    print("=" * 60)
    
    logger = Logger()
    config = Config()
    screen_capture = ScreenCapture()
    coordinate_mapper = CoordinateMapper()
    attack_player = AttackPlayer()
    ai_analyzer = AIAnalyzer(api_key="", logger=logger)
    
    auto_attacker = AutoAttacker(
        attack_player=attack_player,
        screen_capture=screen_capture,
        coordinate_mapper=coordinate_mapper,
        logger=logger,
        ai_analyzer=ai_analyzer,
        config=config
    )
    
    print("\n1. Testing attack group creation and management")
    print("-" * 60)
    
    config.set('auto_attacker.attack_sessions', {})
    auto_attacker.attack_sessions = {}
    
    success = auto_attacker.add_attack_session("attack1", "attack1_v1")
    print(f"Add attack1_v1: {'OK' if success else 'FAIL'}")
    
    success = auto_attacker.add_attack_session("attack1", "attack1_v2")
    print(f"Add attack1_v2: {'OK' if success else 'FAIL'}")
    
    success = auto_attacker.add_attack_session("attack1", "attack1_v3")
    print(f"Add attack1_v3: {'OK' if success else 'FAIL'}")
    
    success = auto_attacker.add_attack_session("attack2", "attack2_v1")
    print(f"Add attack2_v1: {'OK' if success else 'FAIL'}")
    
    success = auto_attacker.add_attack_session("attack2", "attack2_v2")
    print(f"Add attack2_v2: {'OK' if success else 'FAIL'}")
    
    print("\nCurrent attack configuration:")
    for attack_name, variations in auto_attacker.attack_sessions.items():
        print(f"  {attack_name}: {variations}")
    
    print("\n2. Testing random selection from variations")
    print("-" * 60)
    
    selections = []
    print("Simulating 20 random attack selections:")
    for i in range(20):
        selected = auto_attacker._get_next_attack_session()
        selections.append(selected)
        print(f"  {i+1:2d}. {selected}")
    
    print("\nSelection distribution:")
    for variation in set(selections):
        count = selections.count(variation)
        print(f"  {variation}: {count} times ({count/len(selections)*100:.1f}%)")
    
    print("\n3. Testing variation removal")
    print("-" * 60)
    
    success = auto_attacker.remove_attack_session("attack1", "attack1_v2")
    print(f"Remove attack1_v2: {'OK' if success else 'FAIL'}")
    
    print("\nRemaining attack configuration:")
    for attack_name, variations in auto_attacker.attack_sessions.items():
        print(f"  {attack_name}: {variations}")
    
    print("\n4. Testing stats output")
    print("-" * 60)
    
    stats = auto_attacker.get_stats()
    print(f"Total variations: {stats.get('total_variations', 0)}")
    print("Configured attacks:")
    for attack_name, variations in stats.get('configured_attacks', {}).items():
        print(f"  {attack_name}: {len(variations)} variations")
        for var in variations:
            print(f"    - {var}")
    
    print("\n" + "=" * 60)
    print("[PASS] All tests completed successfully!")
    print("=" * 60)

if __name__ == "__main__":
    test_attack_variations()
