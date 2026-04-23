import json
import google.generativeai as genai
from google.generativeai.types import GenerationConfig
from google.api_core import retry
from typing import Optional, Dict, Any
from backend.app.services.ai.base import LLMProvider

class GeminiProvider(LLMProvider):
    def __init__(self, api_key: str, model_name: str):
        if not api_key:
            raise ValueError("Gemini API key is required")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)
        self.model_name = model_name

    @retry.Retry(timeout=300)
    def generate_text(self, prompt: str, **kwargs) -> Optional[str]:
        try:
            response = self.model.generate_content(prompt)
            return response.text if response else None
        except Exception as e:
            print(f"Gemini error (text): {e}")
            return None

    @retry.Retry(timeout=300)
    def generate_json(self, prompt: str, **kwargs) -> Optional[Dict[str, Any]]:
        try:
            # Używamy natywnego wsparcia dla JSON w Gemini jeśli model to wspiera
            generation_config = GenerationConfig(response_mime_type="application/json")
            response = self.model.generate_content(prompt, generation_config=generation_config)
            
            if not response or not response.text:
                return None
                
            cleaned_text = response.text.strip()
            # Usuwamy ewentualne bloki kodu markdown
            if cleaned_text.startswith("```json"):
                cleaned_text = cleaned_text[7:-3].strip()
            elif cleaned_text.startswith("```"):
                cleaned_text = cleaned_text[3:-3].strip()
                
            return json.loads(cleaned_text)
        except Exception as e:
            print(f"Gemini error (json): {e}")
            return None
