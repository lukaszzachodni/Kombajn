from abc import ABC, abstractmethod
from typing import Any
from moviepy.Clip import Clip

class ClipProcessor(ABC):
    """
    Abstract interface for all clip-generating processors.
    Follows Interface Segregation and Liskov Substitution.
    """
    @abstractmethod
    def create_clip(self, width: int, height: int, context: Any, **kwargs) -> Clip:
        """
        Creates a MoviePy clip based on provided data.
        
        :param width: Target width of the project.
        :param height: Target height of the project.
        :param context: The Pydantic model containing logic (Element or Background).
        :param kwargs: Additional metadata (like bg_duration).
        """
        pass
