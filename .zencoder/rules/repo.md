---
description: Repository Information Overview
alwaysApply: true
---

# COC Attack Bot Information

## Summary
A Windows automation bot for Clash of Clans that automates attack sessions with AI-powered base analysis. Enables coordinate mapping, attack recording, automated playback, and intelligent base loot evaluation using Google Gemini API. Designed for educational purposes with full keyboard automation and image processing capabilities.

## Structure
**Root directories:**
- `src/` - Main application source code
- `core/` - Core automation modules (screen capture, recording, playback, coordinate mapping, AI analysis)
- `ui/` - Console-based user interface
- `utils/` - Configuration and logging utilities
- `coordinates/` - Saved button coordinate mappings by screen resolution
- `recordings/` - Recorded attack session files
- `screenshots/` - Captured game window screenshots
- `templates/` - Image templates for future feature expansion
- `logs/` - Application log files

## Language & Runtime
**Language**: Python  
**Version**: 3.8 or later  
**Build System**: pip (no build compilation needed)  
**Package Manager**: pip  
**Platform**: Windows 10+ only  

## Dependencies
**Main Dependencies**:
- `pyautogui>=0.9.54` - Mouse and keyboard automation
- `keyboard>=0.13.0` - Hotkey detection and keyboard control
- `pywin32>=306` - Windows API access for window detection
- `opencv-python>=4.8.0` - Image processing and template matching
- `Pillow>=9.5.0` - Image handling and manipulation
- `numpy>=1.24.0` - Numerical operations and array handling
- `requests>=2.31.0` - HTTP requests (Google Gemini API integration)

## Build & Installation
```bash
# Install dependencies
pip install -r requirements.txt

# Copy and configure the configuration file
copy src\utils\example.config.py src\utils\config.py

# Run the bot
python main.py
```

**Alternative (Windows batch launcher)**:
```bash
run_bot.bat
```

## Configuration
**File**: `src/utils/config.py` (JSON-based)

**Key Sections**:
- `bot` - Bot metadata (name, version, author)
- `automation` - Click delays, playback speed, recording duration limits
- `display` - UI logging levels and progress display options
- `directories` - Paths for screenshots, recordings, coordinates, templates, logs
- `hotkeys` - F-key bindings for coordinate mapping, recording, and playback
- `game` - Window detection settings, template matching thresholds (supports Clash of Clans, BlueStacks, NoxPlayer, LDPlayer, MEmu)
- `ai_analyzer` - Google Gemini API key, minimum loot thresholds for auto-attack

## Main Entry Points
**Primary**: `main.py` - Starts the ConsoleUI application
**Example Usage**: `example_usage.py` - Demonstrates programmatic API usage
**Windows Batch Launcher**: `run_bot.bat` - Dependency checker and application launcher

## Testing
**Framework**: Manual test script (not automated test framework)
**Test File**: `test_attack_variations.py` - Tests attack variation management, selection distribution, and statistics

**Run Test**:
```bash
python test_attack_variations.py
```

**Test Coverage**:
- Attack group creation and management
- Random variation selection and distribution
- Variation removal and cleanup
- Statistics generation

## Core Modules
**`src/core/`**:
- `screen_capture.py` - Game window detection and screenshot capture
- `coordinate_mapper.py` - Button position recording and coordinate storage
- `attack_recorder.py` - Attack session recording with click and timing data
- `attack_player.py` - Recorded attack playback with variable speed control
- `auto_attacker.py` - Automated attack loop with variation management
- `ai_analyzer.py` - Google Gemini integration for base loot analysis

**`src/ui/`**:
- `console_ui.py` - Interactive console menu system

**`src/utils/`**:
- `config.py` - JSON configuration management with dot-notation access
- `logger.py` - Logging utility for application events

## Key Features
- **Coordinate Mapping** - Map button positions per screen resolution (F1-F3 hotkeys)
- **Attack Recording** - Record sequences of clicks and delays (F5-F7 hotkeys)
- **Attack Playback** - Replay recorded attacks with speed control (F8-F9 hotkeys)
- **Auto Attacker** - Automated search and attack loop with variation rotation
- **AI Analysis** - Google Gemini-powered loot evaluation for base filtering
- **Screenshot Capture** - Game window detection and screenshot management
- **Hotkey Controls** - Configurable F-key bindings for all operations

## Configuration Requirements
- **Clash of Clans** must run in **FULL SCREEN MODE** for accurate coordinate mapping
- Google Gemini API key (optional, for AI base analysis)
- Stable internet connection (for AI features)
