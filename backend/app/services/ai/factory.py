import os
from typing import Optional
from backend.app.services.ai.base import LLMProvider, ImageGenProvider
from backend.app.services.ai.providers.gemini import GeminiProvider
from backend.app.services.ai.providers.imagen import ImagenProvider

from backend.app.schemas.common.ai_preferences import AIPreferences
from backend.app.services.ai.providers.mock import MockLLMProvider, MockImageGenProvider

class AIServiceFactory:
    @staticmethod
    def get_llm_provider(preferences: Optional[AIPreferences] = None, **kwargs) -> LLMProvider:
        provider_name = preferences.llm_provider if preferences else kwargs.get("provider", "gemini")
        model_name = preferences.llm_model if preferences and preferences.llm_model else kwargs.get("model_name")

        if provider_name == "mock":
            return MockLLMProvider()

        if provider_name == "gemini":
            # ... rest unchanged ...

            api_key = kwargs.get("api_key") or os.getenv("GENAI_API_KEY")
            model_name = model_name or os.getenv("GENAI_MODEL_DEFAULT", "gemini-1.5-flash-latest")
            return GeminiProvider(api_key=api_key, model_name=model_name)
        
        if provider_name == "local":
            # Tu w przyszłości LocalLLMProvider
            raise NotImplementedError("Local LLM provider not implemented yet")
            
        raise ValueError(f"Unknown LLM provider: {provider_name}")

    @staticmethod
    def get_image_gen_provider(preferences: Optional[AIPreferences] = None, **kwargs) -> ImageGenProvider:
        provider_name = preferences.image_gen_provider if preferences else kwargs.get("provider", "imagen")
        model_name = preferences.image_gen_model if preferences and preferences.image_gen_model else kwargs.get("model_name")

        if provider_name == "mock":
            return MockImageGenProvider()

        if provider_name == "imagen":
            project_id = kwargs.get("project_id") or os.getenv("GCP_PROJECT_ID")
            location = kwargs.get("location") or os.getenv("GCP_LOCATION", "us-central1")
            model_name = model_name or os.getenv("IMAGEN_PAGE_MODEL_DEFAULT", "imagegeneration@006")
            return ImagenProvider(project_id=project_id, location=location, model_name=model_name)
        
        if provider_name == "local":
            # Tu w przyszłości LocalImageGenProvider (Stable Diffusion)
            raise NotImplementedError("Local ImageGen provider not implemented yet")
            
        raise ValueError(f"Unknown ImageGen provider: {provider_name}")
