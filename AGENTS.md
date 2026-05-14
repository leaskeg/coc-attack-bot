# Repository Guidelines

## Project Overview

COC Attack Bot is a Python 3 desktop automation framework for Clash of Clans that automates attack execution. It features GUI and console interfaces, attack recording/playback, automated attack orchestration with configurable strategies, Google Gemini AI integration, and real-time statistics tracking.

## Project Structure & Module Organization

- **src/core/** - Core automation: `screen_capture.py` handles game window detection and screenshots; `coordinate_mapper.py` maps UI elements across different screen sizes; `attack_recorder.py` captures click sequences; `attack_player.py` replays recorded attacks; `auto_attacker.py` orchestrates automated attack sessions with configurable groups/variations; `ai_analyzer.py` integrates Google Gemini API for attack analysis.
- **src/ui/** - User interfaces: `gui.py` (primary interactive interface), `console_ui.py` (legacy terminal mode).
- **src/utils/** - Helpers: logging, config validation, timing utilities (human-like delays/hesitations), progress tracking, sound notifications, colored console output.
- **main.py** - Entry point supporting three modes: GUI (default), console (`--console`), or headless auto-attack (`--auto-attack`).

## Build, Test, and Development Commands

Install dependencies:
```
pip install -r requirements.txt
```

Run the application:
- **GUI mode** (default): `python main.py`
- **Console mode**: `python main.py --console`
- **Headless auto-attack**: `python main.py --auto-attack`
- **Specific attack group**: `python main.py --auto-attack -g group_name`
- **Custom config**: `python main.py --config path/to/config.py`

Emergency stop during execution: **Ctrl+Alt+S**

## Coding Style & Naming Conventions

- **Type hints**: Comprehensive use of `typing` module (Dict, List, Optional, Tuple, etc.) throughout all modules.
- **Naming**: descriptive method names in snake_case; classes in PascalCase.
- **Logging**: All major operations use the custom `Logger` class (not print statements).
- **Configuration**: Behavior driven by `Config` object with `.get('key', default)` pattern; config validation via `ConfigValidator`.
- **Threading**: Background tasks (stats display, auto-attack loop) use `threading.Thread` with state synchronization via locks.
- **Docstrings**: Methods include docstrings describing purpose and return types.

## Core Dependencies

- **Automation**: `pyautogui`, `keyboard`, `pywin32` - OS-level mouse/keyboard control and window management.
- **Image Processing**: `opencv-python`, `Pillow`, `numpy` - screenshot analysis and template matching.
- **API/Utilities**: `requests` (HTTP), `colorama` (terminal colors), `tqdm` (progress bars).

## Note on Configuration Files

- `src/utils/config.py` (Python config handler) and `config.json` (user configuration) are not tracked in git (listed in .gitignore) and must be provided at runtime.
- `Config` class is expected in `src/utils/config.py` and accessed via `config.get('key', default)` throughout the codebase.
