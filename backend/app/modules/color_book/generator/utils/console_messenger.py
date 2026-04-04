class ConsoleMessenger:
    """
    Manages console message display with optional coloring.
    """

    _COLORS = {
        "RESET": "\u001b[0m",
        "BLACK": "\u001b[30m",
        "RED": "\u001b[31m",
        "GREEN": "\u001b[32m",
        "YELLOW": "\u001b[33m",
        "BLUE": "\u001b[34m",
        "MAGENTA": "\u001b[35m",
        "CYAN": "\u001b[36m",
        "WHITE": "\u001b[37m",
        "BRIGHT_BLACK": "\u001b[90m",
        "BRIGHT_RED": "\u001b[91m",
        "BRIGHT_GREEN": "\u001b[92m",
        "BRIGHT_YELLOW": "\u001b[93m",
        "BRIGHT_BLUE": "\u001b[94m",
        "BRIGHT_MAGENTA": "\u001b[95m",
        "BRIGHT_CYAN": "\u001b[96m",
        "BRIGHT_WHITE": "\u001b[97m",
    }

    @staticmethod
    def _colorize_message(message: str, color: str | None = None) -> str:
        """Adds ANSI color codes to the message."""
        if color and color.upper() in ConsoleMessenger._COLORS:
            return f"{ConsoleMessenger._COLORS[color.upper()]}{message[:140]}{ConsoleMessenger._COLORS['RESET']}"
        return message

    @staticmethod
    def info(message: str, color: str | None = None) -> None:
        """Displays an informational message."""
        print(ConsoleMessenger._colorize_message(message, color))

    @staticmethod
    def section_header(message: str, color: str = "CYAN") -> None:
        """Displays a section header."""
        print(ConsoleMessenger._colorize_message(f"\n--- {message[:140]} ---", color))

    @staticmethod
    def success(message: str, color: str = "GREEN") -> None:
        """Displays a success message."""
        print(ConsoleMessenger._colorize_message(message, color))

    @staticmethod
    def warning(message: str, color: str = "YELLOW") -> None:
        """Displays a warning message."""
        print(ConsoleMessenger._colorize_message(f"Warning: {message[:140]}", color))

    @staticmethod
    def error(message: str, color: str = "RED") -> None:
        """Displays an error message."""
        print(ConsoleMessenger._colorize_message(f"Error: {message[:140]}", color))

    @staticmethod
    def debug(message: str, color: str = "BRIGHT_BLACK") -> None:
        """Displays a debug message."""
        print(ConsoleMessenger._colorize_message(f"Debug: {message[:140]}", color))
