from typing import Dict, Type
from .base import ClipProcessor
from .processors import ColorProcessor, ImageProcessor, TextProcessor

class ProcessorFactory:
    """
    Registry for mapping manifest types to their respective processors.
    Supports Open/Closed principle: add a new entry to _registry to support new types.
    """
    _registry: Dict[str, Type[ClipProcessor]] = {
        "color": ColorProcessor,
        "image": ImageProcessor,
        "text": TextProcessor,
    }

    @classmethod
    def get_processor(cls, type_name: str) -> ClipProcessor:
        """Instantiates the correct processor based on type."""
        processor_class = cls._registry.get(type_name)
        if not processor_class:
            raise ValueError(f"No rendering processor registered for type: '{type_name}'")
        return processor_class()
