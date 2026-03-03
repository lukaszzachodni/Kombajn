from pathlib import Path
from typing import Any

import fsspec

from .config import settings


class StorageManager:
    def __init__(self) -> None:
        self._paths = settings.storage

    def _resolve(self, area: str, *parts: str) -> str:
        base_map = {
            "ssd": self._paths.ssd_root,
            "usb": self._paths.usb_root,
            "hdd": self._paths.hdd_root,
        }
        if area not in base_map:
            raise ValueError(f"Unknown storage area: {area}")
        base = Path(base_map[area])
        return str(base.joinpath(*parts))

    def write_text(self, area: str, *parts: str, content: str) -> None:
        path = self._resolve(area, *parts)
        fs, _, paths = fsspec.get_fs_token_paths(path)
        fs.makedirs(str(Path(paths[0]).parent), exist_ok=True)
        with fs.open(path, "w", encoding="utf-8") as f:
            f.write(content)

    def read_text(self, area: str, *parts: str) -> str:
        path = self._resolve(area, *parts)
        fs, _, _ = fsspec.get_fs_token_paths(path)
        with fs.open(path, "r", encoding="utf-8") as f:
            return f.read()

    def write_json(self, area: str, *parts: str, data: Any) -> None:
        import json

        self.write_text(area, *parts, content=json.dumps(data, indent=2, ensure_ascii=False))
