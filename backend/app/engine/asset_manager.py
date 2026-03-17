import os
import hashlib
from pathlib import Path
from typing import List, Dict, Optional
import shutil

class AssetManager:
    """
    Manages video assets (images, videos, audio) in /data/assets.
    Supports deduplication via MD5 hashing.
    """
    def __init__(self, base_path: str = "/data/assets"):
        self.base_path = Path(base_path)
        self.dirs = {
            "image": self.base_path / "images",
            "video": self.base_path / "videos",
            "audio": self.base_path / "audio",
            "font": self.base_path / "fonts"
        }
        for d in self.dirs.values():
            d.mkdir(parents=True, exist_ok=True)

    def _calculate_hash(self, file_content: bytes) -> str:
        return hashlib.md5(file_content).hexdigest()

    def list_assets(self, asset_type: str) -> List[Dict[str, str]]:
        """Returns a list of assets with their paths and names."""
        target_dir = self.dirs.get(asset_type, self.base_path)
        assets = []
        for f in target_dir.glob("*"):
            if f.is_file():
                assets.append({
                    "name": f.name,
                    "path": str(f).replace("\\", "/"),
                    "rel_path": f"/{f.relative_to(self.base_path.parent)}".replace("\\", "/")
                })
        return assets

    def upload_asset(self, asset_type: str, file_name: str, file_content: bytes) -> str:
        """
        Uploads an asset, checking for duplicates. 
        Returns the final path of the asset.
        """
        target_dir = self.dirs.get(asset_type, self.base_path / "misc")
        target_dir.mkdir(parents=True, exist_ok=True)
        
        file_hash = self._calculate_hash(file_content)
        
        # Check if file with same hash already exists
        for existing in target_dir.glob("*"):
            with open(existing, "rb") as f:
                if self._calculate_hash(f.read()) == file_hash:
                    return f"/{existing.relative_to(self.base_path.parent)}".replace("\\", "/")

        # If not, save it
        final_path = target_dir / file_name
        # Handle filename collisions (different content, same name)
        if final_path.exists():
            final_path = target_dir / f"{file_hash[:8]}_{file_name}"
            
        with open(final_path, "wb") as f:
            f.write(file_content)
            
        return f"/{final_path.relative_to(self.base_path.parent)}".replace("\\", "/")
