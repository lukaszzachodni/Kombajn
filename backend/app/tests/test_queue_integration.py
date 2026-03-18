import pytest
import json
from pathlib import Path
from backend.app.engine.j2v_types import J2VMovie

def test_manifest_deserialization():
    """Verify that manifests from the shared folder are correctly parsed into Pydantic models."""
    manifest_path = Path("backend/app/tests/manifests/test_demo.json")
    
    # Check if manifest exists, if not, create one based on current demo
    if not manifest_path.exists():
        data = {
            "width": 1920, "height": 1080, "fps": 24,
            "scenes": [{"background-color": "#000000", "duration": 1.0}]
        }
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        with open(manifest_path, "w") as f:
            json.dump(data, f)
            
    with open(manifest_path, "r") as f:
        manifest_dict = json.load(f)
        
    # Verify Pydantic model can handle it
    movie = J2VMovie(**manifest_dict)
    assert movie.width == 1920
    assert len(movie.scenes) == 1
    
    print("Manifest deserialization verified.")
