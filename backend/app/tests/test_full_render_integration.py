import pytest
import json
from pathlib import Path
from backend.app.engine.j2v_renderer import J2VMovieRenderer

def test_render_from_json_manifest():
    """Integration test: Load, parse, and render a physical JSON manifest file."""
    manifest_path = Path("backend/app/tests/manifests/demo_001.json")
    assert manifest_path.exists(), f"Manifest {manifest_path} not found"
    
    with open(manifest_path, "r") as f:
        manifest_data = json.load(f)
    
    output_path = Path("/data/ssd/temp/output_demo_001.mp4")
    if output_path.exists():
        output_path.unlink()
        
    # Act: Run renderer
    renderer = J2VMovieRenderer(manifest_data)
    renderer.render_full_movie(str(output_path))
    
    # Assert
    assert output_path.exists()
    assert output_path.stat().st_size > 1000 # Verify it actually wrote data
    print(f"Rendered {output_path} successfully.")
