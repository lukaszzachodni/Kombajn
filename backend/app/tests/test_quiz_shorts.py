import os
from pathlib import Path
import pytest
import numpy as np
from PIL import Image
from moviepy.editor import VideoFileClip, AudioFileClip

from backend.app.engine.renderer import SceneRenderer
from backend.app.schemas import Scene, ImageBackground, TextElement, VideoEditManifest

# --- TEST ASSET GENERATION ---

@pytest.fixture(scope="session")
def dummy_assets(tmp_path_factory):
    """Generates dummy assets for integration testing."""
    assets_dir = tmp_path_factory.mktemp("assets")
    
    # 1. Generate 1080x1920 Background Image
    bg_path = assets_dir / "background.jpg"
    img = Image.new('RGB', (1080, 1920), color=(30, 30, 30))
    img.save(bg_path)
    
    # 2. Generate 10s Silent Audio (using ffmpeg via command line for simplicity)
    audio_path = assets_dir / "audio.mp3"
    os.system(f"ffmpeg -f lavfi -i anullsrc=r=44100:cl=stereo -t 10 -q:a 9 -acodec libmp3lame {audio_path} -y")
    
    return {
        "background": str(bg_path),
        "audio": str(audio_path)
    }

# --- INTEGRATION TEST ---

def test_quiz_shorts_assembly_process(dummy_assets, tmp_path):
    """
    Integration test for the 'Quiz Shorts' assembly process.
    Validates file creation, resolution, duration, and audio presence.
    """
    # 1. Setup Manifest
    project_id = "quiz_shorts_test"
    output_dir = Path("/data/ssd/renders") / project_id
    output_dir.mkdir(parents=True, exist_ok=True)
    
    manifest = VideoEditManifest(
        project_id=project_id,
        width=1080,
        height=1920,
        fps=24,
        scenes=[
            Scene(
                background=ImageBackground(path=dummy_assets["background"], duration=10.0),
                elements=[
                    # Question: 0s - 10s
                    TextElement(
                        text="What is the capital of France?",
                        fontsize=80,
                        position="center",
                        start_time=0.0,
                        duration=10.0
                    ),
                    # Answer: 7s - 10s
                    TextElement(
                        text="PARIS",
                        fontsize=120,
                        color="yellow",
                        position=("center", 1400), # Using tuple for center-bottom logic
                        start_time=7.0,
                        duration=3.0
                    )
                ]
            )
        ]
    )

    # 2. Execute Rendering
    # Note: We are using the SceneRenderer for the visual part.
    # In a real scenario, we might have a ProjectAssembler that also handles audio.
    renderer = SceneRenderer(project_id, manifest.width, manifest.height, manifest.fps)
    scene_path = renderer.render(manifest.scenes[0], index=0)
    
    # Adding Audio (as requested in the test scenario)
    final_output_path = str(output_dir / "final_quiz.mp4")
    video_clip = VideoFileClip(scene_path)
    audio_clip = AudioFileClip(dummy_assets["audio"])
    
    final_video = video_clip.set_audio(audio_clip)
    final_video.write_videofile(final_output_path, codec="libx264", audio_codec="aac")
    
    # 3. Assertions
    
    # Check if file exists and has correct extension
    assert os.path.exists(final_output_path)
    assert final_output_path.endswith(".mp4")
    
    # Check resolution
    with VideoFileClip(final_output_path) as clip:
        assert clip.size == [1080, 1920]
        
        # Check duration (with 0.1s tolerance)
        assert abs(clip.duration - 10.0) <= 0.1
        
        # Check if audio track is present
        assert clip.audio is not None
        assert clip.audio.duration > 0

    # Cleanup
    video_clip.close()
    audio_clip.close()
