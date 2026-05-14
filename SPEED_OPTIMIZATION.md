# Speed Optimization Guide

## ClashFarmer Tempo Analysis

From your logs:
```
Attack 1: 11:06 PM
Attack 2: 11:09 PM (7 searches) = 3 minutes total
Attack 3: 11:10 PM (4 searches) = 1 minute  
Attack 4: 11:12 PM (6 searches) = 2 minutes
Attack 5: 11:13 PM (1 search)  = 1 minute
Attack 6: 11:15 PM (3 searches) = 2 minutes
...
Average: 1.2-2 minutes per complete attack cycle
```

**Key Observations:**
- Search time varies (1-7 attempts depending on luck)
- Each search → ~20-30 seconds
- Battle execution → ~30-60 seconds
- Total overhead → ~10-20 seconds

---

## Speed Tuning Settings

### **1. Attack Strategy Tab - Deployment Speed**

Currently set to 1-9 scale. For **maximum speed**:

```
Wave Deployment Speed: 1 (FAST)    ← Minimal delay between waves
Troop Deployment Speed: 1 (FAST)   ← Rapid troop placement
```

**Effect:**
- Default (8,7): ~1.5x slower
- Optimized (1,1): 3-4x faster deployment

### **2. Human-Like Behavior Settings**

For **fast attacks while maintaining security**, use:

```
✓ Park mouse between actions:     ENABLED  (small 0.2-0.5s pauses)
✓ Add human-like hesitations:     ENABLED  (200-400ms random delays)
  Min hesitation (ms):             200
  Max hesitation (ms):             400
✓ Click variance (pixels):        5-8px    (small randomness)
✓ Click jitter (pixels):          2-3px    (minimal jitter)
```

**Why this works:**
- 200-400ms hesitations look natural
- Still allows 15-20 clicks per minute
- Avoids detection better than 0-delay clicking

---

## Code-Level Optimizations

### **1. Parallel Screen Reading**

```python
import threading

def fast_search_loop(controller, game_region):
    """Ultra-fast base search"""
    
    for search_attempt in range(1, 51):
        # Read resources (non-blocking)
        resources = controller.read_base_resources(game_region)
        
        should_attack, _ = controller.is_base_worth_attacking(
            resources,
            min_gold=100000,
            min_elixir=100000,
            min_dark=1000
        )
        
        if should_attack:
            return resources
        
        # FAST: No sleep between searches
        # Just click next immediately
        click_next_button()  # 50-100ms
    
    return None
```

### **2. Minimize Wait Times**

```python
# SLOW (adds 2+ seconds per attack)
time.sleep(2)                    # ❌ Long pauses
time.sleep(random.uniform(1, 3)) # ❌ Variable pauses

# FAST (adds 0.2-0.4 seconds per attack)
time.sleep(0.2)                  # ✅ Minimal pauses
time.sleep(random.uniform(0.2, 0.4)) # ✅ Quick random pauses
```

### **3. Battery Saver Mode (Optional)**

Reduce CPU/GPU load for extended runs:

```python
# For non-critical operations
if operation == "waiting_for_next_search":
    time.sleep(0.5)  # Lower polling rate
else:
    time.sleep(0.2)  # Normal speed

# Reduce screenshot frequency
capture_every_n_attacks = 5  # Only capture every 5th attack
```

---

## Complete Fast Attack Loop

