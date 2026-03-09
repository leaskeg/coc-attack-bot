"""
Sound notification utility for important events
"""
import sys
import threading
from typing import Optional

# Try to import winsound (Windows only)
try:
    import winsound
    WINSOUND_AVAILABLE = True
except ImportError:
    WINSOUND_AVAILABLE = False


class SoundNotifier:
    """Play sound notifications for key events (Windows only)"""
    
    # Sound frequencies and durations (frequency_hz, duration_ms)
    SOUNDS = {
        'success': [(800, 100), (1000, 150)],
        'error': [(400, 200), (300, 200)],
        'warning': [(600, 150)],
        'info': [(900, 100)],
        'start': [(600, 80), (800, 80), (1000, 100)],
        'stop': [(1000, 80), (800, 80), (600, 100)],
        'notification': [(1200, 100), (1000, 100)],
        'alarm': [(1500, 200), (1000, 200), (1500, 200)]
    }
    
    def __init__(self, enabled: bool = True):
        self.enabled = enabled and WINSOUND_AVAILABLE
        
        if not WINSOUND_AVAILABLE and enabled:
            print("⚠️  Sound notifications not available (winsound not found)")
    
    def is_available(self) -> bool:
        """Check if sound is available"""
        return WINSOUND_AVAILABLE
    
    def play(self, sound_type: str = 'info', blocking: bool = False) -> None:
        """Play a sound notification"""
        if not self.enabled or not WINSOUND_AVAILABLE:
            return
        
        sound_pattern = self.SOUNDS.get(sound_type, self.SOUNDS['info'])
        
        if blocking:
            self._play_pattern(sound_pattern)
        else:
            thread = threading.Thread(target=self._play_pattern, args=(sound_pattern,), daemon=True)
            thread.start()
    
    def _play_pattern(self, pattern: list) -> None:
        """Play a sound pattern"""
        try:
            for frequency, duration in pattern:
                winsound.Beep(frequency, duration)
        except Exception as e:
            pass
    
    def play_success(self) -> None:
        """Play success sound"""
        self.play('success')
    
    def play_error(self) -> None:
        """Play error sound"""
        self.play('error')
    
    def play_warning(self) -> None:
        """Play warning sound"""
        self.play('warning')
    
    def play_notification(self) -> None:
        """Play notification sound"""
        self.play('notification')
    
    def play_alarm(self) -> None:
        """Play alarm sound"""
        self.play('alarm', blocking=True)
    
    def play_start(self) -> None:
        """Play start sound"""
        self.play('start')
    
    def play_stop(self) -> None:
        """Play stop sound"""
        self.play('stop')
    
    def enable(self) -> None:
        """Enable sound notifications"""
        if WINSOUND_AVAILABLE:
            self.enabled = True
    
    def disable(self) -> None:
        """Disable sound notifications"""
        self.enabled = False
    
    def toggle(self) -> bool:
        """Toggle sound notifications"""
        self.enabled = not self.enabled
        return self.enabled
    
    def play_custom(self, frequency: int, duration: int) -> None:
        """Play custom frequency beep"""
        if not self.enabled or not WINSOUND_AVAILABLE:
            return
        
        try:
            winsound.Beep(frequency, duration)
        except Exception:
            pass
    
    @staticmethod
    def play_system_sound(sound: str) -> None:
        """Play Windows system sound"""
        if not WINSOUND_AVAILABLE:
            return
        
        sound_map = {
            'asterisk': winsound.MB_ICONASTERISK,
            'exclamation': winsound.MB_ICONEXCLAMATION,
            'hand': winsound.MB_ICONHAND,
            'question': winsound.MB_ICONQUESTION,
            'ok': winsound.MB_OK
        }
        
        try:
            winsound.MessageBeep(sound_map.get(sound, winsound.MB_OK))
        except Exception:
            pass
