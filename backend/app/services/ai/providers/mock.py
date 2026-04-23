import json
from typing import Optional, Dict, Any, List
from backend.app.services.ai.base import LLMProvider, ImageGenProvider

class MockLLMProvider(LLMProvider):
    def __init__(self, responses: Optional[Dict[str, Any]] = None):
        self.responses = responses or {}

    def generate_text(self, prompt: str, **kwargs) -> Optional[str]:
        return f"Mock response for: {prompt[:50]}..."

    def generate_json(self, prompt: str, **kwargs) -> Optional[Dict[str, Any]]:
        # Zwracamy przykładowy projekt jeśli nic nie zdefiniowano
        return self.responses.get(prompt, {
            "id": "mock_project_001",
            "title": "Mock Coloring Book",
            "coloringBook": {
                "mainProjectDetails": {"title": "Mock", "pageIdeas": []},
                "pagePromptLibrary": [],
                "languageVersions": {}
            }
        })

class MockImageGenProvider(ImageGenProvider):
    def generate_images(
        self, 
        prompt: str, 
        number_of_images: int = 1, 
        aspect_ratio: str = "1:1",
        **kwargs
    ) -> List[bytes]:
        # Zwraca mały pusty obrazek PNG (1x1 przezroczysty)
        return [
            b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\x0bIDAT\x08\x99c\xf8\xff\xff?\x00\x05\xfe\x02\xfe\xdcD\x05\xe8\x00\x00\x00\x00IEND\xaeB`\x82'
        ] * number_of_images
