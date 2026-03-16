import os
import json
from backend.app.engine.j2v_renderer import J2VMovieRenderer

def run_local_j2v_test():
    manifest = {
        "resolution": "shorts",
        "fps": 24,
        "scenes": [
            {
                "comment": "Scene 1 with local TTS",
                "background-color": "#4392F1",
                "duration": 3,
                "elements": [
                    {
                        "type": "text",
                        "text": "J2V LOCAL CLONE",
                        "settings": {
                            "font-size": 80,
                            "font-color": "white",
                            "vertical-position": "center"
                        }
                    },
                    {
                        "type": "voice",
                        "text": "Welcome to the local JSON 2 Video clone test.",
                        "voice": "en-US-Emma",
                        "start": 0.5
                    }
                ]
            },
            {
                "comment": "Scene 2 with fade-in",
                "background-color": "#D22A1F",
                "duration": 2,
                "elements": [
                    {
                        "type": "text",
                        "text": "WORKS LIKE A CHARM",
                        "fade-in": 1.0,
                        "settings": {
                            "font-size": 60,
                            "font-color": "yellow",
                            "vertical-position": "bottom"
                        }
                    }
                ]
            }
        ]
    }

    print("🚀 Starting J2V Local Renderer...")
    renderer = J2VMovieRenderer(manifest)
    output_path = "/data/ssd/renders/j2v_smoke_test.mp4"
    renderer.render_full_movie(output_path)
    print(f"✅ Render finished: {output_path}")

if __name__ == "__main__":
    run_local_j2v_test()
