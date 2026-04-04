import json
import google.generativeai as genai
from google.generativeai.types import GenerationConfig
from google.api_core import retry
from typing import Optional, Dict

from backend.app.modules.color_book.generator.utils.console_messenger import ConsoleMessenger

try:
    from vertexai.preview.generative_models import (
        GenerativeModel as VertexGenerativeModel,
    )
except ImportError:
    ConsoleMessenger.error(
        "Vertex AI modules not found. Please ensure 'google-generativeai' is installed."
    )
    VertexGenerativeModel = None


class GenAIIntegration:
    """
    Handles communication with the GenAI model (Gemini for text generation).
    """

    def __init__(
        self,
        api_key: str,
        model_name: str,
        console_messenger: ConsoleMessenger,
    ) -> None:
        if not api_key or api_key == "YOUR_GENAI_API_KEY":
            raise ValueError(
                "Gemini API key not set. Check your .env file or environment variables."
            )
        if not model_name:
            raise ValueError("Model name for GenAI is not provided.")

        genai.configure(api_key=api_key)

        self.text_model: VertexGenerativeModel = genai.GenerativeModel(model_name)
        self.model_name: str = model_name
        self.console_messenger: ConsoleMessenger = console_messenger

        self.console_messenger.info(
            f"Gemini model '{model_name}' initialized successfully.", color="BLUE"
        )

    @retry.Retry(timeout=300)
    def generate_content_with_config(
        self, prompt: str, generation_config: Optional[GenerationConfig] = None
    ) -> Optional[str]:
        """
        Sends a prompt to GenAI with a given configuration.
        Returns the generated text or None if an error occurs.
        """
        try:
            response = self.text_model.generate_content(
                prompt, generation_config=generation_config
            )
            generated_text: Optional[str] = response.text if response else None
            return generated_text
        except Exception as e:
            self.console_messenger.error(
                f"An error occurred during communication with GenAI API: {e}"
            )
            return None

    @retry.Retry(timeout=300)
    def generate_project(self, full_prompt: str) -> Optional[Dict]:
        """
        Sends a pre-built prompt to GenAI (text model) to generate project structure.
        Returns the parsed JSON dictionary or None if generation fails.
        """
        self.console_messenger.info(
            "Starting project generation via GenAI...", color="CYAN"
        )

        generated_text: Optional[str] = self.generate_content_with_config(
            full_prompt, GenerationConfig(response_mime_type="application/json")
        )

        if not generated_text:
            self.console_messenger.warning(
                "Received empty or invalid response from GenAI (text)."
            )
            return None

        try:
            cleaned_response_text: str = generated_text.strip()
            if cleaned_response_text.startswith(
                "```json"
            ) and cleaned_response_text.endswith("```"):
                cleaned_response_text = cleaned_response_text[
                    len("```json") : -len("```")
                ].strip()

            parsed_json: Dict = json.loads(cleaned_response_text)
            self.console_messenger.success(
                "Project structure generated successfully!", color="GREEN"
            )
            return parsed_json
        except json.JSONDecodeError as e:
            self.console_messenger.error(
                f"Critical error: Failed to parse JSON response from GenAI (text). {e}"
            )
            display_response_text: str = generated_text
            if len(display_response_text) > 200:
                display_response_text = display_response_text[:197] + "..."
            self.console_messenger.error(
                f"Received partial response (parsing attempt): {display_response_text}"
            )
            return None
        except Exception as e:
            self.console_messenger.error(
                f"An error occurred during communication with GenAI API (text): {e}"
            )
            return None
