import keyboard
import threading
import time
from typing import Optional, Callable, List
from ..utils.logger import Logger


class EmergencyStopHandler:
    
    def __init__(self, logger: Optional[Logger] = None):
        self.logger = logger or Logger()
        self.stop_callbacks: List[Callable] = []
        self.is_active = False
        self.monitor_thread = None
        self.stop_triggered = False
        self.hotkey = 'ctrl+alt+s'
    
    def register_callback(self, callback: Callable) -> None:
        
        if callback not in self.stop_callbacks:
            self.stop_callbacks.append(callback)
            self.logger.debug(f"Registered emergency stop callback: {callback.__name__}")
    
    def unregister_callback(self, callback: Callable) -> None:
        
        if callback in self.stop_callbacks:
            self.stop_callbacks.remove(callback)
            self.logger.debug(f"Unregistered emergency stop callback: {callback.__name__}")
    
    def start_monitoring(self) -> None:
        
        if self.is_active:
            self.logger.warning("Emergency stop handler already active")
            return
        
        self.is_active = True
        self.stop_triggered = False
        self.monitor_thread = threading.Thread(target=self._monitor_hotkey, daemon=True)
        self.monitor_thread.start()
        
        self.logger.info(f"Emergency stop monitoring started (hotkey: {self.hotkey})")
    
    def stop_monitoring(self) -> None:
        
        if not self.is_active:
            return
        
        self.is_active = False
        
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2)
        
        self.logger.info("Emergency stop monitoring stopped")
    
    def is_stopped(self) -> bool:
        
        return self.stop_triggered
    
    def trigger_stop(self) -> None:
        
        if self.stop_triggered:
            return
        
        self.stop_triggered = True
        self.logger.critical("EMERGENCY STOP TRIGGERED!")
        
        for callback in self.stop_callbacks:
            try:
                self.logger.info(f"Executing stop callback: {callback.__name__}")
                callback()
            except Exception as e:
                self.logger.error(f"Error in stop callback {callback.__name__}: {e}")
    
    def reset(self) -> None:
        
        self.stop_triggered = False
        self.logger.debug("Emergency stop flag reset")
    
    def _monitor_hotkey(self) -> None:
        
        try:
            keyboard.add_hotkey(self.hotkey, self._on_hotkey_pressed)
            
            while self.is_active:
                time.sleep(0.1)
            
            keyboard.remove_hotkey(self.hotkey)
        
        except Exception as e:
            self.logger.error(f"Hotkey monitoring error: {e}")
            self.is_active = False
    
    def _on_hotkey_pressed(self) -> None:
        
        self.logger.warning(f"Emergency stop hotkey pressed: {self.hotkey}")
        self.trigger_stop()


emergency_stop_handler = None


def get_emergency_stop_handler(logger: Optional[Logger] = None) -> EmergencyStopHandler:
    
    global emergency_stop_handler
    if emergency_stop_handler is None:
        emergency_stop_handler = EmergencyStopHandler(logger=logger)
    return emergency_stop_handler
