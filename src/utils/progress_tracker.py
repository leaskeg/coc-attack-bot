"""
Progress tracking utilities for long-running operations
"""
import time
import threading
from typing import Optional, Callable
from .colored_output import ColoredOutput, Fore, Style

try:
    from tqdm import tqdm
    TQDM_AVAILABLE = True
except ImportError:
    TQDM_AVAILABLE = False


class ProgressTracker:
    """Track progress of long-running operations"""
    
    def __init__(self, total: int, description: str = "", unit: str = "it"):
        self.total = total
        self.current = 0
        self.description = description
        self.unit = unit
        self.start_time = time.time()
        self.use_tqdm = TQDM_AVAILABLE
        
        if self.use_tqdm:
            self.pbar = tqdm(total=total, desc=description, unit=unit, 
                           bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]')
        else:
            self.pbar = None
            print(f"\n{description}")
    
    def update(self, n: int = 1) -> None:
        """Update progress by n steps"""
        self.current += n
        
        if self.use_tqdm and self.pbar:
            self.pbar.update(n)
        else:
            ColoredOutput.progress_bar(
                self.current, 
                self.total, 
                prefix=f"{self.description}: ",
                suffix=f"({self.current}/{self.total})"
            )
    
    def set_description(self, desc: str) -> None:
        """Update description"""
        self.description = desc
        if self.use_tqdm and self.pbar:
            self.pbar.set_description(desc)
    
    def close(self) -> None:
        """Close progress bar"""
        if self.use_tqdm and self.pbar:
            self.pbar.close()
        else:
            print()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class CountdownTimer:
    """Display countdown timer for battles/waits"""
    
    def __init__(self, duration: float, description: str = "Waiting"):
        self.duration = duration
        self.description = description
        self.cancelled = False
        self.thread = None
    
    def start(self, callback: Optional[Callable] = None) -> None:
        """Start countdown timer"""
        def _countdown():
            start = time.time()
            while not self.cancelled:
                elapsed = time.time() - start
                remaining = max(0, self.duration - elapsed)
                
                if remaining <= 0:
                    break
                
                mins = int(remaining // 60)
                secs = int(remaining % 60)
                
                bar_percent = elapsed / self.duration
                bar_width = 40
                filled = int(bar_width * bar_percent)
                bar = "█" * filled + "░" * (bar_width - filled)
                
                # Color based on time remaining
                if remaining > self.duration * 0.66:
                    color = Fore.GREEN
                elif remaining > self.duration * 0.33:
                    color = Fore.YELLOW
                else:
                    color = Fore.RED
                
                print(f"\r{self.description}: [{color}{bar}{Style.RESET_ALL}] "
                      f"{mins:02d}:{secs:02d} remaining", end="", flush=True)
                
                time.sleep(0.5)
            
            print()
            if callback and not self.cancelled:
                callback()
        
        self.thread = threading.Thread(target=_countdown, daemon=True)
        self.thread.start()
    
    def cancel(self) -> None:
        """Cancel countdown"""
        self.cancelled = True
        if self.thread:
            self.thread.join(timeout=2)
    
    def wait(self) -> None:
        """Wait for countdown to finish"""
        if self.thread:
            self.thread.join()


class SpinnerDisplay:
    """Display animated spinner for indeterminate operations"""
    
    SPINNERS = {
        'dots': ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'],
        'line': ['-', '\\', '|', '/'],
        'arrow': ['←', '↖', '↑', '↗', '→', '↘', '↓', '↙'],
        'circle': ['◐', '◓', '◑', '◒'],
        'squares': ['◰', '◳', '◲', '◱']
    }
    
    def __init__(self, message: str = "Loading", style: str = 'dots'):
        self.message = message
        self.style = style
        self.frames = self.SPINNERS.get(style, self.SPINNERS['dots'])
        self.running = False
        self.thread = None
    
    def start(self) -> None:
        """Start spinner animation"""
        self.running = True
        
        def _spin():
            idx = 0
            while self.running:
                frame = self.frames[idx % len(self.frames)]
                print(f"\r{Fore.CYAN}{frame}{Style.RESET_ALL} {self.message}...", 
                      end="", flush=True)
                idx += 1
                time.sleep(0.1)
            print("\r" + " " * (len(self.message) + 10) + "\r", end="", flush=True)
        
        self.thread = threading.Thread(target=_spin, daemon=True)
        self.thread.start()
    
    def stop(self, final_message: Optional[str] = None) -> None:
        """Stop spinner"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=1)
        
        if final_message:
            ColoredOutput.success(final_message)
    
    def __enter__(self):
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self.stop("Done")
        else:
            self.stop()


class MultiProgress:
    """Track multiple progress bars simultaneously"""
    
    def __init__(self):
        self.trackers = {}
        self.lock = threading.Lock()
    
    def add_tracker(self, name: str, total: int, description: str = "") -> None:
        """Add a progress tracker"""
        with self.lock:
            self.trackers[name] = {
                'total': total,
                'current': 0,
                'description': description or name
            }
    
    def update(self, name: str, n: int = 1) -> None:
        """Update specific tracker"""
        with self.lock:
            if name in self.trackers:
                self.trackers[name]['current'] += n
                self._display()
    
    def _display(self) -> None:
        """Display all trackers"""
        print("\r", end="")
        for name, data in self.trackers.items():
            percent = (data['current'] / data['total'] * 100) if data['total'] > 0 else 0
            print(f"{data['description']}: {percent:.0f}% ", end="")
        print("", flush=True)
    
    def remove_tracker(self, name: str) -> None:
        """Remove tracker"""
        with self.lock:
            if name in self.trackers:
                del self.trackers[name]
