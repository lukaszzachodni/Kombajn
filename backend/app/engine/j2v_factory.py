from typing import Any, Dict
from .processors import J2VImageProcessor, J2VTextProcessor, J2VAudioProcessor, J2VVideoProcessor, J2VVoiceProcessor, J2VAudiogramProcessor, J2VSubtitlesProcessor, J2VComponentProcessor

class J2VProcessorFactory:
    """
    Registry for mapping J2V types to local processors.
    """
    _processors = {
        "image": J2VImageProcessor,
        "text": J2VTextProcessor,
        "audio": J2VAudioProcessor,
        "video": J2VVideoProcessor,
        "voice": J2VVoiceProcessor,
        "audiogram": J2VAudiogramProcessor,
        "subtitles": J2VSubtitlesProcessor,
        "component": J2VComponentProcessor
    }

    @classmethod
    def get_processor(cls, type_name: str) -> Any:
        proc_class = cls._processors.get(type_name)
        if not proc_class:
            raise ValueError(f"J2V Processor for '{type_name}' not implemented locally.")
        return proc_class()
