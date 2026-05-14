# Implementing ClashFarmer-Like Automation

This guide shows how to implement the full ClashFarmer attack flow in your bot.

## ClashFarmer Flow vs Your Bot

### ClashFarmer Output:
```
Starting Search Loop
1. Gold 465369, Elixir 482487, DElixir 6528 → (Dead base)
Found a base that satisfies the conditions
Planning attack strategy...
10 seconds have passed, activating hero abilities.
Battle ended
Zooming out.
```

### Your Bot Equivalent:
```python
# Starting Search Loop
while auto_attacking:
    resources = read_base_resources()
    classification = classify_base(resources)
    should_attack, reason = is_base_worth_attacking(resources)
    
    if should_attack:
        execute_attack_with_strategy()
```

---

## Complete Implementation

### 1. **Search & Analyze Loop**

```python
from src.bot_controller import BotController
import time

controller = BotController()
game_region = controller.detect_game_window()

print("=" * 60)
print("Starting Search Loop")
print("=" * 60)

search_count = 1
search_limit = 100

while search_count <= search_limit:
    # Read base resources
    resources = controller.read_base_resources(game_region)
    gold = resources['gold']
    elixir = resources['elixir']
    dark_elixir = resources['dark_elixir']
    
    # Classify base
    classification = controller.classify_base(resources)
    
    print(f"{search_count}. Gold {gold}, Elixir {elixir}, DElixir {dark_elixir}")
    print(f"   ({classification})")
    
    # Check if worth attacking
    should_attack, reason = controller.is_base_worth_attacking(
        resources,
        min_gold=100000,
        min_elixir=100000,
        min_dark=1000
    )
    
    if should_attack:
        print("✓ Found a base that satisfies the conditions")
        break
    else:
        print(f"   ✗ Skipped: {reason}")
        
        # Click next base button
        # TODO: Click "Next" button
        time.sleep(0.5)
        search_count += 1

if should_attack:
    execute_attack_flow(controller, game_region, resources)
else:
    print("No suitable base found after searching")
```

### 2. **Execute Attack with Strategy**

```python
def execute_attack_flow(controller, game_region, resources):
    print("\n" + "=" * 60)
    print(f"Planning attack strategy...")
    print("=" * 60)
    
    # Get strategy config
    strategy = controller.auto_attacker.get_strategy_config()
    
    print(f"Attack Mode: {controller.get_attack_mode().upper()}")
    print(f"Deploy Speed: Wave={strategy.deploy_speed.wave_deployment_speed}, "
          f"Troop={strategy.deploy_speed.troop_deployment_speed}")
    print(f"Attack Sides: {', '.join(controller.auto_attacker.get_attack_sides())}")
    
    # Select army recipe (if not already selected)
    print("\nSelecting army recipes...")
    # TODO: Click army recipe buttons
    
    # Click attack/fight button
    print("Entering battle...\n")
    # TODO: Click "Attack" button
    
    battle_start_time = time.time()
    
    # Find deployment zones
    deployment_zones = controller.auto_attacker.find_deployment_zones(game_region)
    print(f"✓ Found {len(deployment_zones)} smart deployment zones")
    
    previous_deployments = []
    deploy_count = 0
    
    # Main battle loop
    while True:
        elapsed = time.time() - battle_start_time
        
        # Activate heroes at configured time
        hero_delay = controller.auto_attacker.get_hero_activation_delay()
        if hero_delay and elapsed >= hero_delay and deploy_count > 2:
            if not hasattr(execute_attack_flow, 'heroes_activated'):
                print(f"\n⚡ {hero_delay}s have passed, activating hero abilities.")
                # TODO: Click hero ability buttons
                execute_attack_flow.heroes_activated = True
        
        # Check end battle conditions
        end_timeout = controller.auto_attacker.get_end_battle_timeout()
        if end_timeout and elapsed >= end_timeout:
            print(f"\n⏹ Battle timeout ({end_timeout}s) reached - ending battle")
            # TODO: Click end battle / return to home
            break
        
        # Deploy next troop
        deploy_point = controller.auto_attacker.select_deployment_point(
            deployment_zones,
            previous_deployments
        )
        
        if deploy_point:
            print(f"  → Deploying troop #{deploy_count + 1} at {deploy_point}")
            # TODO: Select troop from bar
            # TODO: Click deployment point
            previous_deployments.append(deploy_point)
            deploy_count += 1
            
            # Respect deploy speed
            deploy_factor = controller.auto_attacker.get_deploy_speed_factor('troop')
            time.sleep(0.3 * deploy_factor)
        
        # Check if battle is complete
        if elapsed > 300:  # 5 minutes max
            print("⏹ Battle ended")
            break
        
        time.sleep(0.5)
    
    # Battle finished
    print("\nBattle ended")
    print("Zooming out.")
    # TODO: Zoom out animation
    
    print("\n" + "=" * 60)
    print("ATTACK COMPLETE")
    print(f"Resources Gained: ~{resources['gold']}, ~{resources['elixir']}, ~{resources['dark_elixir']}")
    print("=" * 60 + "\n")
```

