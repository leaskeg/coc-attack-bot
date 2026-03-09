"""
Colored console output utility for enhanced user experience
"""
import sys
from typing import Optional

try:
    from colorama import Fore, Back, Style, init
    init(autoreset=True)
    COLORAMA_AVAILABLE = True
except ImportError:
    COLORAMA_AVAILABLE = False
    class Fore:
        RED = GREEN = YELLOW = BLUE = MAGENTA = CYAN = WHITE = RESET = ""
    class Back:
        RED = GREEN = YELLOW = BLUE = MAGENTA = CYAN = WHITE = RESET = ""
    class Style:
        BRIGHT = DIM = NORMAL = RESET_ALL = ""


class ColoredOutput:
    """Colored console output with fallback for missing colorama"""
    
    @staticmethod
    def is_available() -> bool:
        """Check if colorama is available"""
        return COLORAMA_AVAILABLE
    
    @staticmethod
    def success(message: str, prefix: str = "✅") -> None:
        """Print success message in green"""
        print(f"{Fore.GREEN}{prefix} {message}{Style.RESET_ALL}")
    
    @staticmethod
    def error(message: str, prefix: str = "❌") -> None:
        """Print error message in red"""
        print(f"{Fore.RED}{prefix} {message}{Style.RESET_ALL}")
    
    @staticmethod
    def warning(message: str, prefix: str = "⚠️") -> None:
        """Print warning message in yellow"""
        print(f"{Fore.YELLOW}{prefix} {message}{Style.RESET_ALL}")
    
    @staticmethod
    def info(message: str, prefix: str = "ℹ️") -> None:
        """Print info message in cyan"""
        print(f"{Fore.CYAN}{prefix} {message}{Style.RESET_ALL}")
    
    @staticmethod
    def debug(message: str, prefix: str = "🔍") -> None:
        """Print debug message in magenta"""
        print(f"{Fore.MAGENTA}{prefix} {message}{Style.RESET_ALL}")
    
    @staticmethod
    def highlight(message: str, color: str = "GREEN") -> None:
        """Print highlighted message"""
        color_code = getattr(Fore, color.upper(), Fore.WHITE)
        print(f"{Style.BRIGHT}{color_code}{message}{Style.RESET_ALL}")
    
    @staticmethod
    def header(message: str, width: int = 60, char: str = "=") -> None:
        """Print formatted header"""
        print(f"\n{Fore.CYAN}{Style.BRIGHT}{char * width}")
        print(f"{message.center(width)}")
        print(f"{char * width}{Style.RESET_ALL}\n")
    
    @staticmethod
    def status(message: str, status: str = "OK", status_color: str = "GREEN") -> None:
        """Print message with status indicator"""
        color_code = getattr(Fore, status_color.upper(), Fore.WHITE)
        print(f"{message} ... {color_code}[{status}]{Style.RESET_ALL}")
    
    @staticmethod
    def progress_bar(current: int, total: int, width: int = 40, 
                     prefix: str = "", suffix: str = "") -> None:
        """Print progress bar"""
        if total == 0:
            return
        
        percent = current / total
        filled = int(width * percent)
        bar = "█" * filled + "░" * (width - filled)
        percent_str = f"{percent * 100:.1f}%"
        
        # Color based on progress
        if percent < 0.33:
            color = Fore.RED
        elif percent < 0.66:
            color = Fore.YELLOW
        else:
            color = Fore.GREEN
        
        print(f"\r{prefix}[{color}{bar}{Style.RESET_ALL}] {percent_str} {suffix}", end="", flush=True)
    
    @staticmethod
    def table_row(columns: list, widths: list, colors: Optional[list] = None) -> None:
        """Print formatted table row"""
        if colors is None:
            colors = [Fore.WHITE] * len(columns)
        
        row = ""
        for col, width, color in zip(columns, widths, colors):
            row += f"{color}{str(col):<{width}}{Style.RESET_ALL} "
        print(row)
    
    @staticmethod
    def box(message: str, width: int = 60, style: str = "single") -> None:
        """Print message in a box"""
        if style == "double":
            top = "╔" + "═" * (width - 2) + "╗"
            bottom = "╚" + "═" * (width - 2) + "╝"
            side = "║"
        else:
            top = "┌" + "─" * (width - 2) + "┐"
            bottom = "└" + "─" * (width - 2) + "┘"
            side = "│"
        
        print(f"{Fore.CYAN}{top}")
        
        lines = message.split("\n")
        for line in lines:
            padding = width - len(line) - 4
            print(f"{side} {line}{' ' * padding} {side}")
        
        print(f"{bottom}{Style.RESET_ALL}")
    
    @staticmethod
    def menu_option(number: str, text: str, enabled: bool = True) -> None:
        """Print colored menu option"""
        if enabled:
            print(f"{Fore.CYAN}{number}.{Style.RESET_ALL} {text}")
        else:
            print(f"{Fore.BLACK}{Style.DIM}{number}. {text} (disabled){Style.RESET_ALL}")


# Convenience aliases
cprint = ColoredOutput
