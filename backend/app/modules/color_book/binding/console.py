class ConsoleMessenger:
    # ANSI escape codes for colors
    COLORS = {
        "HEADER": "\033[95m",
        "OKBLUE": "\033[94m",
        "OKCYAN": "\033[96m",
        "OKGREEN": "\033[92m",
        "WARNING": "\033[93m",
        "FAIL": "\033[91m",
        "ENDC": "\033[0m",
        "BOLD": "\033[1m",
        "UNDERLINE": "\033[4m",
    }

    def info(self, message):
        print(f"{self.COLORS['OKBLUE']}{message[:140]}{self.COLORS['ENDC']}")

    def success(self, message):
        print(f"{self.COLORS['OKGREEN']}{message[:140]}{self.COLORS['ENDC']}")

    def warning(self, message):
        print(f"{self.COLORS['WARNING']}{message[:140]}{self.COLORS['ENDC']}")

    def error(self, message):
        print(f"{self.COLORS['FAIL']}{message[:140]}{self.COLORS['ENDC']}")

    def header(self, message):
        print(
            f"{self.COLORS['HEADER']}{self.COLORS['BOLD']}{message[:140]}{self.COLORS['ENDC']}"
        )