### 3. **Full Attack Loop (Search → Attack → Repeat)**

```python
def run_full_attack_loop(controller):
    """
    Complete attack loop matching ClashFarmer flow
    """
    print("🤖 COC Attack Bot Started")
    print("=" * 60)
    
    attack_count = 0
    search_count = 0
    
    while True:
        try:
            game_region = controller.detect_game_window()
            if not game_region:
                print("❌ Game window not detected")
                time.sleep(5)
                continue
            
            print(f"\n{'=' * 60}")
            print(f"ATTACK CYCLE #{attack_count + 1}")
            print(f"{'=' * 60}")
            
            # Search for base
            print("\nStarting Search Loop")
            found_base = False
            search_attempts = 0
            
            while search_attempts < 50:  # Max 50 searches
                search_attempts += 1
                search_count += 1
                
                # Read resources
                resources = controller.read_base_resources(game_region)
                classification = controller.classify_base(resources)
                
                print(f"{search_count}. Gold {resources['gold']}, "
                      f"Elixir {resources['elixir']}, "
                      f"DElixir {resources['dark_elixir']}")
                print(f"   ({classification})")
                
                # Check if suitable
                should_attack, reason = controller.is_base_worth_attacking(resources)
                
                if should_attack:
                    print("✓ Found a base that satisfies the conditions")
                    found_base = True
                    break
                else:
                    print(f"   ✗ {reason}")
                    # Click next
                    # TODO: Click next button
                    time.sleep(1)
            
            if not found_base:
                print("⚠ No suitable base found. Retrying...")
                time.sleep(5)
                continue
            
            # Execute attack
            execute_attack_flow(controller, game_region, resources)
            
            attack_count += 1
            
            # Wait before next attack
            print(f"\n⏳ Waiting 10 seconds before next attack...")
            time.sleep(10)
            
        except KeyboardInterrupt:
            print("\n\n⏹ Attack bot stopped by user")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            time.sleep(5)


if __name__ == "__main__":
    controller = BotController()
    run_full_attack_loop(controller)
```

---

## Resource Detection Accuracy

### Current Implementation:
- **Method**: Color-based pixel counting (no OCR required)
- **Accuracy**: ~70-80% (depends on game theme/lighting)
- **Speed**: ~200ms per screen

### To Improve Accuracy:
1. **Install Tesseract OCR** (optional for better accuracy):
   ```bash
   # Download from: https://github.com/UB-Mannheim/tesseract/wiki
   choco install tesseract  # or manual install
   ```

2. **Update resource_reader.py** to use Tesseract:
   ```python
   import pytesseract
   text = pytesseract.image_to_string(roi, config='--psm 7')
   ```

### Setting Thresholds:

```python
# Conservative: High resources only
should_attack, _ = controller.is_base_worth_attacking(
    resources,
    min_gold=500000,      # 500K minimum
    min_elixir=500000,    # 500K minimum
    min_dark=5000         # 5K minimum
)

# Aggressive: Accept lower resources
should_attack, _ = controller.is_base_worth_attacking(
    resources,
    min_gold=50000,       # 50K minimum
    min_elixir=50000,     # 50K minimum
    min_dark=500          # 500 minimum
)
```

---

## Integration with GUI

The **Attack Strategy** tab already controls:

- **Deploy speeds**: Wave and troop deployment timing
- **Attack sides**: NW, NE, SW, SE quadrant selection
- **Deployment strategy**: Near defenses vs collectors
- **Hero timing**: When to activate abilities
- **Human-like behavior**: Click variance, hesitations, mouse parking

All configured settings are automatically used by the attack loop!

---

## Logging & Monitoring

Enable detailed logging to monitor attacks:

```python
from src.utils.logger import Logger

logger = Logger()
logger.info("Attack started")
logger.debug(f"Resources detected: {resources}")
logger.info("Attack completed")
```

Check `logs/` directory for detailed attack logs.

---

## Next Steps

1. **Implement button detection**: Detect "Next", "Attack", "End Battle" buttons
2. **Troop bar integration**: Auto-select troops from army bar
3. **Army recipe auto-selection**: Detect current army and switch recipes if needed
4. **Zoom detection**: Confirm zoom out after battle
5. **Error recovery**: Handle stuck bases, connection issues, etc.

See `DEPLOYMENT_INTEGRATION_EXAMPLE.py` for more code examples!
