import os
from pathlib import Path
import pytest
from backend.app.engine.renderer import SceneRenderer
from backend.app.schemas import Scene, ColorBackground, TextElement
from backend.app.tasks import assemble_video

# Config for tests
PROJECT_ID = "tdd_test_project"
WIDTH = 640
HEIGHT = 480
FPS = 24

@pytest.fixture
def clean_tmp():
    """Ensure temp directories are clean before/after tests."""
    paths = [
        Path("/data/ssd/temp") / PROJECT_ID,
        Path("/data/ssd/renders") / PROJECT_ID
    ]
    for p in paths:
        if p.exists():
            import shutil
            shutil.rmtree(p)
    yield
    # Optional cleanup after tests
    # for p in paths:
    #     if p.exists():
    #         import shutil
    #         shutil.rmtree(p)

def test_render_single_scene(clean_tmp):
    """
    Test rendering a single 1s scene with text.
    Validates: ProcessorFactory, ColorProcessor, TextProcessor, SceneRenderer.
    """
    scene = Scene(
        background=ColorBackground(type="color", color="red", duration=1.0),
        elements=[
            TextElement(type="text", text="TDD TEST", fontsize=50, color="white", position="center")
        ]
    )
    
    renderer = SceneRenderer(PROJECT_ID, WIDTH, HEIGHT, FPS)
    path = renderer.render(scene, index=0)
    
    assert Path(path).exists()
    assert Path(path).stat().st_size > 0
    assert path.endswith(".mp4")

def test_assemble_two_scenes(clean_tmp):
    """
    Test rendering two scenes and assembling them.
    Validates: Full flow from atoms to final assembly.
    """
    renderer = SceneRenderer(PROJECT_ID, WIDTH, HEIGHT, FPS)
    
    # Scene 1
    s1 = Scene(
        background=ColorBackground(type="color", color="blue", duration=1.0),
        elements=[TextElement(text="SCENE 1")]
    )
    p1 = renderer.render(s1, index=0)
    
    # Scene 2
    s2 = Scene(
        background=ColorBackground(type="color", color="green", duration=1.0),
        elements=[TextElement(text="SCENE 2")]
    )
    p2 = renderer.render(s2, index=1)
    
    # Assembly (using the task logic directly)
    scene_results = [
        {"path": p1, "dry_run": False},
        {"path": p2, "dry_run": False}
    ]
    
    # Mocking celery task call by calling the function directly
    # In real life we'd use .apply() or just test the logic
    result = assemble_video.run(scene_results, PROJECT_ID, FPS)
    
    final_path = result["final_path"]
    assert Path(final_path).exists()
    assert Path(final_path).stat().st_size > 0
    assert result["status"] == "completed"
