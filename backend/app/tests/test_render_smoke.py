import pytest
from backend.app.engine.j2v_renderer import J2VMovieRenderer
from pathlib import Path
import shutil

from datetime import datetime

def test_minimal_render():
    # Arrange: 10s manifest (two 5s scenes)
    now = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    manifest = {
        "width": 1920,
        "height": 1080,
        "fps": 24,
        "scenes": [
            {
                "background-color": "#FF5733",
                "duration": 5.0,
                "elements": [
                    {"type": "text", "text": f"SCENE 1 - {now}", "settings": {"font-size": 80, "font-color": "white"}}
                ]
            },
            {
                "background-color": "#33FF57",
                "duration": 5.0,
                "elements": [
                    {"type": "text", "text": f"SCENE 2 - {now}", "settings": {"font-size": 80, "font-color": "white"}}
                ]
            }
        ]
    }
    
    output_path = Path("/data/ssd/temp/test_output.mp4")
    if output_path.exists():
        output_path.unlink()
        
    # Act
    renderer = J2VMovieRenderer(manifest)
    renderer.render_full_movie(str(output_path))
    
    # Assert
    assert output_path.exists()
    assert output_path.stat().st_size > 0
    
    print("Render successful.")

if __name__ == "__main__":
    test_minimal_render()
