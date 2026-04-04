import json
import os
from typing import Any, Dict, Optional

from backend.app.modules.color_book.generator.utils.console_messenger import ConsoleMessenger


class FileUtils:
    """
    Utility functions for file operations.
    """

    @staticmethod
    def read_json(file_path: str) -> Optional[Dict[str, Any]]:
        """
        Reads a JSON file and returns its content.
        """
        if not os.path.exists(file_path):
            ConsoleMessenger.error(f"File not found at path: {file_path}")
            return None
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            ConsoleMessenger.error(f"JSON decoding error in file {file_path}: {e}")
            return None
        except IOError as e:
            ConsoleMessenger.error(f"Error reading file {file_path}: {e}")
            return None

    @staticmethod
    def write_json(file_path: str, data: Dict[str, Any]) -> bool:
        """
        Writes data to a JSON file.
        """
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            return True
        except IOError as e:
            ConsoleMessenger.error(f"Error writing JSON data to file {file_path}: {e}")
            return False