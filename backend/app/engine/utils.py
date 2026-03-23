import json
import hashlib
from typing import Dict, Any

def get_scene_hash(scene_dict: Dict[str, Any]) -> str:
    """
    Tworzy jednoznaczny hash dla danej konfiguracji sceny (zwalidowany manifest).
    Sortowanie kluczy zapewnia stałość hasha dla tych samych danych.
    """
    serialized = json.dumps(scene_dict, sort_keys=True).encode("utf-8")
    return hashlib.sha256(serialized).hexdigest()

# Przykładowe użycie w rendererze (pseudo-kod):
# scene_hash = get_scene_hash(s_dict)
# cache_path = Path("/data/ssd/cache") / f"{scene_hash}.mp4"
# if cache_path.exists():
#     return str(cache_path)