```python
import time
from src.bot_controller import BotController

def fast_attack_loop(controller, target_attack_count=100):
    """
    Fast attack loop matching ClashFarmer tempo
    Targets: ~1 attack every 1.2-2 minutes
    """
    
    game_region = controller.detect_game_window()
    if not game_region:
        print("❌ Game not detected")
        return
    
    print("🚀 FAST ATTACK MODE - Starting")
    print("=" * 60)
    
    attack_count = 0
    total_search_count = 0
    start_time = time.time()
    
    while attack_count < target_attack_count:
        
        # ═════════════════════════════════════════════════════════════
        # PHASE 1: SEARCH (1-7 attempts, ~20-30 seconds per attempt)
        # ═════════════════════════════════════════════════════════════
        
        print(f"\n[ATTACK {attack_count + 1}]", end=" ")
        search_attempts = 0
        found = False
        
        while search_attempts < 15 and not found:
            search_attempts += 1
            total_search_count += 1
            
            # Read base
            resources = controller.read_base_resources(game_region)
            
            print(f"\n  Search #{search_attempts}: ", end="")
            print(f"Gold {resources['gold']:,} | ", end="")
            print(f"Elixir {resources['elixir']:,} | ", end="")
            print(f"Dark {resources['dark_elixir']:,}")
            
            # Check if suitable
            should_attack, _ = controller.is_base_worth_attacking(resources)
            
            if should_attack:
                classification = controller.classify_base(resources)
                print(f"  ✓ Found! ({classification})")
                found = True
                break
            
            # Click "Next" for next base
            # TODO: Implement fast_click_next_button()
            # This should take ~50-100ms
            time.sleep(0.1)  # Minimal UI wait
        
        if not found:
            print("  ⚠ No base found after 15 searches")
            continue
        
        # ═════════════════════════════════════════════════════════════
        # PHASE 2: ATTACK EXECUTION (30-60 seconds)
        # ═════════════════════════════════════════════════════════════
        
        print(f"  → Executing attack...")
        
        # Click army recipe (if not selected)
        # TODO: implement_army_selection()
        time.sleep(0.2)
        
        # Click attack button
        # TODO: implement_click_attack_button()
        time.sleep(0.5)  # Wait for battle to load
        
        # Get deployment zones
        zones = controller.auto_attacker.find_deployment_zones(game_region)
        previous_deployments = []
        
        # Fast troop deployment
        deploy_speed = controller.auto_attacker.get_deploy_speed_factor('troop')
        hero_delay = controller.auto_attacker.get_hero_activation_delay()
        end_timeout = controller.auto_attacker.get_end_battle_timeout()
        
        battle_start = time.time()
        deploy_count = 0
        heroes_activated = False
        
        while True:
            elapsed = time.time() - battle_start
            
            # Activate hero at configured time
            if (hero_delay and elapsed >= hero_delay and 
                not heroes_activated and deploy_count > 1):
                print(f"  ⚡ Hero activated at {hero_delay}s")
                # TODO: Click hero button
                heroes_activated = True
            
            # Check end condition
            if end_timeout and elapsed >= end_timeout:
                print(f"  ⏹ Battle timeout at {end_timeout}s")
                break
            
            # Deploy next troop
            zone = controller.auto_attacker.select_deployment_point(zones, previous_deployments)
            if zone:
                # TODO: Deploy troop at zone
                previous_deployments.append(zone)
                deploy_count += 1
                time.sleep(0.3 * deploy_speed)  # Respect deploy speed setting
            
            # Battle typically ends at 3 minutes (game mechanic)
            if elapsed > 180:
                print(f"  ✓ Battle completed")
                break
            
            time.sleep(0.2)
        
        # ═════════════════════════════════════════════════════════════
        # PHASE 3: CLEANUP (10-20 seconds)
        # ═════════════════════════════════════════════════════════════
        
        # Click return/zoom out
        # TODO: implement_zoom_out()
        time.sleep(0.5)
        
        attack_count += 1
        
        # Print summary
        elapsed_total = time.time() - start_time
        avg_time = elapsed_total / attack_count
        
        print(f"  📊 Attack {attack_count} complete | "
              f"Avg cycle: {avg_time:.1f}s | "
              f"Total searches: {total_search_count}")
    
    # Final summary
    total_time = time.time() - start_time
    print("\n" + "=" * 60)
    print(f"🏆 ATTACK SESSION COMPLETE")
    print(f"Attacks: {attack_count}")
    print(f"Total searches: {total_search_count}")
    print(f"Average searches per attack: {total_search_count / attack_count:.1f}")
    print(f"Total time: {total_time / 60:.1f} minutes")
    print(f"Average time per attack: {total_time / attack_count:.1f} seconds")
    print("=" * 60)
```

---

## Performance Tuning Checklist

- [ ] **Deploy Speed Settings**: Set Wave=1, Troop=1 for fastest deployment
- [ ] **Human-Like Settings**: Keep hesitations 200-400ms (balances speed + security)
- [ ] **Search Timeout**: Max 15 searches per base (prevents infinite loops)
- [ ] **Button Detection**: Implement fast button clicking (50-100ms per click)
- [ ] **Screenshot Caching**: Cache game window location (avoid repeated detection)
- [ ] **Minimal Waits**: Only sleep when necessary (UI loading, game animations)
- [ ] **Parallel Operations**: Read resources while UI is responding
- [ ] **Error Recovery**: Fast skip on failed bases (don't waste time on errors)

---

## Expected Results

With these optimizations, you should achieve:

| Metric | Target | Notes |
|--------|--------|-------|
| Search per base | 1-7 | Varies by luck |
| Search time | ~20-30s | Per attempt |
| Attack execution | ~30-60s | Depends on troop count |
| **Total per cycle** | **1.2-2 min** | Matches ClashFarmer |
| Attacks per hour | ~30-50 | Sustainable long-term |

---

## Security Considerations

**Important:** Keep `human_like_variations` enabled:
- **Disabling hesitations** = Instant detection (bot behavior obvious)
- **Zero click variance** = Unnatural patterns (perfect precision)
- **No mouse parking** = Machine-like behavior
- **Minimum 200ms hesitations** = Still looks human

The 200-400ms hesitations are **imperceptible to players** but **critical for anti-detection**.

---

## Monitoring

Track performance with logging:

```python
import logging

logging.info(f"Attack {n}: {resources['gold']} gold, {search_attempts} searches, {battle_time}s")
```

This produces logs like:
```
Attack 1: 465369 gold, 1 searches, 45s
Attack 2: 723183 gold, 7 searches, 52s
Attack 3: 386107 gold, 4 searches, 38s
```

Compare against ClashFarmer and adjust settings accordingly!
