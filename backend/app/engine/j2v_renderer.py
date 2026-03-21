import json
import re
import subprocess
import os
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
import numpy as np

# Force MoviePy to use the system ffmpeg which we know has NVENC support
os.environ["IMAGEIO_FFMPEG_EXE"] = "/usr/bin/ffmpeg"
from moviepy.config import change_settings
change_settings({"FFMPEG_BINARY": "/usr/bin/ffmpeg"})

from moviepy.editor import ColorClip, VideoClip, concatenate_videoclips, VideoFileClip, CompositeAudioClip

from .j2v_types import J2VMovie, J2VScene
from .j2v_factory import J2VProcessorFactory

class J2VMovieRenderer:
    RESOLUTION_MAP = {
        "full-hd": (1920, 1080),
        "shorts": (1080, 1920),
        "instagram": (1080, 1080),
        "hd": (1280, 720)
    }

    def __init__(self, manifest_dict: Dict[str, Any]):
        self.raw_manifest = manifest_dict
        self.movie_vars = manifest_dict.get("variables", {})
        self.movie = J2VMovie(**manifest_dict)
        self._resolve_resolution()
        self.temp_dir = Path("/data/ssd/temp") / "j2v_local"
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        self.video_codec = self._detect_codec()

    def _detect_codec(self) -> str:
        # Check for explicit manual override to simulate "No GPU" environment
        if os.environ.get("KOMBAJN_FORCE_CPU", "false").lower() == "true":
            print("DEBUG: GPU Override active via environment variable. Forcing software encoding (libx264).")
            return "libx264"

        # Priority list of encoders
        encoders = ["h264_nvenc", "hevc_nvenc"]
        
        # We need a small test file path
        test_file = self.temp_dir / f"gpu_test_{os.getpid()}.mp4"
        
        for enc in encoders:
            try:
                # Rigorous test: actually try to encode a tiny blank video
                # This ensures both ffmpeg supports the encoder AND the driver is working
                test_cmd = [
                    "/usr/bin/ffmpeg", "-y", "-f", "lavfi", "-i", "color=c=black:s=64x64:d=0.1",
                    "-c:v", enc, str(test_file)
                ]
                res = subprocess.run(test_cmd, capture_output=True, text=True, timeout=10)
                if res.returncode == 0 and test_file.exists():
                    print(f"DEBUG: GPU Acceleration ({enc}) verified and working in process {os.getpid()}.")
                    test_file.unlink()
                    return enc
                else:
                    print(f"DEBUG: GPU test for {enc} failed with code {res.returncode}. Stderr: {res.stderr}")
            except Exception as e:
                print(f"DEBUG: GPU test for {enc} failed with error: {e}")
                continue
            finally:
                if test_file.exists(): test_file.unlink()

        print("DEBUG: GPU Acceleration not working or not available. Using software encoding (libx264).")
        return "libx264"

    def _resolve_resolution(self):
        if self.movie.resolution in self.RESOLUTION_MAP:
            w, h = self.RESOLUTION_MAP[self.movie.resolution]
            self.movie.width = w
            self.movie.height = h

    def _evaluate_expression(self, expr: Any, context_vars: Dict[str, Any]) -> Any:
        if not isinstance(expr, str): return expr
        pattern = r"\{\{\s*(.*?)\s*\}\}"
        def replacer(match):
            key = match.group(1)
            for op in ["==", "!=", ">", "<"]:
                if op in key:
                    parts = key.split(op)
                    left = self._evaluate_expression(f"{{{{{parts[0].strip()}}}}}", context_vars)
                    right = parts[1].strip().strip("'").strip('"')
                    try:
                        l_f, r_f = float(left), float(right)
                        if op == "==": return str(l_f == r_f).lower()
                        if op == "!=": return str(l_f != r_f).lower()
                        if op == ">": return str(l_f > r_f).lower()
                        if op == "<": return str(l_f < r_f).lower()
                    except:
                        if op == "==": return str(str(left) == str(right)).lower()
                        if op == "!=": return str(str(left) != str(right)).lower()
            return str(context_vars.get(key, match.group(0)))
        result = re.sub(pattern, replacer, expr)
        if result.lower() == "true": return True
        if result.lower() == "false": return False
        return result

    def _should_render(self, condition: Optional[Union[str, bool]], context_vars: Dict[str, Any]) -> bool:
        if condition is None or condition == "": return True
        if isinstance(condition, bool): return condition
        val = self._evaluate_expression(condition, context_vars)
        return bool(val)

    def _process_variables(self, data: Any, context_vars: Dict[str, Any]) -> Any:
        if isinstance(data, dict): return {k: self._process_variables(v, context_vars) for k, v in data.items()}
        elif isinstance(data, list): return [self._process_variables(i, context_vars) for i in data]
        else: return self._evaluate_expression(data, context_vars)

    def render_scene(self, scene_dict: Dict[str, Any], index: int, global_vars: Dict[str, Any]) -> List[str]:
        print(f"DEBUG: Processing scene {index}...")
        iterate_key = scene_dict.get("iterate")
        items_to_iterate = []
        if iterate_key and iterate_key in global_vars:
            for item_data in global_vars[iterate_key]:
                new_scene = scene_dict.copy()
                new_scene.pop("iterate")
                items_to_iterate.append((new_scene, {**global_vars, **item_data}))
        else: items_to_iterate = [(scene_dict, global_vars)]

        rendered_paths = []
        for i, (s_dict, context_vars) in enumerate(items_to_iterate):
            if not self._should_render(s_dict.get("condition"), context_vars):
                print(f"DEBUG: Skipping scene {index} due to condition")
                continue
            
            s_data = self._process_variables(s_dict, context_vars)
            scene = J2VScene(**s_data)
            output_path = self.temp_dir / f"scene_{index}_{i:03d}.mp4"
            bg_duration = scene.duration if scene.duration > 0 else 5.0
            
            visual_clips = []
            audio_items = []
            
            bg_color_hex = scene.background_color.lstrip('#')
            bg_rgb = tuple(int(bg_color_hex[i:i+2], 16) for i in (0, 2, 4))
            bg_clip = ColorClip(size=(self.movie.width, self.movie.height), color=bg_rgb, duration=bg_duration)
            visual_clips.append(bg_clip)

            for el_data in s_data.get("elements", []):
                try:
                    processor = J2VProcessorFactory.get_processor(el_data["type"])
                    clip = processor.process(self.movie.width, self.movie.height, el_data, bg_duration)
                    if clip:
                        if hasattr(clip, "w") and hasattr(clip, "h"):
                            visual_clips.append(clip)
                            if clip.audio: audio_items.append(clip.audio)
                        else: audio_items.append(clip)
                    else: print(f"WARNING: Processor for {el_data.get('type')} returned None!")
                except Exception as e:
                    print(f"CRITICAL ERROR in processor for {el_data.get('type')}: {e}")
                    raise e

            scene_duration = scene.duration if scene.duration != -1 else bg_duration

            def resolve_pos(pos, frame_size, clip_size):
                fw, fh = frame_size
                cw, ch = clip_size
                if isinstance(pos, (tuple, list)):
                    x = (fw - cw) // 2 if pos[0] == 'center' else (fw - cw if pos[0] == 'right' else int(pos[0]))
                    y = (fh - ch) // 2 if pos[1] == 'center' else (fh - ch if pos[1] == 'bottom' else int(pos[1]))
                    return x, y
                if isinstance(pos, str):
                    if pos == 'center': return (fw - cw) // 2, (fh - ch) // 2
                return 0, 0

            def make_frame(t):
                frame = visual_clips[0].get_frame(t).copy()
                fh, fw = frame.shape[:2]
                for clip in visual_clips[1:]:
                    if clip.start <= t < clip.end:
                        clip_frame = clip.get_frame(t - clip.start)
                        ch, cw = clip_frame.shape[:2]
                        x, y = resolve_pos(clip.pos(t - clip.start), (fw, fh), (cw, ch))
                        if clip.mask:
                            mask = clip.mask.get_frame(t - clip.start)
                            if len(mask.shape) == 2: mask = np.dstack([mask]*3)
                            x1, y1 = max(0, int(x)), max(0, int(y))
                            x2, y2 = min(fw, x1 + cw), min(fh, y1 + ch)
                            cx1, cy1 = max(0, -int(x)), max(0, -int(y))
                            frame[y1:y2, x1:x2] = (mask[cy1:cy1+(y2-y1), cx1:cx1+(x2-x1)] * clip_frame[cy1:cy1+(y2-y1), cx1:cx1+(x2-x1)] + (1 - mask[cy1:cy1+(y2-y1), cx1:cx1+(x2-x1)]) * frame[y1:y2, x1:x2]).astype('uint8')
                        else:
                            x1, y1 = max(0, int(x)), max(0, int(y))
                            x2, y2 = min(fw, x1 + cw), min(fh, y1 + ch)
                            frame[y1:y2, x1:x2] = clip_frame[max(0, -int(y)):max(0, -int(y))+(y2-y1), max(0, -int(x)):max(0, -int(x))+(x2-x1)]
                return frame

            final_visual = VideoClip(make_frame, duration=scene_duration)
            if audio_items:
                safe_audio = []
                for a in audio_items:
                    actual_duration = min(a.duration, scene_duration - a.start)
                    if actual_duration > 0: safe_audio.append(a.subclip(0, actual_duration).set_start(a.start))
                if safe_audio: final_visual = final_visual.set_audio(CompositeAudioClip(safe_audio))

            final_visual.write_videofile(str(output_path), fps=self.movie.fps, codec=self.video_codec, audio_codec="aac", logger=None)
            for c in visual_clips: c.close()
            for a in audio_items: a.close()
            rendered_paths.append(str(output_path))
            print(f"DEBUG: Successfully rendered {output_path}")
        return rendered_paths

    def render_full_movie(self, output_path: str):
        all_scene_files = []
        for i, scene in enumerate(self.movie.scenes):
            # Convert Pydantic scene to dict for renderer compatibility
            scene_dict = scene.model_dump()
            paths = self.render_scene(scene_dict, i, self.movie_vars)
            all_scene_files.extend(paths)
        if not all_scene_files: raise ValueError("No scenes rendered.")
        clips = [VideoFileClip(p) for p in all_scene_files]
        final_video = concatenate_videoclips(clips, method="compose")
        final_video.write_videofile(output_path, fps=self.movie.fps, codec=self.video_codec, audio_codec="aac")
        for c in clips: c.close()
        for p in all_scene_files: Path(p).unlink()
