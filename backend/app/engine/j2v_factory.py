from .processors.image import J2VImageProcessor
from .processors.text import J2VTextProcessor
from .processors.audio import J2VAudioProcessor
from .processors.video import J2VVideoProcessor
from .processors.voice import J2VVoiceProcessor
from .processors.audiogram import J2VAudiogramProcessor
from .processors.subtitles import J2VSubtitlesProcessor
from .processors.component import J2VComponentProcessor

class J2VProcessorFactory:
    _processors = {
        "image": J2VImageProcessor(),
        "text": J2VTextProcessor(),
        "audio": J2VAudioProcessor(),
        "video": J2VVideoProcessor(),
        "voice": J2VVoiceProcessor(),
        "audiogram": J2VAudiogramProcessor(),
        "subtitles": J2VSubtitlesProcessor(),
        "component": J2VComponentProcessor(),
    }

    @staticmethod
    def get_processor(type_name: str):
        return J2VProcessorFactory._processors.get(type_name)
