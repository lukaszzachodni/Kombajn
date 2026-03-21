from typing import Dict, Any, Type, Optional
import logging

logger = logging.getLogger(__name__)

class J2VProcessorFactory:
    _processors: Dict[str, Any] = {}

    @classmethod
    def register(cls, type_name: str):
        """Decorator to register a processor class."""
        def wrapper(processor_cls: Type):
            instance = processor_cls()
            cls._processors[type_name] = instance
            logger.info(f"Registered processor: {type_name} -> {processor_cls.__name__}")
            return processor_cls
        return wrapper

    @classmethod
    def get_processor(cls, type_name: str) -> Optional[Any]:
        """Retrieve a registered processor instance."""
        processor = cls._processors.get(type_name)
        if not processor:
            logger.warning(f"No processor found for type: {type_name}")
        return processor

# Import processors to trigger registration
# Note: In a real app, this could be automated with glob/importlib
from .processors.image import J2VImageProcessor
from .processors.text import J2VTextProcessor
from .processors.audio import J2VAudioProcessor
from .processors.video import J2VVideoProcessor
from .processors.voice import J2VVoiceProcessor
from .processors.audiogram import J2VAudiogramProcessor
from .processors.subtitles import J2VSubtitlesProcessor
from .processors.component import J2VComponentProcessor

# Manually register them for now (or move decorators to the classes themselves)
J2VProcessorFactory._processors = {
    "image": J2VImageProcessor(),
    "text": J2VTextProcessor(),
    "audio": J2VAudioProcessor(),
    "video": J2VVideoProcessor(),
    "voice": J2VVoiceProcessor(),
    "audiogram": J2VAudiogramProcessor(),
    "subtitles": J2VSubtitlesProcessor(),
    "component": J2VComponentProcessor(),
}
