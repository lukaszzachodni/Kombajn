from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union

class LLMProvider(ABC):
    @abstractmethod
    def generate_text(self, prompt: str, **kwargs) -> Optional[str]:
        """Generuje czysty tekst na podstawie promptu."""
        pass

    @abstractmethod
    def generate_json(self, prompt: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Generuje i parsuje JSON na podstawie promptu."""
        pass

class ImageGenProvider(ABC):
    @abstractmethod
    def generate_images(
        self, 
        prompt: str, 
        number_of_images: int = 1, 
        aspect_ratio: str = "1:1",
        **kwargs
    ) -> List[bytes]:
        """Generuje listę obrazów w formacie bytes (PNG/JPG)."""
        pass
