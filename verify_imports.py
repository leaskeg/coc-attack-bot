#!/usr/bin/env python3
import sys

print("Testing imports...")

try:
    print("  - Importing attack_strategy...")
    from src.utils.attack_strategy import AttackStrategyConfig, DeploySpeedSettings
    print("    ✓ attack_strategy imported")
    
    print("  - Creating default config...")
    config = AttackStrategyConfig.default()
    print(f"    ✓ Default config created")
    print(f"      Wave speed: {config.deploy_speed.wave_deployment_speed}")
    print(f"      Attack sides: {config.strategy.attack_sides}")
    print(f"      Hero enabled: {config.hero_ability.enabled}")
    print(f"      Mouse parking enabled: {config.human_like_variations.enable_mouse_parking}")
    
    print("  - Testing to_dict and from_dict...")
    config_dict = config.to_dict()
    config_restored = AttackStrategyConfig.from_dict(config_dict)
    print(f"    ✓ Config serialization works")
    
    print("\n✅ All imports successful!")
    sys.exit(0)
    
except Exception as e:
    print(f"\n❌ Import error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
