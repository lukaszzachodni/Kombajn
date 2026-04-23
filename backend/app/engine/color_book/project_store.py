import json
import os
from pathlib import Path
from typing import List, Dict, Any, Optional

class ColorBookProjectStore:
    """
    Zarządza projektami kolorowanek na dysku. 
    Struktura: /data/projects/{project_id}/project_data.json + obrazy.
    """
    def __init__(self, base_path: str = "/data/projects"):
        self.base_path = Path(base_path)

    def list_projects(self) -> List[str]:
        """Zwraca listę identyfikatorów projektów (folderów zawierających project_data.json)."""
        projects = []
        if not self.base_path.exists():
            return []
            
        for d in self.base_path.iterdir():
            if d.is_dir() and (d / "project_data.json").exists():
                projects.append(d.name)
        return sorted(projects, reverse=True)

    def get_project_data(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Ładuje główny plik JSON projektu."""
        data_path = self.base_path / project_id / "project_data.json"
        if not data_path.exists():
            return None
        with open(data_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def list_project_files(self, project_id: str) -> List[Dict[str, str]]:
        """Zwraca listę plików w folderze projektu (obrazy, PDF)."""
        proj_path = self.base_path / project_id
        if not proj_path.exists():
            return []
            
        files = []
        for f in proj_path.iterdir():
            if f.is_file() and f.suffix.lower() in ['.png', '.jpg', '.pdf', '.xlsx']:
                files.append({
                    "name": f.name,
                    "type": f.suffix[1:].lower(),
                    "path": str(f)
                })
        return sorted(files, key=lambda x: x['name'])
