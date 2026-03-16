import os
import json
from backend.app.engine.j2v_renderer import J2VMovieRenderer

def run_local_j2v_test():
    # Manifest using 'iterate' and expressions
    manifest = {
        "resolution": "shorts",
        "fps": 24,
        "variables": {
            "slides": [
                {"title": "DYNAMIC SCENE 1", "color": "#4392F1", "text_color": "white"},
                {"title": "DYNAMIC SCENE 2", "color": "#D22A1F", "text_color": "yellow"},
                {"title": "SKIP ME", "color": "#000000", "text_color": "black", "skip": True}
            ]
        },
        "scenes": [
            {
                "iterate": "slides",
                "condition": "{{ skip != true }}",
                "background-color": "{{color}}",
                "duration": 2,
                "elements": [
                    {
                        "type": "text",
                        "text": "{{title}}",
                        "settings": {
                            "font-size": 80,
                            "font-color": "{{text_color}}",
                            "vertical-position": "center"
                        }
                    },
                    {
                        "type": "voice",
                        "text": "This is {{title}}",
                        "start": 0.5
                    }
                ]
            }
        ]
    }

    print("🚀 Starting J2V Local Renderer (Dynamic Mode)...")
    renderer = J2VMovieRenderer(manifest)
    output_path = "/data/ssd/renders/j2v_dynamic_test.mp4"
    renderer.render_full_movie(output_path)
    print(f"✅ Render finished: {output_path}")

if __name__ == "__main__":
    run_local_j2v_test()
