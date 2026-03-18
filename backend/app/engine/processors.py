from typing import Any, Dict, Tuple, Optional, List, Union
from moviepy.editor import ImageClip, TextClip, AudioFileClip, VideoFileClip, ColorClip, afx, vfx
from moviepy.Clip import Clip
from .j2v_base_processor import J2VBaseProcessor
from .j2v_types import (
    ImageElement, TextElement, AudioElement, VideoElement, 
    VoiceElement, AudiogramElement, SubtitlesElement, ComponentElement
)
from .base import ClipProcessor

# --- OLD ENGINE PROCESSORS (For backward compatibility) ---

class ColorProcessor(ClipProcessor):
    def create_clip(self, width: int, height: int, context: Any, bg_duration: float = 0.0) -> Clip:
        duration = context.duration if context.duration > 0 else 5.0
        color = context.color
        if isinstance(color, str) and color.startswith("#"):
            color = tuple(int(color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
        return ColorClip(size=(width, height), color=color, duration=duration)

class ImageProcessor(ClipProcessor):
    def create_clip(self, width: int, height: int, context: Any, bg_duration: float = 0.0) -> Clip:
        path = getattr(context, "path", getattr(context, "src", None))
        duration = getattr(context, "duration", bg_duration)
        clip = ImageClip(path).set_duration(duration)
        return clip.resize(width=width) if (width/height < clip.w/clip.h) else clip.resize(height=height)

class TextProcessor(ClipProcessor):
    def create_clip(self, width: int, height: int, context: Any, bg_duration: float = 0.0) -> Clip:
        duration = getattr(context, "duration", None) or (bg_duration - getattr(context, "start_time", 0.0))
        clip = TextClip(
            context.text,
            fontsize=getattr(context, "fontsize", 70),
            color=getattr(context, "color", "white"),
            font=getattr(context, "font", "DejaVu-Sans"),
            method="label"
        ).set_duration(duration).set_start(getattr(context, "start_time", 0.0))
        pos = getattr(context, "position", "center")
        return clip.set_position(pos)


# --- J2V CLONE PROCESSORS ---

class J2VProcessor:
    """Interface for J2V processors."""
    def process(self, width: int, height: int, element_data: Dict[str, Any], container_duration: float) -> Clip:
        pass

class J2VImageProcessor(J2VProcessor):
    def process(self, width: int, height: int, element_data: Dict[str, Any], container_duration: float) -> Clip:
        el = ImageElement(**element_data)
        clip = ImageClip(el.src)
        if el.resize == "cover":
            clip = clip.resize(width=width) if (width/height > clip.w/clip.h) else clip.resize(height=height)
        elif el.resize == "fit":
            clip = clip.resize(width=width) if (width/height < clip.w/clip.h) else clip.resize(height=height)
        pos_map = {"top-left": (0.05*width, 0.05*height), "center-center": ("center", "center")}
        clip = clip.set_position(pos_map.get(el.position, (el.x, el.y)))
        return J2VBaseProcessor.apply_common_properties(clip, el, container_duration)

class J2VTextProcessor(J2VProcessor):
    def process(self, width: int, height: int, element_data: Dict[str, Any], container_duration: float) -> Clip:
        el = TextElement(**element_data)
        settings = el.settings
        duration = el.duration if el.duration > 0 else container_duration
        txt_clip = TextClip(
            el.text,
            fontsize=int(settings.get("font-size", 70)),
            color=settings.get("font-color", "white"),
            font="Arial",
            method="caption",
            size=(width, None)
        ).set_duration(duration)
        if txt_clip.ismask: txt_clip = txt_clip.to_RGB()
        v_pos = settings.get("vertical-position", "center")
        h_pos = settings.get("horizontal-position", "center")
        txt_clip = txt_clip.set_position((h_pos, v_pos)).set_start(el.start)
        return J2VBaseProcessor.apply_common_properties(txt_clip, el, container_duration)

class J2VAudioProcessor(J2VProcessor):
    def process(self, width: int, height: int, element_data: Dict[str, Any], container_duration: float) -> Clip:
        el = AudioElement(**element_data)
        audio = AudioFileClip(el.src)
        if el.seek > 0: audio = audio.subclip(el.seek)
        safe_duration = el.duration if el.duration > 0 else (container_duration if el.duration == -2 else audio.duration)
        if el.loop == -1 or el.loop > 1:
            audio = audio.fx(afx.audio_loop, duration=safe_duration)
        else:
            audio = audio.subclip(0, min(audio.duration, safe_duration))
        if el.muted: audio = audio.volumex(0)
        else: audio = audio.volumex(el.volume)
        return J2VBaseProcessor.apply_common_properties(audio, el, container_duration)

class J2VVideoProcessor(J2VProcessor):
    def process(self, width: int, height: int, element_data: Dict[str, Any], container_duration: float) -> Clip:
        el = VideoElement(**element_data)
        clip = VideoFileClip(el.src)
        if el.seek > 0: clip = clip.subclip(el.seek)
        if el.resize == "cover":
            clip = clip.resize(width=width) if (width/height > clip.w/clip.h) else clip.resize(height=height)
        elif el.resize == "fit":
            clip = clip.resize(width=width) if (width/height < clip.w/clip.h) else clip.resize(height=height)
        if el.flip_horizontal: clip = clip.fx(vfx.mirror_x)
        if el.flip_vertical: clip = clip.fx(vfx.mirror_y)
        if el.muted: clip = clip.without_audio()
        elif el.volume != 1.0: clip = clip.volumex(el.volume)
        pos_map = {"top-left": (0.05*width, 0.05*height), "center-center": ("center", "center")}
        clip = clip.set_position(pos_map.get(el.position, (el.x, el.y)))
        duration = el.duration if el.duration > 0 else container_duration
        if el.loop == -1 or el.loop > 1: clip = clip.fx(vfx.loop, duration=duration)
        return J2VBaseProcessor.apply_common_properties(clip, el, container_duration)

class J2VVoiceProcessor(J2VProcessor):
    def process(self, width: int, height: int, element_data: Dict[str, Any], container_duration: float) -> Clip:
        el = VoiceElement(**element_data)
        from gtts import gTTS
        import uuid
        from pathlib import Path
        temp_path = Path("/data/ssd/temp/j2v_tts") / f"tts_{uuid.uuid4()}.mp3"
        temp_path.parent.mkdir(parents=True, exist_ok=True)
        lang = el.voice.split("-")[0] if el.voice and "-" in el.voice else "en"
        gTTS(text=el.text, lang=lang).save(str(temp_path))
        audio = AudioFileClip(str(temp_path))
        audio = audio.subclip(0, audio.duration)
        if el.muted: audio = audio.volumex(0)
        else: audio = audio.volumex(el.volume)
        return J2VBaseProcessor.apply_common_properties(audio, el, container_duration)

class J2VAudiogramProcessor(J2VProcessor):
    def process(self, width: int, height: int, element_data: Dict[str, Any], container_duration: float) -> Clip:
        el = AudiogramElement(**element_data)
        clip = ColorClip(size=(width//2, 100), color=(255,255,255), duration=container_duration).set_opacity(el.opacity).set_position(("center", "bottom"))
        return J2VBaseProcessor.apply_common_properties(clip, el, container_duration)

class J2VSubtitlesProcessor(J2VProcessor):
    def process(self, width: int, height: int, element_data: Dict[str, Any], container_duration: float) -> Clip:
        el = SubtitlesElement(**element_data)
        txt = TextClip("Local Subtitles Placeholder", fontsize=40, color='yellow').set_position(("center", "bottom"))
        return J2VBaseProcessor.apply_common_properties(txt, el, container_duration)

class J2VComponentProcessor(J2VProcessor):
    def process(self, width: int, height: int, element_data: Dict[str, Any], container_duration: float) -> Clip:
        el = ComponentElement(**element_data)
        txt = TextClip(f"Component: {el.component}", fontsize=50, color='white', bg_color='blue').set_position("center")
        return J2VBaseProcessor.apply_common_properties(txt, el, container_duration)
