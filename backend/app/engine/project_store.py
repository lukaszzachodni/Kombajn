import json
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from .j2v_types import J2VMovie

class ProjectStore:
    """
    Simple file-based store for J2V projects.
    Stored in /app/data/projects as JSON files for Git-friendliness.
    """
    def __init__(self, base_path: str = "/data/projects"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def save_project(self, name: str, manifest: Dict[str, Any]) -> str:
        # Ensure name is filesystem-friendly
        safe_name = "".join([c if c.isalnum() else "_" for c in name])
        file_path = self.base_path / f"{safe_name}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)
        return safe_name

    def list_projects(self) -> List[str]:
        return [f.stem for f in self.base_path.glob("*.json")]

    def load_project(self, name: str) -> Optional[Dict[str, Any]]:
        file_path = self.base_path / f"{name}.json"
        if not file_path.exists():
            return None
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def delete_project(self, name: str):
        file_path = self.base_path / f"{name}.json"
        if file_path.exists():
            file_path.unlink()
