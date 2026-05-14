#!/usr/bin/env python3
"""
Example: How to integrate deployment detection into your attack execution
This shows how to use the detection system in your attack loop
"""

from src.bot_controller import BotController
import time


def example_attack_with_smart_deployment():
    """
    Example attack flow using smart deployment detection
    """
    controller = BotController()
    
    game_region = controller.detect_game_window()
    if not game_region:
        print("❌ Game window not found!")
        return
    
    print("✓ Game window detected")
    
    # Get deployment zones based on configured strategy
    deployment_zones = controller.auto_attacker.find_deployment_zones(game_region)
    
    if not deployment_zones:
        print("⚠️  No deployment zones found - using fallback positions")
    else:
        print(f"✅ Found {len(deployment_zones)} intelligent deployment zones:")
        for i, zone in enumerate(deployment_zones[:5]):  # Show first 5
            print(f"   Zone {i+1}: {zone}")
    
    # Track where we've already deployed
    previous_deployments = []
    
    troop_types = ['archer', 'barbarian', 'giant', 'goblin']
    deployment_count = 0
    
    for troop in troop_types:
        # Get next deployment point (avoids previous spots)
        deploy_point = controller.auto_attacker.select_deployment_point(
            deployment_zones, 
            previous_deployments
        )
        
        if not deploy_point:
            print(f"⚠️  No valid deployment point for {troop}")
            continue
        
        print(f"📍 Deploying {troop} at {deploy_point}")
        
        # TODO: Click troop in bar
        # TODO: Click deployment point
        # TODO: Add human-like delays
        
        previous_deployments.append(deploy_point)
        deployment_count += 1
        
        # Respect deploy speed setting
        deploy_speed = controller.auto_attacker.get_deploy_speed_factor('troop')
        time.sleep(0.5 * deploy_speed)  # Scale delay by deploy_speed factor
    
    print(f"✅ Deployed {deployment_count} troops intelligently!")


def example_wave_deployment():
    """
    Example using wave deployment (split into multiple waves)
    """
    controller = BotController()
    
    game_region = controller.detect_game_window()
    deployment_zones = controller.auto_attacker.find_deployment_zones(game_region)
    
    # Get number of waves from strategy config
    num_waves = controller.auto_attacker.get_split_waves()
    print(f"🌊 Splitting attack into {num_waves} wave(s)")
    
    # Strategy: use different zones for each wave
    zones_per_wave = len(deployment_zones) // num_waves
    
    for wave in range(num_waves):
        print(f"\n🌊 Wave {wave + 1}/{num_waves}")
        
        # Get zones for this wave
        wave_zones = deployment_zones[
            wave * zones_per_wave:(wave + 1) * zones_per_wave
        ]
        
        # Deploy in this wave's zones
        for zone in wave_zones[:3]:  # Example: 3 deployments per zone
            print(f"  → Deploying at {zone}")
            # TODO: Actual deployment
            time.sleep(0.3)
        
        # Wait between waves
        if wave < num_waves - 1:
            wait_time = 2.0
            print(f"  ⏳ Waiting {wait_time}s before next wave...")
            time.sleep(wait_time)


def example_hero_activation():
    """
    Example: Activate heroes at the right moment
    """
    controller = BotController()
    
    hero_delay = controller.auto_attacker.get_hero_activation_delay()
    
    if hero_delay is None:
        print("⚠️  Hero ability is disabled in strategy settings")
        return
    
    print(f"⚔️  Hero will be activated after {hero_delay} seconds")
    
    attack_start = time.time()
    
    # Simulate deployment loop
    while True:
        elapsed = time.time() - attack_start
        
        if elapsed >= hero_delay:
            print(f"⚡ {hero_delay}s reached - ACTIVATING HEROES!")
            # TODO: Click hero button / activate ability
            break
        
        # TODO: Continue deploying troops
        time.sleep(0.5)


def example_end_battle_detection():
    """
    Example: Auto-end battle when no resources are being collected
    """
    controller = BotController()
    
    end_timeout = controller.auto_attacker.get_end_battle_timeout()
    
    if end_timeout is None:
        print("⚠️  Auto-end battle is disabled")
        return
    
    print(f"⏹️  Battle will auto-end if no resources for {end_timeout}s")
    
    last_resource_time = time.time()
    
    # Simulate battle loop
    while True:
        current_time = time.time()
        
        # Check if resources are being collected
        # TODO: Read resource counter from screen
        resources_gained = False  # Example value
        
        if resources_gained:
            last_resource_time = current_time
        
        no_resource_duration = current_time - last_resource_time
        
        if no_resource_duration >= end_timeout:
            print(f"⏹️  No resources collected for {end_timeout}s - ENDING BATTLE!")
            # TODO: Click end battle button
            break
        
        time.sleep(0.5)


def example_deployment_side_filtering():
    """
    Example: Deploy from specific sides (NW, NE, SW, SE)
    """
    controller = BotController()
    
    game_region = controller.detect_game_window()
    all_zones = controller.auto_attacker.find_deployment_zones(game_region)
    
    enabled_sides = controller.auto_attacker.get_attack_sides()
    print(f"🎯 Attack sides enabled: {', '.join(enabled_sides)}")
    
    # Simple implementation: divide board into quadrants
    x_min, y_min, width, height = game_region
    x_mid = x_min + width // 2
    y_mid = y_min + height // 2
    
    filtered_zones = []
    for x, y in all_zones:
        side = None
        if x < x_mid and y < y_mid:
            side = 'NW'
        elif x >= x_mid and y < y_mid:
            side = 'NE'
        elif x < x_mid and y >= y_mid:
            side = 'SW'
        elif x >= x_mid and y >= y_mid:
            side = 'SE'
        
        if side in enabled_sides:
            filtered_zones.append((x, y))
    
    print(f"✓ Filtered to {len(filtered_zones)} zones on enabled sides")
    return filtered_zones


if __name__ == "__main__":
    print("=" * 60)
    print("DEPLOYMENT DETECTION - INTEGRATION EXAMPLES")
    print("=" * 60)
    
    print("\n[Example 1] Smart Deployment with Zone Detection")
    print("-" * 60)
    # Uncomment to run: example_attack_with_smart_deployment()
    print("(Disabled - requires game running)")
    
    print("\n[Example 2] Wave-Based Deployment")
    print("-" * 60)
    print("(Disabled - requires game running)")
    
    print("\n[Example 3] Hero Activation Timing")
    print("-" * 60)
    print("(Disabled - requires game running)")
    
    print("\n[Example 4] Auto-End Battle Detection")
    print("-" * 60)
    print("(Disabled - requires game running)")
    
    print("\n[Example 5] Side-Based Deployment")
    print("-" * 60)
    print("(Disabled - requires game running)")
    
    print("\n" + "=" * 60)
    print("To use these examples:")
    print("1. Start Clash of Clans game")
    print("2. Open attack screen showing enemy base")
    print("3. Uncomment examples in main() to test")
    print("=" * 60)
